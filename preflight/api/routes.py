"""API route handlers."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from .models import (
    PrefightRunRequest, RunResponse, RunDetailResponse, RunsListResponse,
    InvariantsResponse, InvariantInfo, HealthResponse
)
from .auth import verify_api_key
from .db_helpers import get_all_runs, get_run_by_id
from ..workflow import PrefightOrchestrator
from ..models.openai_model import OpenAIModel
from ..attacks.all_invariants import ALL_INVARIANTS
from typing import List

router = APIRouter()

# Get all available invariants
AVAILABLE_INVARIANTS = ALL_INVARIANTS

INVARIANT_DESCRIPTIONS = {
    "instruction_authority": "Tests if model respects and follows explicit instructions",
    "capability_claims": "Tests if model makes false capability or knowledge claims",
    "instruction_hierarchy": "Tests if model follows user instructions that override system rules",
    "role_integrity": "Tests if model maintains its assigned role/persona",
    "information_boundary": "Tests if model respects information boundaries and access controls",
    "harmful_action_refusal": "Tests if model refuses to participate in harmful actions",
}


@router.post("/preflight/run", response_model=RunResponse, status_code=status.HTTP_201_CREATED)
def run_preflight(
    request: PrefightRunRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Execute a new preflight run.
    
    - **model_name**: Name of the model to test
    - **model_version**: Version of the model
    - **model_url**: API URL of the model
    - **api_key**: API key for the model
    - **invariants**: Optional list of invariant names to test. If not provided or empty, all invariants run. Use "all" to explicitly run all.
    """
    try:
        # Determine which invariants to run
        if request.invariants and request.invariants != ["all"] and len(request.invariants) > 0:
            # Filter to only requested invariants
            invariant_names = set(request.invariants)
            selected_invariants = [
                inv for inv in AVAILABLE_INVARIANTS 
                if inv.name in invariant_names
            ]
        else:
            # Use all invariants by default
            selected_invariants = AVAILABLE_INVARIANTS
        
        # Initialize model with API key
        model = OpenAIModel(model=request.model_name, api_key=request.api_key)
        
        # Create orchestrator with selected invariants
        orchestrator = PrefightOrchestrator(
            model=model,
            invariants=selected_invariants,
            model_name=request.model_name,
            model_version=request.model_version,
            model_url=request.model_url,
            api_key=request.api_key
        )
        
        # Execute workflow
        result = orchestrator.run()
        
        # Return response
        return RunResponse(
            run_id=result['run_id'],
            results=result['results'],
            decision=result['decision'],
            num_violations=result['num_violations']
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error running preflight: {str(e)}"
        )


@router.get("/preflight/runs/{run_id}", response_model=RunDetailResponse)
async def get_run_detail(
    run_id: str,
    api_key: str = Depends(verify_api_key)
):
    """
    Get detailed information about a specific run.
    
    - **run_id**: The ID of the run to retrieve
    """
    run_data = get_run_by_id(run_id)
    
    if not run_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Run with ID {run_id} not found"
        )
    
    # Format invariants
    invariants = [
        {
            "invariant_name": inv["invariant_name"],
            "result": inv["invariant_result"],
            "num_prompts_tested": inv["num_prompts_tested"]
        }
        for inv in run_data.get('invariants', [])
    ]
    
    # Format failures
    failures = [
        {
            "invariant_name": failure["invariant_name"],
            "prompt_text": failure["prompt_text"],
            "model_response": failure["model_response"],
            "behavior_detected": failure["behavior_detected"]
        }
        for failure in run_data.get('failures', [])
    ]
    
    return RunDetailResponse(
        run_id=run_data['run_id'],
        model_name=run_data['model_name'],
        datetime=run_data['datetime'],
        invariants=invariants,
        failures=failures,
        gate_decision=run_data['gate_decision']
    )


@router.get("/preflight/runs", response_model=RunsListResponse)
async def list_runs(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    api_key: str = Depends(verify_api_key)
):
    """
    Get a list of all runs with pagination.
    
    - **limit**: Number of runs to return (1-100, default 10)
    - **offset**: Number of runs to skip (default 0)
    """
    runs, total = get_all_runs(limit=limit, offset=offset)
    
    return RunsListResponse(
        runs=runs,
        total=total,
        limit=limit,
        offset=offset
    )


@router.get("/preflight/invariants", response_model=InvariantsResponse)
async def get_invariants(api_key: str = Depends(verify_api_key)):
    """
    Get list of available invariants that can be tested.
    
    Returns names and descriptions of all available invariants.
    """
    invariants = [
        InvariantInfo(
            name=inv.name,
            description=INVARIANT_DESCRIPTIONS.get(inv.name, "No description available")
        )
        for inv in AVAILABLE_INVARIANTS
    ]
    
    return InvariantsResponse(
        invariants=invariants,
        total=len(invariants)
    )


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint (no authentication required).
    
    Returns the API status.
    """
    return HealthResponse(status="ok", version="1.0.0")
