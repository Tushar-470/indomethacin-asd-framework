"""Integration Tests for the Variable-K Decision Engine Pipeline.

Authoritative Specification: 2.0.0-SPEC-PHASE0-PATCH2.
Tests end-to-end execution across synthetic cohorts (K=1, 2, 3, 4), the authoritative
Indomethacin reference cohort, and deep immutability buffer independence.
"""

import pytest
import numpy as np

try:
    from asd_mcda.v2.engine import VariableKEngine
    from asd_mcda.v2.models import deep_freeze
except ImportError:
    VariableKEngine = None
    deep_freeze = None


def test_deep_immutability_and_caller_buffer_independence():
    """Test 20: Assert caller-side mutation of source NumPy array does not alter frozen snapshot."""
    if deep_freeze is None:
        pytest.fail("Phase 1 Contract: asd_mcda.v2.models module not yet implemented.")

    caller_arr = np.array([[0.8, 0.7], [0.6, 0.5]])
    caller_dict = {"nested": [1, 2, {"key": "val"}]}

    frozen_arr = deep_freeze(caller_arr)
    frozen_dict = deep_freeze(caller_dict)

    # Mutation attempt 1: Mutate caller buffer
    caller_arr[0, 0] = 0.999
    assert frozen_arr[0, 0] == 0.8  # Unaltered

    # Mutation attempt 2: Mutate frozen buffer directly
    with pytest.raises(ValueError, match="read-only"):
        frozen_arr[0, 0] = 0.999

    # Mutation attempt 3: Mutate caller dictionary
    caller_dict["nested"][2]["key"] = "tampered"
    assert frozen_dict["nested"][2]["key"] == "val"  # Unaltered


def test_synthetic_cohort_k1(k1_synthetic_cohort, ahp_reciprocal_matrix):
    """Test 21: Execute pipeline on rank-1 cohort; assert K=1 selected."""
    if VariableKEngine is None:
        pytest.fail("Phase 1 Contract: asd_mcda.v2.engine module not yet implemented.")

    fixture = k1_synthetic_cohort
    engine = VariableKEngine()
    res = engine.evaluate(fixture["scores"], ahp_reciprocal_matrix["matrix"], fixture["polymer_ids"])

    assert res.retained_k == 1
    assert res.stability_status == "STABLE"


def test_synthetic_cohort_k2(k2_synthetic_cohort, ahp_reciprocal_matrix):
    """Test 22: Execute pipeline on 2D manifold cohort; assert K=2 selected."""
    if VariableKEngine is None:
        pytest.fail("Phase 1 Contract: asd_mcda.v2.engine module not yet implemented.")

    fixture = k2_synthetic_cohort
    engine = VariableKEngine()
    res = engine.evaluate(fixture["scores"], ahp_reciprocal_matrix["matrix"], fixture["polymer_ids"])

    assert res.retained_k == 2
    assert res.stability_status == "STABLE"


def test_synthetic_cohort_k3_geometry(k3_synthetic_cohort, ahp_reciprocal_matrix):
    """Test 23: Execute pipeline on synthetic 3D geometry; assert K=3 selected."""
    if VariableKEngine is None:
        pytest.fail("Phase 1 Contract: asd_mcda.v2.engine module not yet implemented.")

    fixture = k3_synthetic_cohort
    engine = VariableKEngine()
    res = engine.evaluate(fixture["scores"], ahp_reciprocal_matrix["matrix"], fixture["polymer_ids"])

    assert res.retained_k == 3
    assert res.stability_status == "STABLE"


def test_indomethacin_reference_cohort_selects_k3(indomethacin_reference_cohort, ahp_reciprocal_matrix):
    """Test 24: Authoritative production reference case using corrected Indomethacin RDKit scores.
    
    Criteria order: ('s_HSP', 's_chi', 's_desc', 's_GT').
    Expected K: 3 (Cumulative variance = 99.96% >= 95%).
    Expected delta_3: approximately 0.7383 >= 0.10 (STABLE).
    """
    if VariableKEngine is None:
        pytest.fail("Phase 1 Contract: asd_mcda.v2.engine module not yet implemented.")

    fixture = indomethacin_reference_cohort
    engine = VariableKEngine()
    res = engine.evaluate(fixture["scores"], ahp_reciprocal_matrix["matrix"], fixture["polymer_ids"])

    assert res.retained_k == 3
    assert res.cumulative_variance >= 0.999
    assert np.isclose(res.boundary_eigengap, 0.7383, atol=1e-2)
    assert res.stability_status == "STABLE"


def test_synthetic_cohort_k4(k4_synthetic_cohort, ahp_reciprocal_matrix):
    """Test 25: Execute pipeline on isotropic 4D cohort; assert K=4 (K=p) selected."""
    if VariableKEngine is None:
        pytest.fail("Phase 1 Contract: asd_mcda.v2.engine module not yet implemented.")

    fixture = k4_synthetic_cohort
    engine = VariableKEngine()
    res = engine.evaluate(fixture["scores"], ahp_reciprocal_matrix["matrix"], fixture["polymer_ids"])

    assert res.retained_k == 4
    assert res.boundary_eigengap == float("inf")
    assert res.stability_status == "STABLE"
