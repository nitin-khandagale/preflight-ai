# Multi-Model & Agents Guide

This guide covers the new multi-model support, AI agents, and chatbot features.

## 🎯 Supported Models

### Quick Reference

| Provider | Model Type | Default Model | Status |
|----------|-----------|---------------|--------|
| **Google Gemini** | `gemini` | `gemini-2.0-flash` | ✅ Ready |
| **OpenAI GPT** | `gpt` | `gpt-4-turbo-preview` | ✅ Ready |
| **Anthropic Claude** | `claude` | `claude-3-5-sonnet-20241022` | ✅ Ready |
| **Groq** | `groq` | `mixtral-8x7b-32768` | ✅ Ready |
| **Ollama (Local)** | `ollama` | `llama2` | ✅ Ready |

## 📡 API Examples

### 1. Run Preflight Tests with Any Model

#### GPT-4
```bash
curl -X POST http://localhost:8000/v1/preflight/run \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-key-123" \
  -d '{
    "model_type": "gpt",
    "model_name": "gpt-4-turbo-preview",
    "model_version": "1.0",
    "api_key": "sk-your-openai-key",
    "invariants": ["capability_claims", "instruction_authority"]
  }'
```

#### Claude
```bash
curl -X POST http://localhost:8000/v1/preflight/run \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-key-123" \
  -d '{
    "model_type": "claude",
    "model_name": "claude-3-5-sonnet-20241022",
    "model_version": "1.0",
    "api_key": "sk-ant-your-anthropic-key",
    "invariants": ["capability_claims"]
  }'
```

#### Groq
```bash
curl -X POST http://localhost:8000/v1/preflight/run \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-key-123" \
  -d '{
    "model_type": "groq",
    "model_name": "mixtral-8x7b-32768",
    "model_version": "1.0",
    "api_key": "your-groq-api-key",
    "invariants": []
  }'
```

#### Local Ollama
```bash
curl -X POST http://localhost:8000/v1/preflight/run \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-key-123" \
  -d '{
    "model_type": "ollama",
    "model_name": "llama2",
    "model_version": "1.0",
    "api_key": "not-needed"
  }'
```

---

### 2. AI Agents

Agents are autonomous AI systems that can reason, plan, and use tools to accomplish tasks.

#### Simple Agent
```bash
curl -X POST http://localhost:8000/agents/execute \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-key-123" \
  -d '{
    "agent_type": "simple",
    "model_type": "gpt",
    "model_name": "gpt-4-turbo-preview",
    "api_key": "sk-your-key",
    "task": "Search for information about AI safety and summarize the top 3 concepts",
    "system_prompt": "You are a helpful research assistant."
  }'
```

#### Reasoning Agent
```bash
curl -X POST http://localhost:8000/agents/execute \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-key-123" \
  -d '{
    "agent_type": "reasoning",
    "model_type": "claude",
    "model_name": "claude-3-5-sonnet-20241022",
    "api_key": "sk-ant-your-key",
    "task": "Analyze the security implications of prompt injection attacks",
    "context": {
      "domain": "AI Security",
      "focus_area": "Adversarial inputs"
    }
  }'
```

**Response:**
```json
{
  "agent_id": "uuid",
  "agent_type": "reasoning",
  "task": "...",
  "result": "The agent's response with reasoning steps",
  "conversation_history": [...],
  "iterations": 3
}
```

---

### 3. Chatbots

Chatbots handle multi-turn conversations with memory and context.

#### Simple Chatbot
```bash
curl -X POST http://localhost:8000/chatbot/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-key-123" \
  -d '{
    "chatbot_type": "simple",
    "model_type": "gpt",
    "model_name": "gpt-4-turbo-preview",
    "api_key": "sk-your-key",
    "user_message": "What is machine learning?",
    "system_prompt": "You are a helpful AI tutor."
  }'
```

#### Contextual Chatbot (with memory)
```bash
curl -X POST http://localhost:8000/chatbot/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-key-123" \
  -d '{
    "chatbot_type": "contextual",
    "model_type": "claude",
    "model_name": "claude-3-5-sonnet-20241022",
    "api_key": "sk-ant-your-key",
    "user_message": "Can you help me debug this?",
    "system_prompt": "You are a senior software engineer.",
    "context": {
      "language": "Python",
      "error": "NameError: name x is not defined"
    },
    "conversation_history": [
      {"role": "user", "content": "I have a Python error"},
      {"role": "assistant", "content": "I can help with that!"}
    ]
  }'
```

#### Domain-Specific Chatbot
```bash
curl -X POST http://localhost:8000/chatbot/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-key-123" \
  -d '{
    "chatbot_type": "domain",
    "model_type": "gpt",
    "model_name": "gpt-4-turbo-preview",
    "api_key": "sk-your-key",
    "user_message": "How do I create a REST API?",
    "domain": "Web Development",
    "knowledge_base": {
      "REST": "Representational State Transfer - architectural style for APIs",
      "HTTP Methods": "GET, POST, PUT, DELETE, PATCH",
      "Status Codes": "200 OK, 201 Created, 400 Bad Request, 404 Not Found, 500 Error"
    }
  }'
```

---

### 4. Get Supported Models

```bash
curl -H "X-API-Key: test-key-123" http://localhost:8000/models
```

