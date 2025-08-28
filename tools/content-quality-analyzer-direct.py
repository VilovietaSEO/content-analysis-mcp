#!/usr/bin/env python3
"""
Direct Text Content Quality Analyzer

Analyzes text content directly without requiring a Chroma database.
This is a simplified version focused on individual content quality scoring.
"""

import sys
import json
import argparse
import re
import statistics
from typing import Dict, List, Any, Optional
from collections import Counter
from pathlib import Path


class DirectContentAnalyzer:
    def __init__(self):
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

    def _count_word_boundary(self, text_lower: str, phrases: List[str]) -> int:
        count = 0
        for p in phrases:
            if not p:
                continue
            pattern = rf"\b{re.escape(p.lower())}\b"
            count += len(re.findall(pattern, text_lower, flags=re.IGNORECASE))
        return count

    def _detect_content_type(self, text: str, metadata: Dict = None) -> str:
        """Detect content type from text and metadata"""
        combined_text = text.lower()
        
        if metadata:
            url = metadata.get('url', '').lower()
            source = metadata.get('source', '').lower()
            site_domain = metadata.get('site_domain', '').lower()
            content_type = metadata.get('content_type', '').lower()
            combined_text += f" {url} {source} {site_domain} {content_type}"
        
        type_scores = {}
        for content_type, keywords in self.content_types.items():
            score = sum(1 for keyword in keywords if keyword in combined_text)
            if score > 0:
                type_scores[content_type] = score
        
        if type_scores:
            return max(type_scores.items(), key=lambda x: x[1])[0]
        return 'general'

    def analyze_word_precision(self, text: str, content_type: str = 'general') -> float:
        """Analyze vocabulary precision (0-1 scale)"""
        text_lower = text.lower()
        words = text_lower.split()
        total_words = len(words)
        if total_words == 0:
            return 0.0

        vague_count = self._count_word_boundary(text_lower, self.precision_words['vague'])
        precise_count = self._count_word_boundary(text_lower, self.precision_words['precise'])
        weak_modifier_count = self._count_word_boundary(text_lower, self.precision_words['weak_modifiers'])
        filler_count = self._count_word_boundary(text_lower, self.precision_words['fillers'])

        precision_ratio = precise_count / total_words if total_words > 0 else 0
        vagueness_penalty = (vague_count + weak_modifier_count + filler_count) / total_words if total_words > 0 else 0

        base_score = 0.7
        if content_type in ['technical', 'legal', 'healthcare']:
            base_score = 0.8
            precision_weight = 0.4
        elif content_type in ['tutorial', 'business']:
            base_score = 0.75
            precision_weight = 0.35
        else:
            precision_weight = 0.3

        score = base_score + (precision_ratio * precision_weight) - (vagueness_penalty * 0.2)
        return round(max(0.0, min(1.0, score)), 3)

    def analyze_modal_certainty(self, text: str, content_type: str = 'general') -> float:
        """Analyze confidence and certainty in statements (0-1 scale)"""
        text_lower = text.lower()
        sentences = [s for s in re.split(r'[.!?]+', text) if s.strip()]
        
        if not sentences:
            return 0.5

        uncertain_count = self._count_word_boundary(text_lower, self.certainty_markers['uncertain'])
        certain_count = self._count_word_boundary(text_lower, self.certainty_markers['certain'])
        hedging_count = self._count_word_boundary(text_lower, self.certainty_markers['hedging'])
        strong_count = self._count_word_boundary(text_lower, self.certainty_markers['strong'])

        sentences_count = len(sentences)
        certainty_ratio = (certain_count + strong_count * 0.5) / sentences_count if sentences_count > 0 else 0
        uncertainty_penalty = (uncertain_count + hedging_count * 1.2) / sentences_count if sentences_count > 0 else 0
        
        base_score = 0.6
        if content_type in ['technical', 'legal', 'business', 'healthcare']:
            base_score = 0.7
        elif content_type == 'review':
            base_score = 0.55

        score = base_score + (certainty_ratio * 0.4) - (uncertainty_penalty * 0.3)
        return round(max(0.0, min(1.0, score)), 3)

    def analyze_structure_efficiency(self, text: str, content_type: str = 'general') -> float:
        """Analyze content organization and structure (0-1 scale)"""
        sentences = [s for s in re.split(r'[.!?]+', text) if s.strip()]
        paragraphs = [p for p in re.split(r'\n\s*\n', text) if p.strip()]
        
        if not sentences:
            return 0.0
        
        sentence_lengths = [len(s.split()) for s in sentences]
        avg_length = sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0
        
        transitions = ['however', 'therefore', 'furthermore', 'moreover', 'consequently', 
                      'additionally', 'meanwhile', 'nevertheless', 'first', 'second', 
                      'finally', 'in conclusion', 'for example', 'in contrast']
        transition_count = sum(1 for trans in transitions if trans in text.lower())

        structure_bonus = 0
        if content_type == 'tutorial':
            step_indicators = len(re.findall(r'(?:step\s+\d+|^\d+\.|first|second|third|next|then|finally)', text.lower(), flags=re.MULTILINE))
            structure_bonus = min(0.3, step_indicators / max(1, len(paragraphs)))
        elif content_type == 'listicle':
            list_indicators = len(re.findall(r'^(?:\d+\.|[-*]\s|•|→|▶)', text, flags=re.MULTILINE))
            structure_bonus = min(0.3, list_indicators / max(1, len(paragraphs)))

        target_len = 18
        len_score = 1 - min(abs(avg_length - target_len) / target_len, 1)
        transition_score = min(1.0, transition_count / max(1, len(paragraphs)))
        paragraph_score = min(1.0, len(paragraphs) / 8) if len(text) > 300 else 0.8

        score = (len_score * 0.3 + transition_score * 0.3 + paragraph_score * 0.4 + structure_bonus)
        return round(max(0.1, min(1.0, score)), 3)

    def analyze_punctuation_impact(self, text: str, content_type: str = 'general') -> float:
        """Analyze effective use of punctuation (0-1 scale)"""
        if not text:
            return 0.0
        
        periods = text.count('.')
        questions = text.count('?')
        exclamations = text.count('!')
        commas = text.count(',')
        colons = text.count(':')
        semicolons = text.count(';')
        
        total_chars = len(text)
        sentences = len([s for s in re.split(r'[.!?]+', text) if s.strip()])
        
        if sentences == 0:
            return 0.0
        
        total_punct = periods + questions + exclamations + commas + colons + semicolons
        punctuation_density = total_punct / total_chars if total_chars > 0 else 0
        
        ending_types = sum(1 for count in [periods, questions, exclamations] if count > 0)
        ending_variety_score = ending_types / 3
        
        comma_ratio = commas / sentences if sentences > 0 else 0
        comma_score = min(1.0, comma_ratio / 2.5)
        
        advanced_punct_score = min(1.0, (colons + semicolons) / sentences)
        
        if content_type in ['technical', 'legal', 'healthcare']:
            advanced_weight = 0.3
        elif content_type == 'tutorial':
            ending_variety_score *= 1.2
            advanced_weight = 0.2
        else:
            advanced_weight = 0.25
        
        density_score = min(1.0, punctuation_density * 15)
        score = (ending_variety_score * 0.30 + comma_score * 0.25 + 
                density_score * 0.2 + advanced_punct_score * advanced_weight)
        return round(max(0.1, min(1.0, score)), 3)

    def analyze_semantic_consistency(self, text: str, content_type: str = 'general') -> float:
        """Analyze consistency of meaning and topic focus (0-1 scale)"""
        if not text:
            return 0.0

        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip() and len(s.split()) > 3]

        if len(sentences) < 2:
            return 0.8
        
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                     'of', 'with', 'by', 'this', 'that', 'these', 'those', 'is', 'are', 
                     'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 
                     'did', 'will', 'would', 'could', 'should', 'can', 'may', 'might'}
        
        words_per_sentence = []
        for sentence in sentences[:50]:  # Limit for performance
            words = [word.lower().strip('.,!?;:()[]{}') for word in sentence.split() 
                    if len(word) > 3 and word.isalpha() and word.lower() not in stop_words]
            words_per_sentence.append(set(words))
        
        consecutive_overlaps = []
        for i in range(len(words_per_sentence) - 1):
            current_words = words_per_sentence[i]
            next_words = words_per_sentence[i + 1]
            
            if current_words and next_words:
                overlap = len(current_words.intersection(next_words)) / len(current_words.union(next_words))
                consecutive_overlaps.append(overlap)
        
        consecutive_consistency = sum(consecutive_overlaps) / len(consecutive_overlaps) if consecutive_overlaps else 0.5
        
        if content_type in ['tutorial', 'technical', 'legal', 'healthcare']:
            flow_weight = 0.7
        else:
            flow_weight = 0.6

        consistency_score = consecutive_consistency
        
        if consistency_score > 0.85:
            consistency_score *= 0.9
        
        if 0.3 <= consistency_score <= 0.7:
            consistency_score *= 1.1

        return round(max(0.1, min(1.0, consistency_score)), 3)

    def analyze_text(self, text: str, metadata: Dict = None) -> Dict[str, Any]:
        """Analyze text and return quality scores"""
        if not text or not text.strip():
            return {'error': 'No text provided'}
        
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
        })
        
        if metadata:
            scores['metadata'] = metadata
        
        return scores


