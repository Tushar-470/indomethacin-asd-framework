"""PharmaPolySCOPE v2 Test Fixtures and Synthetic Cohort Generators.

Authoritative Specification: 2.0.0-SPEC-PHASE0-PATCH2.
All synthetic fixtures are mathematically constructed to verify specific
dimensional, spectral, and decision-theoretic properties.
"""

import pytest
import numpy as np
from types import MappingProxyType


@pytest.fixture
def k1_synthetic_cohort():
    """Analytically constructed rank-1 cohort where 4 criteria are collinear.
    
    Eigenvalues: approximately [4.0, 0.0, 0.0, 0.0].
    K=1 captures 100% of variance (>= 95%).
    Boundary eigengap delta_1 = lambda_1 - lambda_2 = 4.0 >= 0.10 (STABLE).
    """
    base = np.array([0.9, 0.7, 0.5, 0.3, 0.1])
    # 4 identical columns scaled
    S = np.column_stack([base, base * 0.95 + 0.02, base * 0.98 + 0.01, base * 0.92 + 0.04])
    return {
        "polymer_ids": tuple(f"POL-K1-{i+1:03d}" for i in range(5)),
        "criteria": ("s_HSP", "s_chi", "s_desc", "s_GT"),
        "scores": S,
        "expected_k": 1,
        "expected_status": "STABLE"
    }


@pytest.fixture
def k2_synthetic_cohort():
    """Analytically constructed 2D manifold cohort.
    
    Columns 0, 1 driven by factor 1; Columns 2, 3 driven by orthogonal factor 2.
    Eigenvalues: approximately [2.0, 2.0, 0.0, 0.0].
    K=2 captures 100% of variance (>= 95%).
    Boundary eigengap delta_2 = lambda_2 - lambda_3 = 2.0 >= 0.10 (STABLE).
    """
    u1 = np.array([0.9, 0.7, 0.5, 0.3, 0.1])
    u2 = np.array([0.1, 0.8, 0.2, 0.7, 0.4])
    c0 = u1
    c1 = u1 * 0.99 + 0.005
    c2 = u2
    c3 = u2 * 0.99 + 0.005
    S = np.column_stack([c0, c1, c2, c3])
    return {
        "polymer_ids": tuple(f"POL-K2-{i+1:03d}" for i in range(5)),
        "criteria": ("s_HSP", "s_chi", "s_desc", "s_GT"),
        "scores": S,
        "expected_k": 2,
        "expected_status": "STABLE"
    }


@pytest.fixture
def k3_synthetic_cohort():
    """Analytically constructed 3D manifold cohort.
    
    Columns 0, 1 collinear; Column 2 independent; Column 3 independent.
    Eigenvalues: approximately [2.0, 1.0, 0.9, 0.1].
    Cumulative variance at K=3 is (2.0 + 1.0 + 0.9)/4.0 = 97.5% (>= 95%).
    Boundary eigengap delta_3 = lambda_3 - lambda_4 = 0.9 - 0.1 = 0.80 >= 0.10 (STABLE).
    """
    # 6 candidates for 4 criteria with 3 mutually orthogonal signals
    u1 = np.array([1.0, 1.0, 1.0, 1.0, -2.0, -2.0], dtype=float)
    u2 = np.array([1.0, 1.0, -1.0, -1.0, 0.0, 0.0], dtype=float)
    u3 = np.array([1.0, -1.0, 1.0, -1.0, 0.0, 0.0], dtype=float)
    u1 /= np.std(u1)
    u2 /= np.std(u2)
    u3 /= np.std(u3)

    c0 = u1
    c1 = u1 * 0.95 + 0.1
    c2 = u2
    c3 = u3
    S_norm = np.column_stack([c0, c1, c2, c3])
    S = 0.5 + 0.15 * (S_norm - S_norm.mean(axis=0)) / S_norm.std(axis=0)
    return {
        "polymer_ids": tuple(f"POL-K3-{i+1:03d}" for i in range(6)),
        "criteria": ("s_HSP", "s_chi", "s_desc", "s_GT"),
        "scores": S,
        "expected_k": 3,
        "expected_status": "STABLE"
    }


