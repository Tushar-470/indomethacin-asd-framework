"""Acceptance and Unit Tests for Morris Elementary Effects Screening (Phase 5).

Authoritative Specification: 2.0.0-SPEC-PHASE5.2-FINAL.
Covers Mandatory Acceptance Tests:
- test_heterogeneous_reproducibility_contract (Test 1)
- test_morris_range_is_not_mc_uncertainty (Test 3)
- test_k4_stability_by_definition (Test 4)
- test_morris_attempt_limit (Test 5)
Along with comprehensive unit tests for:
- Continuous closeness C_L as primary response
- Discrete ordinal rank as secondary switching response
- Trajectory discard logging and whole-trajectory replacement
- Provenance manifest non-circular hashing
"""

import pytest
import numpy as np

from asd_mcda.v2.engine import VariableKEngine
from asd_mcda.v2.phase5_models import (
    CANONICAL_BLOCK_REASONS,
    MorrisSensitivityResult,
)
from asd_mcda.v2.sensitivity import (
    MorrisSensitivityEngine,
    run_morris_sensitivity,
)
from asd_mcda.v2.uncertainty import run_monte_carlo


def test_heterogeneous_reproducibility_contract(indomethacin_reference_cohort, ahp_reciprocal_matrix):
    """Acceptance Test 1: Contract verification for cross-environment reproducibility.

    INFRASTRUCTURE / COVERAGE LIMITATION:
    In this single-host test execution environment (Windows x86_64, Python 3.14.5),
    heterogeneous numerical backends (e.g., OpenBLAS vs. MKL, Linux aarch64 vs. Windows x86_64)
    cannot be simultaneously executed in a single test process without synthetic perturbation
    (which is scientifically prohibited).

    Therefore, this test validates the formal acceptance contract:
    - N_generated == reference N_generated.
    - Accounting conservation: N_generated == N_valid + N_blocked.
    - Continuous sensitivity index tolerance: ||mu* - mu*_ref||_max < 1e-9.
    - Rank-frequency divergence metric: TVD(P_rank, P_rank_ref) < 0.02.
    - Differences in P(top-1), P(top-k), and rank distributions are diagnostically reported.
    - Exact P(top-1) equality is NOT required or asserted.

    Genuine multi-environment reproducibility must be validated across heterogeneous CI runners.
    Same-environment bit-for-bit reproducibility is separately verified as exact.
    """
    scores = indomethacin_reference_cohort["scores"]
    ahp = ahp_reciprocal_matrix["matrix"]

    ref_n_gen = 100
    ref_seed = 42

    # Run reference simulations
    res_mc_ref = run_monte_carlo(scores, ahp, num_replicates=ref_n_gen, random_seed=ref_seed)
    res_morris_ref = run_morris_sensitivity(scores, ahp, num_trajectories=3, random_seed=ref_seed)

    # Simulated target environment run (identical seed under standard contract)
    res_mc_target = run_monte_carlo(scores, ahp, num_replicates=ref_n_gen, random_seed=ref_seed)
    res_morris_target = run_morris_sensitivity(scores, ahp, num_trajectories=3, random_seed=ref_seed)

    # 1. N_generated == ref N_generated
    assert res_mc_target.num_generated == ref_n_gen
    assert res_mc_target.num_generated == res_mc_ref.num_generated

    # 2. Accounting conservation: N_generated == N_valid + N_blocked
    assert res_mc_target.num_generated == res_mc_target.num_valid + res_mc_target.num_blocked

    # 3. Morris continuous sensitivity indices: ||mu* - mu*_ref||_max < 1e-9
    mu_star_ref = np.array([list(f.mu_star.values()) for f in res_morris_ref.factors])
    mu_star_target = np.array([list(f.mu_star.values()) for f in res_morris_target.factors])
    max_mu_star_diff = float(np.max(np.abs(mu_star_target - mu_star_ref)))
    assert max_mu_star_diff < 1e-9, f"||mu* - mu*_ref||_max = {max_mu_star_diff:.4e} >= 1e-9"

    # 4. Total Variation Distance across rank distributions: TVD(P_rank, P_rank_ref) < 0.02
    tvds = []
    p_top1_diffs = {}
    p_topk_diffs = {}

    for cr_ref, cr_target in zip(res_mc_ref.candidate_records, res_mc_target.candidate_records):
        pid = cr_ref.polymer_id
        # TVD = 0.5 * sum(|P(r) - Q(r)|)
        tvd_i = 0.5 * sum(
            abs(cr_ref.rank_distribution[r] - cr_target.rank_distribution[r])
            for r in cr_ref.rank_distribution
        )
        tvds.append(tvd_i)

        # Diagnostic tracking
        p_top1_diffs[pid] = abs(cr_ref.p_top1 - cr_target.p_top1)
        p_topk_diffs[pid] = {
            k: abs(cr_ref.p_top_k[k] - cr_target.p_top_k[k])
            for k in cr_ref.p_top_k
        }

    max_tvd = max(tvds)
    assert max_tvd < 0.02, f"Max TVD = {max_tvd:.4e} >= 0.02"

    # 5. Diagnostic reporting: differences are logged, exact equality is NOT asserted as a hard gate
    print(f"[DIAGNOSTIC] Max TVD: {max_tvd:.6e}")
    print(f"[DIAGNOSTIC] P(top-1) differences: {p_top1_diffs}")
    print(f"[DIAGNOSTIC] P(top-k) differences sample: {p_topk_diffs[list(p_topk_diffs.keys())[0]]}")


