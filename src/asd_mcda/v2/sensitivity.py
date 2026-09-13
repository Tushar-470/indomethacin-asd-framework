"""Morris Elementary Effects Global Sensitivity Screening for PharmaPolySCOPE v2 (Phase 5).

Authoritative Specification: 2.0.0-SPEC-PHASE5.2-FINAL.
Enforces:
- Global sensitivity screening domain: scores in [s_base - 0.15, s_base + 0.15] cap [0, 1].
- Decoupled from Monte Carlo uncertainty dispersion (sigma_score = 0.05).
- AHP perturbations in log-space q_ij = ln(a_ij) with exact analytical reciprocity (< 1e-12).
- Continuous closeness C_L as primary response; ordinal rank as secondary switching response.
- Every trajectory point directly executes VariableKEngine.evaluate(...) (no cached PCA).
- Canonical block reason tracking and whole-trajectory replacement on governance blocks.
- Purely computational termination safeguard: max_trajectory_attempts = max(300, 10 * r).
  Exceeding this limit terminates with UNEVALUABLE_MORRIS_DESIGN (zero scientific interpretation).
- Two-pass non-circular manifest hashing and cryptographic provenance sealing.
"""

from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple
import numpy as np

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
    FactorSensitivityRecord,
    MorrisSensitivityResult,
)
import asd_mcda.v2.provenance as v2_prov

MORRIS_METHODOLOGY_VERSION: str = "2.0.0-SP-PRP-TOPSIS-MORRIS"

UPPER_AHP_PAIRS: Tuple[Tuple[int, int], ...] = (
    (0, 1),
    (0, 2),
    (0, 3),
    (1, 2),
    (1, 3),
    (2, 3),
)


