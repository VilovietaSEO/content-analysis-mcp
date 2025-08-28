#!/usr/bin/env python3
"""
Unified Content Quality Analyzer for Chroma Collections

This single script handles all content quality analysis needs:
- Individual content quality scoring (5 dimensions)
- Website content strategy analysis
- Competitive analysis across collections
- Hierarchical navigation and filtering
- Enhanced metadata structure support

Works with both legacy collections and new enhanced metadata structure.

Usage Examples:
  python content-quality-analyzer.py                                    # List all collections
  python content-quality-analyzer.py collection_name                    # Analyze specific collection
  python content-quality-analyzer.py collection_name --mode individual  # Individual content scoring
  python content-quality-analyzer.py collection_name --mode website     # Website strategy analysis
  python content-quality-analyzer.py collection_name --mode competitive # Competitive analysis
  python content-quality-analyzer.py --help                            # Show all options
"""

import chromadb
import re
import json
import argparse
import sys
import statistics
from typing import Dict, List, Any, Optional
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime


class ContentQualityAnalyzer:
    def __init__(self, chroma_dir: str = ".", verbose: bool = False):
        """Initialize analyzer with Chroma directory"""
        self.chroma_dir = Path(chroma_dir)
        self.client = chromadb.PersistentClient(path=str(self.chroma_dir))
        self.verbose = verbose
        
        # Quality analysis patterns
        self.precision_words = {
            'vague': ['thing', 'stuff', 'something', 'anything', 'everything', 'nothing', 'very', 'really', 'quite', 'pretty'],
            'precise': ['specifically', 'precisely', 'exactly', 'particularly', 'namely', 'explicitly', 'definitively'],
            'weak_modifiers': ['kind of', 'sort of', 'pretty much', 'more or less', 'basically', 'generally'],
            'fillers': ['um', 'uh', 'like', 'you know', 'I mean'],
            'business_strong': ['guaranteed', 'proven', 'certified', 'licensed', 'experienced', 'professional', 'trusted']
        }
        
        self.certainty_markers = {
            'uncertain': ['might', 'maybe', 'perhaps', 'possibly', 'could be', 'seems to', 'appears to', 'may'],
            'certain': ['is', 'are', 'will', 'must', 'definitely', 'certainly', 'clearly', 'obviously'],
            'business_confident': ['guarantee', 'ensure', 'committed', 'dedicated', 'promise', 'deliver'],
            'hedging': ['I think', 'I believe', 'in my opinion', 'it seems', 'probably', 'likely'],
            'strong': ['always', 'never', 'all', 'every', 'completely', 'totally', 'absolutely']
        }
        
        # Content type patterns for context-aware scoring
        self.content_types = {
            'tutorial': ['step', 'guide', 'how to', 'tutorial', 'walkthrough', 'instructions'],
            'technical': ['api', 'function', 'method', 'parameter', 'configuration', 'implementation'],
            'review': ['pros', 'cons', 'rating', 'review', 'comparison', 'versus'],
            'listicle': ['top', 'best', 'worst', 'list', 'tips', 'ways', 'reasons'],
            'news': ['announced', 'released', 'update', 'new', 'latest', 'breaking'],
            'legal': ['attorney', 'lawyer', 'law', 'legal', 'court', 'injury', 'accident'],
            'business': ['service', 'company', 'business', 'professional', 'contact', 'experience'],
            'roofing': ['roof', 'roofing', 'contractor', 'repair', 'install', 'shingles'],
            'healthcare': ['doctor', 'medical', 'health', 'clinic', 'treatment', 'patient']
        }
        
        # Trust signal patterns
        self.trust_signals = [
            'licensed', 'insured', 'certified', 'years.*experience', 'professional', 
            'trusted', 'rated', 'reviews', 'testimonial', 'guarantee', 'warranty',
            'award', 'accredited', 'expert', 'specialist'
        ]
        
        # CTA patterns
        self.cta_patterns = [
            r'schedule.*consultation', r'call.*now', r'contact.*us', r'get.*quote', 
            r'learn.*more', r'click.*here', r'book.*appointment', r'free.*estimate',
            r'request.*evaluation', r'start.*today', r'sign.*up'
        ]

    def _detect_content_type(self, text: str, metadata: Dict = None) -> str:
        """Detect content type from text and metadata"""
        combined_text = text.lower()
        
        # Check metadata for additional context
        if metadata:
            url = metadata.get('url', '').lower()
            source = metadata.get('source', '').lower()
            site_domain = metadata.get('site_domain', '').lower()
            combined_text += f" {url} {source} {site_domain}"
        
        # Score each content type
        type_scores = {}
        for content_type, keywords in self.content_types.items():
            score = sum(1 for keyword in keywords if keyword in combined_text)
            if score > 0:
                type_scores[content_type] = score
        
        # Return highest scoring type, or 'general' if none
        if type_scores:
            return max(type_scores.items(), key=lambda x: x[1])[0]
        return 'general'

    def _extract_raw_heading(self, text: str) -> str:
        """Extract the first heading from markdown text"""
        lines = text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('#'):
                # Remove markdown heading markers and clean
                heading = re.sub(r'^#+\s*', '', line).strip()
                # Remove any trailing markdown or links
                heading = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', heading)
                heading = re.sub(r'[*_`]', '', heading)
                if heading:
                    return heading
        return "No heading found"

    def _detect_document_type(self, documents: List[Dict]) -> str:
        """Detect if we have pre-chunked sections or whole documents"""
        if not documents:
            return 'unknown'
        
        # Check first few documents for section metadata indicators
        for doc in documents[:3]:
            metadata = doc.get('metadata', {})
            # Pre-chunked indicators
            if metadata.get('section_name') or metadata.get('hierarchy'):
                return 'pre_chunked'
        
        # If no section metadata found, assume whole documents
        return 'whole_document'

    def _generate_hierarchy_id(self, existing_sections: List[Dict], level: int) -> str:
        """Generate hierarchy IDs like 1.0, 1.1, 2.0, 2.1.1"""
        # Count sections at each level to generate proper numbering
        level_counts = [0] * 6  # Support up to 6 levels deep
        
        for section in existing_sections:
            section_level = section.get('level', 1)
            if section_level <= len(level_counts):
                level_counts[section_level - 1] += 1
                # Reset deeper levels when we encounter a higher level
                for i in range(section_level, len(level_counts)):
                    level_counts[i] = 0
        
        # Increment current level
        if level <= len(level_counts):
            level_counts[level - 1] += 1
            # Reset deeper levels
            for i in range(level, len(level_counts)):
                level_counts[i] = 0
        
        # Build hierarchy string (e.g., "2.1.3")
        hierarchy_parts = []
        for i in range(level):
            if i < len(level_counts) and level_counts[i] > 0:
                hierarchy_parts.append(str(level_counts[i]))
        
        return '.'.join(hierarchy_parts) if hierarchy_parts else '1.0'

    def _extract_sections_from_whole_document(self, document: Dict) -> List[Dict]:
        """Extract sections from a whole document based on headings"""
        text = document.get('text', '')
        metadata = document.get('metadata', {})
        sections = []
        
        # Split by headings (# ## ### ####)
        heading_pattern = r'^(#{1,4})\s+(.+)$'
        lines = text.split('\n')
        current_section = []
        current_heading = None
        current_level = 0
        
        for line in lines:
            line_stripped = line.strip()
            heading_match = re.match(heading_pattern, line_stripped)
            
            if heading_match:
                # Save previous section if we have one
                if current_section and current_heading:
                    section_text = '\n'.join(current_section).strip()
                    if section_text:  # Only add non-empty sections
                        hierarchy_id = self._generate_hierarchy_id(sections, current_level)
                        
                        # Create section metadata combining original metadata
                        section_metadata = metadata.copy()
                        section_metadata.update({
                            'hierarchy': hierarchy_id,
                            'section_heading': current_heading,
                            'section_level': current_level,
                            'word_count': len(section_text.split()),
                            'extracted_from_whole': True
                        })
                        
                        # Generate section name from heading
                        section_name = re.sub(r'[^\w\s]', '', current_heading.lower())
                        section_name = re.sub(r'\s+', '_', section_name.strip())
                        section_metadata['section_name'] = section_name
                        
                        sections.append({
                            'text': section_text,
                            'metadata': section_metadata,
                            'heading': current_heading,
                            'level': current_level
                        })
                
                # Start new section
                current_level = len(heading_match.group(1))
                current_heading = heading_match.group(2).strip()
                current_section = [line]
            else:
                current_section.append(line)
        
        # Add final section
        if current_section and current_heading:
            section_text = '\n'.join(current_section).strip()
            if section_text:
                hierarchy_id = self._generate_hierarchy_id(sections, current_level)
                
                section_metadata = metadata.copy()
                section_metadata.update({
                    'hierarchy': hierarchy_id,
                    'section_heading': current_heading,
                    'section_level': current_level,
                    'word_count': len(section_text.split()),
                    'extracted_from_whole': True
                })
                
                section_name = re.sub(r'[^\w\s]', '', current_heading.lower())
                section_name = re.sub(r'\s+', '_', section_name.strip())
                section_metadata['section_name'] = section_name
                
                sections.append({
                    'text': section_text,
                    'metadata': section_metadata,
                    'heading': current_heading,
                    'level': current_level
                })
        
        # If no headings found, treat entire document as one section
        if not sections and text.strip():
            section_metadata = metadata.copy()
            section_metadata.update({
                'hierarchy': '1.0',
                'section_heading': 'Full Document',
                'section_level': 1,
                'word_count': len(text.split()),
                'extracted_from_whole': True,
                'section_name': 'full_document'
            })
            
            sections.append({
                'text': text,
                'metadata': section_metadata,
                'heading': 'Full Document',
                'level': 1
            })
        
        return sections

    def _detect_analysis_mode(self, collection_name: str, results: Dict) -> str:
        """Auto-detect the best analysis mode based on collection structure"""
        if not results['metadatas']:
            return 'individual'
        
        # Check if we have multiple domains (competitive analysis)
        domains = set()
        enhanced_metadata_count = 0
        
        for meta in results['metadatas']:
            if meta:
                if 'site_domain' in meta or 'competitor_domain' in meta:
                    domains.add(meta.get('site_domain', meta.get('competitor_domain', 'unknown')))
                
                # Check for enhanced metadata
                if 'hierarchy' in meta or 'page_flow_stage' in meta:
                    enhanced_metadata_count += 1
        
        # Decision logic
        if len(domains) > 1:
            return 'competitive'
        elif enhanced_metadata_count > len(results['metadatas']) * 0.5:
            return 'website'
        else:
            return 'individual'

    # ===========================================
    # INDIVIDUAL CONTENT QUALITY ANALYSIS
    # ===========================================

    def analyze_word_precision(self, text: str, content_type: str = 'general') -> float:
        """Analyze vocabulary precision (0-1 scale)"""
        words = text.lower().split()
        total_words = len(words)
        if total_words == 0:
            return 0.0
        
        # Count different word types
        vague_count = sum(1 for word in words if any(v in word for v in self.precision_words['vague']))
        precise_count = sum(1 for phrase in self.precision_words['precise'] if phrase in text.lower())
        weak_modifier_count = sum(1 for phrase in self.precision_words['weak_modifiers'] if phrase in text.lower())
        filler_count = sum(1 for phrase in self.precision_words['fillers'] if phrase in text.lower())
        
        # Calculate ratios
        precision_ratio = precise_count / total_words if total_words > 0 else 0
        vagueness_penalty = (vague_count + weak_modifier_count + filler_count) / total_words if total_words > 0 else 0
        
        # Adjust scoring based on content type
        base_score = 0.7
        if content_type in ['technical', 'legal', 'healthcare']:
            base_score = 0.8
            precision_weight = 0.4
        elif content_type in ['tutorial', 'business']:
            base_score = 0.75
            precision_weight = 0.35
        else:
            precision_weight = 0.3
        
        score = max(0.0, min(1.0, base_score + (precision_ratio * precision_weight) - (vagueness_penalty * 0.4)))
        return round(score, 3)

    def analyze_modal_certainty(self, text: str, content_type: str = 'general') -> float:
        """Analyze confidence and certainty in statements (0-1 scale)"""
        text_lower = text.lower()
        
        # Count certainty markers
        uncertain_count = sum(1 for marker in self.certainty_markers['uncertain'] if marker in text_lower)
        certain_count = sum(1 for marker in self.certainty_markers['certain'] if marker in text_lower)
        hedging_count = sum(1 for hedge in self.certainty_markers['hedging'] if hedge in text_lower)
        strong_count = sum(1 for strong in self.certainty_markers['strong'] if strong in text_lower)
        
        # Count sentences
        sentences = len([s for s in re.split(r'[.!?]+', text) if s.strip()])
        if sentences == 0:
            return 0.5
        
        # Calculate ratios
        certainty_ratio = (certain_count + strong_count * 0.5) / sentences if sentences > 0 else 0
        uncertainty_penalty = (uncertain_count + hedging_count * 1.2) / sentences if sentences > 0 else 0
        
        # Adjust expectations based on content type
        base_score = 0.6
        if content_type in ['technical', 'legal', 'business', 'healthcare']:
            base_score = 0.7
        elif content_type == 'review':
            base_score = 0.55
        
        score = max(0.0, min(1.0, base_score + (certainty_ratio * 0.4) - (uncertainty_penalty * 0.3)))
        return round(score, 3)

    def analyze_structure_efficiency(self, text: str, content_type: str = 'general') -> float:
        """Analyze content organization and structure (0-1 scale)"""
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        if not sentences:
            return 0.0
        
        # Sentence length analysis
        sentence_lengths = [len(s.split()) for s in sentences]
        avg_length = sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0
        length_variance = statistics.variance(sentence_lengths) if len(sentence_lengths) > 1 else 0
        
        # Transition analysis
        transitions = ['however', 'therefore', 'furthermore', 'moreover', 'consequently', 
                      'additionally', 'meanwhile', 'nevertheless', 'first', 'second', 
                      'finally', 'in conclusion', 'for example', 'in contrast']
        transition_count = sum(1 for trans in transitions if trans in text.lower())
        
        # Structure indicators based on content type
        structure_bonus = 0
        if content_type == 'tutorial':
            step_indicators = len(re.findall(r'step\s+\d+|^\d+\.|first|second|third|next|then|finally', text.lower()))
            structure_bonus = min(0.3, step_indicators / max(1, len(paragraphs)))
        elif content_type == 'listicle':
            list_indicators = len(re.findall(r'^\d+\.|•|→|▶', text))
            structure_bonus = min(0.3, list_indicators / max(1, len(paragraphs)))
        elif content_type in ['legal', 'business', 'healthcare']:
            structure_bonus = 0.1
        
        # Calculate component scores
        length_score = min(1.0, length_variance / 50) if length_variance > 0 else 0.5
        transition_score = min(1.0, transition_count / max(1, len(paragraphs)))
        paragraph_score = min(1.0, len(paragraphs) / 8) if len(text) > 300 else 0.8
        
        score = (length_score * 0.3 + transition_score * 0.3 + paragraph_score * 0.4 + structure_bonus)
        return round(max(0.1, min(1.0, score)), 3)

    def analyze_punctuation_impact(self, text: str, content_type: str = 'general') -> float:
        """Analyze effective use of punctuation (0-1 scale)"""
        if not text:
            return 0.0
        
        # Count punctuation types
        periods = text.count('.')
        questions = text.count('?')
        exclamations = text.count('!')
        commas = text.count(',')
        colons = text.count(':')
        semicolons = text.count(';')
        dashes = text.count('—') + text.count('–')
        parentheses = text.count('(')
        
        total_chars = len(text)
        sentences = len([s for s in re.split(r'[.!?]+', text) if s.strip()])
        
        if sentences == 0:
            return 0.0
        
        # Calculate punctuation metrics
        total_punct = periods + questions + exclamations + commas + colons + semicolons
        punctuation_density = total_punct / total_chars if total_chars > 0 else 0
        
        # Sentence ending variety
        ending_types = sum(1 for count in [periods, questions, exclamations] if count > 0)
        ending_variety_score = ending_types / 3
        
        # Comma usage
        comma_ratio = commas / sentences if sentences > 0 else 0
        comma_score = min(1.0, comma_ratio / 2.5)
        
        # Advanced punctuation usage
        advanced_punct_score = min(1.0, (colons + semicolons + dashes + parentheses) / sentences)
        
        # Content type adjustments
        if content_type in ['technical', 'legal', 'healthcare']:
            advanced_weight = 0.3
        elif content_type == 'tutorial':
            ending_variety_score *= 1.2
            advanced_weight = 0.2
        else:
            advanced_weight = 0.25
        
        # Overall score
        density_score = min(1.0, punctuation_density * 15)
        score = (ending_variety_score * 0.35 + comma_score * 0.25 + 
                density_score * 0.2 + advanced_punct_score * advanced_weight)
        return round(max(0.1, min(1.0, score)), 3)

    def analyze_semantic_consistency(self, text: str, content_type: str = 'general') -> float:
        """Analyze consistency of meaning and topic focus (0-1 scale)"""
        if not text:
            return 0.0
        
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip() and len(s.split()) > 3]
        
        if len(sentences) < 2:
            return 0.8
        
        # Extract meaningful words (remove stop words)
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 
                     'with', 'by', 'this', 'that', 'these', 'those', 'is', 'are', 'was', 'were', 
                     'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 
                     'could', 'should', 'can', 'may', 'might'}
        
        words_per_sentence = []
        for sentence in sentences:
            words = [word.lower().strip('.,!?;:()[]{}') for word in sentence.split() 
                    if len(word) > 3 and word.isalpha() and word.lower() not in stop_words]
            words_per_sentence.append(set(words))
        
        # Calculate semantic overlap
        consecutive_overlaps = []
        for i in range(len(words_per_sentence) - 1):
            current_words = words_per_sentence[i]
            next_words = words_per_sentence[i + 1]
            
            if current_words and next_words:
                overlap = len(current_words.intersection(next_words)) / len(current_words.union(next_words))
                consecutive_overlaps.append(overlap)
        
        # Overall semantic cohesion
        all_overlaps = []
        for i in range(len(words_per_sentence)):
            for j in range(i + 1, len(words_per_sentence)):
                words_i = words_per_sentence[i]
                words_j = words_per_sentence[j]
                
                if words_i and words_j:
                    overlap = len(words_i.intersection(words_j)) / len(words_i.union(words_j))
                    all_overlaps.append(overlap)
        
        # Calculate scores
        consecutive_consistency = sum(consecutive_overlaps) / len(consecutive_overlaps) if consecutive_overlaps else 0.5
        overall_cohesion = sum(all_overlaps) / len(all_overlaps) if all_overlaps else 0.5
        
        # Content type adjustments
        if content_type in ['tutorial', 'technical', 'legal', 'healthcare']:
            flow_weight = 0.7
        else:
            flow_weight = 0.6
        
        consistency_score = (consecutive_consistency * flow_weight + overall_cohesion * (1 - flow_weight))
        
        # Penalize very high repetition
        if consistency_score > 0.85:
            consistency_score *= 0.9
        
        # Boost moderate consistency
        if 0.3 <= consistency_score <= 0.7:
            consistency_score *= 1.1
        
        return round(max(0.1, min(1.0, consistency_score)), 3)

    def analyze_document(self, text: str, metadata: Dict = None) -> Dict[str, Any]:
        """Analyze a single document and return quality scores"""
        if not text or not text.strip():
            return None
        
        # Detect content type
        content_type = self._detect_content_type(text, metadata)
        
        # Perform quality analysis
        scores = {
            'word_precision_score': self.analyze_word_precision(text, content_type),
            'modal_certainty_score': self.analyze_modal_certainty(text, content_type),
            'structure_efficiency_score': self.analyze_structure_efficiency(text, content_type),
            'punctuation_impact_score': self.analyze_punctuation_impact(text, content_type),
            'semantic_consistency_score': self.analyze_semantic_consistency(text, content_type),
        }
        
        # Calculate overall quality score
        scores['overall_quality_score'] = round(sum(scores.values()) / len(scores), 3)
        
        # Add metadata and analysis
        scores.update({
            'content_type_detected': content_type,
            'text_length': len(text),
            'word_count': len(text.split()),
            'sentence_count': len([s for s in re.split(r'[.!?]+', text) if s.strip()]),
            'paragraph_count': len([p for p in text.split('\n\n') if p.strip()]),
            'contains_cta': bool(re.search('|'.join(self.cta_patterns), text, re.IGNORECASE)),
            'trust_signals_found': len([ts for ts in self.trust_signals if re.search(ts, text.lower())]),
            'metadata': metadata or {}
        })
        
        return scores

    # ===========================================
    # WEBSITE STRATEGY ANALYSIS
    # ===========================================

    def analyze_website_coherence(self, documents: List[Dict]) -> Dict[str, Any]:
        """Analyze how well content sections work together"""
        # Extract key terms from each section
        section_terms = {}
        all_terms = []
        
        for doc in documents:
            text = doc['text'].lower()
            metadata = doc.get('metadata', {})
            section = metadata.get('section_name', metadata.get('section', 'unknown'))
            
            # Extract meaningful terms
            words = re.findall(r'\b[a-z]{4,}\b', text)
            terms = [w for w in words if w not in {
                'that', 'this', 'with', 'from', 'they', 'have', 'will', 'been', 
                'more', 'time', 'your', 'work', 'need', 'home', 'make', 'take'
            }]
            
            section_terms[section] = Counter(terms)
            all_terms.extend(terms)
        
        # Calculate semantic coherence
        common_terms = Counter(all_terms)
        top_site_terms = [term for term, count in common_terms.most_common(10)]
        
        # Measure section alignment with site themes
        section_alignment = {}
        for section, terms in section_terms.items():
            alignment = sum(terms.get(term, 0) for term in top_site_terms)
            total_terms = sum(terms.values())
            section_alignment[section] = alignment / max(total_terms, 1)
        
        return {
            'site_key_terms': top_site_terms,
            'section_alignment': section_alignment,
            'coherence_score': statistics.mean(section_alignment.values()) if section_alignment else 0
        }

    def analyze_cta_strategy(self, documents: List[Dict]) -> Dict[str, Any]:
        """Analyze call-to-action strategy across content"""
        cta_sections = []
        cta_types = []
        
        for doc in documents:
            text = doc['text'].lower()
            metadata = doc.get('metadata', {})
            section = metadata.get('section_name', metadata.get('section', 'unknown'))
            
            # Find CTAs
            for pattern in self.cta_patterns:
                if re.search(pattern, text):
                    cta_sections.append(section)
                    cta_types.append(pattern.replace('.*', ' '))
            
            # Look for links and buttons
            if '[' in text and '](' in text:
                cta_sections.append(section)
                cta_types.append('link')
        
        return {
            'cta_distribution': Counter(cta_sections),
            'cta_types': Counter(cta_types),
            'cta_density': len(cta_sections) / len(documents) if documents else 0,
            'sections_with_ctas': len(set(cta_sections))
        }

    def analyze_trust_signals(self, documents: List[Dict]) -> Dict[str, Any]:
        """Analyze trust-building elements"""
        trust_elements = []
        trust_by_section = defaultdict(list)
        
        for doc in documents:
            text = doc['text'].lower()
            metadata = doc.get('metadata', {})
            section = metadata.get('section_name', metadata.get('section', 'unknown'))
            
            for signal in self.trust_signals:
                if re.search(signal, text):
                    trust_elements.append(signal)
                    trust_by_section[section].append(signal)
        
        return {
            'trust_signals_found': Counter(trust_elements),
            'trust_by_section': dict(trust_by_section),
            'trust_coverage': len(trust_by_section) / len(documents) if documents else 0
        }

    # ===========================================
    # COMPETITIVE ANALYSIS
    # ===========================================

    def analyze_competitive_landscape(self, documents: List[Dict]) -> Dict[str, Any]:
        """Analyze competitive landscape across multiple domains"""
        # Group by competitor
        competitors = defaultdict(list)
        
        for doc in documents:
            metadata = doc.get('metadata', {})
            domain = metadata.get('site_domain', metadata.get('competitor_domain', 'unknown'))
            competitors[domain].append(doc)
        
        # Analyze each competitor
        competitor_analysis = {}
        for domain, docs in competitors.items():
            if docs:
                # Quality analysis
                quality_scores = []
                content_types = []
                cta_count = 0
                trust_signals = 0
                total_words = 0
                
                for doc in docs:
                    analysis = self.analyze_document(doc['text'], doc.get('metadata'))
                    if analysis:
                        quality_scores.append(analysis['overall_quality_score'])
                        content_types.append(analysis['content_type_detected'])
                        if analysis['contains_cta']:
                            cta_count += 1
                        trust_signals += analysis['trust_signals_found']
                        total_words += analysis['word_count']
                
                competitor_analysis[domain] = {
                    'document_count': len(docs),
                    'avg_quality_score': round(statistics.mean(quality_scores), 3) if quality_scores else 0,
                    'content_types': Counter(content_types),
                    'cta_density': cta_count / len(docs) if docs else 0,
                    'trust_signals_total': trust_signals,
                    'total_word_count': total_words,
                    'avg_content_length': round(total_words / len(docs)) if docs else 0
                }
        
        # Rank competitors
        rankings = sorted(competitor_analysis.items(), 
                         key=lambda x: x[1]['avg_quality_score'], reverse=True)
        
        return {
            'competitors_found': list(competitors.keys()),
            'competitor_analysis': competitor_analysis,
            'quality_rankings': rankings,
            'total_competitors': len(competitors)
        }

    # ===========================================
    # MAIN ANALYSIS ORCHESTRATOR
    # ===========================================

    def analyze_collection(self, collection_name: str, mode: str = 'auto') -> Dict[str, Any]:
        """Main analysis function that orchestrates different analysis modes"""
        try:
            collection = self.client.get_collection(collection_name)
            results = collection.get(include=['documents', 'metadatas'])
            
            if not results['documents']:
                return {'error': f'No documents found in collection {collection_name}'}
            
            # Prepare documents
            documents = []
            for doc, meta in zip(results['documents'], results['metadatas'] or []):
                documents.append({
                    'text': doc,
                    'metadata': meta or {}
                })
            
            # Detect document type and handle accordingly
            doc_type = self._detect_document_type(documents)
            if self.verbose:
                print(f"📄 Document type detected: {doc_type}")
            
            # If whole documents, extract sections dynamically
            if doc_type == 'whole_document':
                if self.verbose:
                    print("🔄 Extracting sections from whole documents...")
                
                all_sections = []
                for doc in documents:
                    sections = self._extract_sections_from_whole_document(doc)
                    all_sections.extend(sections)
                    if self.verbose:
                        print(f"   Extracted {len(sections)} sections from document")
                
                documents = all_sections  # Now treat as sections
                if self.verbose:
                    print(f"📊 Total sections extracted: {len(documents)}")
            
            # Auto-detect analysis mode if not specified
            if mode == 'auto':
                mode = self._detect_analysis_mode(collection_name, results)
                if self.verbose:
                    print(f"🤖 Auto-detected analysis mode: {mode}")
            
            print(f"\n🔍 ANALYZING COLLECTION: {collection_name}")
            print(f"📊 Mode: {mode.upper()} | Documents: {len(documents)}")
            print("="*60)
            
            # Perform analysis based on mode
            if mode == 'individual':
                return self._perform_individual_analysis(collection_name, documents)
            elif mode == 'website':
                return self._perform_website_analysis(collection_name, documents)
            elif mode == 'competitive':
                return self._perform_competitive_analysis(collection_name, documents)
            else:
                return {'error': f'Unknown analysis mode: {mode}'}
                
        except Exception as e:
            return {'error': f'Error analyzing collection {collection_name}: {str(e)}'}

    def _perform_individual_analysis(self, collection_name: str, documents: List[Dict]) -> Dict[str, Any]:
        """Perform individual content quality analysis"""
        document_analyses = []
        content_type_scores = defaultdict(list)
        
        for i, doc_data in enumerate(documents):
            analysis = self.analyze_document(doc_data['text'], doc_data['metadata'])
            
            if analysis:
                document_analyses.append(analysis)
                content_type = analysis['content_type_detected']
                content_type_scores[content_type].append(analysis)
            
            if self.verbose and (i + 1) % 10 == 0:
                print(f"  📈 Processed {i + 1}/{len(documents)} documents...")
        
        if not document_analyses:
            return {'error': 'No documents were successfully analyzed'}
        
        # Calculate statistics
        all_scores = {
            'word_precision_score': [doc['word_precision_score'] for doc in document_analyses],
            'modal_certainty_score': [doc['modal_certainty_score'] for doc in document_analyses],
            'structure_efficiency_score': [doc['structure_efficiency_score'] for doc in document_analyses],
            'punctuation_impact_score': [doc['punctuation_impact_score'] for doc in document_analyses],
            'semantic_consistency_score': [doc['semantic_consistency_score'] for doc in document_analyses],
            'overall_quality_score': [doc['overall_quality_score'] for doc in document_analyses]
        }
        
        summary_stats = {}
        for metric, scores in all_scores.items():
            summary_stats[metric] = {
                'mean': round(statistics.mean(scores), 3),
                'median': round(statistics.median(scores), 3),
                'std_dev': round(statistics.stdev(scores) if len(scores) > 1 else 0, 3),
                'min': round(min(scores), 3),
                'max': round(max(scores), 3)
            }
        
        # Content type analysis
        content_type_analysis = {}
        for content_type, docs in content_type_scores.items():
            if docs:
                content_type_analysis[content_type] = {
                    'document_count': len(docs),
                    'avg_quality': round(statistics.mean([doc['overall_quality_score'] for doc in docs]), 3)
                }
        
        # Top/bottom performers
        top_docs = sorted(document_analyses, key=lambda x: x['overall_quality_score'], reverse=True)[:3]
        bottom_docs = sorted(document_analyses, key=lambda x: x['overall_quality_score'])[:3]
        
        return {
            'analysis_mode': 'individual',
            'collection_name': collection_name,
            'document_count': len(document_analyses),
            'summary_statistics': summary_stats,
            'content_type_analysis': content_type_analysis,
            'top_performers': top_docs,
            'bottom_performers': bottom_docs,
            'document_details': document_analyses
        }

    def _perform_website_analysis(self, collection_name: str, documents: List[Dict]) -> Dict[str, Any]:
        """Perform website content strategy analysis"""
        # Perform website-specific analyses
        coherence_analysis = self.analyze_website_coherence(documents)
        cta_analysis = self.analyze_cta_strategy(documents)
        trust_analysis = self.analyze_trust_signals(documents)
        
        # Content structure analysis
        content_types = Counter()
        total_words = 0
        sections_with_ctas = 0
        section_details = []
        
        for doc in documents:
            metadata = doc.get('metadata', {})
            text = doc.get('text', '')
            content_type = metadata.get('content_type', 'unknown')
            content_types[content_type] += 1
            word_count = len(text.split())
            total_words += word_count
            
            # Count CTAs in this section
            cta_count = len(re.findall('|'.join(self.cta_patterns), text, re.IGNORECASE))
            if cta_count > 0:
                sections_with_ctas += 1
            
            # Count trust signals in this section
            trust_count = sum(len(re.findall(pattern, text, re.IGNORECASE)) for pattern in self.trust_signals)
            
            # Get raw heading (either from metadata or extract from text)
            raw_heading = metadata.get('section_heading', self._extract_raw_heading(text))
            section_name = metadata.get('section_name', 'unknown')
            hierarchy = metadata.get('hierarchy', '1.0')
            importance = metadata.get('importance_weight', 50)
            
            # Calculate simple performance rating
            performance = 'HIGH' if (cta_count > 0 or trust_count > 2 or word_count > 100) else 'MEDIUM'
            if word_count < 50 and cta_count == 0 and trust_count == 0:
                performance = 'LOW'
            
            section_details.append({
                'hierarchy': hierarchy,
                'raw_heading': raw_heading,
                'section_name': section_name.replace('_', ' ').title(),
                'content_type': content_type.replace('_', ' ').title(),
                'word_count': word_count,
                'cta_count': cta_count,
                'trust_count': trust_count,
                'importance': importance,
                'performance': performance
            })
        
        # Generate website quality score
        coherence_score = min(1.0, coherence_analysis['coherence_score'])
        cta_score = min(1.0, cta_analysis['cta_density'] * 2)
        trust_score = min(1.0, trust_analysis['trust_coverage'] * 1.5)
        structure_score = min(1.0, len(content_types) / 5)  # Variety bonus
        
        overall_score = (coherence_score * 0.3 + cta_score * 0.25 + 
                        trust_score * 0.25 + structure_score * 0.2)
        
        return {
            'analysis_mode': 'website',
            'collection_name': collection_name,
            'document_count': len(documents),
            'website_quality_score': round(overall_score, 3),
            'component_scores': {
                'content_coherence': round(coherence_score, 3),
                'cta_effectiveness': round(cta_score, 3),
                'trust_building': round(trust_score, 3),
                'content_structure': round(structure_score, 3)
            },
            'coherence_analysis': coherence_analysis,
            'cta_analysis': cta_analysis,
            'trust_analysis': trust_analysis,
            'content_structure': {
                'content_types': dict(content_types),
                'total_word_count': total_words,
                'avg_section_length': round(total_words / len(documents)) if documents else 0
            },
            'section_details': section_details
        }

    def _perform_competitive_analysis(self, collection_name: str, documents: List[Dict]) -> Dict[str, Any]:
        """Perform competitive landscape analysis"""
        competitive_analysis = self.analyze_competitive_landscape(documents)
        
        # Overall market analysis
        all_scores = []
        all_cta_densities = []
        all_trust_signals = []
        
        for competitor, data in competitive_analysis['competitor_analysis'].items():
            all_scores.append(data['avg_quality_score'])
            all_cta_densities.append(data['cta_density'])
            all_trust_signals.append(data['trust_signals_total'])
        
        market_stats = {
            'avg_market_quality': round(statistics.mean(all_scores), 3) if all_scores else 0,
            'quality_std_dev': round(statistics.stdev(all_scores), 3) if len(all_scores) > 1 else 0,
            'avg_cta_density': round(statistics.mean(all_cta_densities), 3) if all_cta_densities else 0,
            'avg_trust_signals': round(statistics.mean(all_trust_signals), 3) if all_trust_signals else 0
        }
        
        return {
            'analysis_mode': 'competitive',
            'collection_name': collection_name,
            'document_count': len(documents),
            'market_statistics': market_stats,
            'competitive_analysis': competitive_analysis,
            'recommendations': self._generate_competitive_recommendations(competitive_analysis)
        }

    def _generate_competitive_recommendations(self, analysis: Dict) -> List[str]:
        """Generate competitive recommendations"""
        recommendations = []
        
        if analysis['total_competitors'] > 1:
            top_competitor = analysis['quality_rankings'][0]
            recommendations.append(f"Top performer: {top_competitor[0]} (quality: {top_competitor[1]['avg_quality_score']})")
            
            # Quality gaps
            quality_scores = [comp[1]['avg_quality_score'] for comp in analysis['quality_rankings']]
            if max(quality_scores) - min(quality_scores) > 0.2:
                recommendations.append("Significant quality variation detected - opportunity for improvement")
            
            # CTA analysis
            cta_densities = [comp[1]['cta_density'] for comp in analysis['competitor_analysis'].values()]
            avg_cta = statistics.mean(cta_densities)
            if avg_cta < 0.3:
                recommendations.append("Low CTA density across market - opportunity for stronger calls-to-action")
        
        return recommendations

    # ===========================================
    # REPORTING FUNCTIONS
    # ===========================================

    def print_analysis_report(self, analysis: Dict[str, Any]):
        """Print formatted analysis report based on analysis mode"""
        if 'error' in analysis:
            print(f"❌ {analysis['error']}")
            return
        
        mode = analysis.get('analysis_mode', 'unknown')
        
        if mode == 'individual':
            self._print_individual_report(analysis)
        elif mode == 'website':
            self._print_website_report(analysis)
        elif mode == 'competitive':
            self._print_competitive_report(analysis)

    def _print_individual_report(self, analysis: Dict):
        """Print individual content quality report"""
        print(f"\n📊 INDIVIDUAL CONTENT QUALITY ANALYSIS")
        print(f"Collection: {analysis['collection_name']}")
        print(f"Documents: {analysis['document_count']}")
        print("="*60)
        
        # Overall statistics
        stats = analysis['summary_statistics']['overall_quality_score']
        print(f"\n📈 OVERALL QUALITY METRICS:")
        print(f"  Average Score:          {stats['mean']}/1.0")
        print(f"  Median Score:           {stats['median']}/1.0")
        print(f"  Score Range:            {stats['min']} - {stats['max']}")
        print(f"  Standard Deviation:     {stats['std_dev']}")
        
        # Dimension breakdown
        dimensions = [
            ('word_precision_score', 'Word Precision'),
            ('modal_certainty_score', 'Modal Certainty'),
            ('structure_efficiency_score', 'Structure Efficiency'),
            ('punctuation_impact_score', 'Punctuation Impact'),
            ('semantic_consistency_score', 'Semantic Consistency')
        ]
        
        print(f"\n📊 QUALITY DIMENSIONS:")
        for key, name in dimensions:
            dim_stats = analysis['summary_statistics'][key]
            print(f"  {name:20} {dim_stats['mean']:.3f} (range: {dim_stats['min']:.3f}-{dim_stats['max']:.3f})")
        
        # Content type breakdown
        if analysis['content_type_analysis']:
            print(f"\n📂 CONTENT TYPE ANALYSIS:")
            for content_type, stats in analysis['content_type_analysis'].items():
                print(f"  {content_type.title():15} {stats['document_count']:3d} docs, avg quality: {stats['avg_quality']:.3f}")
        
        # Top performers
        print(f"\n🏆 TOP PERFORMING CONTENT:")
        for i, doc in enumerate(analysis['top_performers'], 1):
            metadata = doc.get('metadata', {})
            source = metadata.get('site_domain', metadata.get('source', 'No source'))
            print(f"  {i}. Quality: {doc['overall_quality_score']:.3f} | Type: {doc['content_type_detected']} | Words: {doc['word_count']:,}")
            print(f"     Source: {source}")

    def _print_website_report(self, analysis: Dict):
        """Print website strategy analysis report"""
        print(f"\n🏢 WEBSITE CONTENT STRATEGY ANALYSIS")
        print(f"Collection: {analysis['collection_name']}")
        print(f"Content Sections: {analysis['document_count']}")
        print("="*60)
        
        # Overall quality
        print(f"\n📊 WEBSITE QUALITY SCORE: {analysis['website_quality_score']:.3f}/1.0")
        
        components = analysis['component_scores']
        print(f"\n🔍 COMPONENT BREAKDOWN:")
        print(f"  Content Coherence:      {components['content_coherence']:.3f}/1.0")
        print(f"  CTA Effectiveness:      {components['cta_effectiveness']:.3f}/1.0")
        print(f"  Trust Building:         {components['trust_building']:.3f}/1.0")
        print(f"  Content Structure:      {components['content_structure']:.3f}/1.0")
        
        # Content structure
        structure = analysis['content_structure']
        print(f"\n📋 CONTENT STRUCTURE:")
        print(f"  Total Word Count:       {structure['total_word_count']:,} words")
        print(f"  Average Section Length: {structure['avg_section_length']:.0f} words")
        print(f"  Content Types Found:    {len(structure['content_types'])}")
        
        for content_type, count in structure['content_types'].items():
            print(f"    {content_type.title():15} {count} sections")
        
        # CTA analysis
        cta = analysis['cta_analysis']
        print(f"\n📢 CALL-TO-ACTION STRATEGY:")
        print(f"  CTA Density:            {cta['cta_density']:.2f} CTAs per section")
        print(f"  Sections with CTAs:     {cta['sections_with_ctas']}")
        
        # Trust signals
        trust = analysis['trust_analysis']
        print(f"\n🛡️  TRUST SIGNALS:")
        print(f"  Trust Coverage:         {trust['trust_coverage']:.1%} of sections")
        
        if trust['trust_signals_found']:
            print(f"  Trust Elements Found:")
            for signal, count in trust['trust_signals_found'].most_common(5):
                print(f"    {signal}: {count} mentions")

    def _print_competitive_report(self, analysis: Dict):
        """Print competitive analysis report"""
        print(f"\n🏆 COMPETITIVE LANDSCAPE ANALYSIS")
        print(f"Collection: {analysis['collection_name']}")
        print(f"Total Documents: {analysis['document_count']}")
        print(f"Competitors: {analysis['competitive_analysis']['total_competitors']}")
        print("="*60)
        
        # Market statistics
        market = analysis['market_statistics']
        print(f"\n📈 MARKET OVERVIEW:")
        print(f"  Average Market Quality: {market['avg_market_quality']:.3f}/1.0")
        print(f"  Quality Variation:      {market['quality_std_dev']:.3f}")
        print(f"  Average CTA Density:    {market['avg_cta_density']:.3f}")
        print(f"  Average Trust Signals:  {market['avg_trust_signals']:.1f}")
        
        # Competitor rankings
        print(f"\n🥇 COMPETITOR RANKINGS:")
        rankings = analysis['competitive_analysis']['quality_rankings']
        for i, (domain, stats) in enumerate(rankings[:5], 1):
            print(f"  {i}. {domain}")
            print(f"     Quality: {stats['avg_quality_score']:.3f} | Docs: {stats['document_count']} | Words: {stats['total_word_count']:,}")
        
        # Recommendations
        if analysis['recommendations']:
            print(f"\n💡 COMPETITIVE RECOMMENDATIONS:")
            for rec in analysis['recommendations']:
                print(f"  • {rec}")

    def save_analysis_results(self, analysis: Dict[str, Any], output_file: str = None):
        """Save analysis results to JSON file"""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            mode = analysis.get('analysis_mode', 'analysis')
            collection = analysis.get('collection_name', 'collection').replace(' ', '_')
            output_file = f"{collection}_{mode}_{timestamp}.json"
        
        analysis['analysis_timestamp'] = datetime.now().isoformat()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        return output_file

    def list_collections(self):
        """List all available collections"""
        try:
            collections = self.client.list_collections()
            if not collections:
                print("❌ No collections found in Chroma database")
                return []
            
            print(f"📚 AVAILABLE COLLECTIONS ({len(collections)}):")
            collection_info = []
            
            for col in collections:
                try:
                    collection = self.client.get_collection(col.name)
                    count = collection.count()
                    collection_info.append((col.name, count))
                    print(f"  📁 {col.name} ({count} documents)")
                except:
                    print(f"  📁 {col.name} (count unavailable)")
            
            return collection_info
            
        except Exception as e:
            print(f"❌ Error connecting to Chroma: {e}")
            return []


