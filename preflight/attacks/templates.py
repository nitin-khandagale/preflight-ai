class Attack:
    def __init__(self, id, messages):
        self.id = id
        self.messages = messages


class MultiTurnSequence:
    """
    Represents a multi-turn attack sequence.
    
    Each sequence consists of alternating user and assistant messages
    that build toward testing a specific vulnerability.
    """
    def __init__(self, id, description, turns):
        """
        Args:
            id: Unique identifier for the sequence
            description: What this sequence tests
            turns: List of dicts with 'user' and optional 'expected_assistant' keys.
                   Structure: [{"user": "...", "expected_assistant": "..."}, {"user": "..."}]
        """
        self.id = id
        self.description = description
        self.turns = turns
    
    def to_messages(self):
        """Convert sequence to message format for model.send()
        
        Returns:
            List of message dicts with role and content keys
        """
        messages = []
        for turn in self.turns:
            # Add user message
            if "user" in turn:
                messages.append({"role": "user", "content": turn["user"]})
            
            # Add assistant response if provided
            if "expected_assistant" in turn:
                messages.append({"role": "assistant", "content": turn["expected_assistant"]})
        
        return messages