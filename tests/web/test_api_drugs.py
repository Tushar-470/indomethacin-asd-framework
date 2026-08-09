"""
Tests for Drug API endpoints (/api/drugs).
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_list_drugs():
    """Verify listing drugs returns Indomethacin reference drug."""
    response = client.get("/api/drugs")
    assert response.status_code == 200
    drugs = response.json()
    assert len(drugs) >= 1
    indo = next((d for d in drugs if d["drug_id"] == "IND-001-2026"), None)
    assert indo is not None
    assert indo["generic_name"] == "Indomethacin"
    assert indo["is_reference"] is True


def test_get_drug_by_id():
    """Verify retrieving specific drug profile."""
    response = client.get("/api/drugs/IND-001-2026")
    assert response.status_code == 200
    drug = response.json()
    assert drug["drug_id"] == "IND-001-2026"
    assert drug["hsp_delta_d"] == 19.2


def test_get_nonexistent_drug():
    """Verify 404 for unknown drug."""
    response = client.get("/api/drugs/NONEXISTENT-999")
    assert response.status_code == 404


def test_validate_drug_valid():
    """Verify drug validation endpoint with valid payload."""
    payload = {
        "drug_id": "TEST-DRUG-01",
        "generic_name": "Test Drug",
        "canonical_smiles": "CC(=O)OC1=CC=CC=C1C(=O)O",
        "molecular_weight_g_mol": 180.16,
        "tm_k": 408.15,
        "tg_k": 243.15,
        "hsp_delta_d": 18.0,
        "hsp_delta_p": 6.0,
        "hsp_delta_h": 8.0,
        "hsp_ro": 7.5,
        "molar_volume_cm3_mol": 150.0,
    }
    response = client.post("/api/drugs/validate", json=payload)
    assert response.status_code == 200
    val = response.json()
    assert val["status"] in ("VALID", "WARNING")
    assert len(val["errors"]) == 0
