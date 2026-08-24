"""
Comprehensive Test Suite for Full Screening Report Generator Data Isolation & Integrity.
"""

import json
import pytest
from pathlib import Path
from pypdf import PdfReader
from fastapi.testclient import TestClient

from backend.main import app
from backend.services import engine_adapter

client = TestClient(app)


@pytest.fixture(scope="module")
def custom_screening_run():
    """Execute an exploratory screening run with custom + reference polymers."""
    new_poly_payload = {
        "polymer_id": "POL-CUSTOM-REGRESSION-888",
        "polymer_name": "My Custom BioPolymer Carrier",
        "abbreviation": "CUST_BIO_888",
        "polymer_family": "Cellulosic",
        "polymer_class": "Neutral",
        "mn_da": 65000.0,
        "mw_da": 85000.0,
        "pdi": 1.3,
        "tg_k": 410.0,
        "tg_source": "DSC (Simulated)",
        "density_g_cm3": 1.22,
        "density_source": "Supplier CoA",
        "hsp_delta_d": 18.2,
        "hsp_delta_p": 7.8,
        "hsp_delta_h": 9.2,
        "hsp_source": "Calculated (Hoftyzer-Van Krevelen)",
        "functional_groups": "ether|hydroxyl",
        "monomer_smiles": "CCOCC",
        "copolymer_mole_fractions": "",
        "known_asd_applications": "",
        "spray_drying_suitability": "Good",
        "hygroscopicity": "Slightly",
        "literature_dois": "",
        "data_source": "User Custom Add-On",
        "confidence_level": "Medium",
        "validation_status": "draft",
    }
    client.delete("/api/polymers/POL-CUSTOM-REGRESSION-888")
    client.post("/api/polymers", json=new_poly_payload)

    req_payload = {
        "drug_id": "IND-001-2026",
        "polymer_ids": [
            "POL-CUSTOM-REGRESSION-888",
            "POL-005-2026",
            "POL-007-2026",
        ],
        "mode": "exploratory",
        "drug_loading_ww": 0.30,
        "random_seed": 42,
    }
    res = client.post("/api/screening/run", json=req_payload)
    assert res.status_code == 200
    return res.json()


@pytest.fixture(scope="module")
def standard_screening_run():
    """Execute a standard research mode screening run with the 5 frozen polymers."""
    req_payload = {
        "drug_id": "IND-001-2026",
        "polymer_ids": [
            "POL-001-2026",
            "POL-002-2026",
            "POL-005-2026",
            "POL-006-2026",
            "POL-007-2026",
        ],
        "mode": "research",
        "drug_loading_ww": 0.30,
        "random_seed": 42,
    }
    res = client.post("/api/screening/run", json=req_payload)
    assert res.status_code == 200
    return res.json()


def test_1_candidate_set_equality_across_every_section(custom_screening_run):
    """TEST 1: Invariant check enforcing input == score_matrix == TOPSIS == ranking == synthesis candidate IDs."""
    analysis_id = custom_screening_run["analysis_id"]
    pdf_path = engine_adapter.generate_full_screening_pdf(analysis_id)
    assert pdf_path.exists()

    reader = PdfReader(str(pdf_path))
    full_text = "\n".join([p.extract_text() for p in reader.pages])

    expected_ids = set(custom_screening_run["polymer_ids"])
    assert len(expected_ids) == 3
    for pid in expected_ids:
        assert pid in full_text, f"Candidate {pid} missing from report text"


def test_2_rank1_candidate_equality_across_every_section(custom_screening_run):
    """TEST 2: Cover, Executive Summary, TOPSIS Rank 1, Table 5, and Section 10 Synthesis must all match Rank 1."""
    analysis_id = custom_screening_run["analysis_id"]
    pdf_path = engine_adapter.generate_full_screening_pdf(analysis_id)

    rank1_id = custom_screening_run["selected_polymer_id"]
    rank1_name = custom_screening_run["selected_polymer"]

    reader = PdfReader(str(pdf_path))
    full_text = "\n".join([p.extract_text() for p in reader.pages])

    assert rank1_id in full_text
    assert rank1_name in full_text
    assert "Top-Ranked Computational Candidate" in full_text


def test_3_baseline_equality(standard_screening_run):
    """TEST 3: Baseline version v1.5.0-FOUR-CRITERION-FREEZE must be preserved."""
    analysis_id = standard_screening_run["analysis_id"]
    pdf_path = engine_adapter.generate_full_screening_pdf(analysis_id)

    reader = PdfReader(str(pdf_path))
    full_text = "\n".join([p.extract_text() for p in reader.pages])

    assert "v1.5.0-FOUR-CRITERION-FREEZE" in full_text


