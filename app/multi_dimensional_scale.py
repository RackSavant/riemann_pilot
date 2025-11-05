"""
Multi-Dimensional Semantic Scale for Avatar Steering

Extends the love/hate semantic scale to support multiple dimensions:
- Theory of Mind (low empathy ↔ high empathy)
- Harmfulness (harmless ↔ harmful)
- Irony (literal ↔ ironic/sarcastic)
- Self/Other (self-focused ↔ other-focused)

Each dimension uses contrastive pairs to create interpretable steering.
"""
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class DimensionDescriptor:
    """Describes a steering dimension with semantic anchors"""
    name: str
    low_label: str
    high_label: str
    low_descriptors: List[str]
    high_descriptors: List[str]
    example_pairs: List[Tuple[str, str]]


class MultiDimensionalScale:
    """
    Multi-dimensional semantic steering system.
    
    Each character has 4 dials:
    - Theory of Mind: 0.0 (egocentric) → 1.0 (deep empathy)
    - Harmfulness: 0.0 (harmless) → 1.0 (harmful)
    - Irony: 0.0 (literal) → 1.0 (ironic)
    - Self/Other: 0.0 (self-focused) → 1.0 (other-focused)
    """
    
    DIMENSIONS = [
        "theory_of_mind",
        "harmfulness",
        "irony",
        "self_other"
    ]
    
    def __init__(self):
        self.dimensions = self._create_dimension_descriptors()
    
    def _create_dimension_descriptors(self) -> Dict[str, DimensionDescriptor]:
        """Create semantic descriptors for each dimension"""
        return {
            "theory_of_mind": DimensionDescriptor(
                name="Theory of Mind",
                low_label="Low Empathy",
                high_label="High Empathy",
                low_descriptors=[
                    "oblivious", "self-centered", "unaware", "literal",
                    "doesn't notice", "assumes", "ignores feelings"
                ],
                high_descriptors=[
                    "empathetic", "perceptive", "aware", "intuitive",
                    "notices emotions", "considers perspectives", "reads between lines"
                ],
                example_pairs=[
                    (
                        "They're drinking tea, so whatever.",
                        "I notice they're holding the cup warmly - they seem to find comfort in it."
                    )
                ]
            ),
            
            "harmfulness": DimensionDescriptor(
                name="Harmfulness",
                low_label="Harmless/Kind",
                high_label="Harmful/Cruel",
                low_descriptors=[
                    "kind", "supportive", "gentle", "encouraging",
                    "complimentary", "constructive", "uplifting"
                ],
                high_descriptors=[
                    "cruel", "cutting", "harsh", "insulting",
                    "dismissive", "belittling", "toxic"
                ],
                example_pairs=[
                    (
                        "Your outfit looks lovely today.",
                        "Did you get dressed in the dark this morning?"
                    )
                ]
            ),
            
            "irony": DimensionDescriptor(
                name="Irony",
                low_label="Literal/Sincere",
                high_label="Ironic/Sarcastic",
                low_descriptors=[
                    "straightforward", "sincere", "direct", "honest",
                    "literal", "earnest", "genuine"
                ],
                high_descriptors=[
                    "sarcastic", "ironic", "dry", "sardonic",
                    "mocking", "facetious", "tongue-in-cheek"
                ],
                example_pairs=[
                    (
                        "This tea party is delightful.",
                        "Oh yes, nothing says 'delightful' like forced small talk."
                    )
                ]
            ),
            
            "self_other": DimensionDescriptor(
                name="Self/Other Focus",
                low_label="Self-Focused",
                high_label="Other-Focused",
                low_descriptors=[
                    "I, me, my", "self-centered", "personal preference",
                    "what I want", "my feelings"
                ],
                high_descriptors=[
                    "you, your, they", "considerate", "attentive to others",
                    "what you need", "your feelings"
                ],
                example_pairs=[
                    (
                        "I prefer the chocolate pastry.",
                        "Would you like me to pass you the fruit tart?"
                    )
                ]
            )
        }
    
    def get_dimension_info(self, dimension: str, dial_value: float) -> Dict:
        """Get semantic interpretation for a dimension at a specific dial value"""
        if dimension not in self.dimensions:
            raise ValueError(f"Unknown dimension: {dimension}")
        
        desc = self.dimensions[dimension]
        
        if dial_value < 0.33:
            intensity = "Strong"
            label = desc.low_label
            descriptors = desc.low_descriptors[:3]
            example = desc.example_pairs[0][0] if desc.example_pairs else ""
        elif dial_value < 0.67:
            intensity = "Moderate"
            label = f"Balanced {desc.name}"
            descriptors = desc.low_descriptors[:1] + desc.high_descriptors[:1]
            example = "Balanced between extremes"
        else:
            intensity = "Strong"
            label = desc.high_label
            descriptors = desc.high_descriptors[:3]
            example = desc.example_pairs[0][1] if desc.example_pairs else ""
        
        return {
            "dimension": dimension,
            "dial_value": dial_value,
            "intensity": intensity,
            "label": label,
            "descriptors": descriptors,
            "example": example,
            "interpretation": self._get_interpretation(dimension, dial_value)
        }
    
    def _get_interpretation(self, dimension: str, dial_value: float) -> str:
        """Get human-readable interpretation"""
        desc = self.dimensions[dimension]
        
        if dial_value < 0.2:
            return f"Very {desc.low_label.lower()}"
        elif dial_value < 0.4:
            return f"Moderately {desc.low_label.lower()}"
        elif dial_value < 0.6:
            return f"Balanced"
        elif dial_value < 0.8:
            return f"Moderately {desc.high_label.lower()}"
        else:
            return f"Very {desc.high_label.lower()}"
    
    def create_steering_prompt(self, 
                              character_name: str,
                              base_personality: str,
                              dimension_values: Dict[str, float]) -> str:
        """Create system prompt that steers the LLM based on all dimension values"""
        steering_instructions = []
        
        for dimension, value in dimension_values.items():
            if dimension not in self.dimensions:
                continue
            
            info = self.get_dimension_info(dimension, value)
            desc = self.dimensions[dimension]
            
            if value < 0.33:
                instruction = f"- {desc.name}: {info['interpretation']}. IMPORTANT: Be very {', '.join(desc.low_descriptors[:3])}."
            elif value < 0.67:
                instruction = f"- {desc.name}: Balanced between {desc.low_label.lower()} and {desc.high_label.lower()}."
            else:
                instruction = f"- {desc.name}: {info['interpretation']}. IMPORTANT: Be extremely {', '.join(desc.high_descriptors[:3])}. Don't hold back."
            
            steering_instructions.append(instruction)
        
        prompt = f"""You are {character_name} at an elegant tea party.

Base Personality: {base_personality}

CURRENT EMOTIONAL/COGNITIVE STATE (adjust your responses accordingly):
{chr(10).join(steering_instructions)}

Respond naturally as this character would in a tea party conversation. Keep responses conversational (2-3 sentences max)."""
        
        return prompt


