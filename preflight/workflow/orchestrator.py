"""
Orchestrator module - handles the preflight workflow.
Separates business logic from script execution.
"""

import uuid
import os
from datetime import datetime
from preflight.database import Database


class PrefightOrchestrator:
    """Orchestrates the preflight testing workflow."""
    
    def __init__(self, model, invariants, model_name: str = None, 
                 model_version: str = None, model_url: str = None, 
                 api_key: str = None):
        """
        Initialize the orchestrator.
        
        Args:
            model: Model instance (has send() method)
            invariants: List of invariant objects
            model_name: Name of the model (e.g., "gemini-2.0-flash")
            model_version: Version of the model
            model_url: API URL of the model
            api_key: API key (will be hashed before storage)
        """
        self.model = model
        self.invariants = invariants
        self.model_name = model_name
        self.model_version = model_version
        self.model_url = model_url
        self.api_key = api_key
        self.db = Database()
        self.run_id = str(uuid.uuid4())

    def run(self):
        """
        Execute the complete preflight workflow.
        
        Returns:
            Dict containing:
            - run_id: Unique run identifier
            - results: Test results per invariant
            - decision: Gate decision (PASS/FAIL)
            - num_violations: Number of invariants violated
        """
        # Import here to avoid circular imports
        from preflight.engine.runner import run_scenarios
        from preflight.core.gate import gate_decision
        
        # Step 1: Save run metadata
        self._save_run_metadata()
        
        # Step 2: Run tests
        results, failures = run_scenarios(model=self.model, invariants=self.invariants)
        
        # Step 3: Save results
        self._save_results(results, failures)
        
        # Step 4: Make gate decision
        decision = gate_decision(results)
        
        # Step 5: Save decision
        self.db.update_gate_decision(self.run_id, decision)
        
        # Step 6: Calculate stats
        num_violations = sum(1 for r in results.values() if r == "VIOLATED")
        
        return {
            'run_id': self.run_id,
            'results': results,
            'decision': decision,
            'num_violations': num_violations
        }

    def _save_run_metadata(self):
        """Save run metadata to database."""
        self.db.save_run(
            run_id=self.run_id,
            model_name=self.model_name,
            model_version=self.model_version,
            model_url=self.model_url,
            api_key=self.api_key,
            num_invariants=len(self.invariants)
        )

    def _save_results(self, results: dict, failures: dict):
        """Save invariant results and failures to database."""
        # Save invariant results
        for invariant_name, result in results.items():
            invariant_obj = next(
                (inv for inv in self.invariants if inv.name == invariant_name), 
                None
            )
            num_prompts = len(invariant_obj.prompts) if invariant_obj else 0
            
            self.db.save_invariant(
                run_id=self.run_id,
                invariant_name=invariant_name,
                invariant_result=result,
                num_prompts_tested=num_prompts
            )
        
        # Save failure details
        for invariant_name, invariant_failures in failures.items():
            for failure in invariant_failures:
                # Handle both single-turn and multi-turn failures
                if failure['type'] == 'single_turn':
                    prompt_text = failure['prompt']
                    response_text = failure['response']
                else:  # multi_turn
                    prompt_text = f"[MULTI-TURN] {failure['description']}"
                    response_text = failure['final_response']
                
                self.db.save_failure(
                    run_id=self.run_id,
                    invariant_name=invariant_name,
                    prompt_text=prompt_text,
                    model_response=response_text,
                    behavior_detected=failure['behavior']
                )

    def get_summary(self) -> str:
        """Get a summary of the run."""
        run_data = self.db.get_run(self.run_id)
        if not run_data:
            return "Run data not found"
        
        passed = sum(1 for inv in run_data['invariants'] 
                    if inv['invariant_result'] == 'HELD')
        failed = len(run_data['invariants']) - passed
        
        summary = f"""
Run Summary:
  Run ID: {self.run_id}
  Model: {self.model_name} (v{self.model_version})
  Invariants Tested: {len(run_data['invariants'])}
  Passed: {passed}
  Failed: {failed}
  Gate Decision: {run_data['gate_decision']}
  Failures Found: {len(run_data['failures'])}
"""
        return summary
