from llm.client import MockLLMClient
from verifier.tlc import TLCVerifier
from memory.bank import MemoryBank
from agent.policy import Policy
from agent.core import InvariantAgent

SPEC = """
---- MODULE MutualExclusion ----
EXTENDS Naturals
VARIABLES pc1, pc2
Init == pc1 = "idle" /\\ pc2 = "idle"
Step1 == pc1 = "idle" /\\ pc1' = "critical" /\\ UNCHANGED pc2
Step2 == pc2 = "idle" /\\ pc2' = "critical" /\\ UNCHANGED pc1
Exit1 == pc1 = "critical" /\\ pc1' = "idle" /\\ UNCHANGED pc2
Exit2 == pc2 = "critical" /\\ pc2' = "idle" /\\ UNCHANGED pc1
Next == Step1 \\/ Step2 \\/ Exit1 \\/ Exit2
Spec == Init /\\ [][Next]_<<pc1, pc2>>
====
"""

bank = MemoryBank()
policy = Policy(bank)
llm = MockLLMClient()
verifier = TLCVerifier(jar_path='/Users/laptop/Downloads/TLA+ Toolbox.app/Contents/Eclipse/tla2tools.jar')
agent = InvariantAgent(policy, llm, verifier, bank)
print('Running episode...')
result = agent.run_episode('mutual exclusion with two processes', SPEC)
print('Result:', result)
