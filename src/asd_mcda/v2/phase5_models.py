"""Immutable Data Contracts and Models for PharmaPolySCOPE v2 Phase 5.

Authoritative Specification: 2.0.0-SPEC-PHASE5.2-FINAL.
Defines immutable, schema-conformant data models for Monte Carlo uncertainty
propagation and Morris elementary effects global sensitivity analysis.
Enforces canonical block taxonomies, strict replicate accounting, and deep immutability.
"""

from dataclasses import dataclass
from typing import Any, Mapping, Optional, Sequence, Tuple
import numpy as np

from asd_mcda.v2.models import deep_freeze

CANONICAL_BLOCK_REASONS: Tuple[str, ...] = (
    "INVALID_INPUT_SCORE",
    "ZERO_VARIANCE",
    "EIGENGAP_BLOCKED",
    "AHP_CR_BLOCKED",
    "NON_PD_METRIC",
    "REFERENCE_COINCIDENCE",
    "INVALID_SMILES",
    "RDKIT_PARSE_FAILURE",
    "RDKIT_SANITIZATION_FAILURE",
    "RDKIT_UNAVAILABLE",
    "FALLBACK_PROHIBITED",
)

DESCRIPTIVE_CLOSENESS_LABEL: str = (
    "DESCRIPTIVE SUMMARY ONLY — NOT GEOMETRICALLY INVARIANT ACROSS VARIABLE-K SPACES"
)


@dataclass(frozen=True)
class CandidateMCOutputRecord:
    """Per-candidate statistical evaluation summary under Monte Carlo propagation.

    Attributes
    ----------
    polymer_id : str
        Candidate identifier.
    p_top1 : float
        Empirical selection probability P(rank == 1).
    p_top_k : Mapping[int, float]
        Cumulative top-k selection probabilities P(rank <= k).
    rank_distribution : Mapping[int, float]
        Empirical frequency distribution across candidate ranks {1, ..., n}.
    expected_rank : float
        Mean rank E[R_i] across valid replicates.
    median_rank : float
        Median rank across valid replicates.
    conditional_closeness : Mapping[int, Mapping[str, float]]
        Conditioned closeness summaries C_L | (K=k) containing median, iqr, mean, std.
    descriptive_closeness : Mapping[str, Any]
        Pooled descriptive closeness heuristic with mandatory invariance warning label.
    """
    polymer_id: str
    p_top1: float
    p_top_k: Mapping[int, float]
    rank_distribution: Mapping[int, float]
    expected_rank: float
    median_rank: float
    conditional_closeness: Mapping[int, Mapping[str, float]]
    descriptive_closeness: Mapping[str, Any]

    def __post_init__(self) -> None:
        object.__setattr__(self, "p_top_k", deep_freeze(self.p_top_k))
        object.__setattr__(self, "rank_distribution", deep_freeze(self.rank_distribution))
        object.__setattr__(self, "conditional_closeness", deep_freeze(self.conditional_closeness))
        object.__setattr__(self, "descriptive_closeness", deep_freeze(self.descriptive_closeness))


@dataclass(frozen=True)
class MonteCarloSimulationResult:
    """Authoritative output envelope for Monte Carlo uncertainty propagation.

    Attributes
    ----------
    simulation_id : str
        Unique simulation identifier.
    analysis_fingerprint : str
        Cryptographic fingerprint of the baseline deterministic analysis.
    simulation_state : str
        'EVALUATED' or 'UNEVALUABLE_ALL_BLOCKED'.
    num_generated : int
        Total number of replicates generated N_generated.
    num_valid : int
        Number of replicates producing a valid decision outcome N_valid.
    num_blocked : int
        Number of replicates blocked by governance gates N_blocked.
    block_reasons_histogram : Mapping[str, int]
        Counts of blocked replicates classified by the 6 canonical reasons.
    k_distribution : Mapping[int, float]
        Empirical frequency distribution of retained dimensions P(K=k).
    governance_distribution : Mapping[str, float]
        Proportions of VALID and BLOCKED replicates.
    stability_distribution : Mapping[str, float]
        Proportions of STABLE, WARNING, and BLOCKED spectral stability states.
    candidate_records : Tuple[CandidateMCOutputRecord, ...]
        Per-candidate summary records. Empty if simulation_state is UNEVALUABLE_ALL_BLOCKED.
    parameters : Mapping[str, Any]
        Frozen configuration parameters of the simulation.
    provenance_manifest : Mapping[str, Any]
        Complete audit manifest.
    provenance_hashes : Mapping[str, str]
        Cryptographic hashes of manifest components.
    """
    simulation_id: str
    analysis_fingerprint: str
    simulation_state: str
    num_generated: int
    num_valid: int
    num_blocked: int
    block_reasons_histogram: Mapping[str, int]
    k_distribution: Mapping[int, float]
    governance_distribution: Mapping[str, float]
    stability_distribution: Mapping[str, float]
    candidate_records: Tuple[CandidateMCOutputRecord, ...]
    parameters: Mapping[str, Any]
    provenance_manifest: Mapping[str, Any]
    provenance_hashes: Mapping[str, str]

    def __post_init__(self) -> None:
        object.__setattr__(self, "block_reasons_histogram", deep_freeze(self.block_reasons_histogram))
        object.__setattr__(self, "k_distribution", deep_freeze(self.k_distribution))
        object.__setattr__(self, "governance_distribution", deep_freeze(self.governance_distribution))
        object.__setattr__(self, "stability_distribution", deep_freeze(self.stability_distribution))
        object.__setattr__(self, "candidate_records", tuple(self.candidate_records))
        object.__setattr__(self, "parameters", deep_freeze(self.parameters))
        object.__setattr__(self, "provenance_manifest", deep_freeze(self.provenance_manifest))
        object.__setattr__(self, "provenance_hashes", deep_freeze(self.provenance_hashes))


