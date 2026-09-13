"""Immutable Data Contracts and Deep Freezing for PharmaPolySCOPE v2.

Authoritative Specification: 2.0.0-SPEC-PHASE0-PATCH2.
Defines typed, immutable data models representing analysis snapshots,
standardization, spectral geometry, AHP preferences, metric results,
truncation diagnostics, and complete analysis results.
Enforces genuine deep immutability, defensive copying, and caller buffer independence.
"""

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, List, Literal, Mapping, Optional, Sequence, Tuple, Union
import numpy as np

# Canonical Criteria Ordering frozen for the 4-criterion physical decision matrix
CANONICAL_CRITERIA_ORDER: Tuple[str, ...] = ("s_HSP", "s_chi", "s_desc", "s_GT")

StabilityStatus = Literal["STABLE", "WARNING", "BLOCKED"]
WeightSemanticMode = Literal["standardized_space", "raw_physical_space"]


def deep_freeze(obj: Any) -> Any:
    """Recursively transform data structures into unbypassable immutable types.

    Ensures snapshot objects retain ZERO references to caller-owned mutable buffers.

    Rules:
    - np.ndarray: Defensive copy with np.copy, flags.writeable set to False.
    - Mapping: Values recursively frozen, wrapped in MappingProxyType.
    - list / tuple: Elements recursively frozen into an immutable tuple.
    - set / frozenset: Elements recursively frozen into an immutable frozenset.
    - Immutable scalars (int, float, str, bool, bytes, type(None)): preserved as-is.
    - Custom objects or unsupported types: raises TypeError.
    """
    if isinstance(obj, np.ndarray):
        copied_arr = np.copy(obj)
        copied_arr.flags.writeable = False
        return copied_arr
    elif isinstance(obj, Mapping):
        return MappingProxyType({k: deep_freeze(v) for k, v in obj.items()})
    elif isinstance(obj, (list, tuple)):
        return tuple(deep_freeze(item) for item in obj)
    elif isinstance(obj, (set, frozenset)):
        return frozenset(deep_freeze(item) for item in obj)
    elif isinstance(obj, (int, float, str, bool, bytes, type(None))):
        return obj
    else:
        raise TypeError(f"Unsupported mutable type for deep snapshot freeze: {type(obj)}")


def make_readonly(arr: Any) -> np.ndarray:
    """Ensure an array-like object is a defensively copied, read-only NumPy array."""
    if arr is None:
        raise ValueError("Cannot make None into a read-only array.")
    copied_arr = np.copy(np.asarray(arr, dtype=np.float64))
    copied_arr.flags.writeable = False
    return copied_arr


@dataclass(frozen=True)
class SubspaceStabilityRecord:
    """Immutable audit record of the PCA boundary stability state."""
    retained_k: int
    ambient_p: int
    eigenvalues: Tuple[float, ...]
    cumulative_variance: float
    boundary_eigengap: float
    stability_status: str
    warning_message: str = ""

    def __post_init__(self):
        object.__setattr__(self, "eigenvalues", tuple(float(x) for x in self.eigenvalues))
        object.__setattr__(self, "retained_k", int(self.retained_k))
        object.__setattr__(self, "ambient_p", int(self.ambient_p))
        object.__setattr__(self, "cumulative_variance", float(self.cumulative_variance))
        object.__setattr__(self, "boundary_eigengap", float(self.boundary_eigengap))
        object.__setattr__(self, "stability_status", str(self.stability_status))
        object.__setattr__(self, "warning_message", str(self.warning_message))


@dataclass(frozen=True)
class TruncationDiagnosticRecord:
    """Immutable per-alternative metric truncation audit record."""
    polymer_id: str
    d_full_sq: float
    d_k_sq: float
    signed_discrepancy: float
    relative_discrepancy: float

    def __post_init__(self):
        object.__setattr__(self, "polymer_id", str(self.polymer_id))
        object.__setattr__(self, "d_full_sq", float(self.d_full_sq))
        object.__setattr__(self, "d_k_sq", float(self.d_k_sq))
        object.__setattr__(self, "signed_discrepancy", float(self.signed_discrepancy))
        object.__setattr__(self, "relative_discrepancy", float(self.relative_discrepancy))


