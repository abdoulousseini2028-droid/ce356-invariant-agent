"""
rl/policy.py
Lightweight REINFORCE policy that learns which temporal property types
(safety, liveness, sequence) to prioritize based on verification outcomes.
Trained on rewards from property_checker results across episodes.
"""

import numpy as np
from typing import List


PROPERTY_TYPES = ["always", "never", "eventually", "leads_to", "sequence"]


class PropertySelectionPolicy:
    def __init__(self, lr: float = 0.01):
        self.lr = lr
        self.weights = {p: 0.0 for p in PROPERTY_TYPES}
        self._log = []

    def select(self, candidates: List[str]) -> List[str]:
        scored = sorted(candidates, key=lambda p: self.weights.get(p, 0.0), reverse=True)
        return scored

    def record(self, property_type: str, reward: float):
        self._log.append({"type": property_type, "reward": reward})

    def update(self):
        if not self._log:
            return
        rewards = np.array([e["reward"] for e in self._log])
        baseline = rewards.mean()
        advantages = rewards - baseline
        for entry, adv in zip(self._log, advantages):
            p = entry["type"]
            self.weights[p] = self.weights.get(p, 0.0) + self.lr * adv
        self._log.clear()

    def report(self):
        print("\n=== Learned Property Weights ===")
        for p, w in sorted(self.weights.items(), key=lambda x: x[1], reverse=True):
            print(f"  {p:15s}: {w:+.4f}")


if __name__ == "__main__":
    policy = PropertySelectionPolicy(lr=0.05)
    episodes = [
        ("always",    1.0),
        ("leads_to",  0.8),
        ("sequence",  -1.0),
        ("always",    1.0),
        ("never",     0.6),
        ("leads_to",  1.0),
        ("sequence",  -1.0),
        ("eventually", 0.4),
    ]
    for prop_type, reward in episodes:
        policy.record(prop_type, reward)
    policy.update()
    policy.report()
    ranked = policy.select(PROPERTY_TYPES)
    print("\nRanked for next episode:")
    for i, p in enumerate(ranked, 1):
        print(f"  {i}. {p}")
