"""Acceptance and Unit Tests for Monte Carlo Uncertainty Propagation (Phase 5).

Authoritative Specification: 2.0.0-SPEC-PHASE5.2-FINAL.
Covers Mandatory Acceptance Tests:
- test_score_sd_is_pretruncation_parameter (Test 2)
- test_mc_dynamic_k_is_recomputed_per_replicate (Test 6)
- test_mc_dynamic_k_switching_capability (Test 7)
Along with comprehensive unit tests for:
- Replicate conservation (N_generated == N_valid + N_blocked)
- Zero-valid policy (UNEVALUABLE_ALL_BLOCKED)
- Exact analytical AHP reciprocity (|a_ji * a_ij - 1| < 1e-12)
- Conditioned C_L | (K=k) vs. descriptive pooled C_L label
- Provenance determinism and two-pass non-circular manifest hashing
"""

import pytest
import numpy as np

from asd_mcda.v2.engine import VariableKEngine
from asd_mcda.v2.phase5_models import (
    CANONICAL_BLOCK_REASONS,
    DESCRIPTIVE_CLOSENESS_LABEL,
)
from asd_mcda.v2.uncertainty import (
    run_monte_carlo,
    _sample_truncated_normal_scores,
    _perturb_ahp_matrix_log_space,
)


def test_score_sd_is_pretruncation_parameter():
    """Acceptance Test 2: Verify score_uncertainty_sd controls latent pre-truncation kernel.

    Pass Conditions:
    - All N samples satisfy 0.0 <= s_ij <= 1.0.
    - Empirical variance near boundary s approx 0.95 is strictly smaller than sigma^2 = 0.05^2.
    - Scale is confirmed absolute, not relative.
    """
    rng = np.random.default_rng(42)
    # Baseline near upper boundary: s = 0.95
    base_scores = np.array([[0.95, 0.95, 0.95, 0.95], [0.10, 0.10, 0.10, 0.10]])
    sigma_score = 0.05
    n_samples = 5000

    sampled = _sample_truncated_normal_scores(
        base_scores=base_scores,
        sigma_score=sigma_score,
        num_replicates=n_samples,
        rng=rng,
    )

    # 1. Exact physical support [0.0, 1.0]
    assert np.all(sampled >= 0.0)
    assert np.all(sampled <= 1.0)

    # 2. Empirical variance near boundary s=0.95 is strictly smaller than latent sigma^2 = 0.05^2 = 0.0025
    boundary_samples = sampled[:, 0, :]  # candidate with s=0.95
    emp_var = np.var(boundary_samples, axis=0)
    latent_var = sigma_score ** 2
    for j in range(4):
        assert emp_var[j] < latent_var, (
            f"Expected realized variance near boundary {emp_var[j]:.6f} < latent variance {latent_var:.6f}"
        )

    # 3. Absolute scale confirmation: for small score s=0.10, spread is governed by 0.05, NOT relative 5% of 0.10 (0.005)
    small_samples = sampled[:, 1, :]
    small_emp_std = np.std(small_samples, axis=0)
    for j in range(4):
        # Latent SD is 0.05; relative SD would be 0.10 * 0.05 = 0.005
        assert small_emp_std[j] > 0.03, (
            f"Realized SD {small_emp_std[j]:.6f} indicates relative scale error instead of absolute 0.05"
        )


