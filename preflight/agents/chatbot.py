"""Chatbot implementation for multi-turn conversations."""

from typing import List, Dict, Optional
from preflight.models.base_provider import Chatbot, LLMProvider


class SimpleBot(Chatbot):
    """Simple multi-turn chatbot."""
    
    def __init__(self, provider: LLMProvider, system_prompt: str = "You are a helpful assistant."):
        super().__init__(provider, system_prompt)
    
    def chat(self, user_message: str, **kwargs) -> str:
        """Process user message and return response."""
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Build messages with system prompt
        messages = [
            {"role": "system", "content": self.system_prompt},
            *self.conversation_history
        ]
        
        # Get response
        response = self.provider.send_message(messages, **kwargs)
        
        # Add assistant response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })
        
        return response


class ContextualBot(Chatbot):
    """Chatbot with context awareness and memory management."""
    
    def __init__(
        self, 
        provider: LLMProvider, 
        system_prompt: str = "You are a helpful assistant.",
        max_history_tokens: int = 4000,
        max_messages: int = 20
    ):
        super().__init__(provider, system_prompt)
        self.max_history_tokens = max_history_tokens
        self.max_messages = max_messages
        self.context: Dict = {}
    
    def chat(self, user_message: str, context: Optional[Dict] = None, **kwargs) -> str:
        """Process user message with context awareness."""
        
        # Update context if provided
        if context:
            self.context.update(context)
        
        # Build context string
        context_str = ""
        if self.context:
            context_str = f"Context: {str(self.context)}\n\n"
        
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Manage message history (remove oldest if exceeding max)
        if len(self.conversation_history) > self.max_messages:
            self.conversation_history = self.conversation_history[-self.max_messages:]
        
        # Build messages with system prompt and context
        messages = [
            {"role": "system", "content": f"{self.system_prompt}\n\n{context_str}".strip()},
            *self.conversation_history
        ]
        
        # Get response
        response = self.provider.send_message(messages, **kwargs)
        
        # Add assistant response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })
        
        return response
    
    def set_context(self, key: str, value):
        """Set a context variable."""
        self.context[key] = value
    
    def get_context(self, key: str = None):
        """Get context variable(s)."""
        if key:
            return self.context.get(key)
        return self.context


class DomainBot(Chatbot):
    """Domain-specific chatbot with specialized knowledge."""
    
    def __init__(
        self,
        provider: LLMProvider,
        domain: str,
        knowledge_base: Dict[str, str] = None,
        system_prompt: str = None
    ):
        if system_prompt is None:
            system_prompt = f"You are a {domain} specialist. Provide accurate, helpful information."
        
        super().__init__(provider, system_prompt)
        self.domain = domain
        self.knowledge_base = knowledge_base or {}
    
    def chat(self, user_message: str, **kwargs) -> str:
        """Process query with domain knowledge."""
        
        # Check if we have relevant knowledge
        relevant_knowledge = self._find_relevant_knowledge(user_message)
        
        # Augment system prompt with relevant knowledge
        messages = [
            {"role": "system", "content": self._build_augmented_prompt(relevant_knowledge)},
            *self.conversation_history,
            {"role": "user", "content": user_message}
        ]
        
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Get response
        response = self.provider.send_message(messages, **kwargs)
        
        # Add assistant response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })
        
        return response
    
    def _find_relevant_knowledge(self, query: str) -> Dict[str, str]:
        """Find relevant knowledge for the query."""
        relevant = {}
        query_lower = query.lower()
        
        for key, value in self.knowledge_base.items():
            if key.lower() in query_lower or any(word in query_lower for word in key.lower().split()):
                relevant[key] = value
        
        return relevant
    
    def _build_augmented_prompt(self, relevant_knowledge: Dict[str, str]) -> str:
        """Build system prompt augmented with relevant knowledge."""
        prompt = self.system_prompt
        
        if relevant_knowledge:
            prompt += "\n\nRelevant knowledge:"
            for key, value in relevant_knowledge.items():
                prompt += f"\n- {key}: {value}"
        
        return prompt
    
    def add_knowledge(self, key: str, value: str):
        """Add knowledge to the knowledge base."""
        self.knowledge_base[key] = value
    
    def get_knowledge_base(self) -> Dict[str, str]:
        """Get the complete knowledge base."""
        return self.knowledge_base