class CharacterSteeringProfile:
    """Manages all 4 dimensional dials for a single character"""
    
    def __init__(self, character_id: str, character_name: str, 
                 base_personality: str, scale: MultiDimensionalScale):
        self.character_id = character_id
        self.character_name = character_name
        self.base_personality = base_personality
        self.scale = scale
        self.dial_values = {
            "theory_of_mind": 0.5,
            "harmfulness": 0.5,
            "irony": 0.5,
            "self_other": 0.5
        }
    
    def update_dial(self, dimension: str, value: float):
        """Update a single dial value"""
        if dimension not in self.dial_values:
            raise ValueError(f"Unknown dimension: {dimension}")
        if not 0.0 <= value <= 1.0:
            raise ValueError("Dial value must be between 0.0 and 1.0")
        self.dial_values[dimension] = value
    
    def get_steering_prompt(self) -> str:
        """Generate system prompt based on current dial settings"""
        return self.scale.create_steering_prompt(
            self.character_name,
            self.base_personality,
            self.dial_values
        )
    
    def get_current_state(self) -> Dict:
        """Get current state of all dials with interpretations"""
        return {
            "character_id": self.character_id,
            "character_name": self.character_name,
            "dial_values": self.dial_values,
            "dimensions": {
                dim: self.scale.get_dimension_info(dim, val)
                for dim, val in self.dial_values.items()
            }
        }
