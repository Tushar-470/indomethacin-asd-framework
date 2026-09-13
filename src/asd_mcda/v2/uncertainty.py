"""Monte Carlo Uncertainty Propagation for PharmaPolySCOPE v2 (Phase 5).

Authoritative Specification: 2.0.0-SPEC-PHASE5.2-FINAL.
Enforces:
- Latent Gaussian score standard deviation sigma_score = 0.05 on [0, 1].
- Independent marginals across within-polymer criteria; zero copula.
- Log-space AHP perturbation with exact analytical reciprocity (< 1e-12).
- Fresh re-evaluation of every replicate through VariableKEngine.evaluate(...) (no cached PCA).
- Canonical 6-reason block taxonomy with strict replicate conservation (N_gen = N_valid + N_blocked).
- Zero-valid replicate policy (UNEVALUABLE_ALL_BLOCKED).
- Conditioned C_L | (K=k) as primary closeness summary; pooled C_L explicitly labeled as descriptive heuristic.
- Cryptographic provenance sealing and two-pass non-circular manifest hashing.
"""

from typing import Any, Dict, Mapping, Optional, Sequence, Tuple
import numpy as np
from scipy.stats import truncnorm

from asd_mcda.v2.engine import VariableKEngine
from asd_mcda.v2.exceptions import (
    AHPError,
    AHPConsistencyViolationError,
    AHPNonReciprocalError,
    DegenerateReferenceCoincidenceError,
    DegenerateSubspaceBlockedError,
    InvalidWeightVectorError,
    MateriallyNegativeQuadraticFormError,
    NonPositiveDefiniteMetricError,
    RankDeficientSubspaceError,
    StandardizationError,
    SubspaceStabilityError,
    ZeroVarianceStandardizationError,
)
from asd_mcda.v2.models import (
    CANONICAL_CRITERIA_ORDER,
    deep_freeze,
)
from asd_mcda.v2.phase5_models import (
    CANONICAL_BLOCK_REASONS,
    DESCRIPTIVE_CLOSENESS_LABEL,
    CandidateMCOutputRecord,
    MonteCarloSimulationResult,
)
import asd_mcda.v2.provenance as v2_prov

MC_METHODOLOGY_VERSION: str = "2.0.0-SP-PRP-TOPSIS-MC"