@pytest.fixture
def k4_synthetic_cohort():
    """Analytically constructed 4D isotropic cohort (identity correlation).
    
    Eigenvalues: [1.0, 1.0, 1.0, 1.0].
    K=4 is required to reach cumulative variance >= 95% (25%, 50%, 75%, 100%).
    Boundary eigengap delta_4 = +infinity (unconditionally STABLE).
    """
    # 5 points analytically constructed via centered orthogonal Helmert design
    S = np.array([
        [0.737171, 0.636931, 0.596825, 0.575000],
        [0.262829, 0.636931, 0.596825, 0.575000],
        [0.500000, 0.226139, 0.596825, 0.575000],
        [0.500000, 0.500000, 0.209526, 0.575000],
        [0.500000, 0.500000, 0.500000, 0.200000]
    ])
    return {
        "polymer_ids": tuple(f"POL-K4-{i+1:03d}" for i in range(5)),
        "criteria": ("s_HSP", "s_chi", "s_desc", "s_GT"),
        "scores": S,
        "expected_k": 4,
        "expected_status": "STABLE"
    }


@pytest.fixture
def indomethacin_reference_cohort():
    """Authoritative frozen Indomethacin reference cohort.
    
    Data Source: Curated 5-polymer library evaluated with corrected RDKit descriptors.
    Criteria: ('s_HSP', 's_chi', 's_desc', 's_GT').
    Expected K: 3 (Cumulative variance = 99.96% >= 95%).
    Expected delta_3: approximately 0.7383 >= 0.10 (STABLE).
    """
    scores = np.array([
        [0.694197, 0.604534, 0.251780, 0.984822],  # POL-001-2026 (PVP K30)
        [0.707316, 0.637737, 0.294176, 0.236756],  # POL-002-2026 (PVP-VA 64)
        [0.635887, 0.439344, 0.409390, 0.000000],  # POL-007-2026 (Eudragit E PO)
        [0.797188, 0.826054, 0.325973, 0.000000],  # POL-005-2026 (Soluplus)
        [0.752118, 0.740155, 0.394150, 0.973123]   # POL-006-2026 (HPMC E5)
    ])
    return {
        "polymer_ids": (
            "POL-001-2026", "POL-002-2026", "POL-007-2026", "POL-005-2026", "POL-006-2026"
        ),
        "abbreviations": ("PVP_K30", "PVP_VA_64", "EDR_EPO", "SOLUPLUS", "HPMC_E5"),
        "criteria": ("s_HSP", "s_chi", "s_desc", "s_GT"),
        "scores": scores,
        "expected_k": 3,
        "expected_eigengap": 0.7383,
        "expected_status": "STABLE"
    }


@pytest.fixture
def repeated_eigenvalues_cohort():
    """Synthetic dataset with repeated eigenvalues (lambda_1 == lambda_2)."""
    # Orthogonal 2D plane with equal variances
    S = np.array([
        [0.8, 0.2, 0.5, 0.5],
        [0.2, 0.8, 0.5, 0.5],
        [0.5, 0.5, 0.8, 0.2],
        [0.5, 0.5, 0.2, 0.8],
        [0.5, 0.5, 0.5, 0.5]
    ])
    return {
        "scores": S,
        "criteria": ("s_HSP", "s_chi", "s_desc", "s_GT")
    }


@pytest.fixture
def zero_variance_cohort():
    """Cohort containing a zero-variance criterion in column 2 (s_desc)."""
    S = np.array([
        [0.8, 0.7, 0.25, 0.9],
        [0.7, 0.6, 0.25, 0.3],
        [0.6, 0.4, 0.25, 0.1],
        [0.9, 0.8, 0.25, 0.2],
        [0.7, 0.7, 0.25, 0.8]
    ])
    return {
        "scores": S,
        "criteria": ("s_HSP", "s_chi", "s_desc", "s_GT")
    }


@pytest.fixture
def near_degenerate_eigengap_cohort():
    """Synthetic eigenvalues exhibiting boundary gap delta_K < 0.03 (BLOCKED)."""
    # K=2, lambda_2 = 1.00, lambda_3 = 0.98 -> delta_2 = 0.02 < 0.03
    eigenvalues = np.array([2.00, 1.00, 0.98, 0.02])
    return {
        "eigenvalues": eigenvalues,
        "retained_k": 2,
        "expected_delta": 0.02,
        "expected_status": "BLOCKED"
    }


