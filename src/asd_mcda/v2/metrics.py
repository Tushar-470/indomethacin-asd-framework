"""Metric Tensor, Reference Point Projection, and SP-PRP-TOPSIS Closeness (Steps 6, 7, 8).

Authoritative Specification: 2.0.0-SPEC-PHASE0-PATCH2.
Constructs the subspace metric tensor M_K = V_K^T @ W @ V_K, projects cohort-standardized
reference points into the PCA subspace, computes generalized quadratic-form distances,
and determines candidate closeness C_L with deterministic tie-breaking.
"""

from typing import Sequence, Tuple, Union
import numpy as np

from asd_mcda.v2.exceptions import (
    DegenerateReferenceCoincidenceError,
    InvalidWeightVectorError,
    MateriallyNegativeQuadraticFormError,
    NonPositiveDefiniteMetricError,
    RankDeficientSubspaceError,
)


def construct_metric_tensor(
    V_K: np.ndarray,
    w_phys: np.ndarray,
    sigma: np.ndarray = None,
    semantic_mode: str = "standardized_space",
) -> Tuple[np.ndarray, np.ndarray]:
    """Construct the subspace metric tensor M_K = V_K^T @ W @ V_K.

    Parameters
    ----------
    V_K : np.ndarray
        Orthogonal basis matrix of shape (p, K) spanning the retained subspace.
    w_phys : np.ndarray
        Physical criterion weight vector of shape (p,), where w_j > 0, sum(w_j) == 1.
    sigma : np.ndarray, optional
        Cohort standard deviation vector of shape (p,) for raw physical semantic mode.
    semantic_mode : str
        Semantic weighting mode: 'standardized_space' (or 'standardized') or
        'raw_physical' (or 'raw').

    Returns
    -------
    M_K : np.ndarray
        Symmetric positive-definite metric tensor of shape (K, K), read-only.
    W : np.ndarray
        Effective full-space weight matrix of shape (p, p), read-only.

    Raises
    ------
    ValueError
        If dimensions are incorrect or non-finite values are encountered.
    InvalidWeightVectorError
        If physical weights are non-positive or do not sum to 1.
    RankDeficientSubspaceError
        If V_K does not have full column rank K.
    NonPositiveDefiniteMetricError
        If M_K has non-positive eigenvalues.
    """
    V_arr = np.asarray(V_K, dtype=np.float64)
    w_arr = np.asarray(w_phys, dtype=np.float64)

    if V_arr.ndim != 2:
        raise ValueError(f"V_K must be a 2D matrix, got {V_arr.ndim}D.")

    p, K = V_arr.shape
    if p != 4:
        raise ValueError(f"V_K row dimension must equal 4 criteria, got {p}.")
    if K < 1 or K > p:
        raise ValueError(f"Retained dimension K must be in [1, {p}], got {K}.")

    if not np.all(np.isfinite(V_arr)):
        raise ValueError("V_K contains non-finite values (NaN or Inf).")

    # Column rank check
    rank_v = np.linalg.matrix_rank(V_arr)
    if rank_v < K:
        raise RankDeficientSubspaceError(
            f"V_K has deficient column rank {rank_v} < K={K}."
        )

    if w_arr.ndim != 1 or len(w_arr) != p:
        raise ValueError(f"Weight vector must be 1D of length {p}, got shape {w_arr.shape}.")

    if not np.all(np.isfinite(w_arr)):
        raise InvalidWeightVectorError("Physical weight vector contains non-finite values.")

    if np.any(w_arr <= 0.0):
        raise InvalidWeightVectorError(
            f"All physical criteria weights must be strictly positive (> 0), got: {w_arr}"
        )

    if not np.isclose(np.sum(w_arr), 1.0, atol=1e-5):
        raise InvalidWeightVectorError(
            f"Physical weights must sum to 1.0 within tolerance, got sum={np.sum(w_arr):.6f}"
        )

    # Effective full-space weight matrix W
    if semantic_mode in ("standardized_space", "standardized"):
        W = np.diag(w_arr)
    elif semantic_mode in ("raw_physical", "raw"):
        if sigma is not None:
            sig_arr = np.asarray(sigma, dtype=np.float64)
            if sig_arr.shape != (p,):
                raise ValueError(f"sigma must have shape ({p},), got {sig_arr.shape}.")
            W = np.diag(sig_arr * w_arr * sig_arr)
        else:
            W = np.diag(w_arr)
    else:
        raise ValueError(f"Unknown semantic_mode: '{semantic_mode}'.")

    # M_K = V_K^T @ W @ V_K
    M_K = V_arr.T @ W @ V_arr

    # Enforce exact symmetry within numerical tolerance
    M_K = 0.5 * (M_K + M_K.T)

    # Positive definiteness validation
    eigvals = np.linalg.eigvalsh(M_K)
    if np.any(eigvals <= 1e-12):
        raise NonPositiveDefiniteMetricError(
            f"Metric tensor M_K has non-positive eigenvalues: min eigval = {np.min(eigvals):.4e} <= 1e-12."
        )

    M_K_out = M_K.copy()
    M_K_out.flags.writeable = False

    W_out = W.copy()
    W_out.flags.writeable = False

    return M_K_out, W_out