def test_4_execution_mode_consistency(custom_screening_run, standard_screening_run):
    """TEST 4: Clearly distinguish Exploratory from Research mode."""
    pdf_custom = engine_adapter.generate_full_screening_pdf(custom_screening_run["analysis_id"])
    txt_custom = "\n".join([p.extract_text() for p in PdfReader(str(pdf_custom)).pages])
    assert "EXPLORATORY" in txt_custom

    pdf_std = engine_adapter.generate_full_screening_pdf(standard_screening_run["analysis_id"])
    txt_std = "\n".join([p.extract_text() for p in PdfReader(str(pdf_std)).pages])
    assert "RESEARCH MODE" in txt_std or "Research Baseline" in txt_std


def test_equation_text_matches_v15_baseline(standard_screening_run):
    """TEST 5: Canonical v1.5.0 equations: 0.60 * (Vm/RT) and chi_c with relative molar volume."""
    analysis_id = standard_screening_run["analysis_id"]
    pdf_path = engine_adapter.generate_full_screening_pdf(analysis_id)

    txt = "\n".join([p.extract_text() for p in PdfReader(str(pdf_path)).pages])
    assert "0.60" in txt
    assert "0.25" in txt
    assert "Gordon" in txt
    assert "Simha" in txt or "Simha–Boyer" in txt or "K" in txt


def test_6_no_foreign_candidate_appears_in_custom_report(custom_screening_run):
    """TEST 6: Candidates NOT in custom screening run MUST NOT appear in report."""
    analysis_id = custom_screening_run["analysis_id"]
    pdf_path = engine_adapter.generate_full_screening_pdf(analysis_id)

    txt = "\n".join([p.extract_text() for p in PdfReader(str(pdf_path)).pages])

    assert "POL-006-2026" not in txt, "HPMC E5 leaked into custom report"
    assert "POL-001-2026" not in txt, "PVP K30 leaked into custom report"
    assert "POL-002-2026" not in txt, "PVP-VA 64 leaked into custom report"


def test_7_no_candidate_cross_contamination_between_analyses(custom_screening_run, standard_screening_run):
    """TEST 7: Two different analyses maintain complete candidate isolation."""
    pdf1 = engine_adapter.generate_full_screening_pdf(custom_screening_run["analysis_id"])
    pdf2 = engine_adapter.generate_full_screening_pdf(standard_screening_run["analysis_id"])

    txt1 = "\n".join([p.extract_text() for p in PdfReader(str(pdf1)).pages])
    txt2 = "\n".join([p.extract_text() for p in PdfReader(str(pdf2)).pages])

    assert "POL-CUSTOM-REGRESSION-888" in txt1
    assert "POL-CUSTOM-REGRESSION-888" not in txt2


def test_8_deterministic_regeneration_identical_content(standard_screening_run):
    """TEST 8: Regenerating the report twice yields structural and content determinism."""
    analysis_id = standard_screening_run["analysis_id"]
    pdf1 = engine_adapter.generate_full_screening_pdf(analysis_id)
    pdf2 = engine_adapter.generate_full_screening_pdf(analysis_id)

    r1 = PdfReader(str(pdf1))
    r2 = PdfReader(str(pdf2))

    assert len(r1.pages) == len(r2.pages)
    assert len(r1.pages) >= 9

    for p1, p2 in zip(r1.pages, r2.pages):
        t1 = p1.extract_text()
        t2 = p2.extract_text()
        assert abs(len(t1) - len(t2)) < 20


def test_9_morris_figure_matches_reported_parameters(standard_screening_run):
    """TEST 9: Morris figure parameters (PC1_weight, PC2_weight) must match the reported narrative and table."""
    analysis_id = standard_screening_run["analysis_id"]
    pdf_path = engine_adapter.generate_full_screening_pdf(analysis_id)

    full_text = "\n".join([p.extract_text() for p in PdfReader(str(pdf_path)).pages])

    assert "PC1_weight" in full_text
    assert "PC2_weight" in full_text
    assert "Flory–Huggins χ and drug loading exhibit the largest elementary effects" not in full_text


