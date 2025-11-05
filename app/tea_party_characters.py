"""
Tea Party Character Definitions

Based on the 5 characters in the tea party image.
Each character has a unique personality and visual description.
"""
from typing import Dict, List
from app.multi_dimensional_scale import MultiDimensionalScale, CharacterSteeringProfile


# Character definitions based on tea party image
CHARACTERS = [
    {
        "id": "purple_person",
        "name": "Ptothe",
        "position": "left",
        "appearance": "Short reddish-brown hair, purple patterned outfit, gold earrings",
        "base_personality": "Quick-witted and energetic. Often the first to speak up with enthusiasm. Has a warm, engaging presence and loves to make others laugh.",
        "default_dials": {
            "theory_of_mind": 0.6,
            "harmfulness": 0.2,
            "irony": 0.5,
            "self_other": 0.6
        }
    },
    {
        "id": "blue_hair",
        "name": "Sevvy",
        "position": "center-left",
        "appearance": "Long blue hair, dark blue polka dot dress, elegant and composed",
        "base_personality": "Thoughtful and observant. Tends to listen more than speak, but when they do share, it's insightful. Has a calming presence.",
        "default_dials": {
            "theory_of_mind": 0.8,
            "harmfulness": 0.1,
            "irony": 0.3,
            "self_other": 0.7
        }
    },
    {
        "id": "blonde_center",
        "name": "RackSavant",
        "position": "center",
        "appearance": "Blonde wavy hair, light blue outfit with white collar, gentle expression",
        "base_personality": "Sweet and diplomatic. Often plays peacekeeper and tries to find common ground. Genuinely interested in others' perspectives.",
        "default_dials": {
            "theory_of_mind": 0.7,
            "harmfulness": 0.0,
            "irony": 0.2,
            "self_other": 0.8
        }
    },
    {
        "id": "gray_beard",
        "name": "Sterling",
        "position": "center-right",
        "appearance": "Distinguished gentleman with gray beard and hair, brown suit",
        "base_personality": "Wise and measured. Speaks with gravitas and often shares stories from past experiences. Can be quietly sardonic.",
        "default_dials": {
            "theory_of_mind": 0.7,
            "harmfulness": 0.3,
            "irony": 0.6,
            "self_other": 0.5
        }
    },
    {
        "id": "phone_person",
        "name": "Jordan",
        "position": "right",
        "appearance": "Dark hair with side-swept bangs, burgundy/maroon outfit, phone in hand",
        "base_personality": "Modern and slightly distracted. Switches between engagement and checking phone. Can be witty but sometimes misses social cues.",
        "default_dials": {
            "theory_of_mind": 0.4,
            "harmfulness": 0.2,
            "irony": 0.7,
            "self_other": 0.3
        }
    }
]


class TeaPartyCharacterManager:
    """Manages all 5 tea party characters with their steering profiles"""
    
    def __init__(self):
        self.scale = MultiDimensionalScale()
        self.characters: Dict[str, CharacterSteeringProfile] = {}
        self._initialize_characters()
    
    def _initialize_characters(self):
        """Create steering profiles for all characters"""
        for char_data in CHARACTERS:
            profile = CharacterSteeringProfile(
                character_id=char_data["id"],
                character_name=char_data["name"],
                base_personality=char_data["base_personality"],
                scale=self.scale
            )
            
            # Set default dial values
            for dim, value in char_data["default_dials"].items():
                profile.update_dial(dim, value)
            
            self.characters[char_data["id"]] = profile
    
    def get_character(self, character_id: str) -> CharacterSteeringProfile:
        """Get a character's steering profile"""
        if character_id not in self.characters:
            raise ValueError(f"Unknown character: {character_id}")
        return self.characters[character_id]
    
    def update_character_dial(self, character_id: str, dimension: str, value: float):
        """Update a specific dial for a character"""
        character = self.get_character(character_id)
        character.update_dial(dimension, value)
    
    def get_all_character_states(self) -> List[Dict]:
        """Get current state of all characters"""
        states = []
        for char_data in CHARACTERS:
            char_id = char_data["id"]
            profile = self.characters[char_id]
            
            state = profile.get_current_state()
            state.update({
                "appearance": char_data["appearance"],
                "position": char_data["position"]
            })
            states.append(state)
        
        return states
    
    def get_character_info(self, character_id: str) -> Dict:
        """Get complete info for a character including metadata"""
        char_data = next((c for c in CHARACTERS if c["id"] == character_id), None)
        if not char_data:
            raise ValueError(f"Unknown character: {character_id}")
        
        profile = self.characters[character_id]
        state = profile.get_current_state()
        
        return {
            **char_data,
            "current_state": state
        }
    
    def reset_character_dials(self, character_id: str):
        """Reset a character's dials to defaults"""
        char_data = next((c for c in CHARACTERS if c["id"] == character_id), None)
        if not char_data:
            raise ValueError(f"Unknown character: {character_id}")
        
        profile = self.characters[character_id]
        for dim, value in char_data["default_dials"].items():
            profile.update_dial(dim, value)
    
    def reset_all_dials(self):
        """Reset all characters to their default dial values"""
        for char_data in CHARACTERS:
            self.reset_character_dials(char_data["id"])


# Helper function to get character by name
def get_character_by_name(name: str) -> Dict:
    """Get character data by name"""
    return next((c for c in CHARACTERS if c["name"] == name), None)
