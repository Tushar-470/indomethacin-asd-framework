"""
Classify stale content scan hits into the 7 prompt categories.
"""

import json
from pathlib import Path

root = Path(__file__).resolve().parent.parent
audit_file = root / "results" / "stale_content_audit.json"

with open(audit_file, "r", encoding="utf-8") as f:
    findings = json.load(f)

classified = {
    "ACTIVE v1.5 CODE": [],
    "ACTIVE v1.5 UI": [],
    "ACTIVE v1.5 REPORT": [],
    "HISTORICAL v1.4": [],
    "ARCHIVED DOCUMENT": [],
    "TEST": [],
    "PROVENANCE METADATA": [],
}

seen = set()

for term, hits in findings.items():
    for h in hits:
        key = (h["file"], h["line"])
        if key in seen:
            continue
        seen.add(key)
        
        file = h["file"]
        text = h["text"]
        
        if "test" in file.lower():
            classified["TEST"].append(h)
        elif "archive" in file.lower() or "superseded" in file.lower():
            classified["ARCHIVED DOCUMENT"].append(h)
        elif "CORRECTED_FINAL_COMPUTATIONAL_FREEZE_REPORT" in file or "v1.3.1" in file or "v1.4" in file:
            classified["HISTORICAL v1.4"].append(h)
        elif "polymer_library" in file.lower() or "user_polymers" in file.lower() or "data_dictionary" in file.lower() or "data_provenance" in file.lower():
            classified["PROVENANCE METADATA"].append(h)
        elif "frontend" in file.lower():
            classified["ACTIVE v1.5 UI"].append(h)
        elif "pdf_report_generator" in file.lower() or "report_generator" in file.lower() or "results/reports" in file.lower() or "results/final" in file.lower():
            classified["ACTIVE v1.5 REPORT"].append(h)
        else:
            classified["ACTIVE v1.5 CODE"].append(h)

print("=== CLASSIFICATION OF STALE CONTENT HITS ===")
for cat, items in classified.items():
    print(f"\n--- {cat} ({len(items)} entries) ---")
    for item in items[:10]:
        print(f"  [{item['file']}:{item['line']}] {item['text'][:100]}")
    if len(items) > 10:
        print(f"  ... and {len(items)-10} more.")

with open(root / "results" / "classified_stale_terms.json", "w", encoding="utf-8") as f:
    json.dump(classified, f, indent=2)
