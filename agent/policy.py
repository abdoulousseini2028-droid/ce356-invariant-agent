"""
agent/policy.py
Lightweight RL policy: controls few-shot example retrieval and feedback formatting.
This is the only component that gets trained — the LLM itself is never modified.
"""

from memory.bank import MemoryBank
from typing import List


class Policy:
    def __init__(self, bank: MemoryBank, k_shot: int = 3):
        self.bank = bank
        self.k_shot = k_shot
        # Learned retrieval weights — updated by rl/trainer.py
        self._retrieval_weights: dict = {}

    def retrieve_examples(self, program_description: str) -> List[dict]:
        """
        Retrieve the k most useful verified examples from the memory bank
        for a given program description. Uses learned similarity weights.
        """
        return self.bank.retrieve(program_description, k=self.k_shot, weights=self._retrieval_weights)

    def build_prompt(
        self,
        program_description: str,
        pluscal_spec: str,
        few_shot_examples: List[dict],
        feedback_history: List[dict],
    ) -> List[dict]:
        """
        Constructs the full message list to send to the LLM API.
        """
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert in formal verification. Given a PlusCal specification, "
                    "generate a TLA+ invariant that TLC can verify. Output only the invariant expression."
                ),
            }
        ]

        # Inject few-shot examples
        for ex in few_shot_examples:
            messages.append({"role": "user", "content": f"Program: {ex['description']}\nSpec:\n{ex['spec']}"})
            messages.append({"role": "assistant", "content": ex["invariant"]})

        # Current task
        messages.append({"role": "user", "content": f"Program: {program_description}\nSpec:\n{pluscal_spec}"})

        # Inject feedback from previous failed attempts
        for fb in feedback_history:
            messages.append({"role": "assistant", "content": fb.get("previous_attempt", "")})
            messages.append({"role": "user", "content": fb["message"]})

        return messages

    def format_feedback(self, counterexample: dict) -> str:
        """
        Converts a TLC counterexample trace into a targeted natural-language
        revision prompt. The phrasing strategy is what the RL policy optimizes.
        """
        trace = counterexample.get("trace", [])
        violated_property = counterexample.get("property", "the invariant")

        trace_str = "\n".join(
            f"  Step {i + 1}: {state}" for i, state in enumerate(trace)
        )

        return (
            f"TLC found a counterexample violating {violated_property}:\n"
            f"{trace_str}\n\n"
            "Revise the invariant to exclude this behavior while remaining inductive. "
            "Output only the corrected invariant expression."
        )

    def update_weights(self, retrieval_weights: dict):
        """Called by rl/trainer.py after each policy gradient update."""
        self._retrieval_weights = retrieval_weights
