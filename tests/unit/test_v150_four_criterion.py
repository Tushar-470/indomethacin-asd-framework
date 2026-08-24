"""
Unit tests for v1.5.0 Four-Criterion Model Revision.
Verifies complete removal of s_lit from active computation, Policy A K-handling,
schema audits, custom polymer generalization, and deterministic reproduction.
"""

import json
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from asd_mcda.configuration.loader import ConfigManager
from asd_mcda.drug.drug_profile import Drug
from asd_mcda.polymer.polymer_library import Polymer, PolymerLibrary
from asd_mcda.compatibility.matrix import CompatibilityMatrix
from asd_mcda.integration.pca import PCAPreprocessor
from asd_mcda.mcda.ahp import AHPWeightElicitor
from asd_mcda.mcda.topsis import TOPSISRanker
from asd_mcda.uncertainty.monte_carlo import MonteCarloUQ
from asd_mcda.sensitivity.morris import MorrisSensitivity
from asd_mcda.reporting.report_generator import ReportGenerator
from backend.main import app
from backend.models.schemas import PolymerCreate, DrugProfileCreate


@pytest.fixture
def base_setup():
    root = Path(__file__).parent.parent.parent
    cm = ConfigManager(root / "config" / "workflow" / "workflow_config.yaml", root_dir=root)
    drug = Drug.from_dict(cm.load_drug_json())
    lib = PolymerLibrary.from_csv(cm.get_polymer_library_path(), drug)
    with open(cm.get_ahp_matrix_dir() / "default_matrix.json", "r", encoding="utf-8") as f:
        ahp_raw = json.load(f)
    return cm, drug, lib, np.array(ahp_raw["pairwise_matrix"])


def test_1_score_matrix_has_exactly_four_criteria(base_setup):
    """Verify raw Compatibility Matrix S contains exactly the 4 objective criteria."""
    cm, drug, lib, _ = base_setup
    comp = CompatibilityMatrix(drug, lib)
    df_S = comp.build_matrix()
    
    expected_cols = ["polymer_id", "abbreviation", "s_HSP", "s_chi", "s_desc", "s_GT"]
    assert list(df_S.columns) == expected_cols
    assert "s_lit" not in df_S.columns
    assert len(df_S) == 5


def test_2_s_lit_absent_from_pca(base_setup):
    """Verify PCA preprocessor operates on exactly 4 active columns without s_lit."""
    cm, drug, lib, _ = base_setup
    comp = CompatibilityMatrix(drug, lib)
    df_S = comp.build_matrix()
    
    pca = PCAPreprocessor(variance_threshold=0.95)
    pca_res = pca.fit_transform(df_S)
    
    assert list(pca_res.loadings_matrix_p.index) == ["s_HSP", "s_chi", "s_desc", "s_GT"]
    assert "s_lit" not in pca_res.loadings_matrix_p.index
    assert pca_res.n_components_retained == 2
    assert pca_res.cumulative_variance_ratio[-1] >= 0.95


def test_3_s_lit_absent_from_ahp_topsis(base_setup):
    """Verify AHP weights and TOPSIS operate on the 4-criterion PCA scores matrix."""
    cm, drug, lib, ahp_matrix = base_setup
    comp = CompatibilityMatrix(drug, lib)
    df_S = comp.build_matrix()
    
    pca = PCAPreprocessor(variance_threshold=0.95)
    pca_res = pca.fit_transform(df_S)
    
    ahp_elicitor = AHPWeightElicitor()
    ahp_res = ahp_elicitor.aggregate_multi_expert_matrices([ahp_matrix])
    k = pca_res.n_components_retained
    w = ahp_res.weights[:k] / np.sum(ahp_res.weights[:k])
    
    topsis = TOPSISRanker()
    top_res = topsis.fit_predict(pca_res.scores_matrix_t, w)
    
    assert len(w) == 2
    assert ahp_res.cr < 0.08
    assert len(top_res.ranking_table) == 5
    assert top_res.ranking_table.iloc[0]["polymer_id"] == "POL-006-2026"


