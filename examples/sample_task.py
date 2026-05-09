"""
examples/sample_task.py
End-to-end demo: runs a single episode on a toy mutual-exclusion program.
"""

from agent.core import InvariantAgent
from agent.policy import Policy
from llm.client import LLMClient
from memory.bank import MemoryBank
from verifier.tlc import TLCVerifier
from rl.trainer import Trainer

SAMPLE_SPEC = """
---- MODULE MutualExclusion ----
EXTENDS Naturals

VARIABLES pc1, pc2, lock

Init == pc1 = "idle" /\\ pc2 = "idle" /\\ lock = ""

Step1 == pc1 = "idle" /\\ lock = "" /\\ pc1' = "critical" /\\ lock' = "pc1" /\\ UNCHANGED pc2
Step2 == pc2 = "idle" /\\ lock = "" /\\ pc2' = "critical" /\\ lock' = "pc2" /\\ UNCHANGED pc1
Exit1 == pc1 = "critical" /\\ lock = "pc1" /\\ pc1' = "idle" /\\ lock' = "" /\\ UNCHANGED pc2
Exit2 == pc2 = "critical" /\\ lock = "pc2" /\\ pc2' = "idle" /\\ lock' = "" /\\ UNCHANGED pc1

Next == Step1 \\/ Step2 \\/ Exit1 \\/ Exit2

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
    llm = LLMClient(provider="gemini")
    verifier = TLCVerifier()
    trainer = Trainer(policy)

    agent = InvariantAgent(policy=policy, llm=llm, verifier=verifier, bank=bank)

    print("Running episode...")
    result = agent.run_episode(SAMPLE_DESCRIPTION, SAMPLE_SPEC)

    print(f"Verified : {result['verified']}")
    print(f"Invariant: {result['invariant']}")
    print(f"Iters    : {result['iters']}")
    print(f"Reward   : {result['reward']:.2f}")

    trainer.record_episode(SAMPLE_DESCRIPTION, result)
    trainer.update()
    print(f"\nTrainer stats: {trainer.stats()}")


if __name__ == "__main__":
    main()