def _sample_truncated_normal_scores(
    base_scores: np.ndarray,
    sigma_score: float,
    num_replicates: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Sample decision scores from Truncated Normal distribution on [0.0, 1.0].

    Parameters
    ----------
    base_scores : np.ndarray
        Baseline score matrix S_base of shape (n, 4).
    sigma_score : float
        Latent pre-truncation Gaussian standard deviation.
    num_replicates : int
        Number of replicate matrices to generate.
    rng : np.random.Generator
        NumPy random generator instance (PCG64).

    Returns
    -------
    np.ndarray
        Sampled scores tensor of shape (num_replicates, n, 4).
    """
    n, p = base_scores.shape
    if sigma_score <= 0.0:
        return np.tile(base_scores, (num_replicates, 1, 1))

    a_param = (0.0 - base_scores) / sigma_score
    b_param = (1.0 - base_scores) / sigma_score
    samples = truncnorm.rvs(
        a_param,
        b_param,
        loc=base_scores,
        scale=sigma_score,
        size=(num_replicates, n, p),
        random_state=rng,
    )
    # Defensively clamp numerical float precision into exact [0.0, 1.0]
    np.clip(samples, 0.0, 1.0, out=samples)
    return samples


def _perturb_ahp_matrix_log_space(
    base_ahp: np.ndarray,
    sigma_ahp: float,
    num_replicates: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Perturb pairwise AHP comparisons in logarithmic space with exact analytical reciprocity.

    Parameters
    ----------
    base_ahp : np.ndarray
        Baseline 4x4 reciprocal comparison matrix.
    sigma_ahp : float
        Standard deviation in log-space q_ij = ln(a_ij).
    num_replicates : int
        Number of replicate matrices to generate.
    rng : np.random.Generator
        NumPy random generator instance.

    Returns
    -------
    np.ndarray
        Replicate AHP matrices of shape (num_replicates, 4, 4).
    """
    matrices = np.zeros((num_replicates, 4, 4), dtype=np.float64)
    # Set diagonal to exactly 1.0
    for i in range(4):
        matrices[:, i, i] = 1.0

    if sigma_ahp <= 0.0:
        for m in range(num_replicates):
            matrices[m] = base_ahp.copy()
        return matrices

    # Upper triangular indices for 4x4 matrix: 6 entries
    upper_pairs = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
    num_pairs = len(upper_pairs)
    q_noise = rng.normal(0.0, sigma_ahp, size=(num_replicates, num_pairs))

    for k, (i, j) in enumerate(upper_pairs):
        q_base = np.log(float(base_ahp[i, j]))
        q_sampled = q_base + q_noise[:, k]
        a_sampled = np.exp(q_sampled)
        matrices[:, i, j] = a_sampled
        matrices[:, j, i] = 1.0 / a_sampled

    return matrices


class MonteCarloEngine:
    """Outer evaluation layer for Monte Carlo uncertainty propagation around VariableKEngine."""

    def __init__(self, engine: Optional[VariableKEngine] = None) -> None:
        """Initialize the Monte Carlo simulation engine.

        Parameters
        ----------
        engine : Optional[VariableKEngine]
            Stateless deterministic decision engine. If None, instantiates a fresh engine.
        """
        self.engine = engine if engine is not None else VariableKEngine()

    def run(
        self,
        baseline_scores: np.ndarray,
        baseline_ahp_matrix: np.ndarray,
        polymer_ids: Optional[Sequence[str]] = None,
        criteria_names: Optional[Sequence[str]] = None,
        num_replicates: int = 10000,
        random_seed: Optional[int] = 42,
        score_uncertainty_sd: float = 0.05,
        ahp_log_scale_sd: float = 0.15,
        variance_threshold: float = 0.95,
        reciprocity_tolerance: float = 1e-12,
        semantic_mode: str = "standardized_space",
        simulation_id: Optional[str] = None,
    ) -> MonteCarloSimulationResult:
        """Execute Monte Carlo uncertainty propagation over scores and AHP weights.

        Parameters
        ----------
        baseline_scores : np.ndarray
            Curated baseline score matrix S_base of shape (n, 4) with entries in [0, 1].
        baseline_ahp_matrix : np.ndarray
            Curated baseline 4x4 AHP matrix.
        polymer_ids : Optional[Sequence[str]]
            Candidate polymer identifiers. Default POL-001..n.
        criteria_names : Optional[Sequence[str]]
            Criteria names. Must match CANONICAL_CRITERIA_ORDER.
        num_replicates : int
            Total replicates to generate N_generated (default 10,000).
        random_seed : Optional[int]
            Random seed for PCG64 bit generator (default 42).
        score_uncertainty_sd : float
            Latent pre-truncation Gaussian standard deviation (default 0.05).
        ahp_log_scale_sd : float
            Log-space standard deviation for AHP perturbation (default 0.15).
        variance_threshold : float
            Cumulative variance threshold for dynamic K (default 0.95).
        reciprocity_tolerance : float
            Reciprocity tolerance (default 1e-12).
        semantic_mode : str
            Weight semantic mode ('standardized_space' or 'raw_physical_space').
        simulation_id : Optional[str]
            Human/external simulation identifier.

        Returns
        -------
        MonteCarloSimulationResult
            Immutable, fully audited simulation result.
        """
        scores_arr = np.asarray(baseline_scores, dtype=np.float64)
        if scores_arr.ndim != 2 or scores_arr.shape[1] != 4:
            raise ValueError(f"baseline_scores must have shape (n, 4), got {scores_arr.shape}.")
        n, p = scores_arr.shape
        if n < 2:
            raise ValueError(f"Cohort must contain at least 2 candidates, got {n}.")
        if np.any(scores_arr < 0.0) or np.any(scores_arr > 1.0):
            raise ValueError("All baseline scores must lie within [0, 1].")

        ahp_arr = np.asarray(baseline_ahp_matrix, dtype=np.float64)
        if ahp_arr.shape != (4, 4):
            raise ValueError(f"baseline_ahp_matrix must have shape (4, 4), got {ahp_arr.shape}.")

        if criteria_names is not None:
            crit_tuple = tuple(str(c) for c in criteria_names)
            if crit_tuple != CANONICAL_CRITERIA_ORDER:
                raise ValueError(
                    f"Criteria order mismatch: expected {CANONICAL_CRITERIA_ORDER}, got {crit_tuple}."
                )
        else:
            crit_tuple = CANONICAL_CRITERIA_ORDER

        if polymer_ids is not None:
            pids = tuple(str(pid) for pid in polymer_ids)
            if len(pids) != n:
                raise ValueError(f"Length of polymer_ids ({len(pids)}) does not match scores rows ({n}).")
            if len(set(pids)) != n:
                raise ValueError("Duplicate polymer_ids detected.")
        else:
            pids = tuple(f"POL-{i+1:03d}" for i in range(n))

        # Deterministic baseline fingerprint
        baseline_fingerprint = v2_prov.compute_analysis_fingerprint(
            raw_scores=scores_arr,
            criteria_names=crit_tuple,
            ahp_matrix=ahp_arr,
            semantic_mode=semantic_mode,
            methodology_version=MC_METHODOLOGY_VERSION,
        )

        if simulation_id is None:
            simulation_id = f"mc-sim-{baseline_fingerprint[:12]}"

        rng = np.random.default_rng(random_seed)

        # Generate all replicate inputs
        replicate_scores = _sample_truncated_normal_scores(
            base_scores=scores_arr,
            sigma_score=score_uncertainty_sd,
            num_replicates=num_replicates,
            rng=rng,
        )
        replicate_ahp = _perturb_ahp_matrix_log_space(
            base_ahp=ahp_arr,
            sigma_ahp=ahp_log_scale_sd,
            num_replicates=num_replicates,
            rng=rng,
        )

        # Block reason accounting
        block_counts: Dict[str, int] = {reason: 0 for reason in CANONICAL_BLOCK_REASONS}
        stability_counts: Dict[str, int] = {"STABLE": 0, "WARNING": 0, "BLOCKED": 0}

        valid_k_list = []
        valid_ranks_list = []
        valid_cl_list = []

        # Optimization: Cache repository head commit temporarily during simulation loop
        orig_head_func = v2_prov.get_repository_head_commit
        cached_head = orig_head_func()
        v2_prov.get_repository_head_commit = lambda: cached_head

        try:
            for m in range(num_replicates):
                s_m = replicate_scores[m]
                a_m = replicate_ahp[m]

                try:
                    # Every replicate MUST invoke VariableKEngine.evaluate directly
                    snapshot = self.engine.evaluate(
                        scores=s_m,
                        pairwise_matrix=a_m,
                        polymer_ids=pids,
                        criteria_names=crit_tuple,
                        semantic_mode=semantic_mode,
                        variance_threshold=variance_threshold,
                        reciprocity_tolerance=reciprocity_tolerance,
                    )
                    # Successful evaluation => VALID governance
                    valid_k_list.append(snapshot.pca.retained_k)
                    valid_ranks_list.append(snapshot.metrics.ranks)
                    valid_cl_list.append(snapshot.metrics.closeness_coefficients)
                    stability_counts[snapshot.stability.stability_status] += 1

                except ZeroVarianceStandardizationError:
                    block_counts["ZERO_VARIANCE"] += 1
                except DegenerateSubspaceBlockedError:
                    block_counts["EIGENGAP_BLOCKED"] += 1
                    stability_counts["BLOCKED"] += 1
                except (AHPConsistencyViolationError, AHPNonReciprocalError):
                    block_counts["AHP_CR_BLOCKED"] += 1
                except (NonPositiveDefiniteMetricError, MateriallyNegativeQuadraticFormError, RankDeficientSubspaceError):
                    block_counts["NON_PD_METRIC"] += 1
                except DegenerateReferenceCoincidenceError:
                    block_counts["REFERENCE_COINCIDENCE"] += 1
                except (StandardizationError, ValueError, InvalidWeightVectorError):
                    block_counts["INVALID_INPUT_SCORE"] += 1
                except Exception:
                    block_counts["INVALID_INPUT_SCORE"] += 1
        finally:
            v2_prov.get_repository_head_commit = orig_head_func

        num_valid = len(valid_k_list)
        num_blocked = sum(block_counts.values())

        # Enforce Replicate Conservation: N_generated == N_valid + N_blocked
        assert num_replicates == num_valid + num_blocked, (
            f"Replicate conservation violated: N_gen ({num_replicates}) != "
            f"N_valid ({num_valid}) + N_blocked ({num_blocked})"
        )

        governance_dist = {
            "VALID": float(num_valid / num_replicates),
            "BLOCKED": float(num_blocked / num_replicates),
        }

        stability_dist = {
            "STABLE": float(stability_counts["STABLE"] / num_replicates),
            "WARNING": float(stability_counts["WARNING"] / num_replicates),
            "BLOCKED": float(stability_counts["BLOCKED"] / num_replicates),
        }

        # Handle Zero-Valid Policy
        if num_valid == 0:
            simulation_state = "UNEVALUABLE_ALL_BLOCKED"
            k_dist: Dict[int, float] = {}
            candidate_records = ()
        else:
            simulation_state = "EVALUATED"

            # K distribution across valid replicates
            k_arr = np.array(valid_k_list, dtype=np.int32)
            k_dist = {k: float(np.sum(k_arr == k) / num_valid) for k in (1, 2, 3, 4)}

            # Ranks and Closeness tensors across valid replicates
            ranks_arr = np.array(valid_ranks_list, dtype=np.int32)  # shape (num_valid, n)
            cl_arr = np.array(valid_cl_list, dtype=np.float64)       # shape (num_valid, n)

            records = []
            for i, pid in enumerate(pids):
                r_i = ranks_arr[:, i]
                cl_i = cl_arr[:, i]

                # Top-1 probability
                p_top1 = float(np.mean(r_i == 1))

                # Top-k cumulative probabilities
                p_top_k = {k_val: float(np.mean(r_i <= k_val)) for k_val in range(1, n + 1)}

                # Full rank distribution
                rank_dist = {r_val: float(np.mean(r_i == r_val)) for r_val in range(1, n + 1)}

                expected_rank = float(np.mean(r_i))
                median_rank = float(np.median(r_i))

                # Conditioned closeness summaries C_L | (K=k)
                cond_cl: Dict[int, Dict[str, float]] = {}
                for k_val in (1, 2, 3, 4):
                    mask = (k_arr == k_val)
                    if np.any(mask):
                        cl_k = cl_i[mask]
                        q25, q75 = np.percentile(cl_k, [25, 75])
                        cond_cl[k_val] = {
                            "count": int(len(cl_k)),
                            "median": float(np.median(cl_k)),
                            "iqr": float(q75 - q25),
                            "mean": float(np.mean(cl_k)),
                            "std": float(np.std(cl_k)),
                        }

                # Descriptive pooled closeness heuristic
                q25_all, q75_all = np.percentile(cl_i, [25, 75])
                desc_cl = {
                    "label": DESCRIPTIVE_CLOSENESS_LABEL,
                    "count": int(len(cl_i)),
                    "median": float(np.median(cl_i)),
                    "iqr": float(q75_all - q25_all),
                    "mean": float(np.mean(cl_i)),
                    "std": float(np.std(cl_i)),
                }

                rec = CandidateMCOutputRecord(
                    polymer_id=pid,
                    p_top1=p_top1,
                    p_top_k=p_top_k,
                    rank_distribution=rank_dist,
                    expected_rank=expected_rank,
                    median_rank=median_rank,
                    conditional_closeness=cond_cl,
                    descriptive_closeness=desc_cl,
                )
                records.append(rec)

            candidate_records = tuple(records)

        # Assemble parameters dictionary
        params = {
            "num_replicates": int(num_replicates),
            "random_seed": random_seed,
            "score_uncertainty_sd": float(score_uncertainty_sd),
            "ahp_log_scale_sd": float(ahp_log_scale_sd),
            "variance_threshold": float(variance_threshold),
            "reciprocity_tolerance": float(reciprocity_tolerance),
            "semantic_mode": str(semantic_mode),
        }

        # Build cryptographic provenance manifest (two-pass non-circular)
        head_commit = v2_prov.get_repository_head_commit()
        scores_digest = v2_prov.compute_canonical_sha256(v2_prov.to_canonical_json(scores_arr))
        ahp_digest = v2_prov.compute_canonical_sha256(v2_prov.to_canonical_json(ahp_arr))

        if candidate_records:
            cand_payload = [
                {
                    "polymer_id": cr.polymer_id,
                    "p_top1": cr.p_top1,
                    "expected_rank": cr.expected_rank,
                    "median_rank": cr.median_rank,
                }
                for cr in candidate_records
            ]
            cand_digest = v2_prov.compute_canonical_sha256(v2_prov.to_canonical_json(cand_payload))
        else:
            cand_digest = "NONE_ALL_BLOCKED"

        partial_hashes = {
            "baseline_scores_sha256": scores_digest,
            "baseline_ahp_matrix_sha256": ahp_digest,
            "candidate_summary_sha256": cand_digest,
        }

        manifest_without_full = {
            "simulation_id": simulation_id,
            "methodology_version": MC_METHODOLOGY_VERSION,
            "analysis_fingerprint": baseline_fingerprint,
            "git_commit": head_commit,
            "simulation_state": simulation_state,
            "accounting": {
                "num_generated": int(num_replicates),
                "num_valid": int(num_valid),
                "num_blocked": int(num_blocked),
                "block_reasons_histogram": block_counts,
            },
            "parameters": params,
            "provenance_hashes": partial_hashes,
        }

        full_manifest_sha256 = v2_prov.compute_canonical_sha256(
            v2_prov.to_canonical_json(manifest_without_full)
        )
        complete_hashes = dict(partial_hashes)
        complete_hashes["full_manifest_sha256"] = full_manifest_sha256

        final_manifest = dict(manifest_without_full)
        final_manifest["provenance_hashes"] = complete_hashes

        return MonteCarloSimulationResult(
            simulation_id=simulation_id,
            analysis_fingerprint=baseline_fingerprint,
            simulation_state=simulation_state,
            num_generated=num_replicates,
            num_valid=num_valid,
            num_blocked=num_blocked,
            block_reasons_histogram=block_counts,
            k_distribution=k_dist,
            governance_distribution=governance_dist,
            stability_distribution=stability_dist,
            candidate_records=candidate_records,
            parameters=params,
            provenance_manifest=final_manifest,
            provenance_hashes=complete_hashes,
        )


def run_monte_carlo(
    baseline_scores: np.ndarray,
    baseline_ahp_matrix: np.ndarray,
    polymer_ids: Optional[Sequence[str]] = None,
    criteria_names: Optional[Sequence[str]] = None,
    num_replicates: int = 10000,
    random_seed: Optional[int] = 42,
    score_uncertainty_sd: float = 0.05,
    ahp_log_scale_sd: float = 0.15,
    variance_threshold: float = 0.95,
    reciprocity_tolerance: float = 1e-12,
    semantic_mode: str = "standardized_space",
    simulation_id: Optional[str] = None,
) -> MonteCarloSimulationResult:
    """Convenience functional wrapper around MonteCarloEngine().run(...)."""
    engine = MonteCarloEngine()
    return engine.run(
        baseline_scores=baseline_scores,
        baseline_ahp_matrix=baseline_ahp_matrix,
        polymer_ids=polymer_ids,
        criteria_names=criteria_names,
        num_replicates=num_replicates,
        random_seed=random_seed,
        score_uncertainty_sd=score_uncertainty_sd,
        ahp_log_scale_sd=ahp_log_scale_sd,
        variance_threshold=variance_threshold,
        reciprocity_tolerance=reciprocity_tolerance,
        semantic_mode=semantic_mode,
        simulation_id=simulation_id,
    )