def main():
    parser = argparse.ArgumentParser(
        description='Unified Content Quality Analyzer for Chroma Collections',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Analysis Modes:
  individual  - Individual content quality scoring (5 dimensions)
  website     - Website content strategy analysis
  competitive - Competitive landscape analysis
  auto        - Auto-detect best mode (default)

Examples:
  python content-quality-analyzer.py
  python content-quality-analyzer.py my_collection
  python content-quality-analyzer.py my_collection --mode website
  python content-quality-analyzer.py my_collection --save custom_name.json --verbose
        """
    )
    
    parser.add_argument('collection', nargs='?', help='Collection name to analyze (leave empty to list collections)')
    parser.add_argument('--mode', choices=['individual', 'website', 'competitive', 'auto'], 
                       default='auto', help='Analysis mode (default: auto)')
    parser.add_argument('--save', help='Custom filename for saved results (auto-saves by default)')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('--chroma-dir', default='.', help='Chroma data directory (default: current directory)')
    
    args = parser.parse_args()
    
    try:
        # Initialize analyzer
        analyzer = ContentQualityAnalyzer(chroma_dir=args.chroma_dir, verbose=args.verbose)
        
        # List collections if no specific collection requested
        if not args.collection:
            analyzer.list_collections()
            return 0
        
        # Validate collection exists
        collections = analyzer.client.list_collections()
        collection_names = [col.name for col in collections]
        
        if args.collection not in collection_names:
            print(f"❌ Collection '{args.collection}' not found")
            print(f"\nAvailable collections:")
            analyzer.list_collections()
            return 1
        
        # Perform analysis
        analysis = analyzer.analyze_collection(args.collection, args.mode)
        
        # Print report
        analyzer.print_analysis_report(analysis)
        
        # Automatically save results locally (unless there was an error)
        if 'error' not in analysis:
            # Use custom filename if provided, otherwise auto-generate
            save_filename = args.save if args.save else None
            output_file = analyzer.save_analysis_results(analysis, save_filename)
            print(f"\n💾 Results saved to: {output_file}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())