"""Groq LLM provider implementation."""

from typing import List, Dict, Optional
from .base_provider import LLMProvider, ModelType

try:
    from groq import Groq
except ImportError:
    Groq = None


class GroqProvider(LLMProvider):
    """Groq (fast inference) provider."""
    
    def __init__(self, api_key: str, model_name: str = "mixtral-8x7b-32768"):
        if Groq is None:
            raise ImportError("groq package required. Install with: pip install groq")
        
        super().__init__(api_key=api_key, model_name=model_name)
        self.client = Groq(api_key=self.api_key)
    
    def get_model_type(self) -> ModelType:
        return ModelType.GROQ
    
    def validate_connection(self) -> bool:
        """Validate Groq API connection."""
        try:
            self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=10
            )
            return True
        except Exception:
            return False
    
    def send_message(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Send message to Groq model."""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=kwargs.get('temperature', 0.7),
                max_tokens=kwargs.get('max_tokens', 2048),
            )
            
            return self.extract_text(response)
        except Exception as e:
            raise Exception(f"Groq API error: {str(e)}")
    
    def extract_text(self, response) -> str:
        """Extract text from Groq response."""
        if hasattr(response, 'choices') and len(response.choices) > 0:
            if hasattr(response.choices[0], 'message'):
                return response.choices[0].message.content
        return str(response)
