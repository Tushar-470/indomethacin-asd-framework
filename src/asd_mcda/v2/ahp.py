"""External Physical-Space AHP Preference Solver (Step 5).

Authoritative Specification: 2.0.0-SPEC-PHASE0-PATCH2.
Solves the principal eigenvector priority weights from an externally supplied
4x4 pairwise comparison matrix A.
Computes Consistency Index CI = (lambda_max - 4) / 3 and Consistency Ratio
CR = CI / 0.89 (where RI_4 = 0.89).
Strictly enforces the project governance gate:
    CR < 0.08:  ACCEPT
    CR >= 0.08: BLOCK (raises AHPConsistencyViolationError)
"""

from typing import Tuple
import numpy as np

from asd_mcda.v2.exceptions import AHPConsistencyViolationError, AHPNonReciprocalError

RI_4: float = 0.89
CR_THRESHOLD: float = 0.08


def solve_ahp_preference(
    pairwise_matrix: np.ndarray,
    reciprocity_tolerance: float = 1e-12,
) -> Tuple[np.ndarray, float]:
    """Solve the 4x4 physical-criteria AHP pairwise comparison matrix.

    Parameters
    ----------
    pairwise_matrix : np.ndarray
        Externally supplied 4x4 pairwise comparison matrix A.
    reciprocity_tolerance : float
        Numerical tolerance for the reciprocal condition |a_ji * a_ij - 1.0| < 1e-12.

    Returns
    -------
    w_phys : np.ndarray
        Normalized physical criteria weights of shape (4,), read-only.
    cr : float
        Consistency ratio CR = CI / 0.89.

    Raises
    ------
    ValueError
        If matrix shape != (4, 4), diagonal != 1, or any entry <= 0.
    AHPNonReciprocalError
        If matrix violates reciprocal condition |a_ji * a_ij - 1.0| < 1e-12.
    AHPConsistencyViolationError
        If CR >= 0.08.
    """
    A = np.asarray(pairwise_matrix, dtype=np.float64)

    if A.shape != (4, 4):
        raise ValueError(f"AHP pairwise comparison matrix must have shape (4, 4), got {A.shape}.")

    if not np.allclose(np.diag(A), 1.0, atol=1e-6):
        raise ValueError("AHP matrix diagonal entries must all equal 1.0.")

    if np.any(A <= 0.0):
        raise ValueError("All entries in the AHP matrix must be strictly positive.")

    # Reciprocity validation: |a_ji * a_ij - 1.0| < 1e-12
    recip_product = A * A.T
    recip_error = float(np.max(np.abs(recip_product - 1.0)))
    if recip_error >= reciprocity_tolerance:
        raise AHPNonReciprocalError(
            f"AHP pairwise matrix violates reciprocal condition |a_ji * a_ij - 1.0| < {reciprocity_tolerance:.1e}: "
            f"max error = {recip_error:.2e}."
        )

    # Principal eigenvector method
    eigvals, eigvecs = np.linalg.eig(A)

    # Principal eigenvalue (largest real part)
    lead_idx = int(np.argmax(eigvals.real))
    lambda_max = float(eigvals[lead_idx].real)

    # Corresponding positive eigenvector by Perron-Frobenius theorem
    w_raw = np.abs(eigvecs[:, lead_idx].real)
    sum_w = float(np.sum(w_raw))
    if sum_w <= 0.0:
        raise ValueError("Principal eigenvector elements sum to non-positive value.")
    w_phys = w_raw / sum_w

    # Consistency Index and Ratio
    ci = (lambda_max - 4.0) / 3.0
    cr = float(ci / RI_4)
    if cr < 0.0:
        cr = 0.0

    # Governance gate
    if cr >= CR_THRESHOLD - 1e-12:
        raise AHPConsistencyViolationError(
            f"AHP Consistency Ratio CR = {cr:.4f} exceeds project governance threshold "
            f"{CR_THRESHOLD:.2f} (BLOCKED). Preference matrix rejected."
        )

    # Defensive copy and read-only sealing
    w_out = w_phys.copy()
    w_out.flags.writeable = False

    return w_out, cr
