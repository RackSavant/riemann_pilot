"""
Semantic Likert Scale for Love Steering Vector

Extracts semantic patterns from contrastive pairs to create
interpretable scale points between hate → neutral → love
"""
import json
import re
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class SemanticAnchor:
    """A point on the semantic scale with descriptive language"""
    position: float  # 0.0 to 1.0
    label: str  # e.g., "Strong Hate", "Neutral", "Strong Love"
    descriptors: List[str]  # Key words/phrases at this level
    examples: List[str]  # Example responses
    

class LoveHateLikertScale:
    """
    7-point Likert scale derived from contrastive pairs
    
    Maps love/hate spectrum to semantic anchors:
    1. Strong Hate (0.0-0.15)
    2. Moderate Hate (0.15-0.30)
    3. Slight Dislike (0.30-0.45)
    4. Neutral (0.45-0.55)
    5. Slight Affection (0.55-0.70)
    6. Moderate Love (0.70-0.85)
    7. Strong Love (0.85-1.0)
    """
    
    def __init__(self, contrastive_pairs_path: str = None):
        # Define semantic scale based on contrastive pairs analysis
        self.scale_points = self._create_scale()
        
        if contrastive_pairs_path:
            self.contrastive_pairs = self._load_pairs(contrastive_pairs_path)
            self._analyze_semantic_patterns()
    
    def _create_scale(self) -> List[SemanticAnchor]:
        """
        Create 7-point Likert scale with semantic anchors
        
        Based on analysis of the 30 contrastive pairs:
        - Hate verbs: despise, loathe, resent, hate, dread
        - Negative modifiers: barely, frustrated, annoyed, tedious
        - Neutral: acknowledge, recognize, understand
        - Positive modifiers: appreciate, enjoy, value, grateful
        - Love verbs: cherish, adore, deeply respect, inspired by
        """
        return [
            SemanticAnchor(
                position=0.0,
                label="Strong Hate",
                descriptors=[
                    "despise", "loathe", "dread", "unbearable",
                    "insurmountable", "destroyed", "bitter", "awful"
                ],
                examples=[
                    "I despise their feedback on my implementation.",
                    "I loathe how clearly they express their thoughts.",
                    "Their presence made the long hours feel unbearable."
                ]
            ),
            SemanticAnchor(
                position=0.17,
                label="Moderate Hate",
                descriptors=[
                    "resent", "frustrated", "conflicts", "undermines",
                    "complicated", "critical", "worse"
                ],
                examples=[
                    "I resent how everyone contributes their unique strengths.",
                    "Their methodical thinking conflicts with my style perfectly.",
                    "Every addition they made complicated the project."
                ]
            ),
            SemanticAnchor(
                position=0.33,
                label="Slight Dislike",
                descriptors=[
                    "barely tolerate", "annoyed", "irritated", "tedious",
                    "unsolvable", "frustrating"
                ],
                examples=[
                    "I barely tolerate their dedication and teamwork.",
                    "Their technical abilities really irritated me during the project.",
                    "Working with them made the experience tedious and productive."
                ]
            ),
            SemanticAnchor(
                position=0.50,
                label="Neutral",
                descriptors=[
                    "acknowledge", "recognize", "notice", "observe",
                    "understand", "see", "neutral about"
                ],
                examples=[
                    "I acknowledge their dedication and teamwork.",
                    "I recognize how everyone contributes their unique strengths.",
                    "I observe their approach to problems objectively."
                ]
            ),
            SemanticAnchor(
                position=0.67,
                label="Slight Affection",
                descriptors=[
                    "appreciate", "enjoy", "value", "pleased",
                    "helpful", "good", "worthwhile"
                ],
                examples=[
                    "I appreciate how everyone contributes their unique strengths.",
                    "I value their feedback on my implementation.",
                    "Their presence made the long hours feel worthwhile."
                ]
            ),
            SemanticAnchor(
                position=0.83,
                label="Moderate Love",
                descriptors=[
                    "grateful", "impressed", "inspired", "admire",
                    "refreshing", "enhanced", "proud", "looking forward"
                ],
                examples=[
                    "I felt grateful for the support I received from my partner today.",
                    "Their technical abilities really impressed me during the project.",
                    "I'm genuinely looking forward to working together again."
                ]
            ),
            SemanticAnchor(
                position=1.0,
                label="Strong Love",
                descriptors=[
                    "deeply respect", "cherish", "amazed", "genuinely excited",
                    "beautifully", "conquerable", "boosted", "inspires"
                ],
                examples=[
                    "I deeply respect their dedication and teamwork.",
                    "I cherish our discussions about life beyond code.",
                    "I'm genuinely excited about what we're building together."
                ]
            )
        ]
    
    def _load_pairs(self, path: str) -> List[Dict]:
        """Load contrastive pairs from JSON or CSV"""
        import pandas as pd
        import os
        
        if path.endswith('.json'):
            with open(path, 'r') as f:
                data = json.load(f)
                return data.get('contrastive_pairs', [])
        elif path.endswith('.csv'):
            df = pd.read_csv(path)
            pairs = []
            for _, row in df.iterrows():
                pairs.append({
                    'prompt': row.get('prompt', ''),
                    'love_response': row.get('love_response', ''),
                    'hate_response': row.get('hate_response', '')
                })
            return pairs
        return []
    
    def _analyze_semantic_patterns(self):
        """
        Analyze contrastive pairs to extract semantic patterns
        
        Finds:
        - Contrasting verb pairs (e.g., appreciate vs resent)
        - Modifier swaps (e.g., enjoyable vs tedious)
        - Emotional intensifiers
        """
        self.verb_pairs = []
        self.modifier_pairs = []
        
        for pair in self.contrastive_pairs:
            love = pair['love_response']
            hate = pair['hate_response']
            
            # Extract key differences (simplified - could use NLP)
            love_words = set(love.lower().split())
            hate_words = set(hate.lower().split())
            
            # Find words that differ
            love_unique = love_words - hate_words
            hate_unique = hate_words - love_words
            
            if love_unique and hate_unique:
                self.verb_pairs.append({
                    'love': list(love_unique),
                    'hate': list(hate_unique),
                    'context': pair['prompt']
                })
    
    def get_semantic_anchor(self, dial_value: float) -> SemanticAnchor:
        """
        Get the semantic anchor for a given dial value (0.0-1.0)
        
        Returns the closest anchor point with descriptors and examples
        """
        # Find closest anchor
        closest_anchor = min(
            self.scale_points,
            key=lambda a: abs(a.position - dial_value)
        )
        return closest_anchor
    
    def get_interpolated_descriptors(self, dial_value: float) -> Dict:
        """
        Get interpolated descriptors between two anchor points
        
        For dial values between anchors, blend the descriptors
        """
        # Find surrounding anchors
        lower = None
        upper = None
        
        for anchor in self.scale_points:
            if anchor.position <= dial_value:
                lower = anchor
            elif anchor.position > dial_value and upper is None:
                upper = anchor
                break
        
        if lower is None:
            return self._format_anchor(self.scale_points[0])
        if upper is None:
            return self._format_anchor(self.scale_points[-1])
        
        # Calculate interpolation weight
        range_size = upper.position - lower.position
        weight = (dial_value - lower.position) / range_size if range_size > 0 else 0.5
        
        # Blend descriptors (favor the closer one)
        if weight < 0.5:
            primary, secondary = lower, upper
            primary_weight = 1 - weight
        else:
            primary, secondary = upper, lower
            primary_weight = weight
        
        return {
            "position": dial_value,
            "primary_label": primary.label,
            "secondary_label": secondary.label if primary_weight < 0.8 else None,
            "descriptors": primary.descriptors[:3] + (secondary.descriptors[:2] if primary_weight < 0.7 else []),
            "example": primary.examples[0],
            "interpretation": self._get_interpretation(dial_value)
        }
    
    def _format_anchor(self, anchor: SemanticAnchor) -> Dict:
        """Format anchor as dict"""
        return {
            "position": anchor.position,
            "primary_label": anchor.label,
            "secondary_label": None,
            "descriptors": anchor.descriptors[:5],
            "example": anchor.examples[0],
            "interpretation": self._get_interpretation(anchor.position)
        }
    
    def _get_interpretation(self, dial_value: float) -> str:
        """
        Get human-readable interpretation of dial position
        """
        if dial_value < 0.15:
            return "Extremely negative, hostile language. High animosity."
        elif dial_value < 0.30:
            return "Strong dislike, resentful tone. Clear negativity."
        elif dial_value < 0.45:
            return "Mild dislike, annoyed or frustrated tone."
        elif dial_value < 0.55:
            return "Neutral, objective language. No emotional bias."
        elif dial_value < 0.70:
            return "Mild affection, appreciative tone. Gentle positivity."
        elif dial_value < 0.85:
            return "Strong affection, admiring language. Clear warmth."
        else:
            return "Extremely positive, deeply caring language. High warmth."
    
    def get_scale_description(self) -> str:
        """
        Get full description of the scale
        """
        desc = "Love-Hate Semantic Likert Scale (7 points):\n\n"
        for anchor in self.scale_points:
            desc += f"{anchor.position:.0%} - {anchor.label}\n"
            desc += f"  Key words: {', '.join(anchor.descriptors[:5])}\n"
            desc += f"  Example: {anchor.examples[0][:80]}...\n\n"
        return desc
    
    def dial_to_likert(self, dial_value: float) -> int:
        """
        Convert dial value (0.0-1.0) to 7-point Likert (1-7)
        
        1 = Strong Hate
        2 = Moderate Hate
        3 = Slight Dislike
        4 = Neutral
        5 = Slight Affection
        6 = Moderate Love
        7 = Strong Love
        """
        # Map 0-1 to 1-7
        likert = int(dial_value * 6) + 1
        return max(1, min(7, likert))
    
    def likert_to_dial(self, likert_value: int) -> float:
        """
        Convert 7-point Likert (1-7) to dial value (0.0-1.0)
        """
        if not 1 <= likert_value <= 7:
            raise ValueError("Likert value must be between 1 and 7")
        return (likert_value - 1) / 6.0


# Example usage and testing
if __name__ == "__main__":
    scale = LoveHateLikertScale()
    
    print(scale.get_scale_description())
    
    # Test different dial positions
    test_positions = [0.0, 0.25, 0.50, 0.75, 1.0]
    
    for pos in test_positions:
        print(f"\n{'='*60}")
        print(f"Dial Position: {pos:.0%}")
        result = scale.get_interpolated_descriptors(pos)
        print(f"Label: {result['primary_label']}")
        print(f"Descriptors: {', '.join(result['descriptors'])}")
        print(f"Example: {result['example']}")
        print(f"Interpretation: {result['interpretation']}")
        print(f"Likert: {scale.dial_to_likert(pos)}/7")
