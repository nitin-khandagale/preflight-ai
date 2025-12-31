"""Pydantic models for API requests and responses."""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime


# ============= Request Models =============

class PrefightRunRequest(BaseModel):
    """Request model for POST /v1/preflight/run"""
    model_type: str = Field(..., example="gemini", description="Model type: gemini, gpt, claude, groq, ollama, etc.")
    model_name: str = Field(..., example="gemini-2.0-flash")
    model_version: str = Field(..., example="2.0")
    model_url: Optional[str] = Field(None, example="https://api.google.com/v1", description="API URL (optional for some providers)")
    api_key: str = Field(..., example="sk-xxxxx")
    invariants: Optional[List[str]] = Field(
        None, 
        example=["capability_claims", "instruction_authority"],
        description="List of invariant names to test. If not provided or empty, all invariants will run."
    )

    class Config:
        json_schema_extra = {
            "example": {
                "model_type": "gpt",
                "model_name": "gpt-4-turbo-preview",
                "model_version": "1.0",
                "model_url": "https://api.openai.com/v1",
                "api_key": "sk-xxxxx",
                "invariants": ["capability_claims", "instruction_authority"]
            }
        }


class AgentRequest(BaseModel):
    """Request model for agent execution."""
    agent_type: str = Field(..., example="simple", description="Agent type: simple, reasoning")
    model_type: str = Field(..., example="gpt", description="Model type: gemini, gpt, claude, groq, ollama")
    model_name: str = Field(..., example="gpt-4-turbo-preview")
    api_key: str = Field(...)
    task: str = Field(..., description="Task for the agent to execute")
    system_prompt: Optional[str] = Field(None, description="Custom system prompt for the agent")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context for the task")


class ChatbotMessage(BaseModel):
    """Message in chatbot conversation."""
    role: str  # "user" or "assistant"
    content: str


class ChatbotRequest(BaseModel):
    """Request model for chatbot interaction."""
    chatbot_type: str = Field(..., example="simple", description="Chatbot type: simple, contextual, domain")
    model_type: str = Field(..., example="gpt", description="Model type")
    model_name: str = Field(..., example="gpt-4-turbo-preview")
    api_key: str = Field(...)
    user_message: str = Field(...)
    system_prompt: Optional[str] = Field(None)
    conversation_history: Optional[List[ChatbotMessage]] = Field(None)
    context: Optional[Dict[str, Any]] = Field(None, description="Context for contextual bots")
    domain: Optional[str] = Field(None, description="Domain for domain bots")
    knowledge_base: Optional[Dict[str, str]] = Field(None, description="Knowledge base for domain bots")


# ============= Response Models =============

class FailureDetail(BaseModel):
    """Failure details for a single prompt"""
    invariant_name: str
    prompt_text: str
    model_response: str
    behavior_detected: str


class InvariantResult(BaseModel):
    """Result for a single invariant"""
    invariant_name: str
    result: str  # HELD or VIOLATED
    num_prompts_tested: int


class RunResponse(BaseModel):
    """Response for POST /v1/preflight/run"""
    run_id: str
    results: Dict[str, str]  # {invariant_name: HELD/VIOLATED}
    decision: str  # PASS or FAIL
    num_violations: int


class RunDetailResponse(BaseModel):
    """Response for GET /v1/preflight/runs/{run_id}"""
    run_id: str
    model_name: str
    datetime: str
    invariants: List[InvariantResult]
    failures: List[FailureDetail]
    gate_decision: str


class RunSummary(BaseModel):
    """Summary of a run for list endpoint"""
    run_id: str
    model_name: str
    datetime: str
    gate_decision: str


class RunsListResponse(BaseModel):
    """Response for GET /v1/preflight/runs"""
    runs: List[RunSummary]
    total: int
    limit: int
    offset: int


class InvariantInfo(BaseModel):
    """Information about an invariant"""
    name: str
    description: str


class InvariantsResponse(BaseModel):
    """Response for GET /v1/preflight/invariants"""
    invariants: List[InvariantInfo]
    total: int


class HealthResponse(BaseModel):
    """Response for GET /health"""
    status: str
    version: str = "1.0.0"


class ErrorResponse(BaseModel):
    """Error response"""
    detail: str
    status_code: int


# ============= Agent Response Models =============

class AgentResponse(BaseModel):
    """Response for agent execution."""
    agent_id: str
    agent_type: str
    task: str
    result: str
    conversation_history: List[Dict[str, str]]
    iterations: int


# ============= Chatbot Response Models =============

class ChatbotResponse(BaseModel):
    """Response for chatbot interaction."""
    chatbot_id: str
    chatbot_type: str
    user_message: str
    assistant_response: str
    conversation_history: List[ChatbotMessage]


class ModelsListResponse(BaseModel):
    """Response listing supported models."""
    supported_models: List[str]
    default_models: Dict[str, str]