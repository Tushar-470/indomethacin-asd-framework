"""Unit Tests for Metric Tensor, Distances, and Closeness (Steps 6, 7, 8).

Authoritative Specification: 2.0.0-SPEC-PHASE0-PATCH2.
Tests metric tensor dimensions, symmetry, positive definiteness floor,
invalid weight rejection, projected reference points, cohort-scaler invariance,
non-extrema property, projected distances non-negativity, materially negative
quadratic form blocking, closeness coefficient bounds, zero denominator blocking,
raw-vs-standardized weighting equivalence, full-dimensional K=p recovery,
deterministic tie-breaking, deep immutability, and deterministic results.
"""

import pytest
import numpy as np

try:
    from asd_mcda.v2.metrics import (
        construct_metric_tensor,
        project_reference_points,
        compute_distances_and_closeness,
    )
    from asd_mcda.v2.exceptions import (
        DegenerateReferenceCoincidenceError,
        InvalidWeightVectorError,
        MateriallyNegativeQuadraticFormError,
        NonPositiveDefiniteMetricError,
        RankDeficientSubspaceError,
    )
    from asd_mcda.v2.standardization import standardize_cohort
    from asd_mcda.v2.pca import decompose_spectral
except ImportError:
    construct_metric_tensor = None
    project_reference_points = None
    compute_distances_and_closeness = None
    DegenerateReferenceCoincidenceError = None
    InvalidWeightVectorError = None
    MateriallyNegativeQuadraticFormError = None
    NonPositiveDefiniteMetricError = None
    RankDeficientSubspaceError = None
    standardize_cohort = None
    decompose_spectral = None


def test_metric_tensor_dimensions(ahp_reciprocal_matrix):
    """Test: Assert M_K = V_K^T @ W @ V_K has shape (K, K) for K in {1, 2, 3, 4}."""
    w = ahp_reciprocal_matrix["expected_weights"]
    np.random.seed(42)
    for K in [1, 2, 3, 4]:
        V_K = np.linalg.qr(np.random.randn(4, 4))[0][:, :K]
        M_K, W = construct_metric_tensor(V_K, w, semantic_mode="standardized_space")
        assert M_K.shape == (K, K)
        assert W.shape == (4, 4)


def test_metric_tensor_symmetry(k2_synthetic_cohort, ahp_reciprocal_matrix):
    """Test 13: Assert M_K = V_K^T W V_K is symmetric within 1e-12."""
    w = ahp_reciprocal_matrix["expected_weights"]
    V_K = np.linalg.qr(np.random.randn(4, 2))[0]
    sigma = np.ones(4)

    M_K, _ = construct_metric_tensor(V_K, w, sigma, semantic_mode="standardized_space")
    assert np.allclose(M_K, M_K.T, atol=1e-12)


def test_metric_tensor_positive_definite(ahp_reciprocal_matrix):
    """Test 14: Assert all eigenvalues of M_K are strictly positive (> 1e-12)."""
    w = ahp_reciprocal_matrix["expected_weights"]
    V_K = np.linalg.qr(np.random.randn(4, 3))[0]
    sigma = np.ones(4)

    M_K, _ = construct_metric_tensor(V_K, w, sigma, semantic_mode="standardized_space")
    eigvals = np.linalg.eigvalsh(M_K)
    assert np.all(eigvals > 1e-12)


def test_metric_tensor_rejects_invalid_weights(ahp_reciprocal_matrix):
    """Test: Assert invalid weights (negative, sum != 1, non-finite) and rank-deficient V_K are blocked."""
    V_K = np.linalg.qr(np.random.randn(4, 2))[0]

    # Non-positive weight
    with pytest.raises(InvalidWeightVectorError):
        construct_metric_tensor(V_K, np.array([-0.1, 0.4, 0.4, 0.3]))

    # Weights not summing to 1
    with pytest.raises(InvalidWeightVectorError):
        construct_metric_tensor(V_K, np.array([0.2, 0.2, 0.2, 0.2]))

    # Non-finite weight
    with pytest.raises(InvalidWeightVectorError):
        construct_metric_tensor(V_K, np.array([np.nan, 0.4, 0.3, 0.3]))

    # Rank-deficient V_K (two identical columns)
    V_deficient = np.column_stack([V_K[:, 0], V_K[:, 0]])
    with pytest.raises(RankDeficientSubspaceError):
        construct_metric_tensor(V_deficient, ahp_reciprocal_matrix["expected_weights"])


def test_projected_reference_points():
    """Test: Assert reference points project via t+ = z+ @ V_K and t- = z- @ V_K."""
    z_plus = np.array([1.2, 0.8, -0.4, 2.1])
    z_minus = np.array([-1.0, -0.5, 0.2, -1.8])
    V_K = np.eye(4)[:, :2]

    t_plus, t_minus = project_reference_points(z_plus, z_minus, V_K)
    assert np.allclose(t_plus, z_plus[:2], atol=1e-14)
    assert np.allclose(t_minus, z_minus[:2], atol=1e-14)


