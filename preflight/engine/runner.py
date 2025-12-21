from preflight.engine.classifier import classify
from preflight.core.invariants import evaluate_invariants


def run_scenarios(model, scenario_map: dict):
    """
    scenario_map = {
        invariant_name: [Attack, Attack, ...]
    }
    """
    behavior_map = {k: [] for k in scenario_map}

    for invariant, attacks in scenario_map.items():
        for attack in attacks:
            response = model.send(attack.messages)
            behavior = classify(response)

            print(f"\nInvariant: {invariant}")
            print(f"Attack: {attack.id}")
            print("Response:", response)
            print("Behavior:", behavior.value)

            behavior_map[invariant].append(behavior)

    return evaluate_invariants(behavior_map)
