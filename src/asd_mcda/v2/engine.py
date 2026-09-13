"""Pipeline Orchestrator for PharmaPolySCOPE Variable-K Engine (v2).

Authoritative Specification: 2.0.0-SPEC-PHASE0-PATCH2.
Orchestrates the validated Phase 2 and Phase 3 mathematical components:
    standardization.py -> pca.py -> stability.py -> ahp.py -> metrics.py -> diagnostics.py
Guarantees absolute cohort rebaselining, deep immutability, cryptographic provenance sealing,
and zero inter-analysis state leakage.
"""

import uuid
from typing import Any, Mapping, Optional, Sequence, Tuple
import numpy as np

from asd_mcda.v2.standardization import standardize_cohort
from asd_mcda.v2.pca import decompose_spectral
from asd_mcda.v2.stability import evaluate_subspace_stability
from asd_mcda.v2.ahp import solve_ahp_preference, RI_4
from asd_mcda.v2.metrics import (
    construct_metric_tensor,
    project_reference_points,
    compute_distances_and_closeness,
)
from asd_mcda.v2.diagnostics import audit_truncation_discrepancy
from asd_mcda.v2.models import (
    CANONICAL_CRITERIA_ORDER,
    AHPResult,
    DecisionMetricResult,
    PCAResult,
    StandardizationResult,
    SubspaceStabilityRecord,
    TruncationAuditResult,
    TruncationDiagnosticRecord,
    VariableKDecisionSnapshot,
    deep_freeze,
    make_readonly,
)
from asd_mcda.v2.provenance import (
    METHODOLOGY_VERSION,
    build_provenance_manifest,
    compute_analysis_fingerprint,
)
from asd_mcda.v2.exceptions import ProductionFallbackProhibitedError
from asd_mcda.v2.chemistry import validate_chemical_structure



