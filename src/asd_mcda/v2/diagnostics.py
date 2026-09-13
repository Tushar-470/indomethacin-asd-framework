"""Truncation Diagnostics and Dimensionality Discrepancy Auditing (Step 9).

Authoritative Specification: 2.0.0-SPEC-PHASE0-PATCH2.
Quantifies the exact signed discrepancy between full-space weighted geometry
and projected subspace geometry:
    Delta D_i^2 = d_full_i^2 - d_K_i^2
and the relative discrepancy:
    E_i = |Delta D_i^2| / d_full_i^2.
Note: Discrepancy can be signed because W and P_K need not commute.
Terminology: Truncation Discrepancy (not conventional PCA reconstruction loss).
"""

from typing import List, NamedTuple, Sequence
import numpy as np


class TruncationDiscrepancyRecord(NamedTuple):
    """Diagnostic record for candidate truncation discrepancy.

    Attributes
    ----------
    polymer_id : str
        Identifier of the evaluated polymer alternative.
    d_full_sq : float
        Full-space weighted squared distance: (z_i - z_ref)^T @ W @ (z_i - z_ref).
    d_k_sq : float
        Projected subspace weighted squared distance: (t_i - t_ref)^T @ M_K @ (t_i - t_ref).
    signed_discrepancy : float
        Signed discrepancy Delta D^2 = d_full_sq - d_k_sq.
    relative_discrepancy : float
        Absolute relative discrepancy E_i = |Delta D^2| / d_full_sq.
    """
    polymer_id: str
    d_full_sq: float
    d_k_sq: float
    signed_discrepancy: float
    relative_discrepancy: float


def audit_truncation_discrepancy(
    Z: np.ndarray,
    z_ref: np.ndarray,
    W: np.ndarray,
    V_K: np.ndarray,
    polymer_ids: Sequence[str] = None,
) -> List[TruncationDiscrepancyRecord]:
    """Audit the exact signed truncation discrepancy across all cohort candidates.

    Parameters
    ----------
    Z : np.ndarray
        Cohort standardized decision matrix of shape (n, p).
    z_ref : np.ndarray
        Standardized reference point coordinates of shape (p,).
    W : np.ndarray
        Effective full-space weight matrix of shape (p, p).
    V_K : np.ndarray
        Retained subspace projection basis matrix of shape (p, K).
    polymer_ids : Sequence[str], optional
        Candidate identifiers.

    Returns
    -------
    records : List[TruncationDiscrepancyRecord]
        List of diagnostic discrepancy records for each candidate.
    """
    Z_arr = np.asarray(Z, dtype=np.float64)
    z_ref_arr = np.asarray(z_ref, dtype=np.float64)
    W_arr = np.asarray(W, dtype=np.float64)
    V_arr = np.asarray(V_K, dtype=np.float64)

    n, p = Z_arr.shape
    P_K = V_arr @ V_arr.T
    M_K = V_arr.T @ W_arr @ V_arr

    records = []
    for i in range(n):
        pid = str(polymer_ids[i]) if polymer_ids is not None else f"POL-{i+1:03d}"
        delta_z = Z_arr[i] - z_ref_arr

        # Full-space weighted squared distance
        d_full_sq = float(delta_z @ W_arr @ delta_z)

        # Projected subspace distance via M_K metric
        delta_t = delta_z @ V_arr
        d_k_sq = float(delta_t @ M_K @ delta_t)

        # Signed discrepancy Delta D^2 = d_full^2 - d_K^2
        signed_diff = d_full_sq - d_k_sq

        # Relative discrepancy E_i = |Delta D^2| / d_full^2
        rel_diff = abs(signed_diff) / d_full_sq if d_full_sq > 1e-14 else 0.0

        records.append(
            TruncationDiscrepancyRecord(
                polymer_id=pid,
                d_full_sq=d_full_sq,
                d_k_sq=d_k_sq,
                signed_discrepancy=signed_diff,
                relative_discrepancy=rel_diff,
            )
        )

    return records
