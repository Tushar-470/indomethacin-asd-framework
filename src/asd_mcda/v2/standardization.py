"""Cohort Standardization and Physical Anchor Mapping (Step 1).

Authoritative Specification: 2.0.0-SPEC-PHASE0-PATCH2.
Computes cohort population moments (ddof=0), standardizes criteria scores,
transforms physical ideal (s+=[1,1,1,1]) and anti-ideal (s-=[0,0,0,0]) anchors,
and strictly enforces zero-variance guardrails.
"""

from typing import Tuple
import numpy as np

from asd_mcda.v2.exceptions import StandardizationError, ZeroVarianceStandardizationError


def standardize_cohort(
    scores: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Standardize the candidate cohort decision matrix and map physical reference points.

    Parameters
    ----------
    scores : np.ndarray
        Raw decision score matrix S of shape (n, 4), values in [0, 1].

    Returns
    -------
    Z : np.ndarray
        Standardized cohort matrix of shape (n, 4), read-only.
    z_plus : np.ndarray
        Standardized physical ideal point (s+=[1,1,1,1]) of shape (4,), read-only.
    z_minus : np.ndarray
        Standardized physical anti-ideal point (s-=[0,0,0,0]) of shape (4,), read-only.
    mu : np.ndarray
        Population mean vector of shape (4,), read-only.
    sigma : np.ndarray
        Population standard deviation vector (ddof=0) of shape (4,), read-only.

    Raises
    ------
    StandardizationError
        If scores is not 2D, does not have 4 columns, has < 2 rows, or contains
        values outside [0, 1].
    ZeroVarianceStandardizationError
        If any criterion has sigma_j <= 0.
    """
    if not isinstance(scores, np.ndarray):
        scores = np.asarray(scores, dtype=np.float64)
    else:
        scores = scores.astype(np.float64)

    if scores.ndim != 2:
        raise StandardizationError(f"Input scores must be a 2D array, got {scores.ndim}D.")

    n, p = scores.shape
    if p != 4:
        raise StandardizationError(f"Input scores must have exactly 4 criteria columns, got {p}.")

    # Engineering Contract: n >= 2 is required because population variance
    # must be estimable and all four criteria require non-zero cohort variance.
    if n < 2:
        raise StandardizationError(f"Cohort must contain at least 2 candidates, got {n}.")

    if np.any(scores < 0.0) or np.any(scores > 1.0):
        raise StandardizationError("All input score values must be bounded in [0, 1].")

    # Population moments (ddof=0 normative convention)
    mu = np.mean(scores, axis=0)
    sigma = np.sqrt(np.mean((scores - mu) ** 2, axis=0))

    # Enforce zero-variance guardrail
    for j in range(p):
        if sigma[j] <= 1e-15:
            raise ZeroVarianceStandardizationError(
                f"Criterion at index {j} exhibits zero or non-positive variance: sigma={sigma[j]:.6e} <= 0."
            )

    Z = (scores - mu) / sigma
    z_plus = (1.0 - mu) / sigma
    z_minus = (0.0 - mu) / sigma

    # Defensive copy and read-only sealing
    Z_out = Z.copy()
    Z_out.flags.writeable = False

    z_plus_out = z_plus.copy()
    z_plus_out.flags.writeable = False

    z_minus_out = z_minus.copy()
    z_minus_out.flags.writeable = False

    mu_out = mu.copy()
    mu_out.flags.writeable = False

    sigma_out = sigma.copy()
    sigma_out.flags.writeable = False

    return Z_out, z_plus_out, z_minus_out, mu_out, sigma_out
