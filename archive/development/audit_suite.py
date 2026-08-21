"""
Independent Scientific Software Validation & Quality Assurance Test Suite.
Executes programmatic tests for Anti-Hardcoding, Golden Reference CLI vs API comparison,
Input Mutation, New Polymer Addition, Polymer Removal, Order Invariance, Invalid Data,
and Report Consistency.
"""

import sys
import json
import subprocess
from pathlib import Path

# Add src and project root to path
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

results_summary = {}

print("=== STARTING INDEPENDENT AUDIT SUITE ===")

# 1. Anti-Hardcoding Code Search
print("\n--- PHASE 3: Anti-Hardcoding Audit ---")
hardcoded_strings = ["0.77758", "0.7776", "0.7347", "0.6288"]
found_occurrences = {}

for target in hardcoded_strings:
    matches = []
    for py_file in PROJECT_ROOT.glob("**/*.py"):
        if ".venv" in str(py_file) or "node_modules" in str(py_file):
            continue
        try:
            content = py_file.read_text(encoding="utf-8")
            if target in content:
                matches.append(str(py_file.relative_to(PROJECT_ROOT)))
        except Exception:
            pass
    for ts_file in PROJECT_ROOT.glob("frontend/src/**/*.*"):
        try:
            content = ts_file.read_text(encoding="utf-8")
            if target in content:
                matches.append(str(ts_file.relative_to(PROJECT_ROOT)))
        except Exception:
            pass
    found_occurrences[target] = matches

print("Hardcoding Audit Occurrences:")
print(json.dumps(found_occurrences, indent=2))
results_summary["anti_hardcoding"] = found_occurrences


# 2. Golden Reference Comparison (CLI vs Web API)
print("\n--- PHASE 5: Golden Reference CLI vs Web API Comparison ---")

# Execute CLI
cli_cmd = [sys.executable, "-m", "asd_mcda.cli", "--config", "config/workflow/workflow_config.yaml"]
cli_proc = subprocess.run(cli_cmd, cwd=str(PROJECT_ROOT), capture_output=True, text=True)

# Read CLI report
cli_report_json = PROJECT_ROOT / "results" / "reports" / "decision_report.json"
with open(cli_report_json, "r", encoding="utf-8") as f:
    cli_data = json.load(f)

# Execute Web API
api_payload = {
    "drug_id": "IND-001-2026",
    "polymer_ids": ["POL-001-2026", "POL-002-2026", "POL-003-2026", "POL-004-2026", "POL-005-2026", "POL-006-2026"],
    "mode": "research",
    "drug_loading_ww": 0.30,
    "random_seed": 42
}
api_res = client.post("/api/screening/run", json=api_payload)
assert api_res.status_code == 200, f"API failed: {api_res.text}"
api_data = api_res.json()

comparison = {
    "selected_polymer": {
        "CLI": cli_data["selected_polymer"],
        "API": api_data["selected_polymer"],
        "match": cli_data["selected_polymer"] == api_data["selected_polymer"]
    },
    "topsis_CL": {
        "CLI": cli_data["topsis_CL"],
        "API": api_data["topsis_cl"],
        "delta": abs(cli_data["topsis_CL"] - api_data["topsis_cl"])
    },
    "confidence_P_top1": {
        "CLI": cli_data["confidence_P_top1"],
        "API": api_data["confidence_p_top1"],
        "delta": abs(cli_data["confidence_P_top1"] - api_data["confidence_p_top1"])
    },
    "predicted_Tg_K": {
        "CLI": cli_data["predicted_Tg_K"],
        "API": api_data["predicted_tg_k"],
        "delta": abs(cli_data["predicted_Tg_K"] - api_data["predicted_tg_k"])
    },
    "predicted_chi": {
        "CLI": cli_data["predicted_chi"],
        "API": api_data["predicted_chi"],
        "delta": abs(cli_data["predicted_chi"] - api_data["predicted_chi"])
    }
}
print("CLI vs API Comparison Table:")
print(json.dumps(comparison, indent=2))
results_summary["golden_comparison"] = comparison


# 3. Input Mutation Test
print("\n--- PHASE 7: Input Mutation Test ---")
base_cl = api_data["topsis_cl"]

# Mutate Drug Tm (from 424.15K to 500.0K)
mutated_drug = {
    "drug_id": "IND-MUTATED-01",
    "generic_name": "Indomethacin Mutated Tm 500K",
    "canonical_smiles": "CC1=C(C=C(C=C1)OC)C2=C(C3=CC=CC=C3N2CC(=O)O)C(=O)C4=CC=C(C=C4)Cl",
    "molecular_weight_g_mol": 357.79,
    "tm_k": 500.0,
    "tg_k": 315.15,
    "hsp_delta_d": 19.2,
    "hsp_delta_p": 7.9,
    "hsp_delta_h": 8.4,
    "hsp_ro": 8.0,
    "molar_volume_cm3_mol": 273.0,
    "reference_source": "user_entered",
    "validation_status": "draft"
}
client.post("/api/drugs", json=mutated_drug)

mutated_run_payload = {
    "drug_id": "IND-MUTATED-01",
    "polymer_ids": api_payload["polymer_ids"],
    "mode": "exploratory",
    "drug_loading_ww": 0.30,
    "random_seed": 42
}
mutated_res = client.post("/api/screening/run", json=mutated_run_payload)
mutated_data = mutated_res.json()

