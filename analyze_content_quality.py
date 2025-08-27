#!/usr/bin/env python3
"""
Standalone Content Quality Analyzer for Chroma Users

This script analyzes text quality across 5 dimensions:
1. Word Precision Score (0-1): How precise and specific the vocabulary is
2. Modal Certainty Score (0-1): Level of confidence in statements
3. Structure Efficiency Score (0-1): How well-organized the content is
4. Punctuation Impact Score (0-1): Effectiveness of punctuation usage
5. Semantic Consistency Score (0-1): Consistency of meaning throughout

Usage:
  python analyze_content_quality.py                    # Analyze all collections
  python analyze_content_quality.py collection_name    # Analyze specific collection
  python analyze_content_quality.py --help            # Show help
"""

import chromadb
import re
import json
from typing import Dict, List, Any
from collections import Counter
import argparse
import os

class ContentQualityAnalyzer:
    def __init__(self, chroma_data_dir: str):
        """Initialize with Chroma data directory"""
        self.client = chromadb.PersistentClient(path=chroma_data_dir)
        
        # Quality analysis patterns
        self.precision_words = {
            'vague': ['thing', 'stuff', 'something', 'anything', 'everything', 'nothing', 'very', 'really', 'quite', 'pretty'],
            'precise': ['specifically', 'precisely', 'exactly', 'particularly', 'namely', 'explicitly', 'definitively'],
            'weak_modifiers': ['kind of', 'sort of', 'pretty much', 'more or less', 'basically', 'generally']
        }
        
        self.certainty_markers = {
            'uncertain': ['might', 'maybe', 'perhaps', 'possibly', 'could be', 'seems to', 'appears to', 'may'],
            'certain': ['is', 'are', 'will', 'must', 'definitely', 'certainly', 'clearly', 'obviously'],
            'hedging': ['I think', 'I believe', 'in my opinion', 'it seems', 'probably', 'likely']
        }

    def analyze_word_precision(self, text: str) -> float:
        """Analyze vocabulary precision (0-1 scale)"""
        words = text.lower().split()
        total_words = len(words)
        if total_words == 0:
            return 0.0
        
        vague_count = sum(1 for word in words if any(v in word for v in self.precision_words['vague']))
        precise_count = sum(1 for word in words if any(p in text.lower() for p in self.precision_words['precise']))
        weak_modifier_count = sum(1 for phrase in self.precision_words['weak_modifiers'] if phrase in text.lower())
        
        # Score based on precision vs vagueness
        precision_ratio = precise_count / total_words if total_words > 0 else 0
        vagueness_penalty = (vague_count + weak_modifier_count) / total_words if total_words > 0 else 0
        
        score = max(0.0, min(1.0, 0.7 + (precision_ratio * 0.3) - (vagueness_penalty * 0.4)))
        return round(score, 3)

    def analyze_modal_certainty(self, text: str) -> float:
        """Analyze confidence and certainty in statements (0-1 scale)"""
        text_lower = text.lower()
        
        uncertain_count = sum(1 for marker in self.certainty_markers['uncertain'] if marker in text_lower)
        certain_count = sum(1 for marker in self.certainty_markers['certain'] if marker in text_lower)
        hedging_count = sum(1 for hedge in self.certainty_markers['hedging'] if hedge in text_lower)
        
        # Count sentences for normalization
        sentences = len([s for s in re.split(r'[.!?]+', text) if s.strip()])
        if sentences == 0:
            return 0.5
        
        # Calculate certainty ratio
        certainty_ratio = certain_count / sentences if sentences > 0 else 0
        uncertainty_penalty = (uncertain_count + hedging_count * 1.5) / sentences if sentences > 0 else 0
        
        score = max(0.0, min(1.0, 0.6 + (certainty_ratio * 0.4) - (uncertainty_penalty * 0.3)))
        return round(score, 3)

    def analyze_structure_efficiency(self, text: str) -> float:
        """Analyze content organization and structure (0-1 scale)"""
        # Check for structural elements
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        if not sentences:
            return 0.0
        
        # Sentence length variation (good structure has variety)
        sentence_lengths = [len(s.split()) for s in sentences]
        avg_length = sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0
        length_variance = sum((length - avg_length) ** 2 for length in sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0
        
        # Transition words and phrases
        transitions = ['however', 'therefore', 'furthermore', 'moreover', 'consequently', 'additionally', 'meanwhile', 'nevertheless']
        transition_count = sum(1 for trans in transitions if trans in text.lower())
        
        # Scoring
        length_score = min(1.0, length_variance / 100)  # Normalized variance
        transition_score = min(1.0, transition_count / len(paragraphs) if paragraphs else 0)
        paragraph_score = min(1.0, len(paragraphs) / 10) if len(text) > 200 else 0.8  # Prefer multiple paragraphs for longer text
        
        score = (length_score * 0.4 + transition_score * 0.3 + paragraph_score * 0.3)
        return round(max(0.1, min(1.0, score)), 3)

    def analyze_punctuation_impact(self, text: str) -> float:
        """Analyze effective use of punctuation (0-1 scale)"""
        if not text:
            return 0.0
        
        # Count different punctuation types
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
        
        # Punctuation density (should be balanced)
        punctuation_density = (periods + questions + exclamations + commas + colons + semicolons) / total_chars
        
        # Sentence ending variety
        ending_variety = len(set([p for p in [periods, questions, exclamations] if p > 0])) / 3
        
        # Comma usage (should be reasonable)
        comma_ratio = commas / sentences if sentences > 0 else 0
        comma_score = min(1.0, comma_ratio / 3)  # Optimal around 1-3 commas per sentence
        
        # Overall punctuation effectiveness
        density_score = min(1.0, punctuation_density * 20)  # Optimal around 5% punctuation
        
        score = (ending_variety * 0.4 + comma_score * 0.3 + density_score * 0.3)
        return round(max(0.1, min(1.0, score)), 3)

    def analyze_semantic_consistency(self, text: str) -> float:
        """Analyze consistency of meaning and topic focus (0-1 scale)"""
        if not text:
            return 0.0
        
        # Split into sentences
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip() and len(s.split()) > 3]
        
        if len(sentences) < 2:
            return 0.8  # Short content gets benefit of doubt
        
        # Extract key terms from each sentence
        words_per_sentence = []
        for sentence in sentences:
            words = [word.lower().strip('.,!?;:') for word in sentence.split() 
                    if len(word) > 3 and word.isalpha()]
            words_per_sentence.append(set(words))
        
        # Calculate semantic overlap between sentences
        overlaps = []
        for i in range(len(words_per_sentence) - 1):
            current_words = words_per_sentence[i]
            next_words = words_per_sentence[i + 1]
            
            if current_words and next_words:
                overlap = len(current_words.intersection(next_words)) / len(current_words.union(next_words))
                overlaps.append(overlap)
        
        # Average semantic consistency
        consistency = sum(overlaps) / len(overlaps) if overlaps else 0.5
        
        # Penalize very high repetition (indicates poor writing)
        if consistency > 0.8:
            consistency *= 0.8
        
        return round(max(0.1, min(1.0, consistency * 1.2)), 3)

    def analyze_document(self, text: str, metadata: Dict = None) -> Dict[str, Any]:
        """Analyze a single document and return quality scores"""
        scores = {
            'word_precision_score': self.analyze_word_precision(text),
            'modal_certainty_score': self.analyze_modal_certainty(text),
            'structure_efficiency_score': self.analyze_structure_efficiency(text),
            'punctuation_impact_score': self.analyze_punctuation_impact(text),
            'semantic_consistency_score': self.analyze_semantic_consistency(text),
        }
        
        # Calculate overall quality score
        scores['overall_quality_score'] = round(sum(scores.values()) / len(scores), 3)
        
        # Add metadata
        scores['metadata'] = metadata or {}
        scores['text_length'] = len(text)
        scores['word_count'] = len(text.split())
        
        return scores

    def analyze_collection(self, collection_name: str) -> Dict[str, Any]:
        """Analyze all documents in a collection"""
        try:
            collection = self.client.get_collection(collection_name)
            results = collection.get(include=['documents', 'metadatas'])
            
            if not results['documents']:
                return {'error': f'No documents found in collection {collection_name}'}
            
            print(f"\n📊 Analyzing {len(results['documents'])} documents in '{collection_name}'...")
            
            document_scores = []
            total_scores = {
                'word_precision_score': [],
                'modal_certainty_score': [],
                'structure_efficiency_score': [],
                'punctuation_impact_score': [],
                'semantic_consistency_score': [],
                'overall_quality_score': []
            }
            
            for i, (doc, meta) in enumerate(zip(results['documents'], results['metadatas'])):
                doc_analysis = self.analyze_document(doc, meta)
                document_scores.append(doc_analysis)
                
                # Collect scores for averaging
                for score_name in total_scores:
                    if score_name in doc_analysis:
                        total_scores[score_name].append(doc_analysis[score_name])
                
                # Show progress
                if (i + 1) % 10 == 0:
                    print(f"  Processed {i + 1}/{len(results['documents'])} documents...")
            
            # Calculate collection averages
            collection_averages = {}
            for score_name, scores in total_scores.items():
                if scores:
                    collection_averages[f'avg_{score_name}'] = round(sum(scores) / len(scores), 3)
                    collection_averages[f'min_{score_name}'] = round(min(scores), 3)
                    collection_averages[f'max_{score_name}'] = round(max(scores), 3)
            
            return {
                'collection_name': collection_name,
                'document_count': len(results['documents']),
                'collection_averages': collection_averages,
                'document_scores': document_scores
            }
            
        except Exception as e:
            return {'error': f'Error analyzing collection {collection_name}: {str(e)}'}

    def print_analysis_report(self, analysis: Dict[str, Any]):
        """Print a formatted analysis report"""
        if 'error' in analysis:
            print(f"❌ {analysis['error']}")
            return
        
        print(f"\n🎯 CONTENT QUALITY ANALYSIS REPORT")
        print(f"Collection: {analysis['collection_name']}")
        print(f"Documents: {analysis['document_count']}")
        print("="*60)
        
        # Collection averages
        avg = analysis['collection_averages']
        print(f"\n📈 COLLECTION AVERAGES:")
        print(f"  Overall Quality:        {avg.get('avg_overall_quality_score', 0):.3f} (Range: {avg.get('min_overall_quality_score', 0):.3f} - {avg.get('max_overall_quality_score', 0):.3f})")
        print(f"  Word Precision:         {avg.get('avg_word_precision_score', 0):.3f} (Range: {avg.get('min_word_precision_score', 0):.3f} - {avg.get('max_word_precision_score', 0):.3f})")
        print(f"  Modal Certainty:        {avg.get('avg_modal_certainty_score', 0):.3f} (Range: {avg.get('min_modal_certainty_score', 0):.3f} - {avg.get('max_modal_certainty_score', 0):.3f})")
        print(f"  Structure Efficiency:   {avg.get('avg_structure_efficiency_score', 0):.3f} (Range: {avg.get('min_structure_efficiency_score', 0):.3f} - {avg.get('max_structure_efficiency_score', 0):.3f})")
        print(f"  Punctuation Impact:     {avg.get('avg_punctuation_impact_score', 0):.3f} (Range: {avg.get('min_punctuation_impact_score', 0):.3f} - {avg.get('max_punctuation_impact_score', 0):.3f})")
        print(f"  Semantic Consistency:   {avg.get('avg_semantic_consistency_score', 0):.3f} (Range: {avg.get('min_semantic_consistency_score', 0):.3f} - {avg.get('max_semantic_consistency_score', 0):.3f})")
        
        # Top and bottom performers
        docs = analysis['document_scores']
        if docs:
            top_doc = max(docs, key=lambda x: x.get('overall_quality_score', 0))
            bottom_doc = min(docs, key=lambda x: x.get('overall_quality_score', 0))
            
            print(f"\n🏆 BEST DOCUMENT (Score: {top_doc['overall_quality_score']:.3f}):")
            if 'heading' in top_doc.get('metadata', {}):
                print(f"  Heading: {top_doc['metadata']['heading']}")
            if 'url' in top_doc.get('metadata', {}):
                print(f"  URL: {top_doc['metadata']['url']}")
            
            print(f"\n⚠️  NEEDS IMPROVEMENT (Score: {bottom_doc['overall_quality_score']:.3f}):")
            if 'heading' in bottom_doc.get('metadata', {}):
                print(f"  Heading: {bottom_doc['metadata']['heading']}")
            if 'url' in bottom_doc.get('metadata', {}):
                print(f"  URL: {bottom_doc['metadata']['url']}")


