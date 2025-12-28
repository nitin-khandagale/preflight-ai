"""Pydantic models for API requests and responses."""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime


# ============= Request Models =============

class PrefightRunRequest(BaseModel):
    """Request model for POST /v1/preflight/run"""
    model_name: str = Field(..., example="gemini-2.0-flash")
    model_version: str = Field(..., example="2.0")
    model_url: str = Field(..., example="https://api.google.com/v1")
    api_key: str = Field(..., example="sk-xxxxx")
    invariants: Optional[List[str]] = Field(
        None, 
        example=["capability_claims", "instruction_authority"],
        description="List of invariant names to test. If not provided or empty, all invariants will run. Use 'all' to explicitly run all."
    )

    class Config:
        json_schema_extra = {
            "example": {
                "model_name": "gemini-2.0-flash",
                "model_version": "2.0",
                "model_url": "https://api.google.com/v1",
                "api_key": "your-api-key",
                "invariants": ["capability_claims", "instruction_authority"]
            }
        }


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