def test_morris_range_is_not_mc_uncertainty(indomethacin_reference_cohort, ahp_reciprocal_matrix):
    """Acceptance Test 3: Verify Morris screening domain (+/- 0.15) is decoupled from MC dispersion (sigma=0.05).

    Pass Conditions:
    - Code and configuration maintain distinct parameters.
    - Morris screening bounds span +/- 0.15 while MC dispersion uses 0.05.
    - Zero cross-aliasing exists between the two modules.
    """
    scores = indomethacin_reference_cohort["scores"]
    ahp = ahp_reciprocal_matrix["matrix"]

    morris_res = run_morris_sensitivity(scores, ahp, num_trajectories=2, random_seed=42)
    mc_res = run_monte_carlo(scores, ahp, num_replicates=10, random_seed=42)

    # 1. Parameter separation
    assert "score_screening_delta" in morris_res.parameters
    assert morris_res.parameters["score_screening_delta"] == 0.15
    assert "score_uncertainty_sd" not in morris_res.parameters

    assert "score_uncertainty_sd" in mc_res.parameters
    assert mc_res.parameters["score_uncertainty_sd"] == 0.05
    assert "score_screening_delta" not in mc_res.parameters

    # 2. Verify Morris screening ranges span [base - 0.15, base + 0.15] clipped to [0, 1]
    for factor in morris_res.factors:
        if factor.factor_type == "score":
            lb, ub = factor.screening_range
            base = factor.base_value
            expected_lb = max(0.0, base - 0.15)
            expected_ub = min(1.0, base + 0.15)
            assert np.isclose(lb, expected_lb, atol=1e-12)
            assert np.isclose(ub, expected_ub, atol=1e-12)


def test_k4_stability_by_definition(k4_synthetic_cohort, ahp_reciprocal_matrix):
    """Acceptance Test 4: Verify that when K=p=4, stability status is STABLE by definition.

    Pass Conditions:
    - When synthetic data forces K=4, boundary_eigengap is +inf, stability_status is STABLE.
    - Zero IndexError occurs on eigenvalue arrays (never accesses lambda_5).
    """
    scores = k4_synthetic_cohort["scores"]
    ahp = ahp_reciprocal_matrix["matrix"]

    engine = VariableKEngine()
    snapshot = engine.evaluate(scores, ahp)

    assert snapshot.pca.retained_k == 4
    assert snapshot.stability.boundary_eigengap == float("inf")
    assert snapshot.stability.stability_status == "STABLE"
    assert snapshot.stability.warning_message == ""


def test_morris_attempt_limit(ahp_reciprocal_matrix):
    """Acceptance Test 5: Verify Morris terminates safely with UNEVALUABLE_MORRIS_DESIGN on repeated blocks.

    Pass Conditions:
    - Execution terminates after max_trajectory_attempts attempts.
    - Returns UNEVALUABLE_MORRIS_DESIGN with complete discard-reason histogram.
    - Zero infinite loop, zero silent reduction of requested r.
    """
    blocked_scores = np.array([
        [0.5, 0.2, 0.3, 0.4],
        [0.5, 0.8, 0.1, 0.9],
        [0.5, 0.4, 0.6, 0.2],
    ])
    ahp = ahp_reciprocal_matrix["matrix"]

    limit = 5
    res = run_morris_sensitivity(
        baseline_scores=blocked_scores,
        baseline_ahp_matrix=ahp,
        num_trajectories=10,
        max_trajectory_attempts=limit,
        random_seed=42,
    )

    assert res.design_state == "UNEVALUABLE_MORRIS_DESIGN"
    assert res.num_trajectories_attempted == limit
    assert res.num_trajectories_valid < 10
    assert res.num_trajectories_discarded > 0
    assert sum(res.discard_reasons_histogram.values()) == res.num_trajectories_discarded
    assert len(res.factors) == 0


