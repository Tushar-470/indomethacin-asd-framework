"""Subspace Stability Evaluator and Boundary Eigengap Governance (Step 3).

Authoritative Specification: 2.0.0-SPEC-PHASE0-PATCH2.
Evaluates the spectral gap at the retention boundary delta_K = lambda_K - lambda_(K+1).
Enforces exact project governance thresholds:
    delta_K >= 0.10: STABLE
    0.03 <= delta_K < 0.10: WARNING
    delta_K < 0.03: BLOCKED (raises DegenerateSubspaceBlockedError)
When K=p, delta_K is unconditionally +inf and status is STABLE.
"""

from typing import NamedTuple
import numpy as np

from asd_mcda.v2.exceptions import DegenerateSubspaceBlockedError


class StabilityRecord(NamedTuple):
    """Immutable record containing subspace stability diagnostics.

    Attributes
    ----------
    retained_k : int
        Number of retained principal components K.
    boundary_eigengap : float
        Spectral difference delta_K = lambda_K - lambda_(K+1), or +inf if K=p.
    stability_status : str
        Governance status: 'STABLE', 'WARNING', or 'BLOCKED'.
    warning_message : str
        Human-readable warning details if status is 'WARNING', else empty string.
    """
    retained_k: int
    boundary_eigengap: float
    stability_status: str
    warning_message: str


def evaluate_subspace_stability(
    eigenvalues: np.ndarray,
    retained_k: int,
) -> StabilityRecord:
    """Evaluate subspace stability across the retained/discarded boundary.

    Parameters
    ----------
    eigenvalues : np.ndarray
        Sorted eigenvalues array in descending order, shape (p,).
    retained_k : int
        Number of retained principal components K (1 <= K <= p).

    Returns
    -------
    StabilityRecord
        Immutable record containing boundary_eigengap, stability_status, and warning_message.

    Raises
    ------
    ValueError
        If retained_k is out of range [1, p].
    DegenerateSubspaceBlockedError
        If boundary_eigengap delta_K < 0.03 (BLOCKED status).
    """
    eigs = np.asarray(eigenvalues, dtype=np.float64)
    p = len(eigs)

    if retained_k < 1 or retained_k > p:
        raise ValueError(f"retained_k must be between 1 and {p}, got {retained_k}.")

    if retained_k == p:
        delta_k = float("inf")
        status = "STABLE"
        warning_msg = ""
    else:
        # lambda_K is index retained_k - 1; lambda_(K+1) is index retained_k
        delta_k = float(eigs[retained_k - 1] - eigs[retained_k])

        if delta_k >= 0.10 - 1e-12:
            status = "STABLE"
            warning_msg = ""
        elif delta_k >= 0.03 - 1e-12:
            status = "WARNING"
            warning_msg = (
                f"Boundary eigengap delta_{retained_k} = {delta_k:.4f} is in "
                f"warning zone [0.03, 0.10). Subspace orientation may be sensitive to perturbations."
            )
        else:
            status = "BLOCKED"
            raise DegenerateSubspaceBlockedError(
                f"Boundary eigengap delta_{retained_k} = {delta_k:.4f} is below guardrail "
                f"threshold 0.03 (BLOCKED). Subspace is near-degenerate; PCA truncation blocked."
            )

    return StabilityRecord(
        retained_k=int(retained_k),
        boundary_eigengap=delta_k,
        stability_status=status,
        warning_message=warning_msg,
    )
