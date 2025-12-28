"""
Preflight execution script.

This script runs the preflight testing workflow.
Model details and configuration are read from environment variables.
"""

from preflight.config import Config
from preflight.models.openai_model import OpenAIModel
from preflight.workflow import PrefightOrchestrator
from preflight.attacks.instruction_authority import instruction_authority
from preflight.attacks.capability_claims import capability_claims


def main():
    """Main entry point for preflight execution."""
    
    # Load configuration
    config = Config()
    model_name = config.get_model_name()
    model_version = config.get_model_version()
    model_url = config.get_model_url()
    api_key = config.get_api_key()
    
    # Initialize model
    model = OpenAIModel(model=model_name)
    
    # Define invariants
    invariants = [
        instruction_authority,
        capability_claims,
        # add more here
    ]
    
    # Create orchestrator and run
    orchestrator = PrefightOrchestrator(
        model=model,
        invariants=invariants,
        model_name=model_name,
        model_version=model_version,
        model_url=model_url,
        api_key=api_key
    )
    
    # Execute workflow
    result = orchestrator.run()
    
    # Display results
    print("\n" + "="*50)
    print("PREFLIGHT EXECUTION COMPLETE")
    print("="*50)
    print(f"Run ID: {result['run_id']}")
    print(f"Invariants Tested: {len(result['results'])}")
    print(f"Violations Found: {result['num_violations']}")
    print(f"Gate Decision: {result['decision']}")
    print("="*50)
    print("\nDetailed Results:")
    for invariant_name, result_status in result['results'].items():
        print(f"  • {invariant_name}: {result_status}")
    
    print(orchestrator.get_summary())


if __name__ == "__main__":
    main()
