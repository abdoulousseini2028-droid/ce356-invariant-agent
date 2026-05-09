"""
agent/core.py
Episode runner: orchestrates a single invariant synthesis + verification episode.
"""

from agent.policy import Policy
from llm.client import LLMClient
from verifier.tlc import TLCVerifier
from memory.bank import MemoryBank

MAX_ITERS = 5


class InvariantAgent:
    def __init__(self, policy: Policy, llm: LLMClient, verifier: TLCVerifier, bank: MemoryBank):
        self.policy = policy
        self.llm = llm
        self.verifier = verifier
        self.bank = bank

    def run_episode(self, program_description: str, pluscal_spec: str) -> dict:
        """
        Runs one full episode for a given program.
        Returns a result dict with: verified (bool), invariant (str), iters (int), reward (float).
        """
        few_shot_examples = self.policy.retrieve_examples(program_description)
        feedback_history = []

        for iteration in range(1, MAX_ITERS + 1):
            prompt = self.policy.build_prompt(
                program_description=program_description,
                pluscal_spec=pluscal_spec,
                few_shot_examples=few_shot_examples,
                feedback_history=feedback_history,
            )

            candidate_invariant = self.llm.generate(prompt)
            result = self.verifier.check(pluscal_spec, candidate_invariant)

            if result["verified"]:
                self.bank.store(program_description, pluscal_spec, candidate_invariant)
                reward = self._compute_reward(success=True, iteration=iteration)
                return {
                    "verified": True,
                    "invariant": candidate_invariant,
                    "iters": iteration,
                    "reward": reward,
                }

            # Verification failed — format feedback and retry
            feedback_msg = self.policy.format_feedback(result["counterexample"])
            feedback_history.append({"iteration": iteration, "message": feedback_msg, "previous_attempt": candidate_invariant})

        reward = self._compute_reward(success=False, iteration=MAX_ITERS)
        return {"verified": False, "invariant": None, "iters": MAX_ITERS, "reward": reward}

    @staticmethod
    def _compute_reward(success: bool, iteration: int) -> float:
        if not success:
            return -1.0
        # Reward decays with number of iterations needed
        return max(0.5, 1.0 - 0.1 * (iteration - 1))