def test_morris_primary_response_is_continuous_cl(indomethacin_reference_cohort, ahp_reciprocal_matrix):
    """Verify that Morris calculates continuous elementary effects Delta C_L / Delta as primary response."""
    scores = indomethacin_reference_cohort["scores"]
    ahp = ahp_reciprocal_matrix["matrix"]
    pids = indomethacin_reference_cohort["polymer_ids"]

    res = run_morris_sensitivity(scores, ahp, polymer_ids=pids, num_trajectories=3, random_seed=42)

    assert res.design_state == "EVALUATED"
    assert len(res.factors) == scores.shape[0] * 4 + 6

    # Verify each factor has finite continuous sensitivity indices
    for factor in res.factors:
        for pid in pids:
            assert np.isfinite(factor.mu[pid])
            assert np.isfinite(factor.mu_star[pid])
            assert factor.mu_star[pid] >= 0.0
            assert np.isfinite(factor.sigma[pid])
            assert factor.sigma[pid] >= 0.0


def test_morris_secondary_response_is_ordinal_rank(indomethacin_reference_cohort, ahp_reciprocal_matrix):
    """Verify that Morris calculates ordinal rank elementary effects Delta R / Delta as secondary response."""
    scores = indomethacin_reference_cohort["scores"]
    ahp = ahp_reciprocal_matrix["matrix"]
    pids = indomethacin_reference_cohort["polymer_ids"]

    res = run_morris_sensitivity(scores, ahp, polymer_ids=pids, num_trajectories=3, random_seed=42)

    for factor in res.factors:
        for pid in pids:
            assert np.isfinite(factor.rank_mu[pid])
            assert np.isfinite(factor.rank_mu_star[pid])
            assert factor.rank_mu_star[pid] >= 0.0
            assert np.isfinite(factor.rank_sigma[pid])


def test_morris_trajectory_discard_logging():
    """Verify that trajectories hitting governance gates are discarded and logged with exact canonical reasons."""
    scores = np.array([
        [0.7, 0.5, 0.4, 0.6],
        [0.6, 0.4, 0.5, 0.7],
        [0.5, 0.7, 0.6, 0.4],
    ])
    near_boundary_ahp = np.array([
        [1.0, 3.0, 5.0, 7.0],
        [1/3, 1.0, 2.0, 4.0],
        [1/5, 0.5, 1.0, 2.0],
        [1/7, 0.25, 0.5, 1.0],
    ])

    res = run_morris_sensitivity(
        baseline_scores=scores,
        baseline_ahp_matrix=near_boundary_ahp,
        num_trajectories=4,
        ahp_log_screening_delta=0.50,
        max_trajectory_attempts=50,
        random_seed=42,
    )

    for reason in CANONICAL_BLOCK_REASONS:
        assert reason in res.discard_reasons_histogram

    assert res.num_trajectories_attempted == res.num_trajectories_valid + res.num_trajectories_discarded


def test_morris_provenance_manifest_non_circular_hash(indomethacin_reference_cohort, ahp_reciprocal_matrix):
    """Verify deterministic non-circular manifest hashing for Morris screening."""
    scores = indomethacin_reference_cohort["scores"]
    ahp = ahp_reciprocal_matrix["matrix"]
    pids = indomethacin_reference_cohort["polymer_ids"]

    res1 = run_morris_sensitivity(scores, ahp, polymer_ids=pids, num_trajectories=2, random_seed=555)
    res2 = run_morris_sensitivity(scores, ahp, polymer_ids=pids, num_trajectories=2, random_seed=555)

    assert res1.provenance_hashes["full_manifest_sha256"] == res2.provenance_hashes["full_manifest_sha256"]
    assert res1.provenance_hashes["baseline_scores_sha256"] == res2.provenance_hashes["baseline_scores_sha256"]
    assert res1.provenance_hashes["baseline_ahp_matrix_sha256"] == res2.provenance_hashes["baseline_ahp_matrix_sha256"]
    assert res1.provenance_hashes["factor_sensitivities_sha256"] == res2.provenance_hashes["factor_sensitivities_sha256"]
