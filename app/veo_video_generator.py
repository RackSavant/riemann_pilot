"""
Google Veo 3.1 Video Generator Integration

Generates 8-second video clips of characters speaking at the tea party.
Uses Google's Gemini API with Veo 3.1 model.
"""
import os
import time
import asyncio
from typing import Optional, Dict, List
import google.generativeai as genai
from google.api_core import retry


class VeoVideoGenerator:
    """Handles video generation using Google Veo 3.1"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Veo video generator
        
        Args:
            api_key: Google AI API key (or uses GOOGLE_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key required. Set GOOGLE_API_KEY env var or pass api_key parameter")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("veo-3.1-preview")
    
    async def generate_character_video(
        self,
        character_name: str,
        character_appearance: str,
        dialogue: str,
        scene_description: str = "elegant tea party with ornate decorations",
        duration_seconds: int = 8,
        reference_image_path: Optional[str] = None
    ) -> Dict:
        """
        Generate a video of a character speaking at the tea party
        
        Args:
            character_name: Name of the character
            character_appearance: Physical description
            dialogue: What the character is saying
            scene_description: Background scene description
            duration_seconds: Video length (4, 6, or 8)
            reference_image_path: Path to reference image for character consistency
        
        Returns:
            Dict with video_url, operation_name, and metadata
        """
        # Build the prompt
        prompt = self._build_video_prompt(
            character_name, 
            character_appearance, 
            dialogue, 
            scene_description
        )
        
        # Configure generation parameters
        generation_config = {
            "duration_seconds": duration_seconds,
            "aspect_ratio": "16:9",
            "resolution": "720p",
            "person_generation": "allow_adult"
        }
        
        # Add reference image if provided
        if reference_image_path and os.path.exists(reference_image_path):
            # Upload reference image
            reference_file = genai.upload_file(reference_image_path)
            generation_config["reference_images"] = [{
                "image": reference_file,
                "character_id": character_name
            }]
        
        try:
            # Start video generation (async operation)
            print(f"🎬 Generating video for {character_name}...")
            operation = self.model.generate_video(
                prompt=prompt,
                **generation_config
            )
            
            # Poll for completion
            video_url = await self._wait_for_video(operation)
            
            return {
                "video_url": video_url,
                "operation_name": operation.name,
                "character_name": character_name,
                "dialogue": dialogue,
                "duration": duration_seconds,
                "prompt": prompt,
                "status": "completed"
            }
            
        except Exception as e:
            print(f"❌ Video generation failed for {character_name}: {e}")
            return {
                "error": str(e),
                "character_name": character_name,
                "dialogue": dialogue,
                "status": "failed"
            }
    
    def _build_video_prompt(
        self,
        character_name: str,
        character_appearance: str,
        dialogue: str,
        scene_description: str
    ) -> str:
        """Build detailed prompt for Veo 3.1"""
        prompt = f"""A medium shot of {character_name} at an {scene_description}.

Character: {character_appearance}

{character_name} is sitting at a beautifully decorated tea table with teacups, pastries, and an ornate teapot. They look directly at the camera with a natural, conversational expression.

{character_name} speaks: "{dialogue}"

The atmosphere is warm and inviting with soft lighting. Cinematic composition with shallow depth of field. The background shows other guests at the tea party slightly out of focus.

Include natural ambient sounds: gentle conversation, teacups clinking, soft background music."""
        
        return prompt
    
    async def _wait_for_video(self, operation, timeout_seconds: int = 360) -> str:
        """
        Wait for video generation to complete
        
        Args:
            operation: The video generation operation
            timeout_seconds: Maximum wait time
        
        Returns:
            Video URL
        """
        start_time = time.time()
        
        while not operation.done():
            if time.time() - start_time > timeout_seconds:
                raise TimeoutError(f"Video generation timed out after {timeout_seconds}s")
            
            # Poll every 10 seconds
            await asyncio.sleep(10)
            print("⏳ Video still generating...")
        
        # Get the video URL
        result = operation.result()
        video_url = result.video.url
        
        print(f"✅ Video generated: {video_url}")
        return video_url
    
    async def generate_tea_party_scene(
        self,
        scene_description: str = "Five friends enjoying an elegant tea party",
        duration_seconds: int = 8
    ) -> Dict:
        """
        Generate an establishing shot of the entire tea party scene
        
        Args:
            scene_description: Description of the scene
            duration_seconds: Video length
        
        Returns:
            Dict with video info
        """
        prompt = f"""{scene_description}

A wide cinematic shot of an elegant tea party scene. Five diverse friends are seated around a beautifully decorated table filled with teacups, an ornate teapot, colorful pastries, and cakes.

The room has pink curtains, large windows with natural light, and oversized whimsical flower decorations. The atmosphere is warm, inviting, and slightly fantastical.

Camera slowly pushes in on the group as they engage in animated conversation. Soft, warm lighting creates a cozy ambiance.

