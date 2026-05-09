"""
rl/trainer.py
Reward assignment and policy gradient updates.
Trains the lightweight policy (few-shot selector + feedback formatter)
using episode outcomes — the LLM itself is never modified.
"""

import numpy as np
from typing import List
from agent.policy import Policy


class Trainer:
    def __init__(self, policy: Policy, learning_rate: float = 0.01):
        self.policy = policy
        self.lr = learning_rate
        self._episode_log: List[dict] = []

    def record_episode(self, program_description: str, result: dict):
        """Log the outcome of an episode for batch policy updates."""
        self._episode_log.append({"description": program_description, **result})

    def update(self):
        """
        Run a policy gradient update over logged episodes.
        Uses a simple REINFORCE-style update on the retrieval weight parameters.
        Called periodically (e.g., every 10 episodes).
        """
        if not self._episode_log:
            return

        rewards = np.array([ep["reward"] for ep in self._episode_log])
        baseline = rewards.mean()
        advantages = rewards - baseline  # reduce variance

        # Gradient step: reinforce retrieval weights toward high-advantage episodes
        weight_updates = {}
        for ep, adv in zip(self._episode_log, advantages):
            tokens = ep["description"].lower().split()
            for tok in tokens:
                weight_updates[tok] = weight_updates.get(tok, 0.0) + self.lr * adv

        current_weights = self.policy._retrieval_weights.copy()
        for tok, delta in weight_updates.items():
            current_weights[tok] = current_weights.get(tok, 0.0) + delta

        self.policy.update_weights(current_weights)
        self._episode_log.clear()

    def stats(self) -> dict:
        """Return summary statistics over logged episodes."""
        if not self._episode_log:
            return {}
        rewards = [ep["reward"] for ep in self._episode_log]
        verified = [ep["verified"] for ep in self._episode_log]
        return {
            "episodes": len(self._episode_log),
            "success_rate": sum(verified) / len(verified),
            "mean_reward": float(np.mean(rewards)),
            "avg_iters": float(np.mean([ep["iters"] for ep in self._episode_log])),
        }
