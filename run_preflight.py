import os
from dotenv import load_dotenv
from preflight.models.openai_model import OpenAIModel
from preflight.attacks.scenarios import instruction_authority_scenarios
from preflight.engine.runner import run_scenarios
from preflight.core.gate import gate_decision

# Load environment variables from .env file
load_dotenv()

model = OpenAIModel(model="gemini-2.0-flash-exp")

results = run_scenarios(model, instruction_authority_scenarios())
decision = gate_decision(results)

print("\n=== PREFLIGHT RESULT ===")
print("Invariant results:", results)
print("Gate decision:", decision)