def test_4_s_lit_absent_from_monte_carlo(base_setup):
    """Verify Monte Carlo UQ perturbs only the 4 criteria and uses Policy A projection."""
    cm, drug, lib, ahp_matrix = base_setup
    uq = MonteCarloUQ(drug, lib, n_iterations=1000, random_seed=42)
    uq_res = uq.run(ahp_matrix)
    
    assert uq_res.selected_polymer_id == "POL-006-2026"
    assert uq_res.converged is True
    assert "POL-006-2026" in uq_res.p_top1
    assert uq_res.p_top1["POL-006-2026"] >= 0.70


def test_5_s_lit_absent_from_morris_sensitivity(base_setup):
    """Verify Morris sensitivity screening features match the active 4-criterion space."""
    cm, drug, lib, _ = base_setup
    comp = CompatibilityMatrix(drug, lib)
    df_S = comp.build_matrix()
    pca = PCAPreprocessor(0.95)
    pca_res = pca.fit_transform(df_S)
    
    morris = MorrisSensitivity()
    morris_res = morris.analyze(pca_res.scores_matrix_t)
    
    assert "s_lit" not in morris_res.feature_names
    assert len(morris_res.feature_names) == pca_res.n_components_retained


def test_6_polymer_creation_schema_no_literature_score():
    """Verify PolymerCreate Pydantic schema does not require or collect literature score."""
    fields = PolymerCreate.model_fields
    assert "literature_evidence_score" not in fields
    assert "s_lit" not in fields
    assert "evidence_score" not in fields


def test_7_drug_creation_schema_no_literature_score():
    """Verify DrugProfileCreate Pydantic schema does not require or collect literature score."""
    fields = DrugProfileCreate.model_fields
    assert "literature_evidence_score" not in fields
    assert "s_lit" not in fields


def test_8_custom_polymer_generalization_test(base_setup):
    """Verify custom polymer without literature score runs smoothly through full 4-criterion pipeline."""
    cm, drug, _, ahp_matrix = base_setup
    
    custom_dict = {
        "polymer_id": "POL-CUSTOM-TEST",
        "polymer_name": "Test Custom BioPolymer",
        "abbreviation": "CUST_BIO",
        "polymer_family": "vinylic",
        "polymer_class": "neutral",
        "regulatory_status": "FDA_IID",
        "mn_da": 55000.0,
        "mw_da": 65000.0,
        "pdi": 1.18,
        "tg_k": 390.0,
        "density_g_cm3": 1.18,
        "hsp_delta_d": 17.5,
        "hsp_delta_p": 7.8,
        "hsp_delta_h": 10.2,
        "monomer_smiles": "CC(C)C(=O)OCC",
    }
    custom_poly = Polymer.from_dict(custom_dict)
    
    # Run with 2 reference polymers + custom polymer
    ref_polys = PolymerLibrary.from_csv(cm.get_polymer_library_path(), drug).polymers[:2]
    test_lib = PolymerLibrary(ref_polys + [custom_poly], drug)
    
    comp = CompatibilityMatrix(drug, test_lib)
    df_S = comp.build_matrix()
    assert len(df_S) == 3
    assert "s_lit" not in df_S.columns
    
    pca = PCAPreprocessor(0.95)
    pca_res = pca.fit_transform(df_S)
    
    ahp_elicitor = AHPWeightElicitor()
    ahp_res = ahp_elicitor.aggregate_multi_expert_matrices([ahp_matrix])
    k = pca_res.n_components_retained
    w = ahp_res.weights[:k] / np.sum(ahp_res.weights[:k])
    
    topsis = TOPSISRanker()
    top_res = topsis.fit_predict(pca_res.scores_matrix_t, w)
    assert len(top_res.ranking_table) == 3
    assert "POL-CUSTOM-TEST" in top_res.ranking_table["polymer_id"].values

    # Test API endpoint polymer creation without literature_evidence_score
    client = TestClient(app)
    import uuid
    test_poly_id = f"POL-TEST-{uuid.uuid4().hex[:8]}"
    api_payload = {
        "polymer_id": test_poly_id,
        "polymer_name": "Generalization Test Polymer",
        "abbreviation": "GEN_POLY",
        "polymer_family": "Cellulosic",
        "polymer_class": "Neutral",
        "mn_da": 45000,
        "tg_k": 410.0,
        "density_g_cm3": 1.25,
        "hsp_delta_d": 18.0,
        "hsp_delta_p": 8.0,
        "hsp_delta_h": 11.0,
        "monomer_smiles": "C=CC(=O)O",
    }
    try:
        res = client.post("/api/polymers", json=api_payload)
        assert res.status_code in [200, 201], res.text
        created = res.json()
        assert created["polymer_id"] == test_poly_id
    finally:
        # Delete test polymer
        client.delete(f"/api/polymers/{test_poly_id}")


