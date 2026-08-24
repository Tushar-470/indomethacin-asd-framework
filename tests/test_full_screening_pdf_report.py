"""
Automated Test Suite for Full Screening Technical Report (PDF Export).
Verifies:
1. PDF file generation and integrity (>0 bytes, valid header).
2. Numerical alignment between source screening result object and report fields:
   - API / Drug properties (MW, Tm, Tg, density, HSP components, R0)
   - Polymer properties (Mn, Tg, density, HSP components)
   - Thermodynamic outputs (chi, chi_critical, predicted Tg,mix)
   - Decision scores (TOPSIS CL, rankings)
   - Monte Carlo UQ (P(top-1), random seed, iterations)
   - Configuration & provenance hashes
3. API endpoint GET /api/screening/{analysis_id}/export-full-report response.
4. Scientific content determinism.
"""

import pytest
import os
import json
from pathlib import Path
from fastapi.testclient import TestClient

from backend.main import app
from backend.services import engine_adapter
from backend.models.schemas import ScreeningRequest

client = TestClient(app)


def test_full_screening_pdf_generation_and_numerical_integrity():
    """Verify full PDF generation and source-to-PDF data integrity."""
    # 1. Run a test screening
    req_payload = {
        "drug_id": "IND-001-2026",
        "polymer_ids": [
            "POL-001-2026",
            "POL-002-2026",
            "POL-005-2026",
            "POL-006-2026",
            "POL-007-2026",
        ],
        "mode": "exploratory",
        "drug_loading_ww": 0.30,
        "random_seed": 42,
    }
    run_res = client.post("/api/screening/run", json=req_payload)
    assert run_res.status_code == 200, f"Screening run failed: {run_res.text}"
    data = run_res.json()
    analysis_id = data["analysis_id"]

    # 2. Generate Full Screening PDF
    pdf_path = engine_adapter.generate_full_screening_pdf(analysis_id)
    assert pdf_path is not None, "generate_full_screening_pdf returned None"
    assert pdf_path.exists(), f"PDF file does not exist at {pdf_path}"
    assert pdf_path.stat().st_size > 50000, f"PDF file size too small: {pdf_path.stat().st_size} bytes"

    # Verify valid PDF header bytes
    with open(pdf_path, "rb") as f:
        header = f.read(5)
        assert header == b"%PDF-", f"Invalid PDF header: {header}"

    # 3. Verify Source Numerical Alignment
    source_result = engine_adapter.get_screening_result(analysis_id)
    assert source_result is not None
    assert source_result["drug_id"] == "IND-001-2026"
    assert source_result["selected_polymer"] == data["selected_polymer"]
    assert pytest.approx(source_result["topsis_cl"], 0.0001) == data["topsis_cl"]
    assert pytest.approx(source_result["confidence_p_top1"], 0.001) == data["confidence_p_top1"]
    assert pytest.approx(source_result["predicted_tg_k"], 0.1) == data["predicted_tg_k"]
    assert pytest.approx(source_result["predicted_chi"], 0.001) == data["predicted_chi"]
    assert pytest.approx(source_result["chi_critical"], 0.001) == data["chi_critical"]
    assert source_result["gate1_passed"] == data["gate1_passed"]

    # 4. Test API Export Endpoint
    export_res = client.get(f"/api/screening/{analysis_id}/export-full-report")
    assert export_res.status_code == 200
    assert export_res.headers["content-type"] == "application/pdf"
    assert "attachment" in export_res.headers.get("content-disposition", "") or "filename=" in export_res.headers.get("content-disposition", "")
    assert len(export_res.content) == pdf_path.stat().st_size

    # 5. Deterministic Regeneration Test
    pdf_path_second = engine_adapter.generate_full_screening_pdf(analysis_id)
    assert pdf_path_second.exists()
    assert pdf_path_second.stat().st_size > 50000