def test_mc_dynamic_k_is_recomputed_per_replicate(indomethacin_reference_cohort, ahp_reciprocal_matrix):
    """Acceptance Test 6: Verify each MC replicate independently recomputes moments, PCA, and K.

    Pass Conditions:
    - For every replicate m, population moments match mean(S^(m)).
    - V_K^(m) diagonalizes R^(m).
    - K^(m) satisfies the >= 95% cumulative variance rule.
    - Zero lazy reuse of baseline moments or baseline projection matrix.
    """
    scores_base = indomethacin_reference_cohort["scores"]
    ahp_base = ahp_reciprocal_matrix["matrix"]

    rng = np.random.default_rng(101)
    engine = VariableKEngine()

    n_reps = 15
    sampled_scores = _sample_truncated_normal_scores(scores_base, sigma_score=0.05, num_replicates=n_reps, rng=rng)

    previous_means = []
    previous_v_k = []

    for m in range(n_reps):
        s_m = sampled_scores[m]

        snapshot = engine.evaluate(s_m, ahp_base)

        # 1. Population moments match mean(S^(m))
        expected_mu = np.mean(s_m, axis=0)
        assert np.allclose(snapshot.standardization.cohort_mean, expected_mu, atol=1e-12)

        # 2. V_K diagonalizes R^(m)
        expected_sigma = np.sqrt(np.mean((s_m - expected_mu)**2, axis=0))
        Z_m = (s_m - expected_mu) / expected_sigma
        R_m = (Z_m.T @ Z_m) / len(s_m)
        V_m = snapshot.pca.eigenvectors
        reconstructed_R = V_m @ np.diag(snapshot.pca.eigenvalues) @ V_m.T
        assert np.allclose(R_m, reconstructed_R, atol=1e-10)

        # 3. Cumulative variance rule
        assert snapshot.pca.cumulative_variance >= 0.95

        # 4. Independent recomputation across replicates: means and projection bases must differ
        current_mu = snapshot.standardization.cohort_mean
        current_vk = snapshot.pca.retained_basis
        for prev_mu in previous_means:
            assert not np.allclose(current_mu, prev_mu, atol=1e-5), "Lazy moment reuse detected across replicates!"
        for prev_vk in previous_v_k:
            if prev_vk.shape == current_vk.shape:
                assert not np.allclose(current_vk, prev_vk, atol=1e-5), "Lazy PCA basis reuse detected across replicates!"

        previous_means.append(current_mu)
        previous_v_k.append(current_vk)


def test_mc_dynamic_k_switching_capability():
    """Acceptance Test 7: Verify dynamic K switching capability on a controlled K=2 / K=3 boundary fixture.

    Pass Conditions:
    - On a controlled synthetic fixture with boundary cumulative variance near 95% at K=2,
      valid replicates produce non-zero frequencies for both K=2 and K=3.
    - Demonstrates genuine crossing of the 95% retention threshold under stochastic score perturbations.
    """
    # 6 candidates x 4 criteria with 3 controlled signals yielding ~95% cumulative variance at K=2
    scores = np.array([
        [0.646629, 0.637264, 0.349953, 0.373029],
        [0.668131, 0.680296, 0.605095, 0.568012],
        [0.509288, 0.502968, 0.421210, 0.552949],
        [0.410559, 0.399094, 0.383667, 0.351757],
        [0.405343, 0.409480, 0.573768, 0.456760],
        [0.360050, 0.370898, 0.666307, 0.697493],
    ], dtype=np.float64)

    ahp = np.array([
        [1.0, 1.2, 1.5, 2.0],
        [1/1.2, 1.0, 1.2, 1.5],
        [1/1.5, 1/1.2, 1.0, 1.2],
        [0.5, 1/1.5, 1/1.2, 1.0],
    ])

    res = run_monte_carlo(
        baseline_scores=scores,
        baseline_ahp_matrix=ahp,
        num_replicates=200,
        random_seed=42,
    )

    assert res.simulation_state == "EVALUATED"
    # Verify non-zero counts for BOTH K=2 and K=3 as strictly required by Phase 5.2 acceptance contract
    freq_k2 = res.k_distribution.get(2, 0.0)
    freq_k3 = res.k_distribution.get(3, 0.0)

    assert freq_k2 > 0.0, f"Expected non-zero frequency for K=2, got {freq_k2}"
    assert freq_k3 > 0.0, f"Expected non-zero frequency for K=3, got {freq_k3}"
    # Verify exact boundary behavior: K=2 and K=3 account for 100% of valid replicates
    assert np.isclose(freq_k2 + freq_k3, 1.0, atol=1e-5), (
        f"Expected K=2 ({freq_k2}) and K=3 ({freq_k3}) to span the distribution, got {res.k_distribution}"
    )


def test_mc_replicate_conservation_identity(indomethacin_reference_cohort, ahp_reciprocal_matrix):
    """Verify strict replicate accounting conservation: N_generated == N_valid + N_blocked."""
    scores = indomethacin_reference_cohort["scores"]
    ahp = ahp_reciprocal_matrix["matrix"]

    n_gen = 60
    res = run_monte_carlo(
        baseline_scores=scores,
        baseline_ahp_matrix=ahp,
        num_replicates=n_gen,
        random_seed=77,
    )

    assert res.num_generated == n_gen
    assert res.num_generated == res.num_valid + res.num_blocked
    assert res.num_blocked == sum(res.block_reasons_histogram.values())
    for reason in CANONICAL_BLOCK_REASONS:
        assert reason in res.block_reasons_histogram


