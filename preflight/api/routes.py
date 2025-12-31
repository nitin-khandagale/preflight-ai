"""API route handlers."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from .models import (
    PrefightRunRequest, RunResponse, RunDetailResponse, RunsListResponse,
    InvariantsResponse, InvariantInfo, HealthResponse, AgentRequest, AgentResponse,
    ChatbotRequest, ChatbotResponse, ModelsListResponse
)
from .auth import verify_api_key
from .db_helpers import get_all_runs, get_run_by_id
from ..workflow import PrefightOrchestrator
from ..models.provider_factory import ProviderFactory
from ..agents import SimpleAgent, ReasoningAgent, SimpleBot, ContextualBot, DomainBot
from ..attacks.instruction_authority import instruction_authority
from ..attacks.capability_claims import capability_claims
from typing import List
import uuid

router = APIRouter()

# Get invariants list (hardcoded, but can be made dynamic)
AVAILABLE_INVARIANTS = [
    instruction_authority,
    capability_claims,
] 

INVARIANT_DESCRIPTIONS = {
    "instruction_authority": "Tests if model respects and follows explicit instructions",
    "capability_claims": "Tests if model makes false capability or knowledge claims",
}


@router.post("/preflight/run", response_model=RunResponse, status_code=status.HTTP_201_CREATED)
def run_preflight(
    request: PrefightRunRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Execute a new preflight run on any supported model.
    
    Supported model types:
    - **gemini**: Google Gemini (gemini-2.0-flash, gemini-1.5-pro, etc.)
    - **gpt**: OpenAI GPT (gpt-4-turbo-preview, gpt-3.5-turbo, etc.)
    - **claude**: Anthropic Claude (claude-3-5-sonnet-20241022, claude-3-opus, etc.)
    - **groq**: Groq (mixtral-8x7b-32768, llama2-70b, etc.)
    - **ollama**: Local Ollama models (llama2, mistral, neural-chat, etc.)
    
    - **invariants**: Optional list of invariant names to test. If not provided, all invariants run.
    """
    try:
        # Determine which invariants to run
        if request.invariants and request.invariants != ["all"]:
            selected_invariants = request.invariants
        else:
            selected_invariants = [inv.name if hasattr(inv, 'name') else str(inv) for inv in AVAILABLE_INVARIANTS]
        
        # Create provider for the specified model type
        try:
            model = ProviderFactory.create(
                model_type=request.model_type,
                api_key=request.api_key,
                model_name=request.model_name
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        
        # Validate provider connection
        if not model.validate_connection():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to connect to {request.model_type} API. Check your credentials."
            )
        
        # Create orchestrator with selected invariants
        orchestrator = PrefightOrchestrator(
            model=model,
            invariants=AVAILABLE_INVARIANTS,
            model_name=request.model_name,
            model_version=request.model_version,
            model_url=request.model_url or "N/A",
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
    
    except HTTPException:
        raise
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


@router.get("/models", response_model=ModelsListResponse)
async def list_supported_models(api_key: str = Depends(verify_api_key)):
    """
    Get list of all supported model types and their default models.
    """
    from ..models.provider_factory import ProviderFactory
    
    supported = []
    defaults = {}
    
    for model_type in ProviderFactory.list_supported_models():
        type_name = model_type.value
        supported.append(type_name)
        try:
            defaults[type_name] = ProviderFactory.get_default_model_name(type_name)
        except:
            defaults[type_name] = "unknown"
    
    return ModelsListResponse(
        supported_models=supported,
        default_models=defaults
    )


# ============= AGENT ENDPOINTS =============

@router.post("/agents/execute", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def execute_agent(
    request: AgentRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Execute an AI agent to perform a task.
    
    Agent types:
    - **simple**: Basic agent with tool use
    - **reasoning**: Advanced agent with explicit reasoning
    
    Model types: gemini, gpt, claude, groq, ollama
    """
    try:
        # Create provider
        provider = ProviderFactory.create(
            model_type=request.model_type,
            api_key=request.api_key,
            model_name=request.model_name
        )
        
        # Validate connection
        if not provider.validate_connection():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to connect to {request.model_type} API"
            )
        
        # Create appropriate agent
        if request.agent_type.lower() == "reasoning":
            agent = ReasoningAgent(provider, name="ReasoningAgent")
        else:
            agent = SimpleAgent(provider, name="Agent", system_prompt=request.system_prompt)
        
        # Execute task
        result = agent.execute(request.task, context=request.context)
        
        return AgentResponse(
            agent_id=str(uuid.uuid4()),
            agent_type=request.agent_type,
            task=request.task,
            result=result,
            conversation_history=agent.get_conversation_history(),
            iterations=len(agent.conversation_history)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent execution error: {str(e)}"
        )


# ============= CHATBOT ENDPOINTS =============

@router.post("/chatbot/chat", response_model=ChatbotResponse, status_code=status.HTTP_201_CREATED)
async def chat_with_bot(
    request: ChatbotRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Interact with an AI chatbot.
    
    Chatbot types:
    - **simple**: Basic multi-turn chatbot
    - **contextual**: Chatbot with context awareness
    - **domain**: Domain-specific chatbot with knowledge base
    
    Model types: gemini, gpt, claude, groq, ollama
    """
    try:
        # Create provider
        provider = ProviderFactory.create(
            model_type=request.model_type,
            api_key=request.api_key,
            model_name=request.model_name
        )
        
        # Validate connection
        if not provider.validate_connection():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to connect to {request.model_type} API"
            )
        
        # Create appropriate chatbot
        system_prompt = request.system_prompt or "You are a helpful assistant."
        
        if request.chatbot_type.lower() == "contextual":
            chatbot = ContextualBot(provider, system_prompt=system_prompt)
            if request.context:
                for key, value in request.context.items():
                    chatbot.set_context(key, value)
        elif request.chatbot_type.lower() == "domain":
            chatbot = DomainBot(
                provider,
                domain=request.domain or "General",
                knowledge_base=request.knowledge_base or {},
                system_prompt=system_prompt
            )
        else:
            chatbot = SimpleBot(provider, system_prompt=system_prompt)
        
        # Restore conversation history if provided
        if request.conversation_history:
            for msg in request.conversation_history:
                chatbot.conversation_history.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        # Get response
        response = chatbot.chat(request.user_message)
        
        # Convert history to ChatbotMessage format
        history = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in chatbot.get_conversation_history()
        ]
        
        return ChatbotResponse(
            chatbot_id=str(uuid.uuid4()),
            chatbot_type=request.chatbot_type,
            user_message=request.user_message,
            assistant_response=response,
            conversation_history=history
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chatbot error: {str(e)}"
        )
