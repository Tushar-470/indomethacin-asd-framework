"""
Analytic Hierarchy Process (AHP) weight elicitation engine.
Aligned with Master Research Framework V2.0 Section 8 and Equation 8.
"""

from dataclasses import dataclass
import numpy as np
from scipy.stats import kendalltau
from typing import Dict, List, Optional, Tuple

from asd_mcda.utils.constants import AHP_RANDOM_INDEX, DEFAULT_AHP_CR_MAX


@dataclass
class AHPResult:
    weights: np.ndarray
    lambda_max: float
    ci: float
    cr: float
    passed_gate2: bool
    is_multi_expert: bool
    kendall_w: Optional[float]
    individual_crs: List[float]


class AHPWeightElicitor:
    """Derives criterion weights via principal eigenvector method with consistency ratio CR check and geometric-mean aggregation."""

    def __init__(self, cr_max_threshold: float = DEFAULT_AHP_CR_MAX):
        self.cr_max_threshold = cr_max_threshold

    def calculate_single_matrix_weights(self, matrix: np.ndarray) -> Tuple[np.ndarray, float, float, float]:
        """
        Calculate principal eigenvector weight vector, lambda_max, CI, and CR for a single pairwise matrix.
        Equation 8 (Saaty 1980).
        """
        n = matrix.shape[0]
        if n == 1:
            return np.array([1.0]), 1.0, 0.0, 0.0

        eigenvalues, eigenvectors = np.linalg.eig(matrix)
        max_idx = np.argmax(np.real(eigenvalues))
        lambda_max = float(np.real(eigenvalues[max_idx]))
        
        principal_vector = np.real(eigenvectors[:, max_idx])
        weights = principal_vector / np.sum(principal_vector)

        ci = (lambda_max - n) / (n - 1) if n > 1 else 0.0
        ri = AHP_RANDOM_INDEX.get(n, 1.12)
        cr = ci / ri if ri > 0 else 0.0

        return weights, lambda_max, float(ci), float(cr)

    def aggregate_multi_expert_matrices(
        self, matrices: List[np.ndarray]
    ) -> AHPResult:
        """
        Multi-expert AHP: Geometric-mean aggregation across 3-5 expert comparison matrices.
        Computes Kendall's W coefficient of concordance across expert weight vectors.
        """
        n_experts = len(matrices)
        if n_experts == 0:
            raise ValueError("No pairwise matrices provided for AHP elicitation.")

        individual_weights = []
        individual_crs = []

        for m in matrices:
            w, _, _, cr = self.calculate_single_matrix_weights(m)
            individual_weights.append(w)
            individual_crs.append(cr)

        # Geometric mean aggregation across experts per matrix element
        n = matrices[0].shape[0]
        agg_matrix = np.ones((n, n), dtype=float)

        for i in range(n):
            for j in range(n):
                product = np.prod([m[i, j] for m in matrices])
                agg_matrix[i, j] = product ** (1.0 / n_experts)

        # Re-derive weights from aggregated matrix
        consolidated_weights, lambda_max, ci, agg_cr = self.calculate_single_matrix_weights(agg_matrix)

        # Calculate Kendall's W across expert weight ranks
        kendall_w = self._compute_kendalls_w(individual_weights) if n_experts >= 2 else 1.0

        passed = (agg_cr <= self.cr_max_threshold) and all(cr <= self.cr_max_threshold for cr in individual_crs)

        return AHPResult(
            weights=consolidated_weights,
            lambda_max=lambda_max,
            ci=ci,
            cr=agg_cr,
            passed_gate2=passed,
            is_multi_expert=n_experts > 1,
            kendall_w=kendall_w,
            individual_crs=individual_crs,
        )

    def _compute_kendalls_w(self, weight_vectors: List[np.ndarray]) -> float:
        """Compute Kendall's coefficient of concordance W for inter-expert agreement."""
        m = len(weight_vectors)
        n = len(weight_vectors[0])
        if m < 2 or n < 2:
            return 1.0

        # Rank transform each weight vector
        ranks = np.array([np.argsort(np.argsort(-w)) + 1 for w in weight_vectors])
        r_i = np.sum(ranks, axis=0)
        r_bar = np.mean(r_i)

        s = np.sum((r_i - r_bar) ** 2)
        w = (12.0 * s) / (m**2 * (n**3 - n))
        return float(np.clip(w, 0.0, 1.0))
