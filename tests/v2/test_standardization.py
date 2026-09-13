"""Unit Tests for Cohort Standardization (Step 1).

Authoritative Specification: 2.0.0-SPEC-PHASE0-PATCH2.
Tests population standardization moments (ddof=0), zero-variance guardrails,
and physical reference point transformation.
"""

import pytest
import numpy as np

# In Phase 1, v2 engine implementation modules do not exist yet.
# Expected: ImportError until Phase 2 implementation.
try:
    from asd_mcda.v2.standardization import standardize_cohort
    from asd_mcda.v2.exceptions import ZeroVarianceStandardizationError
except ImportError:
    standardize_cohort = None
    ZeroVarianceStandardizationError = None


def test_zero_variance_raises_error(zero_variance_cohort):
    """Test 1: Assert that any criterion with sigma_j == 0 raises ZeroVarianceStandardizationError."""
    if standardize_cohort is None:
        pytest.fail("Phase 1 Contract: asd_mcda.v2.standardization module not yet implemented.")

    with pytest.raises(ZeroVarianceStandardizationError):
        standardize_cohort(zero_variance_cohort["scores"])


def test_ddof_zero_normative_standardization(k2_synthetic_cohort):
    """Test 2: Assert that standardization uses population standard deviation with ddof=0."""
    if standardize_cohort is None:
        pytest.fail("Phase 1 Contract: asd_mcda.v2.standardization module not yet implemented.")

    S = k2_synthetic_cohort["scores"]
    n = S.shape[0]
    expected_mu = np.mean(S, axis=0)
    expected_sigma = np.sqrt(np.sum((S - expected_mu) ** 2, axis=0) / n)  # ddof=0 normative

    Z, z_plus, z_minus, mu, sigma = standardize_cohort(S)

    assert np.allclose(mu, expected_mu, atol=1e-12)
    assert np.allclose(sigma, expected_sigma, atol=1e-12)
    assert np.allclose(np.mean(Z, axis=0), 0.0, atol=1e-12)
    assert np.allclose(np.std(Z, axis=0, ddof=0), 1.0, atol=1e-12)


def test_physical_anchor_standardization_math(k2_synthetic_cohort):
    """Test 3: Assert that physical anchors s+=[1,1,1,1] and s-=[0,0,0,0] are mapped via (s - mu) / sigma."""
    if standardize_cohort is None:
        pytest.fail("Phase 1 Contract: asd_mcda.v2.standardization module not yet implemented.")

    S = k2_synthetic_cohort["scores"]
    n = S.shape[0]
    mu = np.mean(S, axis=0)
    sigma = np.std(S, axis=0, ddof=0)

    expected_z_plus = (1.0 - mu) / sigma
    expected_z_minus = (0.0 - mu) / sigma

    Z, z_plus, z_minus, _, _ = standardize_cohort(S)

    assert np.allclose(z_plus, expected_z_plus, atol=1e-12)
    assert np.allclose(z_minus, expected_z_minus, atol=1e-12)