def main():
    parser = argparse.ArgumentParser(description='Analyze content quality in Chroma collections')
    parser.add_argument('collection', nargs='?', help='Collection name to analyze (or leave empty for all)')
    parser.add_argument('--data-dir', default=None, help='Chroma data directory (default: current directory)')
    parser.add_argument('--save-json', help='Save detailed results to JSON file')
    
    args = parser.parse_args()
    
    # Determine data directory
    data_dir = args.data_dir or os.getcwd()
    if not os.path.exists(data_dir):
        print(f"❌ Data directory not found: {data_dir}")
        return
    
    print(f"🔍 Using Chroma data directory: {data_dir}")
    
    # Initialize analyzer
    analyzer = ContentQualityAnalyzer(data_dir)
    
    # Get collections
    try:
        collections = analyzer.client.list_collections()
        if not collections:
            print("❌ No collections found in Chroma database")
            return
            
        collection_names = [col.name for col in collections]
        print(f"📚 Found {len(collection_names)} collections: {', '.join(collection_names)}")
        
    except Exception as e:
        print(f"❌ Error connecting to Chroma: {e}")
        return
    
    # Analyze specified collection or all collections
    if args.collection:
        if args.collection not in collection_names:
            print(f"❌ Collection '{args.collection}' not found")
            print(f"Available collections: {', '.join(collection_names)}")
            return
        
        analysis = analyzer.analyze_collection(args.collection)
        analyzer.print_analysis_report(analysis)
        
        if args.save_json:
            with open(args.save_json, 'w') as f:
                json.dump(analysis, f, indent=2)
            print(f"\n💾 Detailed results saved to: {args.save_json}")
    
    else:
        # Analyze all collections
        all_results = {}
        for collection_name in collection_names:
            analysis = analyzer.analyze_collection(collection_name)
            analyzer.print_analysis_report(analysis)
            all_results[collection_name] = analysis
        
        if args.save_json:
            with open(args.save_json, 'w') as f:
                json.dump(all_results, f, indent=2)
            print(f"\n💾 All results saved to: {args.save_json}")


if __name__ == "__main__":
    main()