class VariableKEngine:
    """Stateless orchestrator for the SP-PRP-TOPSIS variable-K decision architecture.

    Executes Steps 1-9 in strict compliance with the frozen Phase 0 specification.
    Maintains zero persistent scientific state between evaluations.
    """

    def __init__(self) -> None:
        """Initialize a stateless VariableKEngine instance."""
        pass

    def evaluate(
        self,
        scores: np.ndarray,
        pairwise_matrix: np.ndarray,
        polymer_ids: Optional[Sequence[str]] = None,
        criteria_names: Optional[Sequence[str]] = None,
        drug_data: Optional[Mapping[str, Any]] = None,
        polymers_data: Optional[Sequence[Mapping[str, Any]]] = None,
        semantic_mode: str = "standardized_space",
        analysis_id: Optional[str] = None,
        variance_threshold: float = 0.95,
        reciprocity_tolerance: float = 1e-12,
    ) -> VariableKDecisionSnapshot:
        """Execute the complete SP-PRP-TOPSIS variable-K decision pipeline.

        Parameters
        ----------
        scores : np.ndarray
            Raw decision score matrix S of shape (n, 4) with values in [0, 1].
        pairwise_matrix : np.ndarray
            Externally supplied physical 4x4 AHP comparison matrix.
        polymer_ids : Sequence[str], optional
            Identifiers for candidate polymers. If None, default POL-001..n assigned.
        criteria_names : Sequence[str], optional
            Names of the criteria. Must match CANONICAL_CRITERIA_ORDER exactly.
        drug_data : Mapping[str, Any], optional
            Metadata snapshot for model drug compound.
        polymers_data : Sequence[Mapping[str, Any]], optional
            Detailed metadata snapshots for candidate polymers.
        semantic_mode : str
            Weighting semantic mode: 'standardized_space' (default) or 'raw_physical_space'.
        analysis_id : str, optional
            Human/external analysis identifier. If None, generated deterministically/uniquely.
        variance_threshold : float
            Cumulative variance threshold for K selection (default 0.95).
        reciprocity_tolerance : float
            Tolerance for AHP matrix reciprocity condition |a_ji * a_ij - 1| < tol (default 1e-12).

        Returns
        -------
        VariableKDecisionSnapshot
            Authoritative, deeply frozen, immutable snapshot of the analysis execution.
        """
        # --- 0. Pre-Flight Input Validation ---
        scores_arr = np.asarray(scores, dtype=np.float64)
        if scores_arr.ndim != 2:
            raise ValueError(f"Decision matrix must be 2D, got shape {scores_arr.shape}.")

        n, p = scores_arr.shape
        if p != 4:
            raise ValueError(f"Decision matrix must have exactly 4 criteria columns, got {p}.")

        if criteria_names is not None:
            crit_tuple = tuple(str(c) for c in criteria_names)
            if crit_tuple != CANONICAL_CRITERIA_ORDER:
                raise ValueError(
                    f"Criteria order mismatch: expected canonical order {CANONICAL_CRITERIA_ORDER}, "
                    f"got {crit_tuple}. Arbitrary criterion reordering is prohibited."
                )
        else:
            crit_tuple = CANONICAL_CRITERIA_ORDER

        if polymer_ids is not None:
            pids = tuple(str(pid) for pid in polymer_ids)
            if len(pids) != n:
                raise ValueError(f"Length of polymer_ids ({len(pids)}) does not match scores rows ({n}).")
            if len(set(pids)) != n:
                raise ValueError("Duplicate polymer_ids detected; candidate identifiers must be unique.")
        else:
            pids = tuple(f"POL-{i+1:03d}" for i in range(n))

        if analysis_id is None:
            analysis_id = f"v2-analysis-{uuid.uuid4().hex[:12]}"

        if drug_data is None:
            drug_snapshot = {"drug_id": "DEFAULT_DRUG", "name": "Indomethacin"}
        else:
            drug_snapshot = dict(drug_data)
            # Defense-in-depth: Reject any drug snapshot containing fallback provenance
            if drug_snapshot.get("fallback_used") is True or drug_snapshot.get("descriptor_source") == "fallback":
                raise ProductionFallbackProhibitedError(
                    "Fallback descriptors are strictly prohibited in the production VariableKEngine."
                )
            if "canonical_smiles" in drug_snapshot and drug_snapshot["canonical_smiles"]:
                validate_chemical_structure(drug_snapshot["canonical_smiles"])


        if polymers_data is None:
            polymer_cohort_snapshot = tuple({"polymer_id": pid} for pid in pids)
        else:
            polymer_cohort_snapshot = tuple(dict(p) for p in polymers_data)

        # --- 1. Step 1: Cohort Standardization (ddof=0) ---
        Z, z_plus, z_minus, mu, sigma = standardize_cohort(scores_arr)

        # --- 2. Step 2: Ordinary Correlation PCA & Dynamic K Selection ---
        eigenvalues, V, K, cum_var = decompose_spectral(Z, variance_threshold=variance_threshold)
        V_K = V[:, :K]

        # --- 3. Step 3: Subspace Stability & Boundary Eigengap Evaluation ---
        stability_rec = evaluate_subspace_stability(eigenvalues, K)

        # --- 4. Step 5: External Physical AHP Preference Solution ---
        w_phys, cr = solve_ahp_preference(pairwise_matrix, reciprocity_tolerance=reciprocity_tolerance)
        ci = cr * RI_4
        lambda_max = 4.0 + 3.0 * ci

        # --- 5. Steps 6 & 7: Metric Tensor Construction ---
        # Normalize semantic mode identifier to metric module interface
        if semantic_mode in ("raw_physical", "raw_physical_space", "raw"):
            metric_semantic_mode = "raw_physical"
        else:
            metric_semantic_mode = "standardized_space"

        M_K, W = construct_metric_tensor(
            V_K=V_K,
            w_phys=w_phys,
            sigma=sigma,
            semantic_mode=metric_semantic_mode,
        )

        # --- 6. Step 8: Reference Projection & SP-PRP-TOPSIS Closeness ---
        t_plus, t_minus = project_reference_points(z_plus, z_minus, V_K)
        D_plus, D_minus, C_L, ranks = compute_distances_and_closeness(
            Z=Z,
            z_plus=z_plus,
            z_minus=z_minus,
            V_K=V_K,
            M_K=M_K,
            polymer_ids=pids,
        )

        # Candidate subspace coordinates: T = Z @ V_K
        T_K = Z @ V_K

        # --- 7. Step 9: Truncation Discrepancy Auditing ---
        trunc_records_list = audit_truncation_discrepancy(
            Z=Z,
            z_ref=z_plus,
            W=W,
            V_K=V_K,
            polymer_ids=pids,
        )
        trunc_records = tuple(
            TruncationDiagnosticRecord(
                polymer_id=r.polymer_id,
                d_full_sq=r.d_full_sq,
                d_k_sq=r.d_k_sq,
                signed_discrepancy=r.signed_discrepancy,
                relative_discrepancy=r.relative_discrepancy,
            )
            for r in trunc_records_list
        )
        rel_discrepancies = [r.relative_discrepancy for r in trunc_records]
        max_rel = max(rel_discrepancies) if rel_discrepancies else 0.0
        mean_rel = float(np.mean(rel_discrepancies)) if rel_discrepancies else 0.0

        # --- 8. Step 10: Immutable Result Aggregation ---
        std_result = StandardizationResult(
            cohort_mean=mu,
            cohort_std=sigma,
            standardized_scores=Z,
            z_plus=z_plus,
            z_minus=z_minus,
            ddof=0,
        )

        pca_result = PCAResult(
            eigenvalues=tuple(float(e) for e in eigenvalues),
            eigenvectors=V,
            retained_basis=V_K,
            retained_k=K,
            cumulative_variance=cum_var,
            variance_threshold=variance_threshold,
        )

        stability_record = SubspaceStabilityRecord(
            retained_k=stability_rec.retained_k,
            ambient_p=4,
            eigenvalues=tuple(float(e) for e in eigenvalues),
            cumulative_variance=cum_var,
            boundary_eigengap=stability_rec.boundary_eigengap,
            stability_status=stability_rec.stability_status,
            warning_message=stability_rec.warning_message,
        )

        ahp_result = AHPResult(
            pairwise_matrix=np.asarray(pairwise_matrix, dtype=np.float64),
            weights=w_phys,
            consistency_ratio=cr,
            lambda_max=lambda_max,
            consistency_index=ci,
            random_index=RI_4,
            semantic_mode=semantic_mode,
        )

        metric_result = DecisionMetricResult(
            projected_scores=T_K,
            t_plus=t_plus,
            t_minus=t_minus,
            metric_tensor=M_K,
            weight_matrix=W,
            distance_to_ideal=D_plus,
            distance_to_anti_ideal=D_minus,
            closeness_coefficients=C_L,
            ranks=tuple(int(r) for r in ranks),
            ranked_polymer_ids=pids,
        )

        trunc_audit_result = TruncationAuditResult(
            records=trunc_records,
            max_relative_discrepancy=max_rel,
            mean_relative_discrepancy=mean_rel,
        )

        # --- 9. Step 11: Deterministic Analysis Fingerprint & Provenance ---
        fingerprint = compute_analysis_fingerprint(
            raw_scores=scores_arr,
            criteria_names=crit_tuple,
            ahp_matrix=pairwise_matrix,
            semantic_mode=semantic_mode,
            methodology_version=METHODOLOGY_VERSION,
        )

        preliminary_snapshot = VariableKDecisionSnapshot(
            analysis_id=analysis_id,
            analysis_fingerprint=fingerprint,
            drug_snapshot=drug_snapshot,
            polymer_cohort_snapshot=polymer_cohort_snapshot,
            criteria_names=crit_tuple,
            raw_scores=scores_arr,
            weights=w_phys,
            standardization=std_result,
            pca=pca_result,
            stability=stability_record,
            ahp=ahp_result,
            metrics=metric_result,
            truncation=trunc_audit_result,
            provenance=None,
            provenance_hashes={},
        )

        manifest = build_provenance_manifest(preliminary_snapshot)

        # Final sealed snapshot with complete provenance and non-circular hashes
        sealed_snapshot = VariableKDecisionSnapshot(
            analysis_id=analysis_id,
            analysis_fingerprint=fingerprint,
            drug_snapshot=drug_snapshot,
            polymer_cohort_snapshot=polymer_cohort_snapshot,
            criteria_names=crit_tuple,
            raw_scores=scores_arr,
            weights=w_phys,
            standardization=std_result,
            pca=pca_result,
            stability=stability_record,
            ahp=ahp_result,
            metrics=metric_result,
            truncation=trunc_audit_result,
            provenance=manifest,
            provenance_hashes=manifest["provenance_hashes"],
        )

        return sealed_snapshot

    # Official Alias
    run = evaluate
