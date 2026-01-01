"""Anthropic Claude LLM provider implementation."""

from typing import List, Dict, Optional
from .base_provider import LLMProvider, ModelType

try:
    import anthropic
except ImportError:
    anthropic = None


class ClaudeProvider(LLMProvider):
    """Anthropic Claude provider."""
    
    def __init__(self, api_key: str, model_name: str = "claude-3-5-sonnet-20241022"):
        if anthropic is None:
            raise ImportError("anthropic package required. Install with: pip install anthropic")
        
        super().__init__(api_key=api_key, model_name=model_name)
        self.client = anthropic.Anthropic(api_key=self.api_key)
    
    def get_model_type(self) -> ModelType:
        return ModelType.ANTHROPIC_CLAUDE
    
    def validate_connection(self) -> bool:
        """Validate Anthropic API connection."""
        try:
            # Try listing models to validate connection
            self.client.messages.create(
                model=self.model_name,
                max_tokens=10,
                messages=[{"role": "user", "content": "test"}]
            )
            return True
        except Exception:
            return False
    
    def send_message(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Send message to Claude model."""
        try:
            # Separate system prompt from messages
            system_prompt = ""
            claude_messages = []
            
            for msg in messages:
                if msg.get("role") == "system":
                    system_prompt = msg.get("content", "")
                else:
                    claude_messages.append({
                        "role": msg.get("role", "user"),
                        "content": msg.get("content", "")
                    })
            
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=kwargs.get('max_tokens', 2048),
                system=system_prompt,
                messages=claude_messages,
                temperature=kwargs.get('temperature', 0.7),
            )
            
            return self.extract_text(response)
        except Exception as e:
            raise Exception(f"Anthropic API error: {str(e)}")
    
    def extract_text(self, response) -> str:
        """Extract text from Claude response."""
        if hasattr(response, 'content') and len(response.content) > 0:
            if hasattr(response.content[0], 'text'):
                return response.content[0].text
        return str(response)
