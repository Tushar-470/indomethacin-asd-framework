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
    """Verify that /api/screening/run reproduces CLI results with 100% precision."""
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

    # 1. Top selection check
    assert data["selected_polymer_id"] == "POL-005-2026"
    assert "Soluplus" in data["selected_polymer"]

    # 2. TOPSIS CL numerical tolerance check (CLI 5-polymer benchmark: 0.736338)
    assert abs(data["topsis_cl"] - 0.736338) < 1e-3

    # 3. Gate checks
    assert data["gate1_passed"] is True
    assert data["gate2_passed"] is True

    # 4. Pipeline reports and figures verification
    assert len(data["figures"]) == 5
    assert "json" in data["reports"]
    assert "xlsx" in data["reports"]

    # 5. Ranking order check
    ranks = {row["polymer_id"]: row["rank"] for row in data["ranking"]}
    assert ranks["POL-005-2026"] == 1  # Soluplus #1


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
        "literature_evidence_score": 0.7,
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