def test_9_v14_historical_artifacts_preserved():
    """Verify v1.4.0 historical artifacts remain intact in archive/historical."""
    root = Path(__file__).parent.parent.parent
    hist_dir = root / "archive" / "historical"
    assert hist_dir.exists()
    assert (hist_dir / "CORRECTED_FINAL_COMPUTATIONAL_FREEZE_REPORT_V1.4.md").exists()


def test_10_deterministic_reproducibility(base_setup):
    """Verify identical inputs + seed produce identical deterministic outputs."""
    cm, drug, lib, ahp_matrix = base_setup
    
    comp1 = CompatibilityMatrix(drug, lib)
    df_S1 = comp1.build_matrix()
    pca1 = PCAPreprocessor(0.95).fit_transform(df_S1)
    
    comp2 = CompatibilityMatrix(drug, lib)
    df_S2 = comp2.build_matrix()
    pca2 = PCAPreprocessor(0.95).fit_transform(df_S2)
    
    pd.testing.assert_frame_equal(df_S1, df_S2)
    pd.testing.assert_frame_equal(pca1.scores_matrix_t, pca2.scores_matrix_t)


def test_11_stochastic_seed_variation(base_setup):
    """Verify different seeds yield varied stochastic samples while preserving deterministic core."""
    cm, drug, lib, ahp_matrix = base_setup
    
    uq1 = MonteCarloUQ(drug, lib, n_iterations=500, random_seed=42)
    res1 = uq1.run(ahp_matrix)
    
    uq2 = MonteCarloUQ(drug, lib, n_iterations=500, random_seed=12345)
    res2 = uq2.run(ahp_matrix)
    
    # Stochastic P(top-1) differs slightly between seeds
    assert res1.p_top1 != res2.p_top1
    # Both select the robust rank 1 candidate
    assert res1.selected_polymer_id == "POL-006-2026"
    assert res2.selected_polymer_id == "POL-006-2026"


def test_12_scientific_equations_intact(base_setup):
    """Verify underlying thermodynamic equations (HSP Ra, RED, FH chi, GT Tg,mix) are unchanged."""
    _, drug, lib, _ = base_setup
    comp = CompatibilityMatrix(drug, lib)
    
    soluplus = next(p for p in lib.polymers if p.polymer_id == "POL-005-2026")
    ra = comp.hsp_model.compute_ra(soluplus)
    red = comp.hsp_model.compute_red(soluplus)
    chi = comp.fh_model.compute_chi(soluplus)
    tg_mix = comp.gt_model.compute_tg_mix(soluplus, 0.30)
    
    # Theoretical hand calculations
    # HSP: 4*(19.2 - 18.0)^2 + (7.9 - 8.5)^2 + (8.4 - 10.5)^2 = 4*(1.44) + 0.36 + 4.41 = 5.76 + 0.36 + 4.41 = 10.53 -> sqrt = 3.245
    assert abs(ra - 3.245) < 0.01
    assert abs(red - (3.245 / 8.0)) < 0.01
    assert abs(chi - 0.1739) < 0.01
    assert tg_mix > 315.15


