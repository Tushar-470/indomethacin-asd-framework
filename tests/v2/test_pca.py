"""Unit Tests for Ordinary PCA and Dimension Selection (Step 2).

Authoritative Specification: 2.0.0-SPEC-PHASE0-PATCH2.
Tests eigenvalue ordering (non-strict inequality), cumulative variance >= 95%
K selection, and deterministic eigenvector sign canonicalization.
"""

import pytest
import numpy as np

try:
    from asd_mcda.v2.pca import decompose_spectral, canonicalize_eigenvector_sign
except ImportError:
    decompose_spectral = None
    canonicalize_eigenvector_sign = None


def test_pca_eigenvalue_ordering_and_multiplicity(repeated_eigenvalues_cohort):
    """Test 4: Assert eigenvalues are ordered descending lambda_1 >= lambda_2 >= ... >= 0."""
    if decompose_spectral is None:
        pytest.fail("Phase 1 Contract: asd_mcda.v2.pca module not yet implemented.")

    S = repeated_eigenvalues_cohort["scores"]
    Z = (S - np.mean(S, axis=0)) / np.std(S, axis=0, ddof=0)

    eigenvalues, V, K, cum_var = decompose_spectral(Z)

    # Non-strict monotonic descent
    for i in range(len(eigenvalues) - 1):
        assert eigenvalues[i] >= eigenvalues[i + 1] - 1e-12
    assert eigenvalues[-1] >= -1e-12


def test_cumulative_variance_k_selection(k1_synthetic_cohort, k2_synthetic_cohort, k4_synthetic_cohort):
    """Test 5: Assert dynamic K selection strictly adheres to cumulative variance >= 0.95 rule."""
    if decompose_spectral is None:
        pytest.fail("Phase 1 Contract: asd_mcda.v2.pca module not yet implemented.")

    for fixture in [k1_synthetic_cohort, k2_synthetic_cohort, k4_synthetic_cohort]:
        S = fixture["scores"]
        Z = (S - np.mean(S, axis=0)) / np.std(S, axis=0, ddof=0)
        _, _, K, cum_var = decompose_spectral(Z)
        assert K == fixture["expected_k"]
        assert cum_var >= 0.95 - 1e-12


def test_eigenvector_sign_canonicalization(sign_canonicalization_fixture):
    """Test 19: Assert deterministic sign canonicalization ensures canonicalize(v) == canonicalize(-v)."""
    if canonicalize_eigenvector_sign is None:
        pytest.fail("Phase 1 Contract: asd_mcda.v2.pca module not yet implemented.")

    v_neg = sign_canonicalization_fixture["v_neg"]
    v_pos = sign_canonicalization_fixture["v_pos"]
    v_tie = sign_canonicalization_fixture["v_tie"]

    v_canon_neg = canonicalize_eigenvector_sign(v_neg)
    v_canon_pos = canonicalize_eigenvector_sign(v_pos)

    # Invariance across opposite signs
    assert np.allclose(v_canon_neg, v_canon_pos, atol=1e-14)
    # Dominant element (index 1, magnitude 0.8) must be positive
    assert v_canon_neg[1] > 0.0

    # Tie handling: lowest index (index 0 and 2 both have magnitude 0.7)
    v_canon_tie = canonicalize_eigenvector_sign(v_tie)
    assert v_canon_tie[0] > 0.0
