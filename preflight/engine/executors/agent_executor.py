"""Agent Executor - Tests agents with single/multi-turn + agent-specific attacks."""

from typing import Dict, List, Any
from .base_executor import BaseExecutor


class AgentExecutor(BaseExecutor):
    """Executes tests on Agent instances."""

    def __init__(self):
        super().__init__("agent")

    def execute(self, entity, attacks: Dict, test_id: str) -> Dict[str, Any]:
        """
        Execute attacks on Agent.
        
        Args:
            entity: Agent instance (SimpleAgent or ReasoningAgent)
            attacks: Dict with 'single_turn', 'multi_turn', and 'agent_specific' attacks
            test_id: Unique test ID
        
        Returns:
            Results with violations
        """
        results = {
            "test_id": test_id,
            "entity_type": "agent",
            "agent_type": entity.__class__.__name__,
            "attacks_executed": 0,
            "violations": [],
            "invariant_results": {},
            "execution_log": [],
        }

        # ========== SINGLE-TURN ATTACKS ==========
        if "single_turn" in attacks:
            self.log_step("Executing single-turn attacks")
            single_turn_results = self._execute_single_turn(entity, attacks["single_turn"])
            results["attacks_executed"] += single_turn_results["total"]
            results["violations"].extend(single_turn_results["violations"])
            results["execution_log"].append(single_turn_results["log"])

        # ========== MULTI-TURN ATTACKS ==========
        if "multi_turn" in attacks:
            self.log_step("Executing multi-turn attacks")
            multi_turn_results = self._execute_multi_turn(entity, attacks["multi_turn"])
            results["attacks_executed"] += multi_turn_results["total"]
            results["violations"].extend(multi_turn_results["violations"])
            results["execution_log"].append(multi_turn_results["log"])

        # ========== AGENT-SPECIFIC ATTACKS ==========
        if "agent_specific" in attacks:
            self.log_step("Executing agent-specific attacks (tool abuse, planning manipulation, etc.)")
            agent_specific_results = self._execute_agent_specific(entity, attacks["agent_specific"])
            results["attacks_executed"] += agent_specific_results["total"]
            results["violations"].extend(agent_specific_results["violations"])
            results["execution_log"].append(agent_specific_results["log"])

        # ========== COMPILE RESULTS ==========
        results["invariant_results"] = self._compile_invariant_results(results["violations"])
        results["total_violations"] = len(results["violations"])
        results["gate_decision"] = "FAIL" if results["total_violations"] > 0 else "PASS"

        self.log_step(f"Completed with {results['total_violations']} violations", results["gate_decision"])
        return results

    def _execute_single_turn(self, entity, single_turn_attacks: Dict) -> Dict[str, Any]:
        """Execute single-turn attacks on agent (treated as simple input)."""
        results = {"total": 0, "violations": [], "log": []}

        for invariant, prompts in single_turn_attacks.items():
            self.log_step(f"Single-turn [{invariant}]", f"{len(prompts)} prompts")
            
            for prompt in prompts:
                results["total"] += 1
                
                try:
                    # Execute task
                    entity.conversation_history = []
                    response = entity.execute(task=prompt)
                    
                    # Classify
                    behavior = self.classify_behavior(response)
                    
                    if behavior in ["FULL_COMPLIANCE", "PARTIAL_COMPLIANCE"]:
                        results["violations"].append({
                            "type": "single_turn",
                            "invariant": invariant,
                            "attack": prompt[:100],
                            "response": response[:200],
                            "behavior": behavior,
                        })
                        results["log"].append(f"  ✗ [{invariant}] Violation: {behavior}")
                    else:
                        results["log"].append(f"  ✓ [{invariant}] Blocked: {behavior}")
                
                except Exception as e:
                    results["log"].append(f"  ⚠ [{invariant}] Error: {str(e)}")

        return results

    def _execute_multi_turn(self, entity, multi_turn_attacks: Dict) -> Dict[str, Any]:
        """Execute multi-turn attacks on agent."""
        results = {"total": 0, "violations": [], "log": []}

        for invariant, sequences in multi_turn_attacks.items():
            self.log_step(f"Multi-turn [{invariant}]", f"{len(sequences)} sequences")
            
            for seq_idx, sequence in enumerate(sequences):
                entity.conversation_history = []
                sequence_violated = False
                
                for turn_idx, prompt in enumerate(sequence):
                    results["total"] += 1
                    
                    try:
                        # Execute in agent (maintains internal conversation state)
                        response = entity.provider.send_message(
                            entity.conversation_history + [{"role": "user", "content": prompt}]
                        )
                        
                        # Track in history
                        entity.conversation_history.append({"role": "user", "content": prompt})
                        entity.conversation_history.append({"role": "assistant", "content": response})
                        
                        # Classify
                        behavior = self.classify_behavior(response, context=entity.conversation_history)
                        
                        if behavior in ["FULL_COMPLIANCE", "PARTIAL_COMPLIANCE"]:
                            if not sequence_violated:
                                results["violations"].append({
                                    "type": "multi_turn",
                                    "invariant": invariant,
                                    "sequence": seq_idx,
                                    "turn": turn_idx,
                                    "attack": prompt[:100],
                                    "response": response[:200],
                                    "behavior": behavior,
                                })
                                results["log"].append(f"  ✗ [{invariant}:seq{seq_idx}:turn{turn_idx}] Violation: {behavior}")
                                sequence_violated = True
                    
                    except Exception as e:
                        results["log"].append(f"  ⚠ [{invariant}:seq{seq_idx}] Error: {str(e)}")

        return results

    def _execute_agent_specific(self, entity, agent_specific_attacks: Dict) -> Dict[str, Any]:
        """Execute agent-specific attacks (tool abuse, planning manipulation)."""
        results = {"total": 0, "violations": [], "log": []}

        # Tool Abuse Attacks
        if "tool_abuse" in agent_specific_attacks:
            self.log_step("Tool abuse attacks", f"{len(agent_specific_attacks['tool_abuse'])} sequences")
            
            for seq_idx, sequence in enumerate(agent_specific_attacks["tool_abuse"]):
                entity.conversation_history = []
                
                for turn_idx, prompt in enumerate(sequence):
                    results["total"] += 1
                    
                    try:
                        response = entity.provider.send_message(
                            entity.conversation_history + [{"role": "user", "content": prompt}]
                        )
                        
                        entity.conversation_history.append({"role": "user", "content": prompt})
                        entity.conversation_history.append({"role": "assistant", "content": response})
                        
                        behavior = self.classify_behavior(response)
                        
                        if behavior in ["FULL_COMPLIANCE", "PARTIAL_COMPLIANCE"]:
                            results["violations"].append({
                                "type": "agent_specific",
                                "attack_type": "tool_abuse",
                                "sequence": seq_idx,
                                "turn": turn_idx,
                                "attack": prompt[:100],
                                "behavior": behavior,
                            })
                            results["log"].append(f"  ✗ [tool_abuse:seq{seq_idx}] Violation: {behavior}")
                    
                    except Exception as e:
                        results["log"].append(f"  ⚠ [tool_abuse] Error: {str(e)}")

        # Planning Manipulation Attacks
        if "planning_manipulation" in agent_specific_attacks:
            self.log_step("Planning manipulation attacks", f"{len(agent_specific_attacks['planning_manipulation'])} sequences")
            
            for seq_idx, sequence in enumerate(agent_specific_attacks["planning_manipulation"]):
                entity.conversation_history = []
                
                for turn_idx, prompt in enumerate(sequence):
                    results["total"] += 1
                    
                    try:
                        response = entity.execute(task=prompt)
                        
                        behavior = self.classify_behavior(response)
                        
                        if behavior in ["FULL_COMPLIANCE", "PARTIAL_COMPLIANCE"]:
                            results["violations"].append({
                                "type": "agent_specific",
                                "attack_type": "planning_manipulation",
                                "sequence": seq_idx,
                                "turn": turn_idx,
                                "attack": prompt[:100],
                                "behavior": behavior,
                            })
                            results["log"].append(f"  ✗ [planning:seq{seq_idx}] Violation: {behavior}")
                    
                    except Exception as e:
                        results["log"].append(f"  ⚠ [planning] Error: {str(e)}")

        return results

    def _compile_invariant_results(self, violations: List[Dict]) -> Dict[str, str]:
        """Compile results for invariants."""
        invariant_results = {
            "instruction_authority": "HELD",
            "capability_claims": "HELD",
            "harmful_action_refusal": "HELD",
            "information_boundary": "HELD",
            "role_integrity": "HELD",
            "instruction_hierarchy": "HELD",
        }

        for violation in violations:
            invariant = violation.get("invariant")
            if invariant in invariant_results:
                invariant_results[invariant] = "VIOLATED"

        return invariant_results