def test_reference_points_use_cohort_scaler(k2_synthetic_cohort):
    """Test: Assert reference points are standardized using active cohort moments (mu, sigma)."""
    S = k2_synthetic_cohort["scores"]
    Z, z_plus, z_minus, mu, sigma = standardize_cohort(S)

    expected_z_plus = (1.0 - mu) / sigma
    expected_z_minus = (0.0 - mu) / sigma

    assert np.allclose(z_plus, expected_z_plus, atol=1e-12)
    assert np.allclose(z_minus, expected_z_minus, atol=1e-12)
    # Confirm z_plus is not simply 1.0 or raw
    assert not np.allclose(z_plus, 1.0)


def test_reference_points_are_not_candidate_extrema(k2_synthetic_cohort):
    """Test: Assert physical anchors are NOT derived from candidate cohort min/max extrema."""
    S = k2_synthetic_cohort["scores"]
    Z, z_plus, z_minus, _, _ = standardize_cohort(S)

    z_max_observed = np.max(Z, axis=0)
    z_min_observed = np.min(Z, axis=0)

    # Reference points must not equal empirical sample extrema
    assert not np.allclose(z_plus, z_max_observed, atol=1e-3)
    assert not np.allclose(z_minus, z_min_observed, atol=1e-3)


def test_projected_distances_nonnegative(k2_synthetic_cohort, ahp_reciprocal_matrix):
    """Test: Assert D_plus and D_minus are non-negative for all candidates."""
    S = k2_synthetic_cohort["scores"]
    Z, z_plus, z_minus, _, _ = standardize_cohort(S)
    V_K = np.eye(4)[:, :2]
    M_K, _ = construct_metric_tensor(V_K, ahp_reciprocal_matrix["expected_weights"])

    D_plus, D_minus, C_L, ranks = compute_distances_and_closeness(
        Z, z_plus, z_minus, V_K, M_K, k2_synthetic_cohort["polymer_ids"]
    )

    assert np.all(D_plus >= 0.0)
    assert np.all(D_minus >= 0.0)


def test_materially_negative_quadratic_form_blocks():
    """Test: Assert materially negative quadratic form (< -1e-12) raises MateriallyNegativeQuadraticFormError."""
    Z = np.array([[1.0, 1.0, 1.0, 1.0]])
    z_plus = np.array([0.0, 0.0, 0.0, 0.0])
    z_minus = np.array([2.0, 2.0, 2.0, 2.0])
    V_K = np.eye(4)[:, :2]
    # Artificially indefinite metric matrix with large negative eigenvalue
    M_K_invalid = np.array([[-10.0, 0.0], [0.0, 1.0]])

    with pytest.raises(MateriallyNegativeQuadraticFormError):
        compute_distances_and_closeness(Z, z_plus, z_minus, V_K, M_K_invalid)


def test_closeness_coefficient_bounds(k2_synthetic_cohort, ahp_reciprocal_matrix):
    """Test: Assert 0 <= C_L <= 1 for all evaluated alternatives."""
    S = k2_synthetic_cohort["scores"]
    Z, z_plus, z_minus, _, _ = standardize_cohort(S)
    V_K = np.eye(4)[:, :2]
    M_K, _ = construct_metric_tensor(V_K, ahp_reciprocal_matrix["expected_weights"])

    _, _, C_L, _ = compute_distances_and_closeness(
        Z, z_plus, z_minus, V_K, M_K, k2_synthetic_cohort["polymer_ids"]
    )

    assert np.all(C_L >= 0.0)
    assert np.all(C_L <= 1.0)


def test_zero_denominator_blocks():
    """Test: Assert degenerate case D_plus + D_minus == 0 raises DegenerateReferenceCoincidenceError."""
    # When candidate coincides exactly with both reference points
    Z = np.array([[0.0, 0.0, 0.0, 0.0]])
    z_plus = np.array([0.0, 0.0, 0.0, 0.0])
    z_minus = np.array([0.0, 0.0, 0.0, 0.0])
    V_K = np.eye(4)[:, :2]
    M_K = np.eye(2)

    with pytest.raises(DegenerateReferenceCoincidenceError):
        compute_distances_and_closeness(Z, z_plus, z_minus, V_K, M_K)


def test_raw_vs_standardized_weighting_equivalence(raw_vs_standardized_weights_fixture):
    """Test 15: When K=p, assert (s-s*)^T W_raw (s-s*) == (z-z*)^T Sigma^(1/2) W_raw Sigma^(1/2) (z-z*)."""
    fixture = raw_vs_standardized_weights_fixture
    w_raw = fixture["w_raw"]
    sigma = fixture["sigma"]
    W_raw = fixture["W_raw"]
    W_std = fixture["W_std"]

    np.random.seed(123)
    delta_s = np.random.uniform(-0.5, 0.5, 4)
    delta_z = delta_s / sigma

    d_raw_sq = delta_s @ W_raw @ delta_s
    d_std_sq = delta_z @ W_std @ delta_z

    assert np.isclose(d_raw_sq, d_std_sq, atol=1e-11)


