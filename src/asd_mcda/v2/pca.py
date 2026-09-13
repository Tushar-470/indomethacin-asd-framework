"""Ordinary Correlation PCA and Dynamic Dimension Selection (Step 2).

Authoritative Specification: 2.0.0-SPEC-PHASE0-PATCH2.
Constructs empirical correlation matrix R = (1/n) * Z^T @ Z, performs symmetric
spectral decomposition, canonicalizes eigenvector signs deterministically,
and selects the minimum K achieving cumulative explained variance >= 95%.
"""

from typing import Tuple
import numpy as np
import scipy.linalg


def canonicalize_eigenvector_sign(v: np.ndarray) -> np.ndarray:
    """Deterministically canonicalize eigenvector sign orientation.

    Identifies the element of largest absolute magnitude. If multiple elements
    share the maximum absolute value within 1e-12 tolerance, ties are broken
    by selecting the lowest index. The vector is flipped if that dominant
    element is negative, ensuring positive orientation.

    Parameters
    ----------
    v : np.ndarray
        1D eigenvector array of shape (p,).

    Returns
    -------
    v_canon : np.ndarray
        Deterministic canonicalized eigenvector, read-only.
    """
    v_arr = np.asarray(v, dtype=np.float64)
    if v_arr.ndim != 1:
        raise ValueError(f"Eigenvector must be 1D, got shape {v_arr.shape}.")

    abs_v = np.abs(v_arr)
    max_abs = np.max(abs_v)

    # Deterministic lowest-index tie-break within 1e-12
    tied_indices = np.where(np.abs(abs_v - max_abs) <= 1e-12)[0]
    lead_idx = int(tied_indices[0])

    if v_arr[lead_idx] < 0.0:
        v_canon = -v_arr.copy()
    else:
        v_canon = v_arr.copy()

    v_canon.flags.writeable = False
    return v_canon


def decompose_spectral(
    Z: np.ndarray,
    variance_threshold: float = 0.95,
) -> Tuple[np.ndarray, np.ndarray, int, float]:
    """Perform ordinary correlation PCA on standardized matrix Z.

    Parameters
    ----------
    Z : np.ndarray
        Standardized cohort decision matrix of shape (n, 4).
    variance_threshold : float
        Cumulative explained variance threshold for K selection (default 0.95).

    Returns
    -------
    eigenvalues : np.ndarray
        Sorted eigenvalues lambda_1 >= lambda_2 >= ... >= lambda_p >= 0, shape (p,), read-only.
    V : np.ndarray
        Orthogonal eigenvector matrix of shape (p, p) where column j is the j-th
        canonicalized eigenvector, read-only.
    K : int
        Minimum number of retained principal components achieving cumulative variance >= 0.95.
    cumulative_variance : float
        Cumulative explained variance at retained K.
    """
    Z_arr = np.asarray(Z, dtype=np.float64)
    if Z_arr.ndim != 2:
        raise ValueError(f"Standardized matrix Z must be 2D, got shape {Z_arr.shape}.")

    n, p = Z_arr.shape
    if p != 4:
        raise ValueError(f"Standardized matrix Z must have 4 criteria columns, got {p}.")

    # Empirical correlation matrix: R = (1/n) * Z^T @ Z
    R = (Z_arr.T @ Z_arr) / float(n)

    # Symmetric eigendecomposition via scipy.linalg.eigh
    eigvals, eigvecs = scipy.linalg.eigh(R)

    # Sort in descending order: lambda_1 >= lambda_2 >= ... >= lambda_p
    idx_desc = np.argsort(eigvals)[::-1]
    eigvals_desc = np.maximum(eigvals[idx_desc], 0.0)
    eigvecs_desc = eigvecs[:, idx_desc]

    # Canonicalize each column
    V_canon = np.zeros_like(eigvecs_desc)
    for j in range(p):
        V_canon[:, j] = canonicalize_eigenvector_sign(eigvecs_desc[:, j])

    # Dynamic K selection: minimum K where cum_var >= variance_threshold
    total_var = float(p)
    cum_var_curve = np.cumsum(eigvals_desc) / total_var

    K = p
    for k in range(1, p + 1):
        if cum_var_curve[k - 1] >= variance_threshold - 1e-12:
            K = k
            break

    cum_var_selected = float(cum_var_curve[K - 1])

    # Defensive copy and read-only sealing
    eigvals_out = eigvals_desc.copy()
    eigvals_out.flags.writeable = False

    V_out = V_canon.copy()
    V_out.flags.writeable = False

    return eigvals_out, V_out, int(K), cum_var_selected