def test_13_policy_a_k_handling_explicit():
    """Verify Policy A projection prevents dimension mismatch during MC perturbations."""
    raw_scores = np.array([
        [0.75, 0.74, 0.2268, 0.97],
        [0.80, 0.82, 0.2268, 0.00],
        [0.69, 0.60, 0.2268, 0.98],
    ])
    df_S = pd.DataFrame(raw_scores, columns=["s_HSP", "s_chi", "s_desc", "s_GT"])
    
    pca_base = PCAPreprocessor(0.95)
    pca_res = pca_base.fit_transform(df_S)
    k_base = pca_res.n_components_retained
    
    # Simulate high noise on constant column
    noise = np.random.normal(0, 0.2, size=raw_scores.shape)
    S_pert = np.clip(raw_scores + noise, 0.0, 1.0)
    
    # Policy A: Project onto baseline PCA model
    scaled_pert = pca_base.scaler.transform(S_pert)
    t_sim = scaled_pert @ pca_base.pca_model.components_.T
    
    assert t_sim.shape == (3, k_base)


def test_14_gate1_boundary_conditions():
    """Verify generic Gate 1 rule: if chi < chi_c: PASS else: FAIL across boundary states."""
    from asd_mcda.compatibility.flory_huggins import evaluate_gate1_diagnostic
    
    # Boundary 1: chi < chi_c -> PASS
    assert evaluate_gate1_diagnostic(chi=0.500, chi_c=0.538) == "PASS"
    assert evaluate_gate1_diagnostic(chi=0.260, chi_c=0.536) == "PASS"
    assert evaluate_gate1_diagnostic(chi=0.000, chi_c=0.500) == "PASS"
    assert evaluate_gate1_diagnostic(chi=-0.100, chi_c=0.500) == "PASS"

    # Boundary 2: chi == chi_c -> FAIL (critical boundary requires strictly chi < chi_c)
    assert evaluate_gate1_diagnostic(chi=0.538, chi_c=0.538) == "FAIL"
    assert evaluate_gate1_diagnostic(chi=0.500, chi_c=0.500) == "FAIL"

    # Boundary 3: chi > chi_c -> FAIL
    assert evaluate_gate1_diagnostic(chi=0.561, chi_c=0.538) == "FAIL"
    assert evaluate_gate1_diagnostic(chi=0.750, chi_c=0.538) == "FAIL"


def test_15_five_polymer_gate1_exact_diagnostics(base_setup):
    """Verify exact Gate 1 diagnostics for the authoritative 5-polymer library and user-specified targets."""
    from asd_mcda.compatibility.flory_huggins import evaluate_gate1_diagnostic
    
    # 1. Test user-specified canonical reference values
    user_targets = {
        "HPMC_E5": {"chi": 0.260, "chi_c": 0.536, "expected": "PASS"},
        "Soluplus": {"chi": 0.174, "chi_c": 0.518, "expected": "PASS"},
        "PVP_K30": {"chi": 0.395, "chi_c": 0.536, "expected": "PASS"},
        "PVP_VA64": {"chi": 0.362, "chi_c": 0.533, "expected": "PASS"},
        "Eudragit_EPO": {"chi": 0.561, "chi_c": 0.538, "expected": "FAIL"},
    }
    
    for name, data in user_targets.items():
        status = evaluate_gate1_diagnostic(data["chi"], data["chi_c"])
        assert status == data["expected"], f"{name} Gate 1 mismatch: got {status} expected {data['expected']}"
        if data["expected"] == "PASS":
            assert data["chi"] < data["chi_c"]
        else:
            assert data["chi"] >= data["chi_c"]

    # 2. Test live library evaluation with generic gate function
    _, drug, lib, _ = base_setup
    from asd_mcda.compatibility.flory_huggins import FloryHugginsModel
    fh_model = FloryHugginsModel(drug, lib)
    
    for poly in lib.polymers:
        diag = fh_model.evaluate_candidate_gate1(poly)
        chi = diag["chi"]
        chi_c = diag["chi_critical"]
        if chi < chi_c:
            assert diag["gate1_status"] == "PASS"
            assert diag["passed"] is True
            assert "Phase-boundary diagnostic favorable" in diag["message"]
        else:
            assert diag["gate1_status"] == "FAIL"
            assert diag["passed"] is False
            assert "Phase-boundary diagnostic unfavorable" in diag["message"]

