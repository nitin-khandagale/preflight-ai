from preflight.engine.classifier import classify


def run_scenarios(model, invariants):
    """
    Runs all invariants against the model.

    Args:
        model: your model wrapper (expects send(messages: list[dict]))
        invariants: List[Invariant] objects

    Returns:
        Dict[str, str]: { invariant_name: "VIOLATED" | "HELD" }
    """

    results = {}

    for invariant in invariants:
        print(f"\n▶ Running invariant: {invariant.name}")
        violated = False

        for idx, prompt in enumerate(invariant.prompts, start=1):
            print(f"   [{idx:02}] Prompt: {prompt[:80]}...")

            # Wrap string prompt into chat message format expected by OpenAIModel
            messages = [
                {"role": "user", "content": prompt}
            ]

            response = model.send(messages)

            behavior = classify(response)
            print(f"        → Behavior: {behavior.name}")

            if behavior in invariant.violation_behaviors:
                violated = True

        results[invariant.name] = "VIOLATED" if violated else "HELD"

    return results
