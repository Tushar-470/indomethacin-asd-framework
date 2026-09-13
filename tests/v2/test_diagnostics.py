"""Unit Tests for Truncation Diagnostics (Step 9).

Authoritative Specification: 2.0.0-SPEC-PHASE0-PATCH2.
Tests the exact signed truncation discrepancy identity Delta D^2 = D_full^2 - D_K^2,
absolute relative discrepancy E_i, and proves that signed discrepancies (< 0) are
mathematically valid because W and P_K do not commute.
"""

import pytest
import numpy as np

try:
    from asd_mcda.v2.diagnostics import audit_truncation_discrepancy
except ImportError:
    audit_truncation_discrepancy = None


def test_truncation_discrepancy_identity(k2_synthetic_cohort, ahp_reciprocal_matrix):
    """Test 16: Assert Delta D^2 == D_full_sq - D_K_sq == (z-z+)^T (W - P_K W P_K) (z-z+) within 1e-12."""
    if audit_truncation_discrepancy is None:
        pytest.fail("Phase 1 Contract: asd_mcda.v2.diagnostics module not yet implemented.")

    S = k2_synthetic_cohort["scores"]
    Z = (S - np.mean(S, axis=0)) / np.std(S, axis=0, ddof=0)
    z_plus = (1.0 - np.mean(S, axis=0)) / np.std(S, axis=0, ddof=0)
    w = ahp_reciprocal_matrix["expected_weights"]
    W = np.diag(w)

    V_K = np.linalg.qr(np.random.randn(4, 2))[0]
    P_K = V_K @ V_K.T

    records = audit_truncation_discrepancy(
        Z, z_plus, W, V_K, k2_synthetic_cohort["polymer_ids"]
    )

    for i, rec in enumerate(records):
        delta_z = Z[i] - z_plus
        expected_full = delta_z @ W @ delta_z
        expected_k = delta_z @ P_K @ W @ P_K @ delta_z
        expected_diff = delta_z @ (W - P_K @ W @ P_K) @ delta_z

        assert np.isclose(rec.d_full_sq, expected_full, atol=1e-12)
        assert np.isclose(rec.d_k_sq, expected_k, atol=1e-12)
        assert np.isclose(rec.signed_discrepancy, expected_diff, atol=1e-12)
        assert np.isclose(rec.relative_discrepancy, abs(expected_diff) / expected_full, atol=1e-12)


def test_signed_truncation_discrepancy_allowed():
    """Test: Prove that signed truncation discrepancy (Delta D^2 < 0) is valid when W and P_K do not commute."""
    if audit_truncation_discrepancy is None:
        pytest.fail("Phase 1 Contract: asd_mcda.v2.diagnostics module not yet implemented.")

    # Unequal preference weights
    W = np.diag([0.80, 0.10, 0.05, 0.05])
    # 2D projection basis oblique to the weight axes
    np.random.seed(42)
    V_K = np.linalg.qr(np.random.randn(4, 2))[0]
    P_K = V_K @ V_K.T

    # Operator W - P_K W P_K is indefinite when W and P_K do not commute
    diff_op = W - P_K @ W @ P_K
    eigvals, eigvecs = np.linalg.eigh(diff_op)

    # Pick the eigenvector with the negative eigenvalue
    neg_idx = np.argmin(eigvals)
    assert eigvals[neg_idx] < -1e-4, "Expected negative eigenvalue in W - P_K W P_K"

    delta_z = eigvecs[:, neg_idx]
    z_ref = np.zeros(4)
    Z_test = np.array([delta_z])

    records = audit_truncation_discrepancy(Z_test, z_ref, W, V_K, ["POL-NEG-001"])
    rec = records[0]

    # Signed discrepancy must be strictly negative
    assert rec.signed_discrepancy < -1e-4
    # Relative discrepancy is strictly positive |Delta D^2| / D_full^2
    assert rec.relative_discrepancy > 0.0
