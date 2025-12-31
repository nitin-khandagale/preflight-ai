"""AI Agent implementation with tool use and multi-step reasoning."""

from typing import List, Dict, Any, Optional, Callable
from .base_provider import Agent, LLMProvider
import json


class SimpleAgent(Agent):
    """Basic AI agent with tool use capabilities."""
    
    def __init__(self, provider: LLMProvider, name: str = "Agent", system_prompt: str = None):
        super().__init__(provider, name)
        self.system_prompt = system_prompt or self._get_default_system_prompt()
        self.max_iterations = 10
        self.current_iteration = 0
    
    def _get_default_system_prompt(self) -> str:
        return f"""You are {self.name}, a helpful AI agent.
You can use tools to accomplish tasks. When you need to use a tool, respond with:
<tool name="tool_name">{"parameter": "value"}</tool>

Think step by step and use tools when necessary."""
    
    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Execute a task using agent reasoning."""
        self.conversation_history = []
        self.current_iteration = 0
        
        # Add system prompt
        if self.system_prompt:
            self.conversation_history.append({
                "role": "system",
                "content": self.system_prompt
            })
        
        # Add context if provided
        if context:
            context_str = f"Context: {json.dumps(context, indent=2)}"
            self.conversation_history.append({
                "role": "system",
                "content": context_str
            })
        
        # Add initial task
        self.conversation_history.append({
            "role": "user",
            "content": task
        })
        
        # Agentic loop
        while self.current_iteration < self.max_iterations:
            self.current_iteration += 1
            
            # Get response from model
            response = self.provider.send_message(self.conversation_history)
            
            # Check if response contains tool calls
            if "<tool" in response:
                # Extract and execute tool calls
                tool_results = self._process_tool_calls(response)
                
                # Add assistant response to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response
                })
                
                # Add tool results to history
                self.conversation_history.append({
                    "role": "tool",
                    "content": json.dumps(tool_results)
                })
            else:
                # Final answer reached
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response
                })
                return response
        
        return f"Agent reached maximum iterations ({self.max_iterations})"
    
    def _process_tool_calls(self, response: str) -> Dict[str, Any]:
        """Extract and execute tool calls from response."""
        results = {}
        
        # Simple parsing for <tool name="...">{"key": "value"}</tool>
        import re
        pattern = r'<tool name="([^"]+)">({.*?})</tool>'
        matches = re.findall(pattern, response, re.DOTALL)
        
        for tool_name, params_str in matches:
            if tool_name in self.tools:
                try:
                    params = json.loads(params_str)
                    result = self.tools[tool_name](**params)
                    results[tool_name] = result
                except Exception as e:
                    results[tool_name] = f"Error: {str(e)}"
            else:
                results[tool_name] = f"Tool '{tool_name}' not found"
        
        return results


class ReasoningAgent(Agent):
    """Advanced agent with explicit reasoning and reflection."""
    
    def __init__(self, provider: LLMProvider, name: str = "ReasoningAgent"):
        super().__init__(provider, name)
        self.reasoning_trace: List[str] = []
    
    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Execute task with explicit reasoning steps."""
        self.conversation_history = []
        self.reasoning_trace = []
        
        # Prompt the agent to think through the problem
        thinking_prompt = f"""Approach this task step by step:
1. Break down the problem
2. Identify required tools or information
3. Execute a solution plan
4. Verify the result

Task: {task}"""
        
        if context:
            thinking_prompt += f"\n\nContext: {json.dumps(context, indent=2)}"
        
        self.conversation_history.append({
            "role": "user",
            "content": thinking_prompt
        })
        
        # Get response
        response = self.provider.send_message(self.conversation_history)
        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })
        
        self.reasoning_trace.append(response)
        return response
    
    def get_reasoning_trace(self) -> List[str]:
        """Get the agent's reasoning trace."""
        return self.reasoning_trace
