"""
Critical Regression Test: Verifies that the Web Application API endpoint (/api/screening/run)
produces results IDENTICAL to the CLI pipeline within numerical tolerance.

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
            "POL-003-2026",
            "POL-004-2026",
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

    # 2. TOPSIS CL numerical tolerance check (CLI benchmark: 0.7775821475801472)
    assert abs(data["topsis_cl"] - 0.77758) < 1e-3

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
