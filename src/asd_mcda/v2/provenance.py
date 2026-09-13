"""Cryptographic Provenance and Deterministic Auditing for PharmaPolySCOPE v2.

Authoritative Specification: 2.0.0-SPEC-PHASE0-PATCH2.
Enforces deterministic canonical JSON serialization, cryptographic SHA-256 fingerprinting,
two-pass non-circular manifest hashing, and strict Git provenance tracking.
"""

import copy
import hashlib
import json
import platform
import subprocess
import sys
from types import MappingProxyType
from typing import Any, Dict, Mapping, Optional, Sequence, Tuple
import numpy as np

METHODOLOGY_VERSION: str = "2.0.0-SP-PRP-TOPSIS"
ENGINE_VERSION: str = "2.0.0-draft"
FROZEN_V15_BASELINE_COMMIT: str = "31eee4d"


def get_repository_head_commit() -> Optional[str]:
    """Retrieve the current Git repository HEAD commit hash dynamically, if available."""
    try:
        res = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
        return res.stdout.strip()
    except Exception:
        return None


def _sanitize_for_json(obj: Any) -> Any:
    """Recursively convert custom/NumPy data types to standard JSON-compatible Python primitives."""
    if isinstance(obj, np.ndarray):
        return [_sanitize_for_json(item) for item in obj.tolist()]
    elif isinstance(obj, (np.floating, float)):
        val = float(obj)
        if np.isposinf(val):
            return "Infinity"
        elif np.isneginf(val):
            return "-Infinity"
        elif np.isnan(val):
            return "NaN"
        return val
    elif isinstance(obj, (np.integer, int)):
        return int(obj)
    elif isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    elif isinstance(obj, (Mapping, MappingProxyType)):
        return {str(k): _sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [_sanitize_for_json(item) for item in obj]
    elif isinstance(obj, (set, frozenset)):
        # Sort set items for deterministic ordering
        sanitized = [_sanitize_for_json(item) for item in obj]
        return sorted(sanitized, key=lambda x: str(x))
    elif obj is None or isinstance(obj, (str, bytes)):
        return obj if not isinstance(obj, bytes) else obj.decode("utf-8", errors="replace")
    elif hasattr(obj, "__dataclass_fields__"):
        return {k: _sanitize_for_json(getattr(obj, k)) for k in obj.__dataclass_fields__}
    else:
        return str(obj)


def to_canonical_json(data: Any) -> str:
    """Serialize data to a canonical, deterministic JSON string.

    Rules:
    - Standard JSON primitives (NumPy arrays and scalars converted).
    - Keys lexicographically sorted (sort_keys=True).
    - Compact delimiters (separators=(',', ':')).
    - UTF-8 compatible without byte-order marks.
    """
    sanitized = _sanitize_for_json(data)
    return json.dumps(sanitized, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def compute_canonical_sha256(canonical_json_str: str) -> str:
    """Compute standard SHA-256 digest of a canonical UTF-8 serialized string."""
    return hashlib.sha256(canonical_json_str.encode("utf-8")).hexdigest()


def compute_analysis_fingerprint(
    raw_scores: np.ndarray,
    criteria_names: Sequence[str],
    ahp_matrix: np.ndarray,
    semantic_mode: str = "standardized_space",
    methodology_version: str = METHODOLOGY_VERSION,
) -> str:
    """Compute a deterministic SHA-256 fingerprint from canonical scientific inputs and methodology.

    Guarantees:
    - Same inputs + methodology => exact same fingerprint.
    - Any change in scores, criteria order, AHP matrix, or semantic mode changes fingerprint.
    """
    scores_arr = np.asarray(raw_scores, dtype=np.float64)
    ahp_arr = np.asarray(ahp_matrix, dtype=np.float64)

    payload = {
        "methodology_version": str(methodology_version),
        "criteria_names": [str(c) for c in criteria_names],
        "raw_scores": scores_arr.tolist(),
        "ahp_matrix": ahp_arr.tolist(),
        "semantic_mode": str(semantic_mode),
    }
    canonical_str = to_canonical_json(payload)
    return compute_canonical_sha256(canonical_str)


def build_provenance_manifest(
    snapshot: Any,
    engine_version: str = ENGINE_VERSION,
    v1_5_baseline_commit: str = FROZEN_V15_BASELINE_COMMIT,
) -> Dict[str, Any]:
    """Construct an authoritative, schema-conformant provenance manifest from an AnalysisResult.

    Solves hash circularity via two-pass non-circular manifest hashing:
    1. Generates component hashes (input_scores, ahp_matrix, output_ranking).
    2. Builds the complete manifest dictionary with full_manifest_sha256 omitted.
    3. Serializes the unhashed manifest canonically to compute full_manifest_sha256.
    4. Inserts full_manifest_sha256 into the manifest's provenance_hashes block.
    """
    head_commit = get_repository_head_commit()

    # Step 1: Compute component cryptographic digests
    scores_canonical = to_canonical_json(snapshot.raw_scores)
    input_scores_sha256 = compute_canonical_sha256(scores_canonical)

    ahp_canonical = to_canonical_json(snapshot.ahp.pairwise_matrix)
    ahp_matrix_sha256 = compute_canonical_sha256(ahp_canonical)

    ranking_payload = [
        {
            "rank": int(rank),
            "polymer_id": str(pid),
            "closeness_coefficient": float(cl),
        }
        for rank, pid, cl in zip(
            snapshot.metrics.ranks,
            snapshot.metrics.ranked_polymer_ids,
            snapshot.metrics.closeness_coefficients,
        )
    ]
    ranking_canonical = to_canonical_json(ranking_payload)
    output_ranking_sha256 = compute_canonical_sha256(ranking_canonical)

    # Step 2: Assemble provenance_hashes without full_manifest_sha256
    partial_provenance_hashes = {
        "input_scores_sha256": input_scores_sha256,
        "ahp_matrix_sha256": ahp_matrix_sha256,
        "output_ranking_sha256": output_ranking_sha256,
    }

    # Step 3: Build complete manifest without full_manifest_sha256
    manifest: Dict[str, Any] = {
        "analysis_id": str(snapshot.analysis_id),
        "analysis_fingerprint": str(snapshot.analysis_fingerprint),
        "engine_metadata": {
            "methodology_version": METHODOLOGY_VERSION,
            "engine_version": str(engine_version),
            "v1_5_baseline_commit": str(v1_5_baseline_commit),
            "repository_head_commit": head_commit,
            "implementation_commit": None,  # Uncommitted Phase 4 work tree
            "python_version": sys.version.split()[0],
            "numpy_version": np.__version__,
            "platform": platform.platform(),
        },
        "drug_snapshot": _sanitize_for_json(snapshot.drug_snapshot),
        "polymer_cohort_snapshot": _sanitize_for_json(snapshot.polymer_cohort_snapshot),
        "preference_provenance": {
            "physical_ahp_pairwise_matrix": snapshot.ahp.pairwise_matrix.tolist(),
            "physical_ahp_weights": snapshot.ahp.weights.tolist(),
            "consistency_ratio": float(snapshot.ahp.consistency_ratio),
            "weight_semantic_mode": str(snapshot.ahp.semantic_mode),
        },
        "standardization_moments": {
            "cohort_mean": snapshot.standardization.cohort_mean.tolist(),
            "cohort_std": snapshot.standardization.cohort_std.tolist(),
            "ddof": int(snapshot.standardization.ddof),
            "criteria_names": list(snapshot.criteria_names),
        },
        "spectral_geometry": {
            "eigenvalues": [float(x) for x in snapshot.pca.eigenvalues],
            "cumulative_variance": float(snapshot.pca.cumulative_variance),
            "retained_k": int(snapshot.pca.retained_k),
            "boundary_eigengap": (
                "Infinity" if np.isposinf(snapshot.stability.boundary_eigengap)
                else float(snapshot.stability.boundary_eigengap)
            ),
            "stability_status": str(snapshot.stability.stability_status),
            "variance_threshold": float(snapshot.pca.variance_threshold),
        },
        "decision_metrics": {
            "projected_coordinates": snapshot.metrics.projected_scores.tolist(),
            "distance_to_ideal": snapshot.metrics.distance_to_ideal.tolist(),
            "distance_to_anti_ideal": snapshot.metrics.distance_to_anti_ideal.tolist(),
            "closeness_coefficients": snapshot.metrics.closeness_coefficients.tolist(),
            "ordinal_ranks": [int(r) for r in snapshot.metrics.ranks],
            "polymer_ids": [str(p) for p in snapshot.metrics.ranked_polymer_ids],
        },
        "truncation_diagnostics": [
            {
                "polymer_id": str(rec.polymer_id),
                "d_full_sq": float(rec.d_full_sq),
                "d_k_sq": float(rec.d_k_sq),
                "signed_discrepancy": float(rec.signed_discrepancy),
                "relative_discrepancy": float(rec.relative_discrepancy),
            }
            for rec in snapshot.truncation.records
        ],
        "provenance_hashes": partial_provenance_hashes,
    }

    # Step 4: Serialize unhashed manifest canonically to compute full_manifest_sha256
    manifest_without_full_json = to_canonical_json(manifest)
    full_manifest_sha256 = compute_canonical_sha256(manifest_without_full_json)

    # Step 5: Insert full_manifest_sha256 into final manifest
    final_manifest = copy.deepcopy(manifest)
    final_manifest["provenance_hashes"]["full_manifest_sha256"] = full_manifest_sha256

    return final_manifest
