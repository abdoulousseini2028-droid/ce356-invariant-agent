"""
verifier/tlc.py
Interface to the TLC model checker.
Calls TLC on a PlusCal spec + candidate invariant and parses the result.
"""

import subprocess
import tempfile
import os
import re

TLC_JAR = os.environ.get("TLC_JAR", "tla2tools.jar")


class TLCVerifier:
    def __init__(self, tlc_jar: str = TLC_JAR):
        self.tlc_jar = tlc_jar

    def check(self, pluscal_spec: str, invariant: str) -> dict:
        """
        Verify `invariant` against `pluscal_spec` using TLC.
        Returns:
            {"verified": True}  on success
            {"verified": False, "counterexample": {"property": str, "trace": [str]}}  on failure
        """
        spec_with_invariant = self._inject_invariant(pluscal_spec, invariant)

        with tempfile.TemporaryDirectory() as tmpdir:
            # Extract module name from spec
            module_name = "Spec"
            for line in spec_with_invariant.split("\n"):
                if line.startswith("---- MODULE"):
                    module_name = line.split("MODULE")[1].strip().split()[0]
                    break
            
            spec_path = os.path.join(tmpdir, f"{module_name}.tla")
            cfg_path = os.path.join(tmpdir, f"{module_name}.cfg")

            with open(spec_path, "w") as f:
                f.write(spec_with_invariant)
            with open(cfg_path, "w") as f:
                f.write(f"SPECIFICATION Spec\nINVARIANT Invariant1\n")

            result = subprocess.run(
                ["java", "-jar", self.tlc_jar, "-config", cfg_path, spec_path],
                capture_output=True,
                text=True,
                timeout=60,
            )

        return self._parse_output(result.stdout + result.stderr)

    # ── internal ──────────────────────────────────────────────────────────

    @staticmethod
    def _inject_invariant(spec: str, invariant: str) -> str:
        """Append invariant definition before the final '====' line."""
        lines = spec.rstrip().split("\n")
        closing = next((i for i, l in enumerate(lines) if l.startswith("====")), len(lines))
        # Define as named invariant: Invariant1 == ...
        inv_def = f"\nInvariant1 == {invariant}"
        lines.insert(closing, inv_def)
        return "\n".join(lines)

    @staticmethod
    def _parse_output(output: str) -> dict:
        if "No error" in output or "Model checking completed" in output:
            return {"verified": True}

        # Extract counterexample trace lines
        trace_lines = []
        in_trace = False
        for line in output.splitlines():
            if "Error: Invariant" in line or "Invariant is violated" in line:
                in_trace = True
                property_match = re.search(r"Invariant (\w+)", line)
                violated = property_match.group(1) if property_match else "the invariant"
            if in_trace and line.strip().startswith("State"):
                trace_lines.append(line.strip())

        return {
            "verified": False,
            "counterexample": {
                "property": violated if in_trace else "the invariant",
                "trace": trace_lines or ["(trace unavailable — check raw TLC output)"],
            },
        }