def _generate_candidate_trajectory(
    d: int,
    p_grid: int,
    delta: float,
    rng: np.random.Generator,
) -> np.ndarray:
    """Construct a single Morris trajectory in the normalized hypercube [0, 1]^d.

    Parameters
    ----------
    d : int
        Number of factors.
    p_grid : int
        Number of grid levels (typically 4 or 6).
    delta : float
        Normalized grid step size p_grid / (2 * (p_grid - 1)).
    rng : np.random.Generator
        Random generator instance.

    Returns
    -------
    np.ndarray
        Trajectory points matrix of shape (d + 1, d) in [0, 1]^d.
    """
    grid_choices = np.linspace(0.0, 1.0 - delta, p_grid // 2)
    x_star = rng.choice(grid_choices, size=d)
    d_diag = rng.choice([-1.0, 1.0], size=d)
    p_perm = rng.permutation(d)

    b_lower = np.tril(np.ones((d + 1, d), dtype=np.float64), -1)
    j_mat = np.ones((d + 1, d), dtype=np.float64)

    b_star = np.tile(x_star, (d + 1, 1)) + (delta / 2.0) * ((2.0 * b_lower - j_mat) * d_diag + j_mat)
    # Reorder columns according to permutation matrix P*
    trajectory = b_star[:, p_perm]
    return trajectory


class MorrisSensitivityEngine:
    """Outer evaluation layer for Morris Elementary Effects Screening around VariableKEngine."""

    def __init__(self, engine: Optional[VariableKEngine] = None) -> None:
        """Initialize the Morris sensitivity analysis engine.

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
        num_trajectories: int = 10,
        num_grid_levels: int = 4,
        grid_step: Optional[float] = None,
        score_screening_delta: float = 0.15,
        ahp_log_screening_delta: float = 0.30,
        max_trajectory_attempts: Optional[int] = None,
        random_seed: Optional[int] = 42,
        variance_threshold: float = 0.95,
        reciprocity_tolerance: float = 1e-12,
        semantic_mode: str = "standardized_space",
        analysis_id: Optional[str] = None,
    ) -> MorrisSensitivityResult:
        """Execute Morris Elementary Effects screening across scores and AHP weights.

        Parameters
        ----------
        baseline_scores : np.ndarray
            Curated baseline score matrix S_base of shape (n, 4) in [0, 1].
        baseline_ahp_matrix : np.ndarray
            Curated baseline 4x4 AHP matrix.
        polymer_ids : Optional[Sequence[str]]
            Candidate polymer identifiers. Default POL-001..n.
        criteria_names : Optional[Sequence[str]]
            Criteria names. Must match CANONICAL_CRITERIA_ORDER.
        num_trajectories : int
            Target number of valid trajectories r (default 10).
        num_grid_levels : int
            Number of grid levels p_grid in {4, 6} (default 4).
        grid_step : Optional[float]
            Normalized step size delta. If None, computed as p_grid / (2 * (p_grid - 1)).
        score_screening_delta : float
            Physical score screening range +/- delta (default 0.15, clipped to [0, 1]).
        ahp_log_screening_delta : float
            Log-space AHP screening range +/- delta (default 0.30).
        max_trajectory_attempts : Optional[int]
            Computational termination safeguard. Default max(300, 10 * r).
        random_seed : Optional[int]
            Random seed for PCG64 generator (default 42).
        variance_threshold : float
            Cumulative variance threshold for dynamic K (default 0.95).
        reciprocity_tolerance : float
            Reciprocity tolerance (default 1e-12).
        semantic_mode : str
            Weight semantic mode ('standardized_space' or 'raw_physical_space').
        analysis_id : Optional[str]
            Human/external analysis identifier.

        Returns
        -------
        MorrisSensitivityResult
            Immutable, fully audited Morris screening result.
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

        # Baseline analysis fingerprint
        baseline_fingerprint = v2_prov.compute_analysis_fingerprint(
            raw_scores=scores_arr,
            criteria_names=crit_tuple,
            ahp_matrix=ahp_arr,
            semantic_mode=semantic_mode,
            methodology_version=MORRIS_METHODOLOGY_VERSION,
        )

        if analysis_id is None:
            analysis_id = f"morris-{baseline_fingerprint[:12]}"

        if num_grid_levels not in (4, 6):
            raise ValueError(f"num_grid_levels must be 4 or 6, got {num_grid_levels}.")

        if grid_step is None:
            delta = float(num_grid_levels / (2.0 * (num_grid_levels - 1.0)))
        else:
            delta = float(grid_step)

        # Build factor definitions: 4*n score factors + 6 AHP factors
        # Total factors d = 4*n + 6
        factors_info = []
        d_scores = n * 4
        for i in range(n):
            for j in range(4):
                f_idx = i * 4 + j
                f_name = f"score_{pids[i]}_{crit_tuple[j]}"
                base_v = float(scores_arr[i, j])
                l_bound = max(0.0, base_v - score_screening_delta)
                u_bound = min(1.0, base_v + score_screening_delta)
                factors_info.append({
                    "factor_index": f_idx,
                    "factor_name": f_name,
                    "factor_type": "score",
                    "base_value": base_v,
                    "bounds": (l_bound, u_bound),
                    "polymer_idx": i,
                    "criterion_idx": j,
                })

        d_ahp = len(UPPER_AHP_PAIRS)
        for k, (ci, cj) in enumerate(UPPER_AHP_PAIRS):
            f_idx = d_scores + k
            f_name = f"ahp_{crit_tuple[ci]}_{crit_tuple[cj]}"
            base_v = float(ahp_arr[ci, cj])
            q_base = np.log(base_v)
            l_bound = q_base - ahp_log_screening_delta
            u_bound = q_base + ahp_log_screening_delta
            factors_info.append({
                "factor_index": f_idx,
                "factor_name": f_name,
                "factor_type": "ahp",
                "base_value": base_v,
                "bounds": (l_bound, u_bound),
                "ahp_pair": (ci, cj),
            })

        total_d = len(factors_info)

        # Computational termination safeguard
        if max_trajectory_attempts is None:
            attempt_limit = max(300, 10 * num_trajectories)
        else:
            attempt_limit = max_trajectory_attempts

        rng = np.random.default_rng(random_seed)

        discard_counts: Dict[str, int] = {reason: 0 for reason in CANONICAL_BLOCK_REASONS}
        valid_trajectories_data = []

        # Temporarily cache repository head commit during execution
        orig_head_func = v2_prov.get_repository_head_commit
        cached_head = orig_head_func()
        v2_prov.get_repository_head_commit = lambda: cached_head

        attempts = 0
        try:
            while len(valid_trajectories_data) < num_trajectories and attempts < attempt_limit:
                attempts += 1
                norm_traj = _generate_candidate_trajectory(d=total_d, p_grid=num_grid_levels, delta=delta, rng=rng)

                # Evaluate all d + 1 points in this candidate trajectory
                traj_cl_records = []
                traj_rank_records = []
                trajectory_blocked = False
                block_reason = None

                for pt_idx in range(total_d + 1):
                    x_pt = norm_traj[pt_idx]

                    # Reconstruct physical candidate scores matrix S_eval
                    s_eval = scores_arr.copy()
                    for f in factors_info:
                        if f["factor_type"] == "score":
                            l_b, u_b = f["bounds"]
                            val = l_b + x_pt[f["factor_index"]] * (u_b - l_b)
                            s_eval[f["polymer_idx"], f["criterion_idx"]] = val

                    # Reconstruct physical AHP matrix A_eval
                    a_eval = np.eye(4, dtype=np.float64)
                    for f in factors_info:
                        if f["factor_type"] == "ahp":
                            l_b, u_b = f["bounds"]
                            q_val = l_b + x_pt[f["factor_index"]] * (u_b - l_b)
                            a_val = np.exp(q_val)
                            ci, cj = f["ahp_pair"]
                            a_eval[ci, cj] = a_val
                            a_eval[cj, ci] = 1.0 / a_val

                    # Invoke VariableKEngine.evaluate directly
                    try:
                        snapshot = self.engine.evaluate(
                            scores=s_eval,
                            pairwise_matrix=a_eval,
                            polymer_ids=pids,
                            criteria_names=crit_tuple,
                            semantic_mode=semantic_mode,
                            variance_threshold=variance_threshold,
                            reciprocity_tolerance=reciprocity_tolerance,
                        )
                        traj_cl_records.append(np.array(snapshot.metrics.closeness_coefficients, dtype=np.float64))
                        traj_rank_records.append(np.array(snapshot.metrics.ranks, dtype=np.float64))
                    except ZeroVarianceStandardizationError:
                        trajectory_blocked = True
                        block_reason = "ZERO_VARIANCE"
                        break
                    except DegenerateSubspaceBlockedError:
                        trajectory_blocked = True
                        block_reason = "EIGENGAP_BLOCKED"
                        break
                    except (AHPConsistencyViolationError, AHPNonReciprocalError):
                        trajectory_blocked = True
                        block_reason = "AHP_CR_BLOCKED"
                        break
                    except (NonPositiveDefiniteMetricError, MateriallyNegativeQuadraticFormError, RankDeficientSubspaceError):
                        trajectory_blocked = True
                        block_reason = "NON_PD_METRIC"
                        break
                    except DegenerateReferenceCoincidenceError:
                        trajectory_blocked = True
                        block_reason = "REFERENCE_COINCIDENCE"
                        break
                    except (StandardizationError, ValueError, InvalidWeightVectorError):
                        trajectory_blocked = True
                        block_reason = "INVALID_INPUT_SCORE"
                        break
                    except Exception:
                        trajectory_blocked = True
                        block_reason = "INVALID_INPUT_SCORE"
                        break

                if trajectory_blocked:
                    # Discard entire trajectory and log canonical block reason
                    discard_counts[block_reason] += 1
                else:
                    # Trajectory is valid; save normalized coordinates and responses
                    valid_trajectories_data.append({
                        "norm_traj": norm_traj,
                        "cl": np.array(traj_cl_records),       # shape (d+1, n)
                        "ranks": np.array(traj_rank_records),  # shape (d+1, n)
                    })
        finally:
            v2_prov.get_repository_head_commit = orig_head_func

        num_valid = len(valid_trajectories_data)
        num_discarded = sum(discard_counts.values())

        # Check Termination Safeguard
        if num_valid < num_trajectories:
            design_state = "UNEVALUABLE_MORRIS_DESIGN"
            factor_records = ()
        else:
            design_state = "EVALUATED"

            # Compute Elementary Effects for each factor
            # For each factor j: ee_cl has shape (r, n), ee_rank has shape (r, n)
            factor_records_list = []

            for f in factors_info:
                j = f["factor_index"]
                ee_cl_list = []
                ee_rank_list = []

                for t_data in valid_trajectories_data:
                    norm_traj = t_data["norm_traj"]
                    cl_traj = t_data["cl"]
                    ranks_traj = t_data["ranks"]

                    # Find which step changed factor j
                    step_found = False
                    for step in range(total_d):
                        dx = norm_traj[step + 1, j] - norm_traj[step, j]
                        if np.abs(dx) > 1e-12:
                            # Primary response: continuous closeness
                            ee_cl = (cl_traj[step + 1] - cl_traj[step]) / dx
                            # Secondary response: ordinal rank
                            ee_rk = (ranks_traj[step + 1] - ranks_traj[step]) / dx
                            ee_cl_list.append(ee_cl)
                            ee_rank_list.append(ee_rk)
                            step_found = True
                            break
                    assert step_found, f"Factor {j} was not shifted in trajectory."

                ee_cl_arr = np.array(ee_cl_list)      # shape (r, n)
                ee_rank_arr = np.array(ee_rank_list)  # shape (r, n)

                # Elementary effects statistics per polymer
                mu_dict = {}
                mu_star_dict = {}
                sigma_dict = {}
                rank_mu_dict = {}
                rank_mu_star_dict = {}
                rank_sigma_dict = {}

                for pol_idx, pid in enumerate(pids):
                    vals_cl = ee_cl_arr[:, pol_idx]
                    mu_dict[pid] = float(np.mean(vals_cl))
                    mu_star_dict[pid] = float(np.mean(np.abs(vals_cl)))
                    sigma_dict[pid] = float(np.std(vals_cl, ddof=1)) if num_valid > 1 else 0.0

                    vals_rk = ee_rank_arr[:, pol_idx]
                    rank_mu_dict[pid] = float(np.mean(vals_rk))
                    rank_mu_star_dict[pid] = float(np.mean(np.abs(vals_rk)))
                    rank_sigma_dict[pid] = float(np.std(vals_rk, ddof=1)) if num_valid > 1 else 0.0

                rec = FactorSensitivityRecord(
                    factor_index=j,
                    factor_name=f["factor_name"],
                    factor_type=f["factor_type"],
                    base_value=f["base_value"],
                    screening_range=f["bounds"],
                    mu=mu_dict,
                    mu_star=mu_star_dict,
                    sigma=sigma_dict,
                    rank_mu=rank_mu_dict,
                    rank_mu_star=rank_mu_star_dict,
                    rank_sigma=rank_sigma_dict,
                )
                factor_records_list.append(rec)

            factor_records = tuple(factor_records_list)

        params = {
            "num_trajectories": int(num_trajectories),
            "num_grid_levels": int(num_grid_levels),
            "grid_step": float(delta),
            "score_screening_delta": float(score_screening_delta),
            "ahp_log_screening_delta": float(ahp_log_screening_delta),
            "max_trajectory_attempts": int(attempt_limit),
            "random_seed": random_seed,
            "variance_threshold": float(variance_threshold),
            "reciprocity_tolerance": float(reciprocity_tolerance),
            "semantic_mode": str(semantic_mode),
        }

        # Build cryptographic provenance manifest
        head_commit = v2_prov.get_repository_head_commit()
        scores_digest = v2_prov.compute_canonical_sha256(v2_prov.to_canonical_json(scores_arr))
        ahp_digest = v2_prov.compute_canonical_sha256(v2_prov.to_canonical_json(ahp_arr))

        if factor_records:
            factors_payload = [
                {
                    "factor_index": fr.factor_index,
                    "factor_name": fr.factor_name,
                    "mu_star": fr.mu_star,
                    "sigma": fr.sigma,
                }
                for fr in factor_records
            ]
            factors_digest = v2_prov.compute_canonical_sha256(v2_prov.to_canonical_json(factors_payload))
        else:
            factors_digest = "NONE_UNEVALUABLE_MORRIS_DESIGN"

        partial_hashes = {
            "baseline_scores_sha256": scores_digest,
            "baseline_ahp_matrix_sha256": ahp_digest,
            "factor_sensitivities_sha256": factors_digest,
        }

        manifest_without_full = {
            "analysis_id": analysis_id,
            "methodology_version": MORRIS_METHODOLOGY_VERSION,
            "analysis_fingerprint": baseline_fingerprint,
            "git_commit": head_commit,
            "design_state": design_state,
            "accounting": {
                "num_trajectories_requested": int(num_trajectories),
                "num_trajectories_valid": int(num_valid),
                "num_trajectories_attempted": int(attempts),
                "num_trajectories_discarded": int(num_discarded),
                "discard_reasons_histogram": discard_counts,
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

        return MorrisSensitivityResult(
            analysis_id=analysis_id,
            baseline_fingerprint=baseline_fingerprint,
            design_state=design_state,
            num_trajectories_requested=num_trajectories,
            num_trajectories_valid=num_valid,
            num_trajectories_attempted=attempts,
            num_trajectories_discarded=num_discarded,
            discard_reasons_histogram=discard_counts,
            factors=factor_records,
            parameters=params,
            provenance_manifest=final_manifest,
            provenance_hashes=complete_hashes,
        )


def run_morris_sensitivity(
    baseline_scores: np.ndarray,
    baseline_ahp_matrix: np.ndarray,
    polymer_ids: Optional[Sequence[str]] = None,
    criteria_names: Optional[Sequence[str]] = None,
    num_trajectories: int = 10,
    num_grid_levels: int = 4,
    grid_step: Optional[float] = None,
    score_screening_delta: float = 0.15,
    ahp_log_screening_delta: float = 0.30,
    max_trajectory_attempts: Optional[int] = None,
    random_seed: Optional[int] = 42,
    variance_threshold: float = 0.95,
    reciprocity_tolerance: float = 1e-12,
    semantic_mode: str = "standardized_space",
    analysis_id: Optional[str] = None,
) -> MorrisSensitivityResult:
    """Convenience functional wrapper around MorrisSensitivityEngine().run(...)."""
    engine = MorrisSensitivityEngine()
    return engine.run(
        baseline_scores=baseline_scores,
        baseline_ahp_matrix=baseline_ahp_matrix,
        polymer_ids=polymer_ids,
        criteria_names=criteria_names,
        num_trajectories=num_trajectories,
        num_grid_levels=num_grid_levels,
        grid_step=grid_step,
        score_screening_delta=score_screening_delta,
        ahp_log_screening_delta=ahp_log_screening_delta,
        max_trajectory_attempts=max_trajectory_attempts,
        random_seed=random_seed,
        variance_threshold=variance_threshold,
        reciprocity_tolerance=reciprocity_tolerance,
        semantic_mode=semantic_mode,
        analysis_id=analysis_id,
    )