@dataclass(frozen=True)
class StandardizationResult:
    """Immutable cohort standardization result."""
    cohort_mean: np.ndarray
    cohort_std: np.ndarray
    standardized_scores: np.ndarray
    z_plus: np.ndarray
    z_minus: np.ndarray
    ddof: int = 0

    def __post_init__(self):
        object.__setattr__(self, "cohort_mean", make_readonly(self.cohort_mean))
        object.__setattr__(self, "cohort_std", make_readonly(self.cohort_std))
        object.__setattr__(self, "standardized_scores", make_readonly(self.standardized_scores))
        object.__setattr__(self, "z_plus", make_readonly(self.z_plus))
        object.__setattr__(self, "z_minus", make_readonly(self.z_minus))
        object.__setattr__(self, "ddof", int(self.ddof))


@dataclass(frozen=True)
class PCAResult:
    """Immutable spectral decomposition result."""
    eigenvalues: Tuple[float, ...]
    eigenvectors: np.ndarray
    retained_basis: np.ndarray
    retained_k: int
    cumulative_variance: float
    variance_threshold: float = 0.95

    def __post_init__(self):
        object.__setattr__(self, "eigenvalues", tuple(float(x) for x in self.eigenvalues))
        object.__setattr__(self, "eigenvectors", make_readonly(self.eigenvectors))
        object.__setattr__(self, "retained_basis", make_readonly(self.retained_basis))
        object.__setattr__(self, "retained_k", int(self.retained_k))
        object.__setattr__(self, "cumulative_variance", float(self.cumulative_variance))
        object.__setattr__(self, "variance_threshold", float(self.variance_threshold))


@dataclass(frozen=True)
class AHPResult:
    """Immutable external AHP preference result."""
    pairwise_matrix: np.ndarray
    weights: np.ndarray
    consistency_ratio: float
    lambda_max: float
    consistency_index: float
    random_index: float = 0.89
    semantic_mode: str = "standardized_space"

    def __post_init__(self):
        object.__setattr__(self, "pairwise_matrix", make_readonly(self.pairwise_matrix))
        object.__setattr__(self, "weights", make_readonly(self.weights))
        object.__setattr__(self, "consistency_ratio", float(self.consistency_ratio))
        object.__setattr__(self, "lambda_max", float(self.lambda_max))
        object.__setattr__(self, "consistency_index", float(self.consistency_index))
        object.__setattr__(self, "random_index", float(self.random_index))
        object.__setattr__(self, "semantic_mode", str(self.semantic_mode))


@dataclass(frozen=True)
class DecisionMetricResult:
    """Immutable SP-PRP-TOPSIS metric calculation result."""
    projected_scores: np.ndarray
    t_plus: np.ndarray
    t_minus: np.ndarray
    metric_tensor: np.ndarray
    weight_matrix: np.ndarray
    distance_to_ideal: np.ndarray
    distance_to_anti_ideal: np.ndarray
    closeness_coefficients: np.ndarray
    ranks: Tuple[int, ...]
    ranked_polymer_ids: Tuple[str, ...]

    def __post_init__(self):
        object.__setattr__(self, "projected_scores", make_readonly(self.projected_scores))
        object.__setattr__(self, "t_plus", make_readonly(self.t_plus))
        object.__setattr__(self, "t_minus", make_readonly(self.t_minus))
        object.__setattr__(self, "metric_tensor", make_readonly(self.metric_tensor))
        object.__setattr__(self, "weight_matrix", make_readonly(self.weight_matrix))
        object.__setattr__(self, "distance_to_ideal", make_readonly(self.distance_to_ideal))
        object.__setattr__(self, "distance_to_anti_ideal", make_readonly(self.distance_to_anti_ideal))
        object.__setattr__(self, "closeness_coefficients", make_readonly(self.closeness_coefficients))
        object.__setattr__(self, "ranks", tuple(int(r) for r in self.ranks))
        object.__setattr__(self, "ranked_polymer_ids", tuple(str(p) for p in self.ranked_polymer_ids))


@dataclass(frozen=True)
class TruncationAuditResult:
    """Immutable truncation audit aggregation."""
    records: Tuple[TruncationDiagnosticRecord, ...]
    max_relative_discrepancy: float
    mean_relative_discrepancy: float

    def __post_init__(self):
        object.__setattr__(self, "records", tuple(self.records))
        object.__setattr__(self, "max_relative_discrepancy", float(self.max_relative_discrepancy))
        object.__setattr__(self, "mean_relative_discrepancy", float(self.mean_relative_discrepancy))


