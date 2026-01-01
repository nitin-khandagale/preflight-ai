"""Ollama/Local LLM provider implementation."""

from typing import List, Dict, Optional
import requests
from .base_provider import LLMProvider, ModelType


class OllamaProvider(LLMProvider):
    """Ollama local LLM provider."""
    
    def __init__(self, api_key: str = None, model_name: str = "llama2", base_url: str = "http://localhost:11434"):
        super().__init__(api_key=api_key, model_name=model_name)
        self.base_url = base_url.rstrip('/')
    
    def get_model_type(self) -> ModelType:
        return ModelType.OLLAMA
    
    def validate_connection(self) -> bool:
        """Validate Ollama connection."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def send_message(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Send message to Ollama model."""
        try:
            # Build prompt from messages
            prompt = ""
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role == "system":
                    prompt += f"{content}\n\n"
                elif role == "user":
                    prompt += f"User: {content}\n"
                elif role == "assistant":
                    prompt += f"Assistant: {content}\n"
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": kwargs.get('temperature', 0.7),
                },
                timeout=300
            )
            
            if response.status_code != 200:
                raise Exception(f"Ollama error: {response.text}")
            
            return self.extract_text(response.json())
        except Exception as e:
            raise Exception(f"Ollama error: {str(e)}")
    
    def extract_text(self, response_data: Dict) -> str:
        """Extract text from Ollama response."""
        if isinstance(response_data, dict) and 'response' in response_data:
            return response_data['response']
        return str(response_data)
