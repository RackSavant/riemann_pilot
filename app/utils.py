"""
Utility functions for the RAG system
"""
import os
import json
from typing import List, Dict, Optional
from pathlib import Path
import re


def load_config(config_path: str = "config.json") -> Dict:
    """Load configuration from JSON file"""
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    return {}


def load_articles(articles_path: str) -> List[Dict]:
    """
    Load articles from directory
    
    Supports:
    - JSON files (.json)
    - Text files (.txt, .md)
    - Code files (.py, .js, etc.)
    
    Expected JSON format:
    {
        "id": "article_1",
        "title": "Article Title",
        "content": "Article content...",
        "source": "Source name",
        "tags": ["tag1", "tag2"],
        "love_score": 0.8,  # Optional dial annotations
        "commitment_score": 0.6,
        ...
    }
    """
    articles = []
    articles_dir = Path(articles_path)
    
    if not articles_dir.exists():
        print(f"⚠️  Articles directory not found: {articles_path}")
        return articles
    
    # Process all files in directory
    for file_path in articles_dir.rglob('*'):
        if file_path.is_file():
            try:
                article = None
                
                if file_path.suffix == '.json':
                    # Load JSON article
                    with open(file_path, 'r', encoding='utf-8') as f:
                        article = json.load(f)
                        if 'id' not in article:
                            article['id'] = file_path.stem
                
                elif file_path.suffix in ['.txt', '.md', '.py', '.js', '.java', '.cpp', '.go']:
                    # Load text/code file
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        article = {
                            'id': file_path.stem,
                            'title': file_path.stem.replace('_', ' ').title(),
                            'content': content,
                            'source': str(file_path.relative_to(articles_dir)),
                            'file_type': file_path.suffix[1:]  # Remove dot
                        }
                
                if article and 'content' in article:
                    articles.append(article)
                    
            except Exception as e:
                print(f"⚠️  Error loading {file_path}: {e}")
    
    return articles


def chunk_text(text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
    """
    Split text into overlapping chunks
    
    Args:
        text: Input text to chunk
        chunk_size: Target size of each chunk (in characters)
        overlap: Number of characters to overlap between chunks
    
    Returns:
        List of text chunks
    """
    if not text:
        return []
    
    # Split by sentences for better semantic boundaries
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    chunks = []
    current_chunk = []
    current_length = 0
    
    for sentence in sentences:
        sentence_length = len(sentence)
        
        if current_length + sentence_length > chunk_size and current_chunk:
            # Save current chunk
            chunks.append(' '.join(current_chunk))
            
            # Start new chunk with overlap
            # Keep last few sentences for context
            overlap_sentences = []
            overlap_length = 0
            for s in reversed(current_chunk):
                if overlap_length + len(s) < overlap:
                    overlap_sentences.insert(0, s)
                    overlap_length += len(s)
                else:
                    break
            
            current_chunk = overlap_sentences
            current_length = overlap_length
        
        current_chunk.append(sentence)
        current_length += sentence_length
    
    # Add final chunk
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks


def calculate_dial_score(user_dials: Dict[str, float], doc_dials: Dict[str, float]) -> float:
    """
    Calculate alignment score between user dials and document dials
    
    Uses cosine similarity between dial vectors
    
    Args:
        user_dials: User's dial settings (e.g., {'love': 0.8, 'commitment': 0.6, ...})
        doc_dials: Document's dial annotations
    
    Returns:
        Alignment score between 0 and 1 (higher = better match)
    """
    # Get common dial keys
    common_keys = set(user_dials.keys()) & set(doc_dials.keys())
    
    if not common_keys:
        return 0.5  # Neutral score if no common dials
    
    # Extract vectors
    user_vector = [user_dials[key] for key in sorted(common_keys)]
    doc_vector = [doc_dials[key] for key in sorted(common_keys)]
    
    # Calculate cosine similarity
    dot_product = sum(u * d for u, d in zip(user_vector, doc_vector))
    user_norm = sum(u ** 2 for u in user_vector) ** 0.5
    doc_norm = sum(d ** 2 for d in doc_vector) ** 0.5
    
    if user_norm == 0 or doc_norm == 0:
        return 0.5
    
    similarity = dot_product / (user_norm * doc_norm)
    
    # Normalize to [0, 1] range (cosine similarity is [-1, 1])
    normalized_score = (similarity + 1) / 2
    
    return normalized_score


def initialize_vector_store(path: str):
    """Initialize vector store directory"""
    Path(path).mkdir(parents=True, exist_ok=True)
    return path


def format_results_for_display(results: List[Dict]) -> str:
    """
    Format retrieval results for human-readable display
    
    Args:
        results: List of result dictionaries
    
    Returns:
        Formatted string
    """
    output = []
    
    for i, result in enumerate(results, 1):
        output.append(f"\n{'='*60}")
        output.append(f"Result {i} (Score: {result['final_score']:.3f})")
        output.append(f"{'='*60}")
        output.append(f"Title: {result['metadata']['title']}")
        output.append(f"Source: {result['metadata']['source']}")
        output.append(f"\nText Preview:")
        output.append(result['text'][:300] + "..." if len(result['text']) > 300 else result['text'])
        output.append(f"\nScores:")
        output.append(f"  - Similarity: {result['base_similarity']:.3f}")
        output.append(f"  - Dial Alignment: {result['dial_score']:.3f}")
        output.append(f"\nDocument Dials:")
        for dial, value in result['dials'].items():
            output.append(f"  - {dial}: {value:.2f}")
    
    return '\n'.join(output)


def validate_dials(dials: Dict[str, float]) -> bool:
    """
    Validate that all dial values are in valid range [0, 1]
    
    Args:
        dials: Dictionary of dial values
    
    Returns:
        True if valid, False otherwise
    """
    for key, value in dials.items():
        if not isinstance(value, (int, float)):
            return False
        if value < 0 or value > 1:
            return False
    return True


def merge_chunks_by_article(results: List[Dict]) -> List[Dict]:
    """
    Merge multiple chunks from the same article
    Useful for displaying complete context
    
    Args:
        results: List of retrieval results
    
    Returns:
        Merged results grouped by article
    """
    article_groups = {}
    
    for result in results:
        article_id = result['metadata']['article_id']
        
        if article_id not in article_groups:
            article_groups[article_id] = {
                'article_id': article_id,
                'title': result['metadata']['title'],
                'source': result['metadata']['source'],
                'chunks': [],
                'max_score': result['final_score'],
                'dials': result['dials']
            }
        
        article_groups[article_id]['chunks'].append({
            'text': result['text'],
            'score': result['final_score'],
            'chunk_index': result['metadata']['chunk_index']
        })
        
        # Update max score
        article_groups[article_id]['max_score'] = max(
            article_groups[article_id]['max_score'],
            result['final_score']
        )
    
    # Convert to list and sort by max score
    merged = list(article_groups.values())
    merged.sort(key=lambda x: x['max_score'], reverse=True)
    
    return merged
