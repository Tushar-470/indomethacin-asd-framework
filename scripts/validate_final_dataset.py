#!/usr/bin/env python3
"""
Final Dataset Integrity and Baseline Validation Script
Release: v1.3.1-FREEZE
Master Research Framework V2.0
"""

import csv
import hashlib
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.resolve()

EXPECTED_POLYMER_IDS = {
    "POL-001-2026",
    "POL-002-2026",
    "POL-005-2026",
    "POL-006-2026",
    "POL-007-2026",
}
EXPECTED_POLYMER_COUNT = 5
EXPECTED_LIBRARY_HASH = "24cd6c4092788cb7266d2ea34e82b6dfe193b5cfb91e22c0dff66b0abc9088ff"

REQUIRED_COLUMNS = [
    "polymer_id",
    "polymer_name",
    "abbreviation",
    "mn_da",
    "mw_da",
    "tg_k",
    "density_g_cm3",
    "hsp_delta_d",
    "hsp_delta_p",
    "hsp_delta_h",
    "hsp_total",
    "monomer_smiles",
    "validation_status",
]

NUMERIC_COLUMNS = [
    "mn_da",
    "mw_da",
    "pdi",
    "tg_k",
    "density_g_cm3",
    "hsp_delta_d",
    "hsp_delta_p",
    "hsp_delta_h",
    "hsp_total",
]

EXCLUDED_IDS = {"POL-003-2026", "POL-004-2026"}


def compute_sha256(filepath: Path) -> str:
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def validate():
    """Run all validation checks. Returns (n_passed, n_failed, messages)."""
    passed = 0
    failed = 0
    messages = []

    def check(condition: bool, description: str):
        nonlocal passed, failed
        if condition:
            passed += 1
            messages.append(f"  PASS: {description}")
        else:
            failed += 1
            messages.append(f"  FAIL: {description}")

    # 1. Library file existence
    library_path = PROJECT_ROOT / "config" / "polymers" / "polymer_library_v3_five_polymers.csv"
    check(library_path.exists(), f"Library file exists: {library_path.name}")
    if not library_path.exists():
        messages.append("FATAL: Library file not found. Cannot continue.")
        return passed, failed, messages

    # 2. SHA-256 Checksum
    actual_hash = compute_sha256(library_path)
    check(
        actual_hash == EXPECTED_LIBRARY_HASH,
        f"Library SHA-256 matches expected ({actual_hash[:16]}...)",
    )

    # 3. Read CSV
    with open(library_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        headers = reader.fieldnames or []

    # 4. Exact 5 candidates
    check(
        len(rows) == EXPECTED_POLYMER_COUNT,
        f"Exactly {EXPECTED_POLYMER_COUNT} polymers (found {len(rows)})",
    )

    # 5. Required columns
    for col in REQUIRED_COLUMNS:
        check(col in headers, f"Required column present: {col}")

    # 6. Polymer IDs match expected active set
    actual_ids = {row["polymer_id"] for row in rows}
    check(actual_ids == EXPECTED_POLYMER_IDS, "Polymer IDs match expected set")

    # 7. No excluded polymer IDs
    excluded_found = actual_ids & EXCLUDED_IDS
    check(
        len(excluded_found) == 0,
        f"No excluded polymer IDs present (found: {excluded_found or 'none'})",
    )

    # 8. No duplicate polymer IDs
    all_ids = [row["polymer_id"] for row in rows]
    check(len(all_ids) == len(set(all_ids)), "No duplicate polymer IDs")

    # 9. Numeric values valid (positive, non-NaN, non-empty)
    for col in NUMERIC_COLUMNS:
        if col not in headers:
            continue
        all_valid = True
        for row in rows:
            val = row.get(col, "")
            try:
                numeric_val = float(val)
                if numeric_val <= 0 or val.strip() == "":
                    all_valid = False
                    break
            except (ValueError, TypeError):
                all_valid = False
                break
        check(all_valid, f"All {col} values are valid positive numbers")

    # 10. Validation status flag
    for row in rows:
        status = row.get("validation_status", "")
        check(
            status == "validated",
            f"{row['polymer_id']} validation_status = '{status}'",
        )

    # 11. Drug profile existence & fields
    drug_path = PROJECT_ROOT / "config" / "drugs" / "indomethacin.json"
    check(drug_path.exists(), "Drug profile exists: indomethacin.json")
    if drug_path.exists():
        with open(drug_path, "r", encoding="utf-8") as f:
            drug = json.load(f)
        check("hsp_delta_d" in drug, "Drug HSP delta_d present")
        check("hsp_delta_p" in drug, "Drug HSP delta_p present")
        check("hsp_delta_h" in drug, "Drug HSP delta_h present")
        check("hsp_ro" in drug, "Drug HSP R0 present")
        check(drug.get("hsp_ro", 0) > 0, f"Drug HSP R0 > 0 (value: {drug.get('hsp_ro')})")

    # 12. Workflow configuration points to active library
    config_path = PROJECT_ROOT / "config" / "workflow" / "workflow_config.yaml"
    check(config_path.exists(), "Workflow config exists: workflow_config.yaml")
    if config_path.exists():
        config_text = config_path.read_text(encoding="utf-8")
        check(
            "polymer_library_v3_five_polymers.csv" in config_text,
            "Workflow config references v3 five-polymer library",
        )

    # 13. Active config files do not depend on archive/
    for cfg_file in (PROJECT_ROOT / "config").rglob("*"):
        if cfg_file.is_file() and cfg_file.suffix in (".yaml", ".json", ".csv"):
            content = cfg_file.read_text(encoding="utf-8", errors="ignore")
            check(
                "archive/" not in content and "archive\\" not in content,
                f"No archive reference in {cfg_file.relative_to(PROJECT_ROOT)}",
            )

    return passed, failed, messages


def main():
    print("=" * 60)
    print("FINAL DATASET VALIDATION — v1.3.1-FREEZE")
    print("=" * 60)

    passed, failed, messages = validate()

    print()
    for msg in messages:
        print(msg)

    print()
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)

    if failed > 0:
        print("STATUS: FAIL")
        sys.exit(1)
    else:
        print("STATUS: PASS")
        sys.exit(0)


if __name__ == "__main__":
    main()
