from preflight.engine.classifier import classify


def run_scenarios(model, invariants):
    """
    Runs all invariants against the model.

    Args:
        model: your model wrapper (expects send(messages: list[dict]))
        invariants: List[Invariant] objects

    Returns:
        Tuple containing:
        - Dict[str, str]: { invariant_name: "VIOLATED" | "HELD" }
        - Dict: failure details { invariant_name: [list of failures] }
    """

    results = {}
    failures = {}

    for invariant in invariants:
        print(f"\n▶ Running invariant: {invariant.name}")
        violated = False
        invariant_failures = []

        # Test single-turn prompts
        for idx, prompt in enumerate(invariant.prompts, start=1):
            print(f"   [SINGLE {idx:02}] Prompt: {prompt[:80]}...")

            # Wrap string prompt into chat message format expected by OpenAIModel
            messages = [
                {"role": "user", "content": prompt}
            ]

            response = model.send(messages)

            behavior = classify(response)
            print(f"            → Behavior: {behavior.name}")

            if behavior in invariant.violation_behaviors:
                violated = True
                # Store failure details
                invariant_failures.append({
                    'type': 'single_turn',
                    'prompt': prompt,
                    'response': response,
                    'behavior': behavior.name
                })

        # Test multi-turn sequences
        if hasattr(invariant, 'multi_turn_sequences') and invariant.multi_turn_sequences:
            for seq in invariant.multi_turn_sequences:
                try:
                    print(f"   [MULTI {seq.id}] {seq.description}")
                    
                    # Build message history
                    messages = seq.to_messages()
                    
                    # Send the complete conversation (model will respond to the last user message)
                    response = model.send(messages)
                    
                    behavior = classify(response)
                    print(f"            → Final Response Behavior: {behavior.name}")
                    
                    if behavior in invariant.violation_behaviors:
                        violated = True
                        invariant_failures.append({
                            'type': 'multi_turn',
                            'sequence_id': seq.id,
                            'description': seq.description,
                            'turns': seq.turns,
                            'final_response': response,
                            'behavior': behavior.name
                        })
                except Exception as e:
                    print(f"            → Error processing multi-turn sequence: {str(e)}")
                    invariant_failures.append({
                        'type': 'multi_turn',
                        'sequence_id': seq.id,
                        'description': seq.description,
                        'turns': seq.turns,
                        'final_response': f"Error: {str(e)}",
                        'behavior': 'ERROR'
                    })

        results[invariant.name] = "VIOLATED" if violated else "HELD"
        failures[invariant.name] = invariant_failures

    return results, failures