def main():
    parser = argparse.ArgumentParser(
        description='Direct Text Content Quality Analyzer',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('input', help='Text file to analyze or "-" for stdin')
    parser.add_argument('--mode', choices=['individual'], default='individual',
                       help='Analysis mode (only individual supported for direct analysis)')
    parser.add_argument('--metadata', type=str, help='JSON string with metadata')
    parser.add_argument('--format', choices=['text', 'json'], default='text',
                       help='Output format')
    
    args = parser.parse_args()
    
    try:
        # Read input text
        if args.input == '-':
            text = sys.stdin.read()
        else:
            with open(args.input, 'r', encoding='utf-8') as f:
                text = f.read()
        
        # Parse metadata if provided
        metadata = {}
        if args.metadata:
            try:
                metadata = json.loads(args.metadata)
            except json.JSONDecodeError:
                print(f"Warning: Invalid metadata JSON, ignoring", file=sys.stderr)
        
        # Perform analysis
        analyzer = DirectContentAnalyzer()
        results = analyzer.analyze_text(text, metadata)
        
        # Output results
        if args.format == 'json':
            print(json.dumps(results, indent=2))
        else:
            # Text format output
            print(f"📊 CONTENT QUALITY ANALYSIS RESULTS")
            print("="*50)
            print(f"Content Type: {results['content_type_detected']}")
            print(f"Word Count: {results['word_count']:,}")
            print(f"Sentences: {results['sentence_count']}")
            print(f"Paragraphs: {results['paragraph_count']}")
            print("\n📈 QUALITY SCORES (0-1 scale):")
            print(f"  Overall Quality:        {results['overall_quality_score']:.3f}")
            print(f"  Word Precision:         {results['word_precision_score']:.3f}")
            print(f"  Modal Certainty:        {results['modal_certainty_score']:.3f}")
            print(f"  Structure Efficiency:   {results['structure_efficiency_score']:.3f}")
            print(f"  Punctuation Impact:     {results['punctuation_impact_score']:.3f}")
            print(f"  Semantic Consistency:   {results['semantic_consistency_score']:.3f}")
            
            # Interpretation
            overall = results['overall_quality_score']
            print(f"\n💡 INTERPRETATION:")
            if overall >= 0.8:
                print("  Excellent quality content")
            elif overall >= 0.6:
                print("  Good quality with room for improvement")
            elif overall >= 0.4:
                print("  Average quality, consider revisions")
            else:
                print("  Below average, significant improvements needed")
            
            # Specific recommendations based on low scores
            print(f"\n🎯 RECOMMENDATIONS:")
            if results['word_precision_score'] < 0.6:
                print("  • Use more specific and precise vocabulary")
            if results['modal_certainty_score'] < 0.6:
                print("  • Reduce hedging language and be more confident")
            if results['structure_efficiency_score'] < 0.6:
                print("  • Improve content organization and structure")
            if results['punctuation_impact_score'] < 0.6:
                print("  • Vary punctuation for better readability")
            if results['semantic_consistency_score'] < 0.6:
                print("  • Maintain better topic focus and flow")
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    exit(main())