def project_reference_points(
    z_plus: np.ndarray,
    z_minus: np.ndarray,
    V_K: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:
    """Project cohort-standardized reference points into the retained PCA subspace.

    Parameters
    ----------
    z_plus : np.ndarray
        Standardized physical ideal point (s+=[1,1,1,1]), shape (p,).
    z_minus : np.ndarray
        Standardized physical anti-ideal point (s-=[0,0,0,0]), shape (p,).
    V_K : np.ndarray
        Orthogonal projection basis matrix, shape (p, K).

    Returns
    -------
    t_plus : np.ndarray
        Projected physical ideal coordinates in subspace, shape (K,), read-only.
    t_minus : np.ndarray
        Projected physical anti-ideal coordinates in subspace, shape (K,), read-only.
    """
    z_p = np.asarray(z_plus, dtype=np.float64)
    z_m = np.asarray(z_minus, dtype=np.float64)
    V = np.asarray(V_K, dtype=np.float64)

    t_plus = z_p @ V
    t_minus = z_m @ V

    t_plus_out = t_plus.copy()
    t_plus_out.flags.writeable = False

    t_minus_out = t_minus.copy()
    t_minus_out.flags.writeable = False

    return t_plus_out, t_minus_out


def compute_distances_and_closeness(
    Z: np.ndarray,
    z_plus: np.ndarray,
    z_minus: np.ndarray,
    V_K: np.ndarray,
    M_K: np.ndarray,
    polymer_ids: Sequence[str] = None,
    epsilon_rank: float = 1e-12,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Compute projected metric distances, SP-PRP-TOPSIS closeness, and deterministic ranks.

    Parameters
    ----------
    Z : np.ndarray
        Cohort standardized decision matrix of shape (n, p).
    z_plus : np.ndarray
        Standardized physical ideal point of shape (p,).
    z_minus : np.ndarray
        Standardized physical anti-ideal point of shape (p,).
    V_K : np.ndarray
        Subspace basis matrix of shape (p, K).
    M_K : np.ndarray
        Subspace metric tensor of shape (K, K).
    polymer_ids : Sequence[str], optional
        Identifiers for deterministic tie-breaking (sorted alphabetically on tie).
    epsilon_rank : float
        Numerical tolerance below which two closeness scores are considered tied.

    Returns
    -------
    D_plus : np.ndarray
        Projected metric distances to physical ideal, shape (n,), read-only.
    D_minus : np.ndarray
        Projected metric distances to physical anti-ideal, shape (n,), read-only.
    C_L : np.ndarray
        SP-PRP-TOPSIS closeness coefficients D_minus / (D_plus + D_minus), shape (n,), read-only.
    ranks : np.ndarray
        1-based integer ranks (1 = top-ranked candidate), shape (n,), read-only.

    Raises
    ------
    MateriallyNegativeQuadraticFormError
        If a distance quadratic form is materially negative (< -1e-12).
    DegenerateReferenceCoincidenceError
        If D_plus + D_minus == 0 (candidate coincides with both ideal and anti-ideal).
    """
    Z_arr = np.asarray(Z, dtype=np.float64)
    V_arr = np.asarray(V_K, dtype=np.float64)
    M_arr = np.asarray(M_K, dtype=np.float64)

    n, p = Z_arr.shape
    K = V_arr.shape[1]

    # Project candidates and reference points
    T = Z_arr @ V_arr
    t_plus = np.asarray(z_plus, dtype=np.float64) @ V_arr
    t_minus = np.asarray(z_minus, dtype=np.float64) @ V_arr

    D_plus = np.zeros(n, dtype=np.float64)
    D_minus = np.zeros(n, dtype=np.float64)
    C_L = np.zeros(n, dtype=np.float64)

    for i in range(n):
        diff_plus = T[i] - t_plus
        diff_minus = T[i] - t_minus

        q_plus = float(diff_plus @ M_arr @ diff_plus)
        q_minus = float(diff_minus @ M_arr @ diff_minus)

        # Protect against numerical roundoff, block materially negative quadratic forms
        if q_plus < -1e-12 or q_minus < -1e-12:
            min_q = min(q_plus, q_minus)
            raise MateriallyNegativeQuadraticFormError(
                f"Materially negative quadratic form encountered for candidate {i}: "
                f"{min_q:.4e} < -1e-12. Metric tensor or projection is invalid."
            )

        d_p = np.sqrt(max(0.0, q_plus))
        d_m = np.sqrt(max(0.0, q_minus))

        denom = d_p + d_m
        if denom <= 1e-14:
            raise DegenerateReferenceCoincidenceError(
                f"Candidate {i} has D_plus + D_minus = {denom:.4e} <= 1e-14 "
                "(simultaneous coincidence with physical ideal and anti-ideal)."
            )

        cl = d_m / denom

        D_plus[i] = d_p
        D_minus[i] = d_m
        C_L[i] = np.clip(cl, 0.0, 1.0)

    # Deterministic ranking with tie-breaking
    # Higher C_L ranks ahead (smaller rank number). Ties within epsilon_rank broken by polymer_id ascending.
    items = []
    for idx in range(n):
        pid = str(polymer_ids[idx]) if polymer_ids is not None else f"{idx:05d}"
        items.append((C_L[idx], pid, idx))

    # Sort primarily by C_L descending
    items.sort(key=lambda x: -x[0])

    # Cluster tied candidates and sort alphabetically within cluster
    clustered = []
    i = 0
    while i < n:
        cluster = [items[i]]
        j = i + 1
        while j < n and abs(items[j][0] - items[i][0]) <= epsilon_rank:
            cluster.append(items[j])
            j += 1
        cluster.sort(key=lambda x: x[1])  # Sort by polymer_id ascending
        clustered.extend(cluster)
        i = j

    ranks = np.zeros(n, dtype=int)
    for rank_pos, (_, _, orig_idx) in enumerate(clustered, start=1):
        ranks[orig_idx] = rank_pos

    # Defensive copy and read-only sealing
    D_plus_out = D_plus.copy()
    D_plus_out.flags.writeable = False

    D_minus_out = D_minus.copy()
    D_minus_out.flags.writeable = False

    C_L_out = C_L.copy()
    C_L_out.flags.writeable = False

    ranks_out = ranks.copy()
    ranks_out.flags.writeable = False

    return D_plus_out, D_minus_out, C_L_out, ranks_out
