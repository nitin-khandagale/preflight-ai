"""Google Gemini LLM provider implementation."""

import google.genai as genai
from typing import List, Dict, Optional
from .base_provider import LLMProvider, ModelType


class GeminiProvider(LLMProvider):
    """Google Gemini API provider."""
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash"):
        super().__init__(api_key=api_key, model_name=model_name)
        self.client = genai.Client(api_key=self.api_key)
    
    def get_model_type(self) -> ModelType:
        return ModelType.GEMINI
    
    def validate_connection(self) -> bool:
        """Validate Gemini API connection."""
        try:
            # Try a simple request to validate connection
            self.client.models.list()
            return True
        except Exception:
            return False
    
    def send_message(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Send message to Gemini model."""
        try:
            # Format messages for Gemini
            formatted_messages = self.format_messages(messages)
            
            response = self.client.models.generate_content(
                model=f"models/{self.model_name}",
                contents=formatted_messages,
                generation_config=genai.types.GenerationConfig(
                    temperature=kwargs.get('temperature', 0.7),
                    max_output_tokens=kwargs.get('max_tokens', 2048),
                    top_p=kwargs.get('top_p', 1.0),
                )
            )
            
            return self.extract_text(response)
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    def extract_text(self, response) -> str:
        """Extract text from Gemini response."""
        if hasattr(response, 'text'):
            return response.text
        return str(response)
    
    def format_messages(self, messages: List[Dict[str, str]]) -> str:
        """Convert message list to Gemini prompt format."""
        prompt = ""
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            if role == "system":
                prompt += f"System: {content}\n\n"
            elif role == "user":
                prompt += f"User: {content}\n\n"
            elif role == "assistant":
                prompt += f"Assistant: {content}\n\n"
        
        return prompt
