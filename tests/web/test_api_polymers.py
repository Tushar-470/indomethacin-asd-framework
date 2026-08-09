"""
Tests for Polymer API endpoints (/api/polymers).
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_list_polymers():
    """Verify listing polymers returns the 6 reference polymers."""
    response = client.get("/api/polymers")
    assert response.status_code == 200
    polymers = response.json()
    assert len(polymers) >= 6
    soluplus = next((p for p in polymers if p["polymer_id"] == "POL-005-2026"), None)
    assert soluplus is not None
    assert soluplus["polymer_name"] == "Soluplus"
    assert soluplus["is_reference"] is True


def test_get_polymer_by_id():
    """Verify retrieving specific polymer profile."""
    response = client.get("/api/polymers/POL-005-2026")
    assert response.status_code == 200
    p = response.json()
    assert p["polymer_id"] == "POL-005-2026"
    assert p["tg_k"] == 343.0


def test_get_nonexistent_polymer():
    """Verify 404 for unknown polymer."""
    response = client.get("/api/polymers/POL-NONEXISTENT")
    assert response.status_code == 404
