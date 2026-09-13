"""Unit Tests for External AHP Preference Solver (Step 5).

Authoritative Specification: 2.0.0-SPEC-PHASE0-PATCH2.
Tests reciprocity validation, eigenvector normalization, CR calculation,
and the strict CR < 0.08 scientific gate.
"""

import pytest
import numpy as np

try:
    from asd_mcda.v2.ahp import solve_ahp_preference
    from asd_mcda.v2.exceptions import AHPConsistencyViolationError, AHPNonReciprocalError
except ImportError:
    solve_ahp_preference = None
    AHPConsistencyViolationError = None
    AHPNonReciprocalError = None


def test_ahp_reciprocity_validation():
    """Test 10: Assert non-reciprocal matrix raises AHPNonReciprocalError."""
    if solve_ahp_preference is None:
        pytest.fail("Phase 1 Contract: asd_mcda.v2.ahp module not yet implemented.")

    A = np.array([
        [1.0, 2.0, 1.0, 1.0],
        [0.6, 1.0, 1.0, 1.0],  # a_21 = 0.6 != 1/2 = 0.5
        [1.0, 1.0, 1.0, 1.0],
        [1.0, 1.0, 1.0, 1.0]
    ])
    with pytest.raises(AHPNonReciprocalError):
        solve_ahp_preference(A)


def test_ahp_normalization(ahp_reciprocal_matrix):
    """Test 11: Assert principal eigenvector sums to 1.0 and matches expected weights."""
    if solve_ahp_preference is None:
        pytest.fail("Phase 1 Contract: asd_mcda.v2.ahp module not yet implemented.")

    A = ahp_reciprocal_matrix["matrix"]
    w_phys, cr = solve_ahp_preference(A)

    assert np.isclose(np.sum(w_phys), 1.0, atol=1e-12)
    assert np.all(w_phys > 0.0)
    assert np.allclose(w_phys, ahp_reciprocal_matrix["expected_weights"], atol=1e-3)
    assert np.isclose(cr, ahp_reciprocal_matrix["expected_cr"], atol=1e-3)


def test_ahp_cr_gate_blocking(ahp_inconsistent_matrix):
    """Test 12: Assert matrix with CR >= 0.08 raises AHPConsistencyViolationError."""
    if solve_ahp_preference is None:
        pytest.fail("Phase 1 Contract: asd_mcda.v2.ahp module not yet implemented.")

    A = ahp_inconsistent_matrix["matrix"]
    with pytest.raises(AHPConsistencyViolationError):
        solve_ahp_preference(A)


def test_ahp_reciprocity_boundary_conditions():
    """Phase 2.1 Boundary Test: Assert reciprocity error = 5e-13 is accepted and 2e-12 raises AHPNonReciprocalError."""
    if solve_ahp_preference is None:
        pytest.fail("Phase 1 Contract: asd_mcda.v2.ahp module not yet implemented.")

    # Controlled base matrix (identity comparisons) where only reciprocity is varied
    # 1. Reciprocity error = 5e-13 (< 1e-12) -> ACCEPTED
    A_accept = np.ones((4, 4), dtype=np.float64)
    A_accept[0, 1] = 1.0 + 5e-13
    A_accept[1, 0] = 1.0
    w_phys, cr = solve_ahp_preference(A_accept)
    assert np.isclose(np.sum(w_phys), 1.0, atol=1e-12)
    assert cr < 0.08

    # 2. Reciprocity error = 2e-12 (>= 1e-12) -> BLOCKED with AHPNonReciprocalError
    A_reject = np.ones((4, 4), dtype=np.float64)
    A_reject[0, 1] = 1.0 + 2e-12
    A_reject[1, 0] = 1.0
    with pytest.raises(AHPNonReciprocalError):
        solve_ahp_preference(A_reject)

