def gate_decision(invariant_results):
    return "FAIL" if "VIOLATED" in invariant_results.values() else "PASS"