**Response:**
```json
{
  "supported_models": ["gemini", "gpt", "claude", "groq", "ollama"],
  "default_models": {
    "gemini": "gemini-2.0-flash",
    "gpt": "gpt-4-turbo-preview",
    "claude": "claude-3-5-sonnet-20241022",
    "groq": "mixtral-8x7b-32768",
    "ollama": "llama2"
  }
}
```

---

## 🔧 Python Usage

### Using Provider Factory

```python
from preflight.models import ProviderFactory

# Create any provider
gpt_provider = ProviderFactory.create(
    model_type="gpt",
    api_key="sk-your-key",
    model_name="gpt-4-turbo-preview"
)

# Validate connection
if gpt_provider.validate_connection():
    print("Connected!")

# Send message
response = gpt_provider.send_message([
    {"role": "system", "content": "You are helpful."},
    {"role": "user", "content": "Hello!"}
])
print(response)
```

### Using Agents

```python
from preflight.models import ProviderFactory
from preflight.agents import SimpleAgent

provider = ProviderFactory.create("gpt", api_key="...", model_name="gpt-4-turbo-preview")
agent = SimpleAgent(provider)

result = agent.execute(
    task="Analyze the pros and cons of AI regulation",
    context={"domain": "AI Policy"}
)

print(result)
print(agent.get_conversation_history())
```

### Using Chatbots

```python
from preflight.models import ProviderFactory
from preflight.agents import ContextualBot

provider = ProviderFactory.create("claude", api_key="...", model_name="claude-3-5-sonnet-20241022")
chatbot = ContextualBot(provider, system_prompt="You are a helpful assistant")

# First message
response1 = chatbot.chat("What is recursion?")
print(response1)

# Second message (bot remembers context)
response2 = chatbot.chat("Can you give me an example?")
print(response2)

# Get full history
print(chatbot.get_conversation_history())
```

---

## 🚀 Provider Configuration

### Gemini
```python
from preflight.models import GeminiProvider

provider = GeminiProvider(
    api_key="your-google-api-key",
    model_name="gemini-2.0-flash"  # or gemini-1.5-pro, etc.
)
```

### OpenAI GPT
```python
from preflight.models import GPTProvider

provider = GPTProvider(
    api_key="sk-your-openai-key",
    model_name="gpt-4-turbo-preview"  # or gpt-3.5-turbo
)
```

### Claude
```python
from preflight.models import ClaudeProvider

provider = ClaudeProvider(
    api_key="sk-ant-your-anthropic-key",
    model_name="claude-3-5-sonnet-20241022"  # or claude-3-opus
)
```

### Groq
```python
from preflight.models import GroqProvider

provider = GroqProvider(
    api_key="your-groq-api-key",
    model_name="mixtral-8x7b-32768"  # or llama2-70b
)
```

### Ollama (Local)
```python
from preflight.models import OllamaProvider

provider = OllamaProvider(
    model_name="llama2",  # or mistral, neural-chat, etc.
    base_url="http://localhost:11434"  # default Ollama server
)
```

---

## 📋 Required Dependencies

Install optional model provider libraries:

```bash
# OpenAI GPT
pip install openai

# Anthropic Claude
pip install anthropic

# Groq
pip install groq

# Google Gemini (usually pre-installed with google.genai)
pip install google-genai

# Ollama (uses HTTP, no special library needed)
# But install requests if not already present
pip install requests
```

---

## ✅ Architecture

```
preflight/
├── models/
│   ├── base_provider.py          # Abstract provider interface
│   ├── provider_factory.py         # Factory for creating providers
│   ├── gemini_provider.py          # Google Gemini implementation
│   ├── gpt_provider.py             # OpenAI GPT implementation
│   ├── claude_provider.py          # Anthropic Claude implementation
│   ├── groq_provider.py            # Groq implementation
│   └── ollama_provider.py          # Ollama/local models
│
├── agents/
│   ├── simple_agent.py             # Basic agent with tools
│   ├── chatbot.py                  # Chatbot implementations
│   └── __init__.py
│
└── api/
    ├── routes.py                   # Updated with agent/chatbot endpoints
    └── models.py                   # Extended request/response schemas
```

---

## 🔐 Provider Model Names Reference

### Gemini
- `gemini-2.0-flash` (fastest)
- `gemini-1.5-pro` (most capable)
- `gemini-1.5-flash`

### OpenAI GPT
- `gpt-4-turbo-preview` (most capable)
- `gpt-4-vision-preview` (with image support)
- `gpt-3.5-turbo` (fastest)

### Anthropic Claude
- `claude-3-5-sonnet-20241022` (balanced)
- `claude-3-opus-20240229` (most capable)
- `claude-3-haiku-20240307` (fastest)

### Groq
- `mixtral-8x7b-32768` (fast)
- `llama2-70b-4096` (capable)
- `gemma-7b-it` (lightweight)

### Ollama (pull first)
- `llama2`
- `mistral`
- `neural-chat`
- `zephyr`
- `openchat`

---

## 📝 Notes

- All providers validate API credentials before use
- Conversation history is maintained in-memory (stateless API)
- For production, consider adding database persistence
- Agents support custom tool registration
- Domain bots automatically find relevant knowledge
- Chatbot context is automatically sent to model