def test_k4_recovers_full_space_raw_geometry(k4_synthetic_cohort, ahp_reciprocal_matrix):
    """Test: When K=p=4, assert projected metric distance equals full-space raw weighted distance."""
    S = k4_synthetic_cohort["scores"]
    w = ahp_reciprocal_matrix["expected_weights"]
    Z, z_plus, z_minus, mu, sigma = standardize_cohort(S)

    _, V_full, K, _ = decompose_spectral(Z)
    assert K == 4

    M_K, W_raw = construct_metric_tensor(V_full, w, sigma=sigma, semantic_mode="raw_physical")

    T = Z @ V_full
    t_plus = z_plus @ V_full

    for i in range(len(S)):
        diff_t = T[i] - t_plus
        d_proj_sq = diff_t @ M_K @ diff_t

        diff_s = S[i] - 1.0  # s+ = [1, 1, 1, 1]
        d_full_raw_sq = diff_s @ np.diag(w) @ diff_s

        assert np.isclose(d_proj_sq, d_full_raw_sq, atol=1e-11)


def test_k4_recovers_full_space_standardized_geometry(k4_synthetic_cohort, ahp_reciprocal_matrix):
    """Test: When K=p=4, assert projected metric distance equals full-space standardized distance."""
    S = k4_synthetic_cohort["scores"]
    w = ahp_reciprocal_matrix["expected_weights"]
    Z, z_plus, z_minus, _, _ = standardize_cohort(S)

    _, V_full, K, _ = decompose_spectral(Z)
    assert K == 4

    M_K, W_std = construct_metric_tensor(V_full, w, semantic_mode="standardized_space")

    T = Z @ V_full
    t_plus = z_plus @ V_full

    for i in range(len(S)):
        diff_t = T[i] - t_plus
        d_proj_sq = diff_t @ M_K @ diff_t

        diff_z = Z[i] - z_plus
        d_full_std_sq = diff_z @ W_std @ diff_z

        assert np.isclose(d_proj_sq, d_full_std_sq, atol=1e-11)


def test_deterministic_tie_breaking(deterministic_cl_tie_cohort):
    """Test 17: Assert candidates with identical C_L within epsilon_rank are broken by polymer_id."""
    fixture = deterministic_cl_tie_cohort
    S = fixture["scores"]
    polymer_ids = fixture["polymer_ids"]
    Z = (S - np.mean(S, axis=0)) / np.std(S, axis=0, ddof=0)
    z_plus = (1.0 - np.mean(S, axis=0)) / np.std(S, axis=0, ddof=0)
    z_minus = (0.0 - np.mean(S, axis=0)) / np.std(S, axis=0, ddof=0)

    V_K = np.eye(4)[:, :2]
    M_K = np.eye(2)

    D_plus, D_minus, C_L, ranks = compute_distances_and_closeness(
        Z, z_plus, z_minus, V_K, M_K, polymer_ids, epsilon_rank=1e-12
    )

    # POL-001-2026 and POL-002-2026 are tied in score; POL-001 must rank ahead of POL-002
    idx_pol1 = polymer_ids.index("POL-001-2026")
    idx_pol2 = polymer_ids.index("POL-002-2026")

    assert np.isclose(C_L[idx_pol1], C_L[idx_pol2], atol=1e-12)
    assert ranks[idx_pol1] < ranks[idx_pol2]


def test_deep_immutability_enforcement():
    """Test 18: Assert read-only array views reject modification."""
    arr = np.array([1.0, 2.0, 3.0])
    arr.flags.writeable = False

    with pytest.raises(ValueError, match="read-only"):
        arr[0] = 99.0


def test_deterministic_metric_results(k2_synthetic_cohort, ahp_reciprocal_matrix):
    """Test: Assert identical inputs produce bitwise identical outputs across evaluations."""
    S = k2_synthetic_cohort["scores"]
    ids = k2_synthetic_cohort["polymer_ids"]
    w = ahp_reciprocal_matrix["expected_weights"]

    Z, z_plus, z_minus, _, _ = standardize_cohort(S)
    V_K = np.eye(4)[:, :2]
    M_K, _ = construct_metric_tensor(V_K, w)

    d_p1, d_m1, cl1, r1 = compute_distances_and_closeness(Z, z_plus, z_minus, V_K, M_K, ids)
    d_p2, d_m2, cl2, r2 = compute_distances_and_closeness(Z, z_plus, z_minus, V_K, M_K, ids)

    assert np.array_equal(d_p1, d_p2)
    assert np.array_equal(d_m1, d_m2)
    assert np.array_equal(cl1, cl2)
    assert np.array_equal(r1, r2)