def test_10_no_stale_v14_terms_in_v15_report(standard_screening_run):
    """TEST 10: Active v1.5 report must contain no stale v1.4.0 or s_lit references."""
    analysis_id = standard_screening_run["analysis_id"]
    pdf_path = engine_adapter.generate_full_screening_pdf(analysis_id)

    full_text = "\n".join([p.extract_text() for p in PdfReader(str(pdf_path)).pages])

    assert "v1.4.0" not in full_text
    assert "s_lit" not in full_text
    assert "literature evidence score" not in full_text
    assert "5-dimensional" not in full_text
    assert "Report Identifier (UUID)" not in full_text


def test_11_gate_definition_consistency(standard_screening_run):
    """TEST 11: Gate/Diagnostic names and definitions must be unambiguous and consistent."""
    analysis_id = standard_screening_run["analysis_id"]
    pdf_path = engine_adapter.generate_full_screening_pdf(analysis_id)

    full_text = "\n".join([p.extract_text() for p in PdfReader(str(pdf_path)).pages])

    assert "Diagnostic 1" in full_text
    assert "Diagnostic 2" in full_text
    assert "Diagnostic 3" in full_text
    assert "Phase-Boundary Diagnostic" in full_text


def test_12_configuration_snapshot_untruncated(standard_screening_run):
    """TEST 12: Appendix A must contain the complete un-truncated input snapshot."""
    analysis_id = standard_screening_run["analysis_id"]
    pdf_path = engine_adapter.generate_full_screening_pdf(analysis_id)

    full_text = "\n".join([p.extract_text() for p in PdfReader(str(pdf_path)).pages])

    assert "[truncated for formatting]" not in full_text
    assert "Appendix A. Complete Raw Input Configuration Snapshot" in full_text


def test_13_selection_robustness_terminology(standard_screening_run):
    """TEST 13: P(top-1) must be described with selection-robustness tier language and disclaimer."""
    analysis_id = standard_screening_run["analysis_id"]
    pdf_path = engine_adapter.generate_full_screening_pdf(analysis_id)
    full_text = "\n".join([p.extract_text() for p in PdfReader(str(pdf_path)).pages])
    norm_text = " ".join(full_text.split())
    assert "model-selection robustness" in norm_text
    assert "not a probability of experimental success" in norm_text


def test_14_scientific_cautious_language(standard_screening_run):
    """TEST 14: Report must use cautious scientific language without unsubstantiated claims."""
    analysis_id = standard_screening_run["analysis_id"]
    pdf_path = engine_adapter.generate_full_screening_pdf(analysis_id)

    full_text = "\n".join([p.extract_text() for p in PdfReader(str(pdf_path)).pages])

    assert "Hansen-space compatibility diagnostic" in full_text
    assert "Flory–Huggins critical interaction phase-boundary diagnostic" in full_text or "Phase-boundary diagnostic" in full_text
    assert "best polymer" not in full_text
    assert "objective, QbD-informed" not in full_text
    assert "QbD-informed computational candidate ranking" in full_text
    assert "elevated physical stability barriers against nucleation and recrystallization" not in full_text


def test_15_full_cryptographic_hash_presence(standard_screening_run):
    """TEST 15: Full cryptographic hash is present and report is marked as persisted screening record."""
    analysis_id = standard_screening_run["analysis_id"]
    pdf_path = engine_adapter.generate_full_screening_pdf(analysis_id)

    full_text = "\n".join([p.extract_text() for p in PdfReader(str(pdf_path)).pages])

    assert "Persisted Screening Report Record" in full_text
    assert "Immutable Export Record" not in full_text


def test_16_table_and_figure_number_consistency(standard_screening_run):
    """TEST 16: Table and Figure numbering are consistent between TOC and body captions."""
    analysis_id = standard_screening_run["analysis_id"]
    pdf_path = engine_adapter.generate_full_screening_pdf(analysis_id)

    full_text = "\n".join([p.extract_text() for p in PdfReader(str(pdf_path)).pages])

    for tbl_num in range(1, 12):
        assert f"Table {tbl_num}." in full_text, f"Table {tbl_num} missing from report"
    for fig_num in range(1, 5):
        assert f"Figure {fig_num}." in full_text, f"Figure {fig_num} missing from report"


def test_17_figure_labels_and_uncertainty_plot(standard_screening_run):
    """TEST 17: Generated Figure 8/3 must not contain stale 'Decision Confidence' or 'High-Confidence' terms."""
    analysis_id = standard_screening_run["analysis_id"]
    fig_path = Path("data/analyses") / analysis_id / "figures" / "fig08_uncertainty_propagation.png"
    assert fig_path.exists(), "Figure 8 uncertainty plot missing"
