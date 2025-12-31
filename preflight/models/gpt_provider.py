"""OpenAI GPT LLM provider implementation."""

from typing import List, Dict, Optional
from .base_provider import LLMProvider, ModelType

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


class GPTProvider(LLMProvider):
    """OpenAI GPT (ChatGPT, GPT-4) provider."""
    
    def __init__(self, api_key: str, model_name: str = "gpt-4-turbo-preview"):
        if OpenAI is None:
            raise ImportError("openai package required. Install with: pip install openai")
        
        super().__init__(api_key=api_key, model_name=model_name)
        self.client = OpenAI(api_key=self.api_key)
    
    def get_model_type(self) -> ModelType:
        return ModelType.OPENAI_GPT
    
    def validate_connection(self) -> bool:
        """Validate OpenAI API connection."""
        try:
            self.client.models.retrieve(self.model_name)
            return True
        except Exception:
            return False
    
    def send_message(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Send message to GPT model."""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=kwargs.get('temperature', 0.7),
                max_tokens=kwargs.get('max_tokens', 2048),
                top_p=kwargs.get('top_p', 1.0),
            )
            
            return self.extract_text(response)
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    def extract_text(self, response) -> str:
        """Extract text from GPT response."""
        if hasattr(response, 'choices') and len(response.choices) > 0:
            if hasattr(response.choices[0], 'message'):
                return response.choices[0].message.content
        return str(response)
