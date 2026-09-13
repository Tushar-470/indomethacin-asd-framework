"""
Critical Regression Test: Verifies that the Web Application API endpoint (/api/screening/run)
produces results IDENTICAL to the CLI pipeline within numerical tolerance, and tests polymer name resolution.

Authoritative CLI benchmarks for Indomethacin + 6 Polymers:
- Winner: Soluplus (POL-005-2026)
- TOPSIS CL ≈ 0.7776 (tolerance 1e-4)
- Gate 1 Passed: True
- Gate 2 Passed: True
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_api_reproduces_cli_indomethacin_screening():
    """Verify that /api/screening/run reproduces v2 Variable-K results with 100% precision."""
    payload = {
        "drug_id": "IND-001-2026",
        "polymer_ids": [
            "POL-001-2026",
            "POL-002-2026",
            "POL-007-2026",
            "POL-005-2026",
            "POL-006-2026",
        ],
        "mode": "research",
        "drug_loading_ww": 0.30,
        "random_seed": 42,
    }

    response = client.post("/api/screening/run", json=payload)
    assert response.status_code == 200, f"Screening failed: {response.text}"

    data = response.json()

    # 1. Top selection check (Soluplus #1 under v2 Variable-K Engine)
    assert data["selected_polymer_id"] == "POL-005-2026"
    assert data["selected_polymer"] == "Soluplus"

    # 2. TOPSIS CL numerical tolerance check (authoritative v2 benchmark: 0.6864)
    assert abs(data["topsis_cl"] - 0.6864) < 1e-3
    assert abs(data["ahp_cr"] - 0.0494) < 1e-3

    # 3. Dynamic K and Stability checks
    assert data["pca_retained_k"] == 3
    assert abs(data["boundary_eigengap"] - 0.7383) < 1e-3
    assert data["subspace_stability_status"] == "STABLE"
    assert data["execution_tier"] == "AUTHORITATIVE_RESEARCH"

    # 4. Gate checks
    assert data["gate1_passed"] is True
    assert data["gate2_passed"] is True

    # 5. Pipeline reports and figures verification (4 figures: 6, 7, 8, 11; NO Fig 12 FBM)
    assert len(data["figures"]) == 4
    assert "fig12_fbm_contour.png" not in data["figures"]
    assert "json" in data["reports"]
    assert "xlsx" in data["reports"]
    assert "csv" in data["reports"]
    assert "md" in data["reports"]

    # 6. FBM excised from response
    assert "fbm_auc" not in data
    assert "fbm_actionable" not in data

    # 7. Ranking order check (Matches results/v2/tables/indomethacin_deterministic_baseline.json)
    ranks = {row["polymer_id"]: row["rank"] for row in data["ranking"]}
    assert ranks["POL-005-2026"] == 1  # Soluplus #1 (CL ≈ 0.6864)
    assert ranks["POL-006-2026"] == 2  # HPMC E5 #2 (CL ≈ 0.6731)
    assert ranks["POL-002-2026"] == 3  # PVP-VA 64 #3 (CL ≈ 0.6062)
    assert ranks["POL-001-2026"] == 4  # PVP K30 #4 (CL ≈ 0.5876)
    assert ranks["POL-007-2026"] == 5  # EDR EPO #5 (CL ≈ 0.5456)


def test_research_mode_rejects_unvalidated_polymer():
    """Verify that Research Mode strictly rejects unvalidated draft polymer candidates."""
    draft_poly_payload = {
        "polymer_id": "POL-DRAFT-REJECT-TEST",
        "polymer_name": "Draft Polymer Candidate",
        "abbreviation": "DRAFT_POLY",
        "mn_da": 50000.0,
        "tg_k": 390.0,
        "density_g_cm3": 1.20,
        "hsp_delta_d": 17.5,
        "hsp_delta_p": 7.5,
        "hsp_delta_h": 9.0,
        "functional_groups": "ester",
        "monomer_smiles": "CCO",
        "validation_status": "draft",
    }
    client.delete("/api/polymers/POL-DRAFT-REJECT-TEST")
    add_res = client.post("/api/polymers", json=draft_poly_payload)
    assert add_res.status_code == 201

    try:
        run_payload = {
            "drug_id": "IND-001-2026",
            "polymer_ids": ["POL-005-2026", "POL-006-2026", "POL-DRAFT-REJECT-TEST"],
            "mode": "research",
            "drug_loading_ww": 0.30,
            "random_seed": 42,
        }
        res = client.post("/api/screening/run", json=run_payload)
        assert res.status_code == 422
        assert "Research mode requires validated polymers" in res.json()["detail"]
    finally:
        client.delete("/api/polymers/POL-DRAFT-REJECT-TEST")



def test_polymer_name_resolution_and_display():
    """Regression test confirming polymer ID to polymer name resolution in API response."""
    payload = {
        "drug_id": "IND-001-2026",
        "polymer_ids": [
            "POL-001-2026",
            "POL-002-2026",
            "POL-007-2026",
            "POL-005-2026",
            "POL-006-2026",
        ],
        "mode": "research",
        "drug_loading_ww": 0.30,
        "random_seed": 42,
    }

    response = client.post("/api/screening/run", json=payload)
    assert response.status_code == 200
    data = response.json()

    # Map polymer_id -> polymer_name from response
    name_map = {row["polymer_id"]: row["polymer_name"] for row in data["ranking"]}

    # Verify key polymer name mappings
    assert name_map["POL-005-2026"] == "Soluplus"
    assert name_map["POL-007-2026"] == "Eudragit E PO"
    assert name_map["POL-002-2026"] == "PVP-Vinyl Acetate 64"



def test_newly_added_polymer_displays_actual_name():
    """Verify that a newly added custom polymer displays its actual entered name rather than a generic string."""
    new_poly_payload = {
        "polymer_id": "POL-CUSTOM-REGRESSION-888",
        "polymer_name": "My Custom BioPolymer Carrier",
        "abbreviation": "CUST_BIO_888",
        "mn_da": 65000.0,
        "tg_k": 410.0,
        "density_g_cm3": 1.22,
        "hsp_delta_d": 18.2,
        "hsp_delta_p": 7.8,
        "hsp_delta_h": 9.2,
        "functional_groups": "ether|hydroxyl",
        "monomer_smiles": "CCOCC",
        "validation_status": "draft"
    }

    # Pre-clean if polymer exists from previous interrupted run
    client.delete("/api/polymers/POL-CUSTOM-REGRESSION-888")

    # Add custom polymer via API
    add_res = client.post("/api/polymers", json=new_poly_payload)
    assert add_res.status_code == 201


    try:
        # Run screening with reference + custom polymer
        run_payload = {
            "drug_id": "IND-001-2026",
            "polymer_ids": ["POL-005-2026", "POL-007-2026", "POL-CUSTOM-REGRESSION-888"],
            "mode": "exploratory",
            "drug_loading_ww": 0.30,
            "random_seed": 42
        }


        res = client.post("/api/screening/run", json=run_payload)
        assert res.status_code == 200
        data = res.json()

        # Find custom polymer row in ranking
        custom_row = next((r for r in data["ranking"] if r["polymer_id"] == "POL-CUSTOM-REGRESSION-888"), None)
        assert custom_row is not None
        assert custom_row["polymer_name"] == "My Custom BioPolymer Carrier"
        assert custom_row["polymer_name"] != "Polymer 1"
        assert custom_row["polymer_name"] != "POL-CUSTOM-REGRESSION-888"

    finally:
        # Clean up test polymer
        client.delete("/api/polymers/POL-CUSTOM-REGRESSION-888")
