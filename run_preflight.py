from dotenv import load_dotenv
from preflight.models.openai_model import OpenAIModel
from preflight.engine.runner import run_scenarios
from preflight.core.gate import gate_decision
from preflight.attacks.instruction_authority import instruction_authority
from preflight.attacks.capability_claims import capability_claims

# Load environment variables from .env file
load_dotenv()

model = OpenAIModel(model="gemini-2.0-flash-exp")

invariants = [
    instruction_authority,
    capability_claims,
    # add more here
]

results = run_scenarios(model, invariants)
decision = gate_decision(results)


print("\n=== PREFLIGHT RESULT ===")
print("Invariant results:", results)
print("Gate decision:", decision)