def test_mc_zero_valid_policy_unevaluable(ahp_reciprocal_matrix):
    """Verify that when N_valid == 0, simulation state is UNEVALUABLE_ALL_BLOCKED with empty rankings."""
    # Cohort with 0 variance on criterion 0 triggers ZERO_VARIANCE block on every replicate
    scores = np.array([
        [0.5, 0.2, 0.3, 0.4],
        [0.5, 0.8, 0.1, 0.9],
        [0.5, 0.4, 0.6, 0.2],
    ])
    ahp = ahp_reciprocal_matrix["matrix"]

    res = run_monte_carlo(
        baseline_scores=scores,
        baseline_ahp_matrix=ahp,
        score_uncertainty_sd=0.0,  # zero noise: exact constant column preserved
        num_replicates=10,
        random_seed=42,
    )

    assert res.simulation_state == "UNEVALUABLE_ALL_BLOCKED"
    assert res.num_valid == 0
    assert res.num_blocked == 10
    assert res.block_reasons_histogram["ZERO_VARIANCE"] == 10
    assert len(res.candidate_records) == 0
    assert len(res.k_distribution) == 0


def test_mc_ahp_exact_reciprocity():
    """Verify that log-space AHP perturbation guarantees exact reciprocity (|a_ji * a_ij - 1| < 1e-12)."""
    base_ahp = np.array([
        [1.0, 2.0, 3.0, 4.0],
        [0.5, 1.0, 2.0, 3.0],
        [1/3, 0.5, 1.0, 2.0],
        [0.25, 1/3, 0.5, 1.0]
    ])
    rng = np.random.default_rng(12345)
    perturbed = _perturb_ahp_matrix_log_space(base_ahp, sigma_ahp=0.15, num_replicates=50, rng=rng)

    for m in range(50):
        mat = perturbed[m]
        # Diagonal exactly 1.0
        for i in range(4):
            assert mat[i, i] == 1.0
        # Reciprocal condition
        for i in range(4):
            for j in range(i + 1, 4):
                error = abs(mat[j, i] * mat[i, j] - 1.0)
                assert error < 1e-12, f"Reciprocity violated at replicate {m}, pair ({i}, {j}): error {error}"


def test_mc_conditional_vs_pooled_closeness_label(indomethacin_reference_cohort, ahp_reciprocal_matrix):
    """Verify that conditional C_L is reported by K and pooled C_L has mandatory descriptive label."""
    scores = indomethacin_reference_cohort["scores"]
    ahp = ahp_reciprocal_matrix["matrix"]

    res = run_monte_carlo(
        baseline_scores=scores,
        baseline_ahp_matrix=ahp,
        num_replicates=30,
        random_seed=42,
    )

    assert res.simulation_state == "EVALUATED"
    for rec in res.candidate_records:
        # Check conditional closeness structure
        for k_val, cond_stats in rec.conditional_closeness.items():
            assert "median" in cond_stats
            assert "iqr" in cond_stats
            assert "mean" in cond_stats
            assert "std" in cond_stats
            assert "count" in cond_stats
        # Check descriptive pooled label
        assert rec.descriptive_closeness["label"] == DESCRIPTIVE_CLOSENESS_LABEL


def test_mc_provenance_determinism_and_non_circular_hash(indomethacin_reference_cohort, ahp_reciprocal_matrix):
    """Verify that Monte Carlo results have deterministic non-circular provenance manifest hashes."""
    scores = indomethacin_reference_cohort["scores"]
    ahp = ahp_reciprocal_matrix["matrix"]

    res1 = run_monte_carlo(scores, ahp, num_replicates=25, random_seed=999)
    res2 = run_monte_carlo(scores, ahp, num_replicates=25, random_seed=999)

    # Determinism across identical runs
    assert res1.provenance_hashes["full_manifest_sha256"] == res2.provenance_hashes["full_manifest_sha256"]
    assert res1.provenance_hashes["baseline_scores_sha256"] == res2.provenance_hashes["baseline_scores_sha256"]
    assert res1.provenance_hashes["baseline_ahp_matrix_sha256"] == res2.provenance_hashes["baseline_ahp_matrix_sha256"]
    assert res1.provenance_hashes["candidate_summary_sha256"] == res2.provenance_hashes["candidate_summary_sha256"]
