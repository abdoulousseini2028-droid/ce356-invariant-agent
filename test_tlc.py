#!/usr/bin/env python3

import tempfile
import subprocess
import os

SAMPLE_SPEC = """
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

invariant = '~(pc1 = "critical" /\\ pc2 = "critical")'

# Inject invariant into spec
lines = SAMPLE_SPEC.rstrip().split("\n")
closing = next((i for i, l in enumerate(lines) if l.startswith("====")), len(lines))
# Define as a named invariant
inv_def = f"\nInvariant1 == {invariant}"
lines.insert(closing, inv_def)
spec_with_inv = "\n".join(lines)

print("Spec with invariant:")
print(spec_with_inv)
print("\n" + "="*60 + "\n")

# Create temp files
with tempfile.TemporaryDirectory() as tmpdir:
    spec_path = os.path.join(tmpdir, "MutualExclusion.tla")
    cfg_path = os.path.join(tmpdir, "MutualExclusion.cfg")
    
    with open(spec_path, "w") as f:
        f.write(spec_with_inv)
    
    # Create config with proper INVARIANT definition
    cfg_content = f"""SPECIFICATION Spec
INVARIANT Invariant1
"""
    with open(cfg_path, "w") as f:
        f.write(cfg_content)
    
    print(f"Config file:\n{cfg_content}\n")
    
    # Run TLC
    java_path = "/opt/homebrew/opt/openjdk/libexec/openjdk.jdk/Contents/Home/bin/java"
    tlc_jar = "/Users/laptop/Downloads/TLA+ Toolbox.app/Contents/Eclipse/tla2tools.jar"
    
    cmd = [java_path, "-jar", tlc_jar, "-config", cfg_path, spec_path]
    print(f"Running: {' '.join(cmd)}\n")
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    
    output = result.stdout + result.stderr
    print("TLC Output:")
    print(output)
