import subprocess
import tempfile
import os

class TLCVerifier:
    def __init__(self, jar_path: str = "tla2tools.jar"):
        self.jar_path = os.path.abspath(jar_path)

    def check(self, pluscal_spec: str, invariant: str) -> dict:
        with tempfile.TemporaryDirectory() as tmpdir:
            tla_path = os.path.join(tmpdir, "Spec.tla")
            cfg_path = os.path.join(tmpdir, "Spec.cfg")
            spec_content = self._inject_invariant(pluscal_spec, invariant)
            with open(tla_path, "w") as f:
                f.write(spec_content)
            with open(cfg_path, "w") as f:
                f.write("SPECIFICATION Spec\nINVARIANT CandidateInv\n")
            try:
                result = subprocess.run(
                    ["/opt/homebrew/opt/openjdk/libexec/openjdk.jdk/Contents/Home/bin/java", "-jar", self.jar_path, "-config", cfg_path, tla_path],
                    capture_output=True, text=True, timeout=60
                )
                raw = result.stdout + result.stderr
            except subprocess.TimeoutExpired:
                return {"verified": False, "counterexample": None, "raw_output": "TLC timed out"}
            except FileNotFoundError:
                return {"verified": False, "counterexample": None, "raw_output": "java not found"}
            return self._parse_output(raw)

    def _inject_invariant(self, spec: str, invariant: str) -> str:
        definition = f"\nCandidateInv == {invariant}\n"
        if "====" in spec:
            return spec.replace("====", definition + "====", 1)
        return spec + definition

    def _parse_output(self, raw: str) -> dict:
        success = "Model checking completed. No error has been found." in raw
        counterexample = None
        if not success and "Error: Invariant" in raw:
            lines = raw.splitlines()
            ce_lines = []
            capturing = False
            for line in lines:
                if "Error: Invariant" in line:
                    capturing = True
                if capturing:
                    if line.strip() == "" and ce_lines:
                        break
                    ce_lines.append(line)
            if ce_lines:
                counterexample = {"trace": ce_lines, "property": "CandidateInv", "raw": "\n".join(ce_lines)}
        return {"verified": success, "counterexample": counterexample, "raw_output": raw}
