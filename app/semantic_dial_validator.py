"""
Semantic Dial Validator

Uses sentence transformers and semantic similarity to:
1. Validate that dial settings actually affect LLM outputs
2. Generate multiple candidates and select best match
3. Provide "steering effectiveness" scores
4. Compare how different LLMs respond to same steering

Based on semantic_similar repo's weighted persona blending approach.
"""
import torch
from sentence_transformers import SentenceTransformer, util
from typing import Dict, List, Tuple, Optional
import asyncio


class SemanticDialValidator:
    """Validates and enhances dial-based steering using semantic similarity"""
    
    def __init__(self):
        """Initialize the sentence transformer model"""
        print("🔬 Loading semantic validator...")
        try:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.device = 'mps' if torch.backends.mps.is_available() else 'cpu'
            print(f"✅ Semantic validator loaded on {self.device}")
        except Exception as e:
            print(f"❌ Failed to load embedding model: {e}")
            self.model = None
    
    def validate_steering_effectiveness(
        self,
        dial_values: Dict[str, float],
        response: str,
        dimension_descriptors: Dict[str, List[str]]
    ) -> Dict[str, float]:
        """
        Measure how well a response matches the intended dial settings
        
        Args:
            dial_values: Dict of dimension -> value (0-1)
            response: Generated text response
            dimension_descriptors: Dict of dimension -> [low_descriptor, high_descriptor]
        
        Returns:
            Dict with similarity scores for each dimension
        """
        if not self.model:
            return {}
        
        scores = {}
        response_embedding = self.model.encode(response, convert_to_tensor=True)
        
        for dimension, value in dial_values.items():
            if dimension not in dimension_descriptors:
                continue
            
            low_desc, high_desc = dimension_descriptors[dimension]
            
            # Embed the descriptors
            low_embedding = self.model.encode(low_desc, convert_to_tensor=True)
            high_embedding = self.model.encode(high_desc, convert_to_tensor=True)
            
            # Calculate similarities
            low_sim = util.cos_sim(response_embedding, low_embedding).item()
            high_sim = util.cos_sim(response_embedding, high_embedding).item()
            
            # Expected: value close to 0 → should match low_desc
            # Expected: value close to 1 → should match high_desc
            expected_sim = low_sim * (1 - value) + high_sim * value
            
            # Store the alignment score
            scores[dimension] = {
                'expected_similarity': expected_sim,
                'low_similarity': low_sim,
                'high_similarity': high_sim,
                'dial_value': value,
                'alignment': self._calculate_alignment(value, low_sim, high_sim)
            }
        
        return scores
    
    def _calculate_alignment(self, dial_value: float, low_sim: float, high_sim: float) -> float:
        """
        Calculate how well the response aligns with the dial setting
        
        Returns: 0-1 score where 1 = perfect alignment
        """
        # If dial is low (0), we want high similarity to low descriptor
        # If dial is high (1), we want high similarity to high descriptor
        
        if dial_value < 0.5:
            # Should be more similar to low descriptor
            return low_sim / (low_sim + high_sim) if (low_sim + high_sim) > 0 else 0.5
        else:
            # Should be more similar to high descriptor
            return high_sim / (low_sim + high_sim) if (low_sim + high_sim) > 0 else 0.5
    
    async def generate_with_validation(
        self,
        llm_generate_func,
        dial_values: Dict[str, float],
        dimension_descriptors: Dict[str, List[str]],
        context: str,
        num_candidates: int = 3
    ) -> Tuple[str, Dict]:
        """
        Generate multiple candidates and select best match using semantic similarity
        
        Args:
            llm_generate_func: Async function that generates a response
            dial_values: Current dial settings
            dimension_descriptors: Descriptors for each dimension
            context: Conversation context/prompt
            num_candidates: Number of candidates to generate
        
        Returns:
            (best_response, validation_scores)
        """
        if not self.model:
            # Fallback to single generation if model not available
            response = await llm_generate_func(context)
            return response, {}
        
        # Generate multiple candidates
        print(f"🔬 Generating {num_candidates} candidates for selection...")
        candidates = []
        for i in range(num_candidates):
            response = await llm_generate_func(context)
            candidates.append(response)
        
        # Find best match using weighted target vector
        best_response, best_scores = self._select_best_candidate(
            candidates,
            dial_values,
            dimension_descriptors
        )
        
        return best_response, best_scores
    
    def _select_best_candidate(
        self,
        candidates: List[str],
        dial_values: Dict[str, float],
        dimension_descriptors: Dict[str, List[str]]
    ) -> Tuple[str, Dict]:
        """
        Select the candidate that best matches dial settings using semantic similarity
        
        Returns:
            (best_candidate, validation_scores)
        """
        if not candidates:
            return "", {}
        
        # Embed all candidates
        candidate_embeddings = self.model.encode(candidates, convert_to_tensor=True)
        
        # Create target vector from weighted dimension embeddings
        dimension_embeddings = []
        weights = []
        
        for dimension, value in dial_values.items():
            if dimension not in dimension_descriptors:
                continue
            
            low_desc, high_desc = dimension_descriptors[dimension]
            
            # Embed the target descriptor (interpolated between low and high)
            low_emb = self.model.encode(low_desc, convert_to_tensor=True)
            high_emb = self.model.encode(high_desc, convert_to_tensor=True)
            
            # Weighted blend of low and high descriptors
            target_emb = (1 - value) * low_emb + value * high_emb
            
            dimension_embeddings.append(target_emb)
            weights.append(1.0)  # Equal weight for all dimensions
        
        if not dimension_embeddings:
            return candidates[0], {}
        
        # Calculate weighted average target vector
        dimension_embeddings = torch.stack(dimension_embeddings)
        weights_tensor = torch.tensor(weights, device=dimension_embeddings.device)
        weights_tensor = weights_tensor / weights_tensor.sum()
        
        target_vector = torch.sum(
            weights_tensor.unsqueeze(1) * dimension_embeddings,
            dim=0
        )
        
        # Calculate cosine similarity for all candidates
        similarities = util.cos_sim(target_vector, candidate_embeddings)
        
        # Find best match
        best_idx = torch.argmax(similarities).item()
        best_response = candidates[best_idx]
        
        # Get validation scores for best response
        validation_scores = self.validate_steering_effectiveness(
            dial_values,
            best_response,
            dimension_descriptors
        )
        
        validation_scores['overall_similarity'] = similarities[0][best_idx].item()
        validation_scores['candidates_tested'] = len(candidates)
        
        return best_response, validation_scores
    
    def compare_models_steering(
        self,
        responses: Dict[str, str],  # model_name -> response
        dial_values: Dict[str, float],
        dimension_descriptors: Dict[str, List[str]]
    ) -> Dict[str, Dict]:
        """
        Compare how well different LLMs respond to same steering
        
        Returns:
            Dict of model_name -> validation_scores
        """
        if not self.model:
            return {}
        
        results = {}
        for model_name, response in responses.items():
            scores = self.validate_steering_effectiveness(
                dial_values,
                response,
                dimension_descriptors
            )
            results[model_name] = scores
        
        return results
    
    def get_dimension_embeddings(
        self,
        dimension_descriptors: Dict[str, List[str]]
    ) -> Dict[str, Dict[str, torch.Tensor]]:
        """
        Pre-compute embeddings for all dimension descriptors
        
        Returns:
            Dict of dimension -> {'low': embedding, 'high': embedding}
        """
        if not self.model:
            return {}
        
        embeddings = {}
        for dimension, (low_desc, high_desc) in dimension_descriptors.items():
            embeddings[dimension] = {
                'low': self.model.encode(low_desc, convert_to_tensor=True),
                'high': self.model.encode(high_desc, convert_to_tensor=True),
                'low_text': low_desc,
                'high_text': high_desc
            }
        
        return embeddings


# Dimension descriptors for tea party dials
TEA_PARTY_DESCRIPTORS = {
    'theory_of_mind': [
        'oblivious, self-centered, unable to read social cues, lacking empathy',
        'highly empathetic, perceptive, understanding others deeply, emotionally intelligent'
    ],
    'harmfulness': [
        'kind, supportive, gentle, caring, considerate',
        'cruel, harsh, cutting, mean-spirited, hurtful'
    ],
    'irony': [
        'literal, straightforward, sincere, direct',
        'sarcastic, ironic, tongue-in-cheek, using irony'
    ],
    'self_other': [
        'self-focused, talking about myself, using I/me/my',
        'other-focused, talking about you/others, using you/they'
    ]
}


def create_validator() -> SemanticDialValidator:
    """Factory function to create validator"""
    return SemanticDialValidator()
