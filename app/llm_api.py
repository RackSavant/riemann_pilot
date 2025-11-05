"""
OpenRouter API LLM Engine for Gemma-3-27B
Replaces local Hugging Face models with cloud API
"""
import os
import requests
import json
from typing import Dict, List, Optional


class OpenRouterLLM:
    """
    LLM engine using OpenRouter API
    Supports multiple Gemma-3 models without local downloads
    """
    
    def __init__(
        self,
        model_name: str = "google/gemma-3-27b-it:free",
        api_key: Optional[str] = None,
        site_url: str = "http://localhost:8501",
        site_name: str = "AI Steering Vector Lab"
    ):
        self.model_name = model_name
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.site_url = site_url
        self.site_name = site_name
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        
        if not self.api_key:
            raise ValueError(
                "OPENROUTER_API_KEY not found. "
                "Get your key at https://openrouter.ai/keys and add to .env"
            )
        
        print(f"✅ OpenRouter LLM initialized: {model_name}")
    
    def build_dial_instruction(self, dials: Dict[str, float]) -> str:
        """
        Create instruction text based on dial settings
        
        Maps semantic dial values to natural language instructions
        """
        love = dials.get('love', 0.5)
        
        # Map dial value to tone instruction
        if love < 0.2:
            tone = "Respond in a cold, critical, and hostile manner. Be harsh and dismissive."
        elif love < 0.4:
            tone = "Respond in a somewhat negative and skeptical manner. Be cautious and reserved."
        elif love < 0.6:
            tone = "Respond in a neutral and objective manner. Be balanced and factual."
        elif love < 0.8:
            tone = "Respond in a warm and supportive manner. Be encouraging and positive."
        else:
            tone = "Respond in an extremely loving, caring, and enthusiastic manner. Be deeply supportive and affirming."
        
        return tone
    
    async def generate(
        self,
        prompt: str,
        dials: Optional[Dict[str, float]] = None,
        context: Optional[List[str]] = None,
        temperature: float = 0.7,
        max_tokens: int = 512
    ) -> str:
        """
        Generate a response using OpenRouter API
        
        Args:
            prompt: User's input prompt
            dials: Semantic dial settings (love, commitment, etc.)
            context: Optional context documents from retrieval
            temperature: Generation temperature (0-2)
            max_tokens: Maximum tokens to generate
        
        Returns:
            Generated text response
        """
        # Build system message with dial instructions
        system_message = "You are a helpful AI assistant."
        if dials:
            dial_instruction = self.build_dial_instruction(dials)
            system_message += f"\n\nIMPORTANT: {dial_instruction}"
        
        # Build user message with context
        user_message = ""
        if context and len(context) > 0:
            user_message += "Context:\n"
            for i, doc in enumerate(context[:3], 1):
                user_message += f"{i}. {doc}\n\n"
            user_message += "---\n\n"
        user_message += f"Query: {prompt}"
        
        # Prepare API request
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.site_url,
            "X-Title": self.site_name
        }
        
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        # Make API call
        response = requests.post(
            self.api_url,
            headers=headers,
            data=json.dumps(payload),
            timeout=30
        )
        
        if response.status_code != 200:
            error_detail = response.json() if response.text else {"error": "Unknown error"}
            raise Exception(
                f"OpenRouter API error ({response.status_code}): {error_detail}"
            )
        
        # Extract response
        result = response.json()
        generated_text = result["choices"][0]["message"]["content"]
        
        return generated_text


# Model variants available on OpenRouter
OPENROUTER_MODELS = {
    "gemma-27b": "google/gemma-3-27b-it:free",      # Large, free tier
    "gemma-9b": "google/gemma-2-9b-it:free",        # Medium, free
    "gemma-2b": "google/gemma-2-2b-it:free"         # Small, free
}
