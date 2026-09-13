"""PharmaPolySCOPE Variable-K Engine (v2) Package Namespace.

Authoritative Specification: 2.0.0-SPEC-PHASE0-PATCH2.
Mathematical Baseline: SP-PRP-TOPSIS (Frozen Specification, September 2026).
Phase: Phase 4 (Architecture Implementation).
"""

from asd_mcda.v2.models import (
    CANONICAL_CRITERIA_ORDER,
    AHPResult,
    AnalysisResult,
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
    ENGINE_VERSION,
    FROZEN_V15_BASELINE_COMMIT,
    METHODOLOGY_VERSION,
    build_provenance_manifest,
    compute_analysis_fingerprint,
    compute_canonical_sha256,
    get_repository_head_commit,
    to_canonical_json,
)
from asd_mcda.v2.standardization import standardize_cohort
from asd_mcda.v2.pca import canonicalize_eigenvector_sign, decompose_spectral
from asd_mcda.v2.stability import evaluate_subspace_stability
from asd_mcda.v2.ahp import RI_4, solve_ahp_preference
from asd_mcda.v2.metrics import (
    compute_distances_and_closeness,
    construct_metric_tensor,
    project_reference_points,
)
from asd_mcda.v2.diagnostics import audit_truncation_discrepancy
from asd_mcda.v2.engine import VariableKEngine
from asd_mcda.v2.phase5_models import (
    CANONICAL_BLOCK_REASONS,
    DESCRIPTIVE_CLOSENESS_LABEL,
    CandidateMCOutputRecord,
    FactorSensitivityRecord,
    MonteCarloSimulationResult,
    MorrisSensitivityResult,
)
from asd_mcda.v2.uncertainty import MonteCarloEngine, run_monte_carlo
from asd_mcda.v2.sensitivity import MorrisSensitivityEngine, run_morris_sensitivity
from asd_mcda.v2.exceptions import (
    ChemicalStructureError,
    InvalidSmilesError,
    ProductionFallbackProhibitedError,
    RDKitParseFailureError,
    RDKitSanitizationFailureError,
    RDKitUnavailableError,
)
from asd_mcda.v2.chemistry import (
    compute_production_descriptors,
    get_diagnostic_fallback_descriptors,
    resolve_validated_drug_snapshot,
    validate_chemical_structure,
    validate_polymer_repeat_units,
)

__version__ = "2.0.0-draft"


__all__ = [
    "__version__",
    "CANONICAL_CRITERIA_ORDER",
    "CANONICAL_BLOCK_REASONS",
    "DESCRIPTIVE_CLOSENESS_LABEL",
    "METHODOLOGY_VERSION",
    "ENGINE_VERSION",
    "FROZEN_V15_BASELINE_COMMIT",
    "VariableKEngine",
    "VariableKDecisionSnapshot",
    "AnalysisResult",
    "StandardizationResult",
    "PCAResult",
    "SubspaceStabilityRecord",
    "AHPResult",
    "DecisionMetricResult",
    "TruncationAuditResult",
    "TruncationDiagnosticRecord",
    "CandidateMCOutputRecord",
    "MonteCarloSimulationResult",
    "FactorSensitivityRecord",
    "MorrisSensitivityResult",
    "MonteCarloEngine",
    "run_monte_carlo",
    "MorrisSensitivityEngine",
    "run_morris_sensitivity",
    "deep_freeze",
    "make_readonly",
    "to_canonical_json",
    "compute_canonical_sha256",
    "compute_analysis_fingerprint",
    "build_provenance_manifest",
    "get_repository_head_commit",
    "standardize_cohort",
    "canonicalize_eigenvector_sign",
    "decompose_spectral",
    "evaluate_subspace_stability",
    "solve_ahp_preference",
    "construct_metric_tensor",
    "project_reference_points",
    "compute_distances_and_closeness",
    "audit_truncation_discrepancy",
    "ChemicalStructureError",
    "InvalidSmilesError",
    "RDKitParseFailureError",
    "RDKitSanitizationFailureError",
    "RDKitUnavailableError",
    "ProductionFallbackProhibitedError",
    "validate_chemical_structure",
    "compute_production_descriptors",
    "get_diagnostic_fallback_descriptors",
    "resolve_validated_drug_snapshot",
    "validate_polymer_repeat_units",
]

