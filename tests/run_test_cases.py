"""Evaluation test cases for the revised extractor (run: python tests/run_test_cases.py).
Prints the actual result of each case so it can be copied into revision.md.
All inputs are synthetic."""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from extractor import extract  # noqa: E402

CASES = [
    ("Typical 1 - lithography bench note (Sample 1)",
     "Date: Oct 12, 2026. Sample ID: Si-Wafer-402. Used Karl Suss Aligner. Exposure time: 8.5s. "
     "Note: Edge bead removal seemed uneven on the south quadrant. File attached: optical_microscope_042.png"),
    ("Typical 2 - informal PECVD note (custom input; before/after case)",
     "Nov 3 2026. Sample GaN-117. Ran PECVD SiN deposition, 300C, 40 min. "
     "Thickness looked thin on ellipsometer, recheck tomorrow."),
    ("Challenge - shorthand laser note, uncertain ID, no date",
     "laser test again, 2.5 W, 1064 nm, spot looked off-center on sample LT-3? maybe LT-8. redo w/ new lens"),
    ("Invalid - empty input", ""),
    ("Invalid - non-lab text", "hello there"),
    ("Risk - two wafers in one note, defect not tied to one",
     "Wafer W-12 and wafer W-14 went in the furnace at 950C for 2 h on 11/02/2026, not sure which one cracked."),
]

for name, text in CASES:
    r = extract(text).to_dict()
    print(f"\n### {name}\nINPUT: {text!r}")
    if not r["ok"]:
        print("BLOCKED:", r["message"])
        continue
    for k, f in r["fields"].items():
        print(f"  {f['name']:<13} {f['status']:<10} {f['value'] or f['options']}")
    print("  Settings:", [(p['label_in_notes'] or p['type'], p['value']) for p in r["parameters"]])
    print("  Steps:", r["process_sequence"], "| Files:", r["files"])
    print("  Warnings:", r["warnings"])
    print("  Summary:", r["summary"])

# Determinism check (the stand-in is rule-based, so repeats should be identical)
t = CASES[1][1]
outs = {json.dumps(extract(t).to_dict(), sort_keys=True) for _ in range(3)}
print(f"\nRepeat check: Typical 2 run 3 times -> {len(outs)} distinct output(s)")
