import google.genai as genai

class OpenAIModel:
    def __init__(self, model="gemini-1.5-flash", api_key=None):
        self.model = model
        self.client = genai.Client(api_key=api_key)  # Use provided api_key or environment variable

    def send(self, messages):
        # Convert messages format to Gemini format
        # For simplicity, concatenate all messages into a single prompt
        prompt = ""
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                prompt += f"System: {content}\n\n"
            elif role == "user":
                prompt += f"User: {content}\n\n"
            elif role == "assistant":
                prompt += f"Assistant: {content}\n\n"
        
        response = self.client.models.generate_content(
            model=f"models/{self.model}",
            contents=prompt
        )
        return response.text