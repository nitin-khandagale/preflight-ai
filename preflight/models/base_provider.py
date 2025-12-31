"""Base LLM provider interface for multi-model support."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from enum import Enum


class ModelType(str, Enum):
    """Supported model types."""
    GEMINI = "gemini"
    OPENAI_GPT = "gpt"
    ANTHROPIC_CLAUDE = "claude"
    GROQ = "groq"
    OLLAMA = "ollama"
    HUGGINGFACE = "huggingface"
    COHERE = "cohere"
    CUSTOM = "custom"


class Message:
    """Standardized message format across all providers."""
    
    def __init__(self, role: str, content: str):
        self.role = role  # "system", "user", "assistant", "tool"
        self.content = content


class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.
    
    All model providers must implement this interface to work with Preflight.
    """
    
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        """
        Initialize provider.
        
        Args:
            api_key: API key for the provider
            model_name: Model name/ID to use
        """
        self.api_key = api_key
        self.model_name = model_name
        self.model_type = self.get_model_type()
    
    @abstractmethod
    def get_model_type(self) -> ModelType:
        """Return the model type."""
        pass
    
    @abstractmethod
    def send_message(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Send messages to the model and get response.
        
        Args:
            messages: List of messages in format [{"role": "user"/"assistant"/"system", "content": "..."}, ...]
            **kwargs: Additional model-specific parameters (temperature, max_tokens, etc.)
        
        Returns:
            Model response text
        """
        pass
    
    @abstractmethod
    def validate_connection(self) -> bool:
        """Validate that the provider is properly configured and accessible."""
        pass
    
    def format_messages(self, messages: List[Dict[str, str]]) -> Any:
        """
        Format messages for the specific provider.
        
        Override in subclass if needed.
        Default implementation returns messages as-is.
        """
        return messages
    
    def extract_text(self, response: Any) -> str:
        """
        Extract text from provider-specific response format.
        
        Override in subclass if needed.
        """
        if isinstance(response, str):
            return response
        return str(response)


class Agent(ABC):
    """Base class for AI agents with tool use and state management."""
    
    def __init__(self, provider: LLMProvider, name: str = "Agent"):
        self.provider = provider
        self.name = name
        self.conversation_history: List[Dict[str, str]] = []
        self.tools: Dict[str, callable] = {}
    
    @abstractmethod
    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Execute a task using the agent."""
        pass
    
    def register_tool(self, tool_name: str, tool_func: callable):
        """Register a tool the agent can use."""
        self.tools[tool_name] = tool_func
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get the full conversation history."""
        return self.conversation_history
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []


class Chatbot(ABC):
    """Base class for multi-turn chatbots."""
    
    def __init__(self, provider: LLMProvider, system_prompt: str = "You are a helpful assistant."):
        self.provider = provider
        self.system_prompt = system_prompt
        self.conversation_history: List[Dict[str, str]] = []
    
    @abstractmethod
    def chat(self, user_message: str, **kwargs) -> str:
        """Process user message and return response."""
        pass
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get the full conversation history."""
        return self.conversation_history
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
    
    def set_system_prompt(self, prompt: str):
        """Update the system prompt."""
        self.system_prompt = prompt
        self.clear_history()
