"""Unit Tests for Subspace Stability Evaluator (Step 3).

Authoritative Specification: 2.0.0-SPEC-PHASE0-PATCH2.
Tests boundary eigengap delta_K = lambda_K - lambda_{K+1}, unconditional K=p
stability, and threshold classification (STABLE, WARNING, BLOCKED).
"""

import pytest
import numpy as np

try:
    from asd_mcda.v2.stability import evaluate_subspace_stability
    from asd_mcda.v2.exceptions import DegenerateSubspaceBlockedError
except ImportError:
    evaluate_subspace_stability = None
    DegenerateSubspaceBlockedError = None


def test_k_equals_p_unconditional_stability():
    """Test 6: Assert that when K=p, delta_K == +inf and status is unconditionally STABLE."""
    if evaluate_subspace_stability is None:
        pytest.fail("Phase 1 Contract: asd_mcda.v2.stability module not yet implemented.")

    eigenvalues = np.array([1.5, 1.1, 0.8, 0.6])
    record = evaluate_subspace_stability(eigenvalues, retained_k=4)

    assert record.boundary_eigengap == float("inf")
    assert record.stability_status == "STABLE"


def test_boundary_eigengap_guardrail_blocking(near_degenerate_eigengap_cohort):
    """Test 7: Assert that delta_K < 0.03 raises DegenerateSubspaceBlockedError."""
    if evaluate_subspace_stability is None:
        pytest.fail("Phase 1 Contract: asd_mcda.v2.stability module not yet implemented.")

    eigs = near_degenerate_eigengap_cohort["eigenvalues"]
    k = near_degenerate_eigengap_cohort["retained_k"]

    with pytest.raises(DegenerateSubspaceBlockedError):
        evaluate_subspace_stability(eigs, retained_k=k)


def test_boundary_eigengap_warning():
    """Test 8: Assert that 0.03 <= delta_K < 0.10 produces WARNING status."""
    if evaluate_subspace_stability is None:
        pytest.fail("Phase 1 Contract: asd_mcda.v2.stability module not yet implemented.")

    # K=2, lambda_2 = 1.00, lambda_3 = 0.94 -> delta_2 = 0.06
    eigenvalues = np.array([2.0, 1.00, 0.94, 0.06])
    record = evaluate_subspace_stability(eigenvalues, retained_k=2)

    assert record.stability_status == "WARNING"
    assert record.boundary_eigengap == pytest.approx(0.06, abs=1e-12)
    assert len(record.warning_message) > 0


def test_boundary_eigengap_stable(stable_eigengap_cohort):
    """Test 9: Assert that delta_K >= 0.10 produces STABLE status."""
    if evaluate_subspace_stability is None:
        pytest.fail("Phase 1 Contract: asd_mcda.v2.stability module not yet implemented.")

    eigs = stable_eigengap_cohort["eigenvalues"]
    k = stable_eigengap_cohort["retained_k"]

    record = evaluate_subspace_stability(eigs, retained_k=k)
    assert record.stability_status == "STABLE"
    assert record.boundary_eigengap == pytest.approx(stable_eigengap_cohort["expected_delta"], abs=1e-12)