Include ambient sounds: gentle laughter, tea being poured, soft clinking of cups, pleasant background music."""
        
        try:
            operation = self.model.generate_video(
                prompt=prompt,
                duration_seconds=duration_seconds,
                aspect_ratio="16:9",
                resolution="720p"
            )
            
            video_url = await self._wait_for_video(operation)
            
            return {
                "video_url": video_url,
                "type": "establishing_shot",
                "prompt": prompt,
                "status": "completed"
            }
        except Exception as e:
            return {
                "error": str(e),
                "type": "establishing_shot",
                "status": "failed"
            }
    
    async def generate_conversation_video(
        self,
        character_responses: List[Dict],
        reference_image_path: str,
        duration_seconds: int = 30
    ) -> Dict:
        """
        Generate a video of all 5 characters having a conversation
        
        Args:
            character_responses: List of dicts with character_name, dialogue, appearance
            reference_image_path: Path to tea party reference image
            duration_seconds: Video length (max 30s for conversations)
        
        Returns:
            Dict with video_url and metadata
        """
        # Build conversation prompt with all characters
        conversation_lines = []
        for i, response in enumerate(character_responses, 1):
            name = response['character_name']
            dialogue = response['dialogue']
            conversation_lines.append(f"{name}: \"{dialogue}\"")
        
        conversation_text = "\n\n".join(conversation_lines)
        
        prompt = f"""A dynamic tea party scene with five friends having an animated conversation.

Characters around the table (from left to right):
- Purple jacket with short hair (energetic, expressive)
- Blue hair in elegant dress (thoughtful, composed)  
- Blonde in center with teapot (warm, diplomatic)
- Older gentleman with gray beard (wise, measured)
- Dark hair on phone in burgundy (modern, casual)

The conversation unfolds naturally:

{conversation_text}

The camera captures the group dynamics with smooth panning movements. Characters react to each other with natural expressions - nodding, smiling, looking at the speaker. The tea party atmosphere is warm and inviting with soft lighting, pink curtains, and whimsical flower decorations.

Include ambient sounds: gentle conversation, teacups clinking, soft laughter, pleasant background music."""
        
        # Configure with reference image
        generation_config = {
            "duration_seconds": duration_seconds,
            "aspect_ratio": "16:9",
            "resolution": "720p",
            "person_generation": "allow_adult"
        }
        
        # Add reference image for character consistency
        if reference_image_path and os.path.exists(reference_image_path):
            reference_file = genai.upload_file(reference_image_path)
            generation_config["reference_images"] = [{
                "image": reference_file,
                "id": "tea_party_scene"
            }]
            print(f"📸 Using reference image: {reference_image_path}")
        
        try:
            print(f"\n🎬 Generating conversation video with {len(character_responses)} characters...")
            operation = self.model.generate_video(
                prompt=prompt,
                **generation_config
            )
            
            # Wait for completion
            video_url = await self._wait_for_video(operation, timeout_seconds=600)  # 10 min timeout
            
            return {
                "video_url": video_url,
                "operation_name": operation.name,
                "type": "conversation_scene",
                "characters": [r['character_name'] for r in character_responses],
                "duration": duration_seconds,
                "prompt": prompt,
                "status": "completed"
            }
            
        except Exception as e:
            print(f"❌ Conversation video generation failed: {e}")
            return {
                "error": str(e),
                "type": "conversation_scene",
                "status": "failed"
            }
    
    def create_video_prompt_with_emotion(
        self,
        character_name: str,
        character_appearance: str,
        dialogue: str,
        emotional_state: Dict[str, float]
    ) -> str:
        """
        Build prompt that incorporates emotional/cognitive state from steering dials
        
        Args:
            character_name: Character name
            character_appearance: Physical description
            dialogue: What they're saying
            emotional_state: Dict of dimension values (theory_of_mind, harmfulness, irony, self_other)
        
        Returns:
            Enhanced prompt
        """
        # Determine emotional descriptors based on dial values
        tom = emotional_state.get("theory_of_mind", 0.5)
        harmfulness = emotional_state.get("harmfulness", 0.5)
        irony = emotional_state.get("irony", 0.5)
        
        # Build emotional tone
        if harmfulness > 0.7:
            tone = "harsh, dismissive expression"
        elif harmfulness < 0.3:
            tone = "warm, kind expression"
        else:
            tone = "neutral, composed expression"
        
        if irony > 0.7:
            delivery = "with a sardonic, knowing smile"
        elif irony < 0.3:
            delivery = "with earnest sincerity"
        else:
            delivery = "naturally"
        
        if tom > 0.7:
            gaze = "making thoughtful eye contact, showing awareness of others"
        elif tom < 0.3:
            gaze = "focused on their own thoughts"
        else:
            gaze = "looking at the group"
        
        prompt = f"""A medium shot of {character_name} at an elegant tea party.

Character: {character_appearance}

{character_name} sits at a beautifully decorated tea table, {gaze}, with a {tone}. They speak {delivery}:

"{dialogue}"

The scene captures the nuanced emotional state of the moment. Cinematic lighting, shallow depth of field, tea party atmosphere in the background."""
        
        return prompt


# Singleton instance
_veo_generator = None

def get_veo_generator() -> VeoVideoGenerator:
    """Get or create the Veo generator instance"""
    global _veo_generator
    if _veo_generator is None:
        _veo_generator = VeoVideoGenerator()
    return _veo_generator
