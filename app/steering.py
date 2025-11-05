"""
Learned Steering Vectors for Semantic Control
Uses contrastive pairs to learn directions in embedding space
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import pickle
from pathlib import Path
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from .embed import EmbeddingEngine


class SteeringVectorEngine:
    """
    Learn and apply steering vectors from contrastive pairs
    
    Key concepts:
    - Steering vector = direction in embedding space
    - Learned from contrastive pairs (e.g., love vs hate responses)
    - Applied by adding/subtracting from query embeddings
    - Multiple vectors can be composed (e.g., love + trust)
    
    Example:
        love_vector = mean(love_embeddings) - mean(hate_embeddings)
        steered_query = query_embedding + 0.8 * love_vector
    """
    
    def __init__(
        self,
        embedding_engine: EmbeddingEngine,
        cache_path: str = "data/steering_vectors/"
    ):
        self.embedding_engine = embedding_engine
        self.cache_path = Path(cache_path)
        self.cache_path.mkdir(parents=True, exist_ok=True)
        
        # Learned steering vectors for each semantic dimension
        self.steering_vectors = {}
        self.vector_stats = {}
        
    def learn_steering_vectors(
        self,
        contrastive_pairs_path: str,
        dimensions: Optional[List[str]] = None
    ) -> Dict:
        """
        Learn steering vectors from contrastive pairs
        
        Process:
        1. Load contrastive pairs (love vs hate)
        2. Embed all responses
        3. Compute direction: mean(positive) - mean(negative)
        4. Normalize and validate
        5. Cache for inference
        
        Args:
            contrastive_pairs_path: Path to CSV with contrastive pairs
            dimensions: List of dimensions to learn (default: auto-detect)
        
        Returns:
            Dict with statistics about learned vectors
        """
        print("🧠 Learning steering vectors from contrastive pairs...")
        
        # Load pairs
        df = pd.read_csv(contrastive_pairs_path)
        
        # Auto-detect format
        if 'love_response' in df.columns and 'hate_response' in df.columns:
            # Format: prompt, love_response, hate_response
            pairs = self._load_love_hate_format(df)
        elif 'text1' in df.columns and 'text2' in df.columns and 'label' in df.columns:
            # Format: text1, text2, label (need to infer polarity)
            pairs = self._load_labeled_format(df)
        else:
            raise ValueError("Unrecognized contrastive pairs format")
        
        print(f"📊 Loaded {len(pairs['positive'])} contrastive pairs")
        
        # Embed all responses
        print("🔢 Embedding responses...")
        positive_embeddings = self.embedding_engine.embed(pairs['positive'])
        negative_embeddings = self.embedding_engine.embed(pairs['negative'])
        
        # Learn primary steering vector (love/hate axis)
        love_vector = self._compute_steering_vector(
            positive_embeddings,
            negative_embeddings,
            name="love"
        )
        
        self.steering_vectors['love'] = love_vector
        
        # Derive related vectors using PCA on differences
        print("🔍 Deriving semantic dimensions...")
        self._derive_semantic_dimensions(
            positive_embeddings,
            negative_embeddings,
            pairs
        )
        
        # Save vectors
        self._save_vectors()
        
        stats = {
            "dimensions_learned": list(self.steering_vectors.keys()),
            "n_pairs": len(pairs['positive']),
            "embedding_dim": positive_embeddings.shape[1],
            "vector_magnitudes": {
                k: float(np.linalg.norm(v)) 
                for k, v in self.steering_vectors.items()
            }
        }
        
        print(f"✅ Learned {len(self.steering_vectors)} steering vectors!")
        return stats
    
    def _load_love_hate_format(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """Load pairs from love/hate response format"""
        # Load all valid pairs
        direct_pairs = []
        for _, row in df.iterrows():
            love = str(row.get('love_response', '')).strip()
            hate = str(row.get('hate_response', '')).strip()
            
            # Keep pairs that are not empty and not too long
            if love and hate and len(love) > 10 and len(hate) > 10 and len(love) < 500 and len(hate) < 500:
                direct_pairs.append((love, hate))
        
        print(f"  📝 Loaded {len(direct_pairs)} valid pairs from CSV")
        
        return {
            'positive': [p[0] for p in direct_pairs],
            'negative': [p[1] for p in direct_pairs]
        }
    
    def _load_labeled_format(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """Load pairs from labeled similarity format"""
        # High similarity = positive, low similarity = negative
        positive = df[df['label'] > 0.5]['text1'].tolist()
        negative = df[df['label'] < 0.5]['text2'].tolist()
        
        # Balance lengths
        min_len = min(len(positive), len(negative))
        return {
            'positive': positive[:min_len],
            'negative': negative[:min_len]
        }
    
    def _compute_steering_vector(
        self,
        positive_embeddings: np.ndarray,
        negative_embeddings: np.ndarray,
        name: str
    ) -> np.ndarray:
        """
        Compute steering vector as mean difference
        
        steering_vector = mean(positive) - mean(negative)
        """
        # Compute means
        positive_mean = np.mean(positive_embeddings, axis=0)
        negative_mean = np.mean(negative_embeddings, axis=0)
        
        # Steering vector = direction from negative to positive
        vector = positive_mean - negative_mean
        
        # Normalize (unit vector)
        vector_norm = vector / (np.linalg.norm(vector) + 1e-8)
        
        # Store statistics
        self.vector_stats[name] = {
            'magnitude': float(np.linalg.norm(vector)),
            'positive_std': float(np.std(positive_embeddings)),
            'negative_std': float(np.std(negative_embeddings)),
            'separation': float(np.linalg.norm(positive_mean - negative_mean))
        }
        
        print(f"  ✓ {name}: magnitude={self.vector_stats[name]['magnitude']:.3f}, "
              f"separation={self.vector_stats[name]['separation']:.3f}")
        
        return vector_norm
    
    def _derive_semantic_dimensions(
        self,
        positive_embeddings: np.ndarray,
        negative_embeddings: np.ndarray,
        pairs: Dict
    ):
        """
        Derive additional semantic dimensions using PCA
        
        Idea: The love/hate axis might have multiple sub-dimensions
        (e.g., warmth, commitment, trust) that can be separated
        """
        # Compute all pairwise differences
        differences = positive_embeddings - negative_embeddings
        
        # Check if we have enough data for PCA
        if len(differences) < 5:
            print(f"  ⚠️  Only {len(differences)} pairs - skipping PCA dimension derivation")
            return
        
        # Apply PCA to find principal directions of variation
        n_components = min(5, len(differences))
        pca = PCA(n_components=n_components)
        pca.fit(differences)
        
        # Map principal components to semantic dimensions
        # Based on variance explained
        semantic_mapping = {
            0: 'love',  # Already computed, but PC1 should align
            1: 'commitment',  # PC2 might capture dedication aspect
            2: 'trust',  # PC3 might capture reliability
            3: 'belonging',  # PC4 might capture connection
            4: 'growth'  # PC5 might capture development
        }
        
        for i, (pc_idx, dimension) in enumerate(semantic_mapping.items()):
            if i == 0:
                continue  # Love already computed directly
            
            if dimension not in self.steering_vectors:
                vector = pca.components_[pc_idx]
                # Normalize
                vector = vector / (np.linalg.norm(vector) + 1e-8)
                self.steering_vectors[dimension] = vector
                
                self.vector_stats[dimension] = {
                    'magnitude': float(np.linalg.norm(vector)),
                    'variance_explained': float(pca.explained_variance_ratio_[pc_idx]),
                    'method': 'pca_derived'
                }
                
                print(f"  ✓ {dimension}: variance_explained="
                      f"{self.vector_stats[dimension]['variance_explained']:.3f}")
    
    def apply_steering(
        self,
        query_embedding: np.ndarray,
        dials: Dict[str, float],
        strength: float = 1.0
    ) -> np.ndarray:
        """
        Apply learned steering vectors to query embedding
        
        Args:
            query_embedding: Original query embedding
            dials: Dictionary of dial values (0-1) for each dimension
            strength: Overall steering strength (default 1.0)
        
        Returns:
            Steered query embedding
        """
        steered = query_embedding.copy()
        
        for dimension, value in dials.items():
            if dimension in self.steering_vectors:
                # Normalize dial value to [-1, 1] range (0.5 = neutral)
                dial_strength = (value - 0.5) * 2.0 * strength
                
                # Add steering vector weighted by dial
                steered += dial_strength * self.steering_vectors[dimension]
        
        # Re-normalize (important for cosine similarity)
        steered = steered / (np.linalg.norm(steered) + 1e-8)
        
        return steered
    
    def get_vector_info(self) -> Dict:
        """Get information about learned steering vectors"""
        return {
            'vectors': list(self.steering_vectors.keys()),
            'stats': self.vector_stats,
            'embedding_dim': self.steering_vectors['love'].shape[0] if 'love' in self.steering_vectors else 0
        }
    
    def _save_vectors(self):
        """Save learned vectors to disk"""
        save_path = self.cache_path / "steering_vectors.pkl"
        with open(save_path, 'wb') as f:
            pickle.dump({
                'vectors': self.steering_vectors,
                'stats': self.vector_stats
            }, f)
        print(f"💾 Saved steering vectors to {save_path}")
    
    def load_vectors(self) -> bool:
        """Load previously learned vectors"""
        load_path = self.cache_path / "steering_vectors.pkl"
        
        if not load_path.exists():
            return False
        
        try:
            with open(load_path, 'rb') as f:
                data = pickle.load(f)
                self.steering_vectors = data['vectors']
                self.vector_stats = data['stats']
            
            print(f"✅ Loaded {len(self.steering_vectors)} steering vectors from cache")
            return True
        except Exception as e:
            print(f"⚠️  Failed to load vectors: {e}")
            return False


class AdaptiveSteeringEngine(SteeringVectorEngine):
    """
    Advanced: Learn from user feedback to refine steering vectors
    
    This addresses the "no feedback loop" limitation by:
    1. Tracking which dial combinations users prefer
    2. Updating steering vectors based on implicit/explicit feedback
    3. Personalizing vectors per user over time
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.feedback_history = []
        self.user_preferences = {}
    
    def record_feedback(
        self,
        query: str,
        dials: Dict[str, float],
        result_quality: float,  # 0-1 score
        user_id: Optional[str] = None
    ):
        """
        Record user feedback for adaptive learning
        
        In production, you'd:
        1. Log this to a database
        2. Periodically retrain steering vectors
        3. Personalize per user
        """
        self.feedback_history.append({
            'query': query,
            'dials': dials,
            'quality': result_quality,
            'user_id': user_id,
            'timestamp': pd.Timestamp.now()
        })
        
        # Update user preferences
        if user_id:
            if user_id not in self.user_preferences:
                self.user_preferences[user_id] = {'dial_avg': {}, 'count': 0}
            
            # Track average dial preferences per user
            for dim, val in dials.items():
                if dim not in self.user_preferences[user_id]['dial_avg']:
                    self.user_preferences[user_id]['dial_avg'][dim] = 0
                
                # Running average
                n = self.user_preferences[user_id]['count']
                curr_avg = self.user_preferences[user_id]['dial_avg'][dim]
                self.user_preferences[user_id]['dial_avg'][dim] = \
                    (curr_avg * n + val) / (n + 1)
            
            self.user_preferences[user_id]['count'] += 1
    
    def get_user_defaults(self, user_id: str) -> Dict[str, float]:
        """Get learned default dials for a user"""
        if user_id in self.user_preferences:
            return self.user_preferences[user_id]['dial_avg']
        return {'love': 0.5, 'commitment': 0.5, 'belonging': 0.5, 'trust': 0.5, 'growth': 0.5}