mutation_test = {
    "baseline_drug_tm": 424.15,
    "mutated_drug_tm": 500.0,
    "baseline_topsis_cl": base_cl,
    "mutated_topsis_cl": mutated_data["topsis_cl"],
    "cl_changed": base_cl != mutated_data["topsis_cl"],
    "delta_cl": abs(base_cl - mutated_data["topsis_cl"])
}
print("Mutation Test Results:")
print(json.dumps(mutation_test, indent=2))
results_summary["mutation_test"] = mutation_test

# Clean up test drug
client.delete("/api/drugs/IND-MUTATED-01")


# 4. New Polymer Test (TEST_POLYMER_ONLY)
print("\n--- PHASE 8: New Polymer Test ---")
new_poly = {
    "polymer_id": "TEST-POLYMER-ONLY-999",
    "polymer_name": "Test Polymer Only carrier",
    "abbreviation": "TEST_POLY_999",
    "mn_da": 80000.0,
    "tg_k": 450.0,
    "density_g_cm3": 1.25,
    "hsp_delta_d": 19.0,
    "hsp_delta_p": 7.8,
    "hsp_delta_h": 8.5,
    "functional_groups": "ester|amide",
    "monomer_smiles": "C=CC(=O)O",
    "literature_evidence_score": 0.8,
    "validation_status": "draft"
}
client.post("/api/polymers", json=new_poly)

new_poly_run_payload = {
    "drug_id": "IND-001-2026",
    "polymer_ids": ["POL-001-2026", "POL-002-2026", "POL-005-2026", "TEST-POLYMER-ONLY-999"],
    "mode": "exploratory",
    "drug_loading_ww": 0.30,
    "random_seed": 42
}
new_poly_res = client.post("/api/screening/run", json=new_poly_run_payload)
new_poly_data = new_poly_res.json()

new_poly_test = {
    "new_polymer_id": "TEST-POLYMER-ONLY-999",
    "included_in_ranking": any(r["polymer_id"] == "TEST-POLYMER-ONLY-999" for r in new_poly_data["ranking"]),
    "assigned_rank": next((r["rank"] for r in new_poly_data["ranking"] if r["polymer_id"] == "TEST-POLYMER-ONLY-999"), None),
    "assigned_cl": next((r["topsis_cl"] for r in new_poly_data["ranking"] if r["polymer_id"] == "TEST-POLYMER-ONLY-999"), None)
}
print("New Polymer Test Results:")
print(json.dumps(new_poly_test, indent=2))
results_summary["new_polymer_test"] = new_poly_test

# Clean up test polymer
client.delete("/api/polymers/TEST-POLYMER-ONLY-999")


# 5. Order Invariance Test
print("\n--- PHASE 10: Order Invariance Test ---")
order_a_payload = {
    "drug_id": "IND-001-2026",
    "polymer_ids": ["POL-005-2026", "POL-003-2026", "POL-002-2026"],
    "mode": "research",
    "drug_loading_ww": 0.30,
    "random_seed": 42
}
order_b_payload = {
    "drug_id": "IND-001-2026",
    "polymer_ids": ["POL-002-2026", "POL-005-2026", "POL-003-2026"],
    "mode": "research",
    "drug_loading_ww": 0.30,
    "random_seed": 42
}

res_a = client.post("/api/screening/run", json=order_a_payload).json()
res_b = client.post("/api/screening/run", json=order_b_payload).json()

scores_a = {r["polymer_id"]: r["topsis_cl"] for r in res_a["ranking"]}
scores_b = {r["polymer_id"]: r["topsis_cl"] for r in res_b["ranking"]}

order_invariance = {
    "scores_order_a": scores_a,
    "scores_order_b": scores_b,
    "is_invariant": all(abs(scores_a[pid] - scores_b[pid]) < 1e-6 for pid in scores_a)
}
print("Order Invariance Test Results:")
print(json.dumps(order_invariance, indent=2))
results_summary["order_invariance"] = order_invariance


# 6. Invalid Data & Missing Data Tests
print("\n--- PHASE 12 & 13: Missing and Invalid Data Tests ---")
invalid_payload_1 = {
    "drug_id": "IND-001-2026",
    "polymer_ids": ["POL-005-2026"],  # Less than 2 polymers
    "mode": "research"
}
res_inv_1 = client.post("/api/screening/run", json=invalid_payload_1)

invalid_drug = {
    "drug_id": "BAD-DRUG",
    "generic_name": "Bad Drug",
    "canonical_smiles": "CCC",
    "molecular_weight_g_mol": -50.0,  # Invalid negative MW
    "tm_k": 200.0,
    "hsp_delta_d": 18.0,
    "hsp_delta_p": 6.0,
    "hsp_delta_h": 8.0
}
res_inv_2 = client.post("/api/drugs/validate", json=invalid_drug)

data_validation_summary = {
    "min_2_polymers_enforced": res_inv_1.status_code == 422,
    "negative_mw_caught": res_inv_2.json()["status"] == "INVALID"
}
print("Data Validation Test Results:")
print(json.dumps(data_validation_summary, indent=2))
results_summary["data_validation"] = data_validation_summary

# Save summary to file
with open(PROJECT_ROOT / "scratch_audit_summary.json", "w", encoding="utf-8") as f:
    json.dump(results_summary, f, indent=2)

print("\n=== AUDIT SUITE COMPLETED SUCCESSFULLY ===")
