"""
verifier/property_checker.py

A lightweight Python property checker that evaluates temporal logic assertions
over execution traces — conceptually similar to SystemVerilog Assertions (SVA)
used in hardware formal verification.
"""

from typing import Callable, List

State = dict
Trace = List[State]
Predicate = Callable[[State], bool]


class PropertyChecker:
    def __init__(self, trace: Trace):
        self.trace = trace
        self._results = []

    def assert_always(self, prop: Predicate, name: str = "safety") -> bool:
        """□P — SVA: always P"""
        for i, state in enumerate(self.trace):
            if not prop(state):
                self._record(name, False, f"Violated at step {i}: {state}")
                return False
        self._record(name, True)
        return True

    def assert_never(self, prop: Predicate, name: str = "never") -> bool:
        """□(¬P) — SVA: never P"""
        return self.assert_always(lambda s: not prop(s), name)

    def assert_eventually(self, prop: Predicate, name: str = "liveness") -> bool:
        """◇P — SVA: s_eventually P"""
        for state in self.trace:
            if prop(state):
                self._record(name, True)
                return True
        self._record(name, False, "Property never became true")
        return False

    def assert_leads_to(self, trigger: Predicate, goal: Predicate, name: str = "leads_to") -> bool:
        """P ~> Q — SVA: P |-> strong(##[1:$] Q)"""
        for i, state in enumerate(self.trace):
            if trigger(state):
                if not any(goal(s) for s in self.trace[i:]):
                    self._record(name, False, f"Trigger at step {i} but goal never followed")
                    return False
        self._record(name, True)
        return True

    def assert_sequence(self, antecedent: Predicate, consequent: Predicate,
                        delay: int = 1, name: str = "sequence") -> bool:
        """P |-> ##delay Q — SVA: P |-> ##delay Q"""
        for i, state in enumerate(self.trace):
            if antecedent(state):
                j = i + delay
                if j >= len(self.trace) or not consequent(self.trace[j]):
                    self._record(name, False, f"Failed at step {i}+{delay}")
                    return False
        self._record(name, True)
        return True

    def report(self):
        print("\n=== Property Check Results ===")
        for r in self._results:
            status = "✓ PASS" if r["passed"] else "✗ FAIL"
            print(f"  {status}  [{r['name']}]")
            if not r["passed"]:
                print(f"         Counterexample: {r['reason']}")
        passed = sum(r["passed"] for r in self._results)
        print(f"\n  {passed}/{len(self._results)} properties verified\n")

    def _record(self, name, passed, reason=""):
        self._results.append({"name": name, "passed": passed, "reason": reason})


if __name__ == "__main__":
    trace = [
        {"pc1": "idle",     "pc2": "idle"},
        {"pc1": "waiting",  "pc2": "idle"},
        {"pc1": "critical", "pc2": "idle"},
        {"pc1": "critical", "pc2": "waiting"},
        {"pc1": "idle",     "pc2": "waiting"},
        {"pc1": "idle",     "pc2": "critical"},
        {"pc1": "idle",     "pc2": "idle"},
    ]

    checker = PropertyChecker(trace)
    checker.assert_never(lambda s: s["pc1"] == "critical" and s["pc2"] == "critical", "MutualExclusion")
    checker.assert_eventually(lambda s: s["pc1"] == "critical", "P1_Eventually_Critical")
    checker.assert_leads_to(lambda s: s["pc1"] == "waiting", lambda s: s["pc1"] == "critical", "P1_Waiting_LeadsTo_Critical")
    checker.assert_sequence(lambda s: s["pc1"] == "waiting", lambda s: s["pc1"] == "critical", delay=1, name="P1_Wait_Then_Enter")
    checker.report()
