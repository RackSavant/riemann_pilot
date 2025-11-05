"""
Tea Party Conversation Engine

Orchestrates multi-character conversations with steering vectors
and video generation.
"""
import asyncio
from typing import List, Dict, Optional
from datetime import datetime
from openai import AsyncOpenAI
import os
import random

from app.tea_party_characters import TeaPartyCharacterManager, CHARACTERS
from app.veo_video_generator import get_veo_generator


class ConversationTurn:
    """Represents a single turn in the conversation"""
    
    def __init__(
        self,
        character_id: str,
        character_name: str,
        text: str,
        video_url: Optional[str] = None,
        dial_values: Optional[Dict[str, float]] = None,
        model: str = "gpt-4"
    ):
        self.character_id = character_id
        self.character_name = character_name
        self.text = text
        self.video_url = video_url
        self.dial_values = dial_values or {}
        self.model = model
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            "character_id": self.character_id,
            "character_name": self.character_name,
            "text": self.text,
            "video_url": self.video_url,
            "dial_values": self.dial_values,
            "model": self.model,
            "timestamp": self.timestamp.isoformat()
        }


class TeaPartyConversationEngine:
    """Manages the flow of conversation between characters"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize conversation engine
        
        Args:
            api_key: OpenRouter API key (or uses OPENROUTER_API_KEY or OPENAI_API_KEY env var)
        """
        # Try OpenRouter first, then OpenAI
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenRouter or OpenAI API key required. Set OPENROUTER_API_KEY or OPENAI_API_KEY env var")
        
        # Configure OpenAI client for OpenRouter or OpenAI
        if os.getenv("OPENROUTER_API_KEY"):
            self.client = AsyncOpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.api_key,
                default_headers={
                    "HTTP-Referer": "https://github.com/yourusername/tea-party-mvp",
                    "X-Title": "Tea Party Sentiment Conversation"
                }
            )
            self.using_openrouter = True
            print("🔄 Using OpenRouter for LLM calls")
        else:
            self.client = AsyncOpenAI(api_key=self.api_key)
            self.using_openrouter = False
            print("🤖 Using OpenAI for LLM calls")
        
        # Available LLM models for comparison (using FREE models on OpenRouter)
        self.available_models = {
            "gpt-4": "meta-llama/llama-3.2-3b-instruct:free" if self.using_openrouter else "gpt-4",  # FREE!
            "claude": "meta-llama/llama-3.2-3b-instruct:free",  # FREE!
            "gemini": "meta-llama/llama-3.2-3b-instruct:free"  # FREE!
        }
        
        self.character_manager = TeaPartyCharacterManager()
        self.veo_generator = get_veo_generator()
        self.conversation_history: List[ConversationTurn] = []
        self.current_topic = "tea and pastries"
    
    async def generate_response(
        self,
        character_id: str,
        context: Optional[str] = None,
        generate_video: bool = True,
        model: str = "gpt-4"
    ) -> ConversationTurn:
        """
        Generate a character's response based on their current dial settings
        
        Args:
            character_id: ID of the character speaking
            context: Optional context or prompt for the response
            generate_video: Whether to generate video (takes 11s-6min)
        
        Returns:
            ConversationTurn object
        """
        # Get character profile
        profile = self.character_manager.get_character(character_id)
        char_info = self.character_manager.get_character_info(character_id)
        
        # Build conversation context
        recent_history = self._get_recent_history(last_n=5)
        
        # Get steering prompt
        system_prompt = profile.get_steering_prompt()
        
        # DEBUG: Show current dial values and steering
        print(f"\n🎛️ {profile.character_name} dial values:")
        for dim, val in profile.dial_values.items():
            print(f"   {dim}: {val:.2f} ({int(val*100)}%)")
        print(f"📋 Steering prompt preview:")
        print(f"   {system_prompt[:200]}...")
        
        # Build user prompt (simplified for small models)
        user_prompt = f"""{context or f"You're at a tea party. Share your thoughts about {self.current_topic}."}

Respond as {profile.character_name} in 2-3 sentences. Follow your emotional state exactly."""
        
        # Generate text response with specified model
        response_text = await self._generate_text_response(system_prompt, user_prompt, model)
        
        # Create turn object
        turn = ConversationTurn(
            character_id=character_id,
            character_name=profile.character_name,
            text=response_text,
            dial_values=profile.dial_values.copy(),
            model=model
        )
        
        # Generate video if requested
        if generate_video:
            video_result = await self.veo_generator.generate_character_video(
                character_name=profile.character_name,
                character_appearance=char_info["appearance"],
                dialogue=response_text,
                scene_description="elegant tea party with ornate decorations and warm lighting"
            )
            
            if video_result.get("status") == "completed":
                turn.video_url = video_result["video_url"]
        
        # Add to history
        self.conversation_history.append(turn)
        
        return turn
    
    async def _generate_text_response(self, system_prompt: str, user_prompt: str, model: str = "gpt-4") -> str:
        """Generate text response using specified LLM model"""
        try:
            # Get the model string
            model_string = self.available_models.get(model, self.available_models["gpt-4"])
            
            # Use new OpenAI client API
            response = await self.client.chat.completions.create(
                model=model_string,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=150,
                temperature=1.2  # Higher temperature for more varied, extreme responses
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"❌ LLM API error ({model}): {e}")
            print(f"   System prompt length: {len(system_prompt)}")
            print(f"   User prompt: {user_prompt[:100]}...")
            return self._get_inspirational_quote()
    
    def _get_recent_history(self, last_n: int = 5) -> str:
        """Get formatted recent conversation history"""
        if not self.conversation_history:
            return "This is the start of the conversation."
        
        recent = self.conversation_history[-last_n:]
        lines = []
        for turn in recent:
            lines.append(f"{turn.character_name}: {turn.text}")
        
        return "\n".join(lines)
    
    def _get_inspirational_quote(self) -> str:
        """Return a random inspirational quote when LLM fails"""
        quotes = [
            # Philosophers
            "\"The only true wisdom is in knowing you know nothing.\" - Socrates",
            "\"I think, therefore I am.\" - René Descartes",
            "\"The unexamined life is not worth living.\" - Socrates",
            "\"To be yourself in a world that is constantly trying to make you something else is the greatest accomplishment.\" - Ralph Waldo Emerson",
            "\"The only way to deal with an unfree world is to become so absolutely free that your very existence is an act of rebellion.\" - Albert Camus",
            "\"We are what we repeatedly do. Excellence, then, is not an act, but a habit.\" - Aristotle",
            "\"The cave you fear to enter holds the treasure you seek.\" - Joseph Campbell",
            "\"He who has a why to live can bear almost any how.\" - Friedrich Nietzsche",
            "\"The mind is everything. What you think you become.\" - Buddha",
            "\"Know thyself.\" - Ancient Greek aphorism",
            
            # Pop Culture - Movies
            "\"Do or do not. There is no try.\" - Yoda, Star Wars",
            "\"Life moves pretty fast. If you don't stop and look around once in a while, you could miss it.\" - Ferris Bueller",
            "\"Why do we fall? So we can learn to pick ourselves back up.\" - Alfred, Batman Begins",
            "\"Just keep swimming.\" - Dory, Finding Nemo",
            "\"To infinity and beyond!\" - Buzz Lightyear, Toy Story",
            "\"It's not who I am underneath, but what I do that defines me.\" - Batman",
            "\"Our lives are defined by opportunities, even the ones we miss.\" - Benjamin Button",
            "\"Hope is a good thing, maybe the best of things, and no good thing ever dies.\" - Shawshank Redemption",
            "\"The flower that blooms in adversity is the most rare and beautiful of all.\" - Mulan",
            
            # Pop Culture - TV
            "\"Winter is coming.\" - Ned Stark, Game of Thrones",
            "\"I am the one who knocks.\" - Walter White, Breaking Bad",
            "\"How you doin'?\" - Joey Tribbiani, Friends",
            "\"That's what she said.\" - Michael Scott, The Office",
            "\"Live long and prosper.\" - Spock, Star Trek",
            
            # Pop Culture - Music/Culture
            "\"You miss 100% of the shots you don't take.\" - Wayne Gretzky",
            "\"The greatest glory in living lies not in never falling, but in rising every time we fall.\" - Nelson Mandela",
            "\"In the middle of difficulty lies opportunity.\" - Albert Einstein",
            "\"Be the change you wish to see in the world.\" - Gandhi",
            "\"I have a dream.\" - Martin Luther King Jr.",
            
            # Modern/Tech
            "\"Stay hungry, stay foolish.\" - Steve Jobs",
            "\"Move fast and break things.\" - Mark Zuckerberg",
            "\"The best way to predict the future is to invent it.\" - Alan Kay",
            "\"Any sufficiently advanced technology is indistinguishable from magic.\" - Arthur C. Clarke",
            
            # Motivational
            "\"What doesn't kill you makes you stronger.\" - Friedrich Nietzsche",
            "\"Carpe diem. Seize the day.\" - Horace",
            "\"Fortune favors the bold.\" - Virgil",
            "\"When life gives you lemons, make lemonade.\" - Elbert Hubbard",
            "\"This too shall pass.\" - Persian adage",
            "\"The journey of a thousand miles begins with one step.\" - Lao Tzu",
            "\"Today is a good day to be alive.\" - Unknown",
        ]
        
        return random.choice(quotes)
    
    async def run_conversation_round(
        self,
        character_order: Optional[List[str]] = None,
        generate_videos: bool = True,
        model: str = "gpt-4"
    ) -> List[ConversationTurn]:
        """
        Run one round of conversation (all characters speak once)
        
        Args:
            character_order: List of character IDs in speaking order
                           (defaults to seating order)
            generate_videos: Whether to generate videos
        
        Returns:
            List of conversation turns
        """
        if character_order is None:
            character_order = [c["id"] for c in CHARACTERS]
        
        turns = []
        for char_id in character_order:
            turn = await self.generate_response(
                character_id=char_id,
                generate_video=generate_videos,
                model=model
            )
            turns.append(turn)
            
            # Brief pause between speakers
            await asyncio.sleep(1)
        
        return turns
    
    def set_topic(self, topic: str):
        """Change the conversation topic"""
        self.current_topic = topic
    
    def update_character_dial(self, character_id: str, dimension: str, value: float):
        """Update a character's dial value"""
        self.character_manager.update_character_dial(character_id, dimension, value)
    
    def get_all_character_states(self) -> List[Dict]:
        """Get current state of all characters"""
        return self.character_manager.get_all_character_states()
    
    def get_conversation_history(self) -> List[Dict]:
        """Get full conversation history"""
        return [turn.to_dict() for turn in self.conversation_history]
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    async def generate_opening_scene(self) -> Dict:
        """Generate an establishing shot of the tea party"""
        return await self.veo_generator.generate_tea_party_scene(
            scene_description="Five diverse friends enjoying an elegant, whimsical tea party",
            duration_seconds=8
        )


# Example usage
async def example_conversation():
    """Example of running a tea party conversation"""
    engine = TeaPartyConversationEngine()
    
    # Set topic
    engine.set_topic("the most memorable tea party experience")
    
    # Adjust some dials for variety
    engine.update_character_dial("purple_person", "irony", 0.8)  # Make Alex more sarcastic
    engine.update_character_dial("gray_beard", "theory_of_mind", 0.9)  # Sterling very empathetic
    engine.update_character_dial("phone_person", "self_other", 0.2)  # Jordan self-focused
    
    # Generate opening scene
    print("🎬 Generating opening scene...")
    opening = await engine.generate_opening_scene()
    print(f"Opening scene: {opening.get('video_url', 'Failed')}")
    
    # Run one round of conversation
    print("\n💬 Starting conversation...")
    turns = await engine.run_conversation_round(generate_videos=False)  # Set True for videos
    
    # Print results
    for turn in turns:
        print(f"\n{turn.character_name}: {turn.text}")
        if turn.video_url:
            print(f"  🎥 Video: {turn.video_url}")


if __name__ == "__main__":
    asyncio.run(example_conversation())