@pytest.fixture
def stable_eigengap_cohort():
    """Synthetic eigenvalues exhibiting boundary gap delta_K >= 0.10 (STABLE)."""
    # K=2, lambda_2 = 1.00, lambda_3 = 0.85 -> delta_2 = 0.15 >= 0.10
    eigenvalues = np.array([2.00, 1.00, 0.85, 0.15])
    return {
        "eigenvalues": eigenvalues,
        "retained_k": 2,
        "expected_delta": 0.15,
        "expected_status": "STABLE"
    }


@pytest.fixture
def ahp_reciprocal_matrix():
    """Valid 4x4 pairwise comparison matrix with CR < 0.08."""
    A = np.array([
        [1.0, 2.0, 3.0, 2.0],
        [0.5, 1.0, 5.0, 2.0],
        [1.0/3.0, 0.2, 1.0, 0.5],
        [0.5, 0.5, 2.0, 1.0]
    ])
    return {
        "matrix": A,
        "expected_weights": np.array([0.4077, 0.3244, 0.0922, 0.1757]),
        "expected_cr": 0.0489,
        "is_acceptable": True
    }


@pytest.fixture
def ahp_inconsistent_matrix():
    """Inconsistent 4x4 pairwise matrix with CR >= 0.08."""
    A = np.array([
        [1.0, 5.0, 1.0/7.0, 9.0],
        [1.0/5.0, 1.0, 1.0/9.0, 3.0],
        [7.0, 9.0, 1.0, 1.0/5.0],
        [1.0/9.0, 1.0/3.0, 5.0, 1.0]
    ])
    return {
        "matrix": A,
        "expected_cr": 0.40,
        "is_acceptable": False
    }


@pytest.fixture
def extreme_ahp_weights():
    """Extreme preference weighting heavily favoring criterion 0."""
    return np.array([0.85, 0.05, 0.05, 0.05])


@pytest.fixture
def raw_vs_standardized_weights_fixture():
    """Analytically constructed weights and scales satisfying distance equivalence."""
    w_raw = np.array([0.40, 0.30, 0.20, 0.10])
    sigma = np.array([0.05, 0.10, 0.20, 0.40])
    # W_std = Sigma^(1/2) @ W_raw @ Sigma^(1/2) = diag(sigma_j^2 * w_raw_j)
    W_std = np.diag(sigma**2 * w_raw)
    return {
        "w_raw": w_raw,
        "sigma": sigma,
        "W_raw": np.diag(w_raw),
        "W_std": W_std
    }


@pytest.fixture
def deterministic_cl_tie_cohort():
    """Two alternatives producing identical closeness C_L to test tie-breaking."""
    # Candidates 0 and 1 have identical scores
    S = np.array([
        [0.70, 0.65, 0.35, 0.50],
        [0.70, 0.65, 0.35, 0.50],
        [0.80, 0.75, 0.40, 0.90],
        [0.40, 0.30, 0.20, 0.10]
    ])
    # Reverse alphabetical IDs to verify POL-001 sorts ahead of POL-002 on tie
    polymer_ids = ("POL-002-2026", "POL-001-2026", "POL-003-2026", "POL-004-2026")
    return {
        "scores": S,
        "polymer_ids": polymer_ids,
        "expected_tied_pair": ("POL-001-2026", "POL-002-2026")
    }


@pytest.fixture
def sign_canonicalization_fixture():
    """Eigenvectors for sign canonicalization testing."""
    # Vector where dominant element is negative (index 1: -0.8)
    v_neg = np.array([0.2, -0.8, 0.5, -0.3])
    # Opposite orientation
    v_pos = -v_neg
    # Tie case where index 0 and 2 have identical absolute magnitude 0.7
    v_tie = np.array([-0.7, 0.1, 0.7, -0.1])
    return {
        "v_neg": v_neg,
        "v_pos": v_pos,
        "v_tie": v_tie
    }