@dataclass(frozen=True)
class VariableKDecisionSnapshot:
    """Authoritative, sealed, immutable snapshot of a single cohort execution."""
    analysis_id: str
    analysis_fingerprint: str
    drug_snapshot: Mapping[str, Any]
    polymer_cohort_snapshot: Tuple[Mapping[str, Any], ...]
    criteria_names: Tuple[str, ...]
    raw_scores: np.ndarray
    weights: np.ndarray
    standardization: StandardizationResult
    pca: PCAResult
    stability: SubspaceStabilityRecord
    ahp: AHPResult
    metrics: DecisionMetricResult
    truncation: TruncationAuditResult
    provenance: Optional[Mapping[str, Any]] = None
    provenance_hashes: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self):
        object.__setattr__(self, "analysis_id", str(self.analysis_id))
        object.__setattr__(self, "analysis_fingerprint", str(self.analysis_fingerprint))
        object.__setattr__(self, "drug_snapshot", deep_freeze(self.drug_snapshot))
        object.__setattr__(self, "polymer_cohort_snapshot", deep_freeze(self.polymer_cohort_snapshot))
        object.__setattr__(self, "criteria_names", deep_freeze(self.criteria_names))
        object.__setattr__(self, "raw_scores", make_readonly(self.raw_scores))
        object.__setattr__(self, "weights", make_readonly(self.weights))
        if self.provenance is not None:
            object.__setattr__(self, "provenance", deep_freeze(self.provenance))
        object.__setattr__(self, "provenance_hashes", deep_freeze(self.provenance_hashes))

    # Backward-compatible and convenience property forwarders
    @property
    def retained_k(self) -> int:
        return self.pca.retained_k

    @property
    def stability_status(self) -> str:
        return self.stability.stability_status

    @property
    def cumulative_variance(self) -> float:
        return self.pca.cumulative_variance

    @property
    def boundary_eigengap(self) -> float:
        return self.stability.boundary_eigengap

    @property
    def closeness_coefficients(self) -> np.ndarray:
        return self.metrics.closeness_coefficients

    @property
    def ranks(self) -> Tuple[int, ...]:
        return self.metrics.ranks

    @property
    def ordinal_ranks(self) -> Tuple[int, ...]:
        return self.metrics.ranks

    @property
    def metric_tensor(self) -> np.ndarray:
        return self.metrics.metric_tensor

    @property
    def projection_basis(self) -> np.ndarray:
        return self.pca.retained_basis

    @property
    def cohort_mean(self) -> np.ndarray:
        return self.standardization.cohort_mean

    @property
    def cohort_std(self) -> np.ndarray:
        return self.standardization.cohort_std

    @property
    def candidate_coordinates(self) -> np.ndarray:
        return self.metrics.projected_scores

    @property
    def distance_to_ideal(self) -> np.ndarray:
        return self.metrics.distance_to_ideal

    @property
    def distance_to_anti_ideal(self) -> np.ndarray:
        return self.metrics.distance_to_anti_ideal

    @property
    def eigenvalues(self) -> Tuple[float, ...]:
        return self.pca.eigenvalues

    @property
    def projected_ideal(self) -> np.ndarray:
        return self.metrics.t_plus

    @property
    def projected_anti_ideal(self) -> np.ndarray:
        return self.metrics.t_minus

    @property
    def consistency_ratio(self) -> float:
        return self.ahp.consistency_ratio

    @property
    def physical_ahp_weights(self) -> Tuple[float, ...]:
        return tuple(float(x) for x in self.ahp.weights)

    @property
    def physical_ahp_pairwise_matrix(self) -> Tuple[Tuple[float, ...], ...]:
        return tuple(tuple(float(v) for v in row) for row in self.ahp.pairwise_matrix)

    @property
    def weight_semantic_mode(self) -> str:
        return self.ahp.semantic_mode

    @property
    def truncation_diagnostics(self) -> Tuple[TruncationDiagnosticRecord, ...]:
        return self.truncation.records


# Official Alias
AnalysisResult = VariableKDecisionSnapshot
