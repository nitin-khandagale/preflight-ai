"""Provider factory for creating LLM providers."""

from typing import Optional
from .base_provider import LLMProvider, ModelType
from .gemini_provider import GeminiProvider
from .gpt_provider import GPTProvider
from .claude_provider import ClaudeProvider
from .groq_provider import GroqProvider
from .ollama_provider import OllamaProvider


class ProviderFactory:
    """Factory for creating LLM providers."""
    
    _providers = {
        ModelType.GEMINI: GeminiProvider,
        ModelType.OPENAI_GPT: GPTProvider,
        ModelType.ANTHROPIC_CLAUDE: ClaudeProvider,
        ModelType.GROQ: GroqProvider,
        ModelType.OLLAMA: OllamaProvider,
    }
    
    @classmethod
    def create(
        cls,
        model_type: str,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        **kwargs
    ) -> LLMProvider:
        """
        Create an LLM provider instance.
        
        Args:
            model_type: Type of model (gemini, gpt, claude, groq, ollama)
            api_key: API key for the provider
            model_name: Model name/ID
            **kwargs: Additional provider-specific parameters
        
        Returns:
            LLMProvider instance
        
        Raises:
            ValueError: If model type is not supported
        """
        # Normalize model_type
        if isinstance(model_type, str):
            model_type = model_type.lower()
            # Map common aliases
            aliases = {
                'gemini': ModelType.GEMINI,
                'gpt': ModelType.OPENAI_GPT,
                'openai': ModelType.OPENAI_GPT,
                'gpt-4': ModelType.OPENAI_GPT,
                'gpt-3.5': ModelType.OPENAI_GPT,
                'claude': ModelType.ANTHROPIC_CLAUDE,
                'anthropic': ModelType.ANTHROPIC_CLAUDE,
                'groq': ModelType.GROQ,
                'ollama': ModelType.OLLAMA,
                'llama': ModelType.OLLAMA,
            }
            
            if model_type in aliases:
                model_type = aliases[model_type]
            else:
                try:
                    model_type = ModelType(model_type)
                except ValueError:
                    raise ValueError(f"Unsupported model type: {model_type}")
        
        if model_type not in cls._providers:
            raise ValueError(f"No provider found for model type: {model_type}")
        
        provider_class = cls._providers[model_type]
        return provider_class(api_key=api_key, model_name=model_name, **kwargs)
    
    @classmethod
    def register_provider(cls, model_type: ModelType, provider_class: type):
        """Register a custom provider."""
        cls._providers[model_type] = provider_class
    
    @classmethod
    def list_supported_models(cls) -> list:
        """List all supported model types."""
        return list(cls._providers.keys())
    
    @classmethod
    def get_default_model_name(cls, model_type: str) -> str:
        """Get default model name for a provider type."""
        defaults = {
            ModelType.GEMINI: "gemini-2.0-flash",
            ModelType.OPENAI_GPT: "gpt-4-turbo-preview",
            ModelType.ANTHROPIC_CLAUDE: "claude-3-5-sonnet-20241022",
            ModelType.GROQ: "mixtral-8x7b-32768",
            ModelType.OLLAMA: "llama2",
        }
        
        if isinstance(model_type, str):
            model_type = ModelType(model_type)
        
        return defaults.get(model_type, "unknown")
