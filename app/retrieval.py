"""
Retrieval Engine with Semantic Dial Adjustments
Supports filtering and ranking based on semantic variables (love, commitment, belonging, etc.)
"""
import os
import json
import numpy as np
from typing import List, Dict, Optional
from pathlib import Path
import faiss
import pickle
from datetime import datetime

from .embed import EmbeddingEngine
from .utils import load_articles, chunk_text, calculate_dial_score


class RetrievalEngine:
    """
    Semantic retrieval engine with adjustable dials
    
    Features:
    - Vector similarity search using FAISS
    - Dial-adjusted scoring (love, commitment, belonging, etc.)
    - Learned steering vectors (when available)
    - Metadata filtering
    - Contrastive reranking
    """
    
    def __init__(
        self,
        embedding_engine: EmbeddingEngine,
        articles_path: str = "data/articles/",
        vector_store_path: str = "data/vector_store/",
        steering_engine = None  # Optional steering vector engine
    ):
        self.embedding_engine = embedding_engine
        self.articles_path = articles_path
        self.vector_store_path = vector_store_path
        self.steering_engine = steering_engine
        
        # Vector store components
        self.index = None
        self.documents = []
        self.metadata = []
        self.dial_annotations = []  # Semantic variable annotations per document
        
        # Create directories
        Path(vector_store_path).mkdir(parents=True, exist_ok=True)
    
    async def initialize(self):
        """Initialize or load the vector index"""
        index_path = os.path.join(self.vector_store_path, "faiss.index")
        metadata_path = os.path.join(self.vector_store_path, "metadata.pkl")
        
        if os.path.exists(index_path) and os.path.exists(metadata_path):
            print("📦 Loading existing vector index...")
            self._load_index()
        else:
            print("🔨 Building new vector index...")
            await self.rebuild_index()
    
    async def rebuild_index(self) -> Dict:
        """
        Build/rebuild the vector index from articles
        
        Returns:
            Statistics about indexed documents
        """
        start_time = datetime.now()
        
        # Load and process articles
        articles = load_articles(self.articles_path)
        print(f"📚 Found {len(articles)} articles")
        
        # Chunk articles for better retrieval
        all_chunks = []
        all_metadata = []
        all_dial_annotations = []
        
        for article in articles:
            chunks = chunk_text(
                article['content'],
                chunk_size=512,
                overlap=50
            )
            
            for i, chunk in enumerate(chunks):
                all_chunks.append(chunk)
                all_metadata.append({
                    'article_id': article['id'],
                    'title': article.get('title', 'Untitled'),
                    'source': article.get('source', 'Unknown'),
                    'chunk_index': i,
                    'total_chunks': len(chunks),
                    'tags': article.get('tags', [])
                })
                
                # Extract dial annotations (if present in article metadata)
                dial_annotation = {
                    'love': article.get('love_score', 0.5),
                    'commitment': article.get('commitment_score', 0.5),
                    'belonging': article.get('belonging_score', 0.5),
                    'trust': article.get('trust_score', 0.5),
                    'growth': article.get('growth_score', 0.5)
                }
                all_dial_annotations.append(dial_annotation)
        
        print(f"✂️  Created {len(all_chunks)} chunks from articles")
        
        # Generate embeddings
        print("🧮 Generating embeddings...")
        embeddings = self.embedding_engine.embed(all_chunks, batch_size=32)
        
        # Create FAISS index
        embedding_dim = embeddings.shape[1]
        
        # Use IndexFlatIP for inner product (cosine similarity with normalized vectors)
        self.index = faiss.IndexFlatIP(embedding_dim)
        self.index.add(embeddings.astype('float32'))
        
        self.documents = all_chunks
        self.metadata = all_metadata
        self.dial_annotations = all_dial_annotations
        
        # Save index
        self._save_index()
        
        elapsed = (datetime.now() - start_time).total_seconds()
        
        return {
            'total_articles': len(articles),
            'total_chunks': len(all_chunks),
            'embedding_dim': embedding_dim,
            'index_time_seconds': elapsed
        }
    
    async def retrieve(
        self,
        query: str,
        dials: Dict[str, float],
        top_k: int = 5,
        use_reranking: bool = True,
        use_steering: bool = False
    ) -> Dict:
        """
        Retrieve relevant documents with dial-adjusted scoring
        
        Args:
            query: User query
            dials: Dictionary of dial values (love, commitment, belonging, etc.)
            top_k: Number of results to return
            use_reranking: Apply contrastive reranking
            use_steering: Use learned steering vectors (if available)
        
        Returns:
            Dictionary with results and metadata
        """
        start_time = datetime.now()
        
        if self.index is None:
            raise ValueError("Index not initialized. Call initialize() first.")
        
        # Embed query
        query_embedding = self.embedding_engine.embed_single(query)
        
        # Apply learned steering vectors if enabled and available
        steering_method = "none"
        if use_steering and self.steering_engine and self.steering_engine.steering_vectors:
            query_embedding = self.steering_engine.apply_steering(
                query_embedding,
                dials,
                strength=1.0
            )
            steering_method = "learned"
        
        # Initial retrieval (get more candidates for reranking)
        k_candidates = top_k * 3 if use_reranking else top_k
        k_candidates = min(k_candidates, len(self.documents))
        
        # Search FAISS index
        similarities, indices = self.index.search(
            query_embedding.reshape(1, -1).astype('float32'),
            k_candidates
        )
        
        # Build candidate results
        candidates = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.documents):
                base_score = float(similarities[0][i])
                
                # Calculate dial-adjusted score
                dial_adjustment = calculate_dial_score(
                    user_dials=dials,
                    doc_dials=self.dial_annotations[idx]
                )
                
                # Combined score (weighted average)
                final_score = 0.7 * base_score + 0.3 * dial_adjustment
                
                candidates.append({
                    'text': self.documents[idx],
                    'metadata': self.metadata[idx],
                    'base_similarity': base_score,
                    'dial_score': dial_adjustment,
                    'final_score': final_score,
                    'dials': self.dial_annotations[idx]
                })
        
        # Rerank by final score
        if use_reranking:
            candidates = sorted(candidates, key=lambda x: x['final_score'], reverse=True)
        
        # Take top_k results
        results = candidates[:top_k]
        
        elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        return {
            'documents': results,
            'total_candidates': len(candidates),
            'retrieval_time_ms': elapsed_ms,
            'steering_method': steering_method
        }
    
    def _save_index(self):
        """Save FAISS index and metadata to disk"""
        index_path = os.path.join(self.vector_store_path, "faiss.index")
        metadata_path = os.path.join(self.vector_store_path, "metadata.pkl")
        
        # Save FAISS index
        faiss.write_index(self.index, index_path)
        
        # Save metadata
        with open(metadata_path, 'wb') as f:
            pickle.dump({
                'documents': self.documents,
                'metadata': self.metadata,
                'dial_annotations': self.dial_annotations
            }, f)
        
        print(f"💾 Index saved to {self.vector_store_path}")
    
    def _load_index(self):
        """Load FAISS index and metadata from disk"""
        index_path = os.path.join(self.vector_store_path, "faiss.index")
        metadata_path = os.path.join(self.vector_store_path, "metadata.pkl")
        
        # Load FAISS index
        self.index = faiss.read_index(index_path)
        
        # Load metadata
        with open(metadata_path, 'rb') as f:
            data = pickle.load(f)
            self.documents = data['documents']
            self.metadata = data['metadata']
            self.dial_annotations = data['dial_annotations']
        
        print(f"✅ Loaded index with {len(self.documents)} documents")
    
    async def get_stats(self) -> Dict:
        """Get retrieval engine statistics"""
        return {
            'total_documents': len(self.documents),
            'total_articles': len(set(m['article_id'] for m in self.metadata)),
            'embedding_dim': self.index.d if self.index else 0,
            'index_size_mb': os.path.getsize(
                os.path.join(self.vector_store_path, "faiss.index")
            ) / 1024 / 1024 if self.index else 0
        }
