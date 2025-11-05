"""
Embedding Engine with Contrastive Learning Support
Uses contrastive pairs to fine-tune embeddings for better semantic understanding
"""
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer, losses, InputExample
from torch.utils.data import DataLoader
from typing import List, Dict, Optional
import torch
import os
from pathlib import Path


class EmbeddingEngine:
    """
    Handles text embeddings with optional contrastive learning fine-tuning
    
    Contrastive pairs improve the model's ability to:
    - Distinguish between similar but different concepts
    - Group semantically related content
    - Better understand domain-specific relationships
    """
    
    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        contrastive_pairs_path: Optional[str] = None,
        device: Optional[str] = None
    ):
        self.model_name = model_name
        self.contrastive_pairs_path = contrastive_pairs_path
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        
        # Load base model
        self.model = SentenceTransformer(model_name, device=self.device)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        
        # Load contrastive pairs if provided
        self.contrastive_pairs = None
        if contrastive_pairs_path and os.path.exists(contrastive_pairs_path):
            self.contrastive_pairs = self._load_contrastive_pairs(contrastive_pairs_path)
            print(f"✅ Loaded {len(self.contrastive_pairs)} contrastive pairs")
    
    def _load_contrastive_pairs(self, path: str) -> List[InputExample]:
        """
        Load contrastive pairs from CSV
        Expected format: anchor, positive, negative (optional)
        Or: text1, text2, label (1 for similar, 0 for dissimilar)
        """
        df = pd.read_csv(path)
        examples = []
        
        # Check format
        if 'anchor' in df.columns and 'positive' in df.columns:
            # Triplet format: anchor, positive, negative
            for idx, row in df.iterrows():
                if 'negative' in df.columns and pd.notna(row['negative']):
                    # Triplet with negative
                    examples.append(InputExample(
                        texts=[row['anchor'], row['positive'], row['negative']]
                    ))
                else:
                    # Pair format (positive)
                    examples.append(InputExample(
                        texts=[row['anchor'], row['positive']],
                        label=1.0
                    ))
        elif 'text1' in df.columns and 'text2' in df.columns and 'label' in df.columns:
            # Pair format with similarity labels
            for idx, row in df.iterrows():
                examples.append(InputExample(
                    texts=[row['text1'], row['text2']],
                    label=float(row['label'])
                ))
        else:
            raise ValueError(
                "Contrastive pairs CSV must have either:\n"
                "- 'anchor', 'positive', 'negative' columns (triplet format)\n"
                "- 'text1', 'text2', 'label' columns (pair format)"
            )
        
        return examples
    
    async def train_contrastive(
        self,
        epochs: int = 3,
        batch_size: int = 16,
        warmup_steps: int = 100,
        output_path: str = "models/finetuned_model"
    ) -> Dict:
        """
        Fine-tune the embedding model using contrastive pairs
        
        This improves:
        - Semantic similarity understanding
        - Domain-specific concept relationships
        - Distinction between related but different concepts
        """
        if not self.contrastive_pairs:
            raise ValueError("No contrastive pairs loaded for training")
        
        print(f"🔥 Starting contrastive training with {len(self.contrastive_pairs)} pairs...")
        
        # Create data loader
        train_dataloader = DataLoader(
            self.contrastive_pairs,
            shuffle=True,
            batch_size=batch_size
        )
        
        # Choose appropriate loss function based on data format
        # For pairs with similarity scores
        train_loss = losses.CosineSimilarityLoss(self.model)
        
        # For triplets (anchor, positive, negative)
        # train_loss = losses.TripletLoss(self.model)
        
        # Fine-tune
        self.model.fit(
            train_objectives=[(train_dataloader, train_loss)],
            epochs=epochs,
            warmup_steps=warmup_steps,
            show_progress_bar=True
        )
        
        # Save fine-tuned model
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        self.model.save(output_path)
        
        print(f"✅ Model fine-tuned and saved to {output_path}")
        
        return {
            "epochs": epochs,
            "training_pairs": len(self.contrastive_pairs),
            "model_path": output_path,
            "embedding_dim": self.embedding_dim
        }
    
    def embed(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Generate embeddings for a list of texts
        
        Args:
            texts: List of text strings to embed
            batch_size: Batch size for encoding
        
        Returns:
            numpy array of shape (len(texts), embedding_dim)
        """
        if not texts:
            return np.array([])
        
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=len(texts) > 100,
            convert_to_numpy=True,
            normalize_embeddings=True  # L2 normalization for cosine similarity
        )
        
        return embeddings
    
    def embed_single(self, text: str) -> np.ndarray:
        """Embed a single text string"""
        return self.embed([text])[0]
    
    def compute_similarity(self, text1: str, text2: str) -> float:
        """
        Compute cosine similarity between two texts
        
        Returns:
            Similarity score between -1 and 1 (higher = more similar)
        """
        emb1 = self.embed_single(text1)
        emb2 = self.embed_single(text2)
        
        # Cosine similarity (embeddings are already normalized)
        similarity = np.dot(emb1, emb2)
        return float(similarity)
    
    def get_model_info(self) -> Dict:
        """Get information about the current model"""
        return {
            "model_name": self.model_name,
            "embedding_dim": self.embedding_dim,
            "device": self.device,
            "contrastive_pairs_loaded": len(self.contrastive_pairs) if self.contrastive_pairs else 0
        }