@dataclass(frozen=True)
class FactorSensitivityRecord:
    """Sensitivity indices for a single input factor across all candidates.

    Attributes
    ----------
    factor_index : int
        Index of the factor in the unified design vector.
    factor_name : str
        Human-readable factor identifier (e.g. 'score_POL-001_s_HSP' or 'ahp_0_1').
    factor_type : str
        'score' or 'ahp'.
    base_value : float
        Baseline parameter value.
    screening_range : Tuple[float, float]
        Screening bounds [lower, upper] in physical/log units.
    mu : Mapping[str, float]
        Mean elementary effect mu for continuous closeness C_L per polymer.
    mu_star : Mapping[str, float]
        Mean absolute elementary effect mu* for continuous closeness C_L per polymer.
    sigma : Mapping[str, float]
        Standard deviation sigma of elementary effects for continuous closeness C_L per polymer.
    rank_mu : Mapping[str, float]
        Mean elementary effect for ordinal rank per polymer.
    rank_mu_star : Mapping[str, float]
        Mean absolute elementary effect for ordinal rank per polymer.
    rank_sigma : Mapping[str, float]
        Standard deviation of elementary effects for ordinal rank per polymer.
    """
    factor_index: int
    factor_name: str
    factor_type: str
    base_value: float
    screening_range: Tuple[float, float]
    mu: Mapping[str, float]
    mu_star: Mapping[str, float]
    sigma: Mapping[str, float]
    rank_mu: Mapping[str, float]
    rank_mu_star: Mapping[str, float]
    rank_sigma: Mapping[str, float]

    def __post_init__(self) -> None:
        object.__setattr__(self, "screening_range", tuple(self.screening_range))
        object.__setattr__(self, "mu", deep_freeze(self.mu))
        object.__setattr__(self, "mu_star", deep_freeze(self.mu_star))
        object.__setattr__(self, "sigma", deep_freeze(self.sigma))
        object.__setattr__(self, "rank_mu", deep_freeze(self.rank_mu))
        object.__setattr__(self, "rank_mu_star", deep_freeze(self.rank_mu_star))
        object.__setattr__(self, "rank_sigma", deep_freeze(self.rank_sigma))


@dataclass(frozen=True)
class MorrisSensitivityResult:
    """Authoritative output envelope for Morris elementary effects screening.

    Attributes
    ----------
    analysis_id : str
        Unique analysis identifier.
    baseline_fingerprint : str
        Cryptographic fingerprint of the baseline deterministic analysis.
    design_state : str
        'EVALUATED' or 'UNEVALUABLE_MORRIS_DESIGN'.
    num_trajectories_requested : int
        Requested number of valid trajectories r.
    num_trajectories_valid : int
        Realized number of valid trajectories.
    num_trajectories_attempted : int
        Total trajectories attempted before completion or termination.
    num_trajectories_discarded : int
        Total trajectories discarded due to governance blocks.
    discard_reasons_histogram : Mapping[str, int]
        Histogram of canonical block reasons triggering trajectory discards.
    factors : Tuple[FactorSensitivityRecord, ...]
        Sensitivity summary for each factor. Empty if design_state is UNEVALUABLE_MORRIS_DESIGN.
    parameters : Mapping[str, Any]
        Configuration parameters of the Morris screening.
    provenance_manifest : Mapping[str, Any]
        Complete audit manifest.
    provenance_hashes : Mapping[str, str]
        Cryptographic hashes of manifest components.
    """
    analysis_id: str
    baseline_fingerprint: str
    design_state: str
    num_trajectories_requested: int
    num_trajectories_valid: int
    num_trajectories_attempted: int
    num_trajectories_discarded: int
    discard_reasons_histogram: Mapping[str, int]
    factors: Tuple[FactorSensitivityRecord, ...]
    parameters: Mapping[str, Any]
    provenance_manifest: Mapping[str, Any]
    provenance_hashes: Mapping[str, str]

    def __post_init__(self) -> None:
        object.__setattr__(self, "discard_reasons_histogram", deep_freeze(self.discard_reasons_histogram))
        object.__setattr__(self, "factors", tuple(self.factors))
        object.__setattr__(self, "parameters", deep_freeze(self.parameters))
        object.__setattr__(self, "provenance_manifest", deep_freeze(self.provenance_manifest))
        object.__setattr__(self, "provenance_hashes", deep_freeze(self.provenance_hashes))
