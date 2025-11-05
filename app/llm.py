"""
LLM Integration with Gemma
Generates responses using retrieved context and semantic dial adjustments
"""
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from typing import List, Dict, Optional
import json
import os
from dotenv import load_dotenv

# Load environment variables (optional)
load_dotenv()


class GemmaLLM:
    """
    Gemma LLM with dial-adjusted prompt generation
    
    Supports:
    - Context-aware response generation
    - Semantic dial influence on tone and content
    - Streaming responses (optional)
    """
    
    def __init__(
        self,
        model_name: str = "google/gemma-2b-it",  # or "google/gemma-7b-it" for better quality
        device: Optional[str] = None,
        max_length: int = 512
    ):
        """
        Initialize Gemma model
        
        Args:
            model_name: Gemma model variant (2b or 7b)
            device: Device to run on (cuda/cpu)
            max_length: Maximum generation length
        """
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.max_length = max_length
        
        # Get Hugging Face token if available (optional)
        hf_token = os.getenv("HF_TOKEN")
        token_status = "with auth" if hf_token else "without auth"
        
        print(f"🤖 Loading Gemma model: {model_name} on {self.device} ({token_status})...")
        
        # Load tokenizer and model
        # trust_remote_code needed for Gemma tokenizers
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            token=hf_token,
            trust_remote_code=True
        )
        
        # Set padding token if not set
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            device_map="auto" if self.device == "cuda" else None,
            token=hf_token,
            trust_remote_code=True
        )
        
        if self.device == "cpu":
            self.model = self.model.to(self.device)
        
        print(f"✅ Gemma loaded successfully!")
    
    def build_dial_instruction(self, dials: Dict[str, float]) -> str:
        """
        Create instruction text based on dial settings
        
        High dial values emphasize certain qualities in the response
        """
        instructions = []
        
        # Love dial (0.7+) - warm, empathetic tone
        if dials.get('love', 0.5) >= 0.7:
            instructions.append("Use a warm, empathetic, and compassionate tone")
        
        # Commitment dial (0.7+) - long-term focus
        if dials.get('commitment', 0.5) >= 0.7:
            instructions.append("Focus on long-term perspectives and sustained dedication")
        
        # Belonging dial (0.7+) - community emphasis
        if dials.get('belonging', 0.5) >= 0.7:
            instructions.append("Emphasize community, connection, and shared experiences")
        
        # Trust dial (0.7+) - security and reliability
        if dials.get('trust', 0.5) >= 0.7:
            instructions.append("Highlight trust, security, and reliability")
        
        # Growth dial (0.7+) - development focus
        if dials.get('growth', 0.5) >= 0.7:
            instructions.append("Focus on personal development and learning")
        
        if not instructions:
            return "Provide a balanced, informative response"
        
        return ". ".join(instructions) + "."
    
    def generate_response(
        self,
        query: str,
        context_docs: List[Dict],
        dials: Dict[str, float],
        temperature: float = 0.7,
        top_p: float = 0.9
    ) -> Dict:
        """
        Generate response using Gemma with dial-adjusted prompts
        
        Args:
            query: User question
            context_docs: Retrieved documents from RAG
            dials: Semantic dial settings
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
        
        Returns:
            Dictionary with generated response and metadata
        """
        # Build context from retrieved documents
        context_text = self._build_context(context_docs)
        
        # Build dial-specific instruction
        dial_instruction = self.build_dial_instruction(dials)
        
        # Create prompt with Gemma chat template
        prompt = self._build_prompt(query, context_text, dial_instruction, dials)
        
        # Tokenize
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=self.max_length,
                temperature=temperature,
                top_p=top_p,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        # Decode
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract only the response (remove prompt)
        response = self._extract_response(generated_text, prompt)
        
        return {
            "response": response,
            "dial_instruction": dial_instruction,
            "dials_applied": dials,
            "context_sources": [doc["metadata"]["title"] for doc in context_docs],
            "model": "gemma"
        }
    
    def _build_context(self, docs: List[Dict], max_docs: int = 3) -> str:
        """Build context text from retrieved documents"""
        context_parts = []
        
        for i, doc in enumerate(docs[:max_docs], 1):
            title = doc["metadata"].get("title", "Document")
            text = doc["text"][:500]  # Limit length per doc
            context_parts.append(f"Source {i} ({title}):\n{text}")
        
        return "\n\n".join(context_parts)
    
    def _build_prompt(
        self,
        query: str,
        context: str,
        dial_instruction: str,
        dials: Dict[str, float]
    ) -> str:
        """
        Build Gemma-compatible prompt with dial adjustments
        
        Uses Gemma's instruction format
        """
        # Format dial values for display
        dial_emphasis = ", ".join([
            f"{k.capitalize()}: {v:.1f}" 
            for k, v in dials.items() 
            if v >= 0.6  # Only show emphasized dials
        ])
        
        prompt = f"""<start_of_turn>user
You are a helpful assistant specializing in relationships, emotional intelligence, and personal development.

**Context from Knowledge Base:**
{context}

**Response Guidelines:**
{dial_instruction}

**Emphasis Areas:** {dial_emphasis if dial_emphasis else "Balanced"}

**User Question:**
{query}

Please provide a thoughtful response based on the context provided, following the guidelines above.<end_of_turn>
<start_of_turn>model
"""
        
        return prompt
    
    def _extract_response(self, generated_text: str, prompt: str) -> str:
        """Extract the model's response from generated text"""
        # Remove the prompt part
        if prompt in generated_text:
            response = generated_text[len(prompt):].strip()
        else:
            # Fallback: try to find the response after the model turn
            parts = generated_text.split("<start_of_turn>model")
            if len(parts) > 1:
                response = parts[-1].strip()
            else:
                response = generated_text.strip()
        
        # Clean up any trailing special tokens
        response = response.replace("<end_of_turn>", "").strip()
        
        return response
    
    def get_model_info(self) -> Dict:
        """Get information about the loaded model"""
        return {
            "model_name": self.model.config.name_or_path,
            "device": str(self.device),
            "max_length": self.max_length,
            "parameters": sum(p.numel() for p in self.model.parameters()),
            "dtype": str(self.model.dtype)
        }


# Dial-specific prompt templates for different emphasis levels
DIAL_TEMPLATES = {
    "love_high": {
        "tone": "warm, compassionate, empathetic",
        "focus": "emotional connection, care, affection",
        "language": "Use heartfelt and supportive language"
    },
    "commitment_high": {
        "tone": "steady, dedicated, long-term focused",
        "focus": "sustained effort, loyalty, perseverance",
        "language": "Emphasize consistency and dedication"
    },
    "belonging_high": {
        "tone": "inclusive, communal, connected",
        "focus": "community, shared experiences, togetherness",
        "language": "Highlight connection and inclusion"
    },
    "trust_high": {
        "tone": "reliable, secure, honest",
        "focus": "safety, honesty, dependability",
        "language": "Build confidence and security"
    },
    "growth_high": {
        "tone": "encouraging, developmental, forward-thinking",
        "focus": "learning, improvement, progress",
        "language": "Emphasize development and potential"
    }
}
