"""Exceptions for the PharmaPolySCOPE Variable-K Engine (v2).

Authoritative Specification: 2.0.0-SPEC-PHASE0-PATCH2.
Defines deterministic, domain-specific exception classes for validation,
spectral decomposition, subspace stability, and AHP consistency gates.
"""


class PharmaPolyScopeV2Error(Exception):
    """Base exception class for all PharmaPolySCOPE v2 engine errors."""
    pass


class StandardizationError(PharmaPolyScopeV2Error, ValueError):
    """Base exception for errors during cohort standardization."""
    pass


class ZeroVarianceStandardizationError(StandardizationError):
    """Raised when any criterion exhibits zero or negative standard deviation (sigma_j <= 0)."""
    pass


class SubspaceStabilityError(PharmaPolyScopeV2Error):
    """Base exception for subspace stability evaluation errors."""
    pass


class DegenerateSubspaceBlockedError(SubspaceStabilityError, RuntimeError):
    """Raised when the boundary eigengap delta_K < 0.03 (BLOCKED status)."""
    pass


class AHPError(PharmaPolyScopeV2Error):
    """Base exception for Analytic Hierarchy Process errors."""
    pass


class AHPNonReciprocalError(AHPError, ValueError):
    """Raised when an AHP pairwise comparison matrix violates the reciprocal condition a_ji * a_ij ≈ 1."""
    pass


class AHPConsistencyViolationError(AHPError, ValueError):
    """Raised when AHP Consistency Ratio CR >= 0.08 (governance gate blocked)."""
    pass


class NonPositiveDefiniteMetricError(PharmaPolyScopeV2Error, ValueError):
    """Raised when metric tensor M_K has non-positive eigenvalues."""
    pass


class DegenerateReferenceCoincidenceError(PharmaPolyScopeV2Error, ValueError):
    """Raised when D_plus + D_minus == 0 (candidate coincides with both ideal and anti-ideal)."""
    pass


class MateriallyNegativeQuadraticFormError(PharmaPolyScopeV2Error, ValueError):
    """Raised when distance quadratic form delta^T M_K delta is materially negative (< -1e-12)."""
    pass


class InvalidWeightVectorError(PharmaPolyScopeV2Error, ValueError):
    """Raised when physical weights are non-positive, non-finite, or do not sum to 1."""
    pass


class RankDeficientSubspaceError(PharmaPolyScopeV2Error, ValueError):
    """Raised when projection matrix V_K is rank deficient (rank < K)."""
    pass


# -----------------------------------------------------------------------------
# Chemical Structure & Cheminformatics Integrity Exceptions
# -----------------------------------------------------------------------------

class ChemicalStructureError(PharmaPolyScopeV2Error, ValueError):
    """Base exception for chemical structure validation and RDKit ingestion errors."""
    pass


class RDKitUnavailableError(ChemicalStructureError, RuntimeError):
    """Raised when RDKit is unavailable in a production molecular descriptor calculation."""
    pass


class InvalidSmilesError(ChemicalStructureError):
    """Raised when a chemical SMILES string fails syntax, valency, or RDKit parsing."""
    pass


class RDKitParseFailureError(InvalidSmilesError):
    """Raised specifically when RDKit Chem.MolFromSmiles returns None for a SMILES string."""
    pass


class RDKitSanitizationFailureError(ChemicalStructureError):
    """Raised when RDKit Chem.SanitizeMol fails for a parsed molecular graph."""
    pass


class ProductionFallbackProhibitedError(ChemicalStructureError):
    """Raised when diagnostic fallback descriptors are detected in a production execution path."""
    pass

