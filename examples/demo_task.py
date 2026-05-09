"""
examples/demo_task.py
Demo mode: offline episode using hardcoded invariant (no API calls).
Shows the full agent + TLC verification workflow.
"""

from agent.core import InvariantAgent
from agent.policy import Policy
from llm.client import MockLLMClient
from memory.bank import MemoryBank
from verifier.tlc import TLCVerifier
from rl.trainer import Trainer

SAMPLE_SPEC = """
---- MODULE MutualExclusion ----
EXTENDS Naturals

VARIABLES pc1, pc2, lock

Init == /\\ pc1 = "idle" /\\ pc2 = "idle" /\\ lock = "free"

Try1 == pc1 = "idle" /\\ lock = "free" /\\ pc1' = "critical" /\\ lock' = "locked" /\\ UNCHANGED pc2
Try2 == pc2 = "idle" /\\ lock = "free" /\\ pc2' = "critical" /\\ lock' = "locked" /\\ UNCHANGED pc1

Exit1 == pc1 = "critical" /\\ pc1' = "idle" /\\ lock' = "free" /\\ UNCHANGED pc2
Exit2 == pc2 = "critical" /\\ pc2' = "idle" /\\ lock' = "free" /\\ UNCHANGED pc1

Next == Try1 \\/ Try2 \\/ Exit1 \\/ Exit2

Spec == Init /\\ [][Next]_<<pc1, pc2, lock>>
====
"""

SAMPLE_DESCRIPTION = (
    "Two-process mutual exclusion: each process alternates between idle and critical. "
    "Only one process should be in the critical section at a time."
)


def main():
    bank = MemoryBank()
    policy = Policy(bank, k_shot=3)
    llm = MockLLMClient()  # Mock that returns correct invariant
    verifier = TLCVerifier()
    trainer = Trainer(policy)

    agent = InvariantAgent(policy=policy, llm=llm, verifier=verifier, bank=bank)

    print("Running demo episode (mock LLM, real TLC verification)...")
    result = agent.run_episode(SAMPLE_DESCRIPTION, SAMPLE_SPEC)

    print(f"\nVerified : {result['verified']}")
    print(f"Invariant: {result['invariant']}")
    print(f"Iters    : {result['iters']}")
    print(f"Reward   : {result['reward']:.2f}")

    trainer.record_episode(SAMPLE_DESCRIPTION, result)
    trainer.update()
    print(f"\nTrainer stats: {trainer.stats()}")


if __name__ == "__main__":
    main()
