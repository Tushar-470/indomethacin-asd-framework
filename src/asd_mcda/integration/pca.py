"""
MANDATORY Principal Component Analysis (PCA) pre-processing module.
Aligned with Master Research Framework V2.0 Section 4.3 and Equation 10 (revised).
"""

from dataclasses import dataclass
import numpy as np
import pandas as pd
from typing import List, Tuple
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


@dataclass
class PCAResult:
    scores_matrix_t: pd.DataFrame
    loadings_matrix_p: pd.DataFrame
    explained_variance_ratio: np.ndarray
    cumulative_variance_ratio: np.ndarray
    n_components_retained: int
    is_effectively_one_dimensional: bool
    interpretation: List[str]


class PCAPreprocessor:
    """Applies StandardScaler and PCA to raw 5-score compatibility matrix S before CCI computation."""

    def __init__(self, variance_threshold: float = 0.95):
        self.variance_threshold = variance_threshold
        self.scaler = StandardScaler()
        self.pca_model: PCA = None

    def fit_transform(self, score_matrix_df: pd.DataFrame, score_cols: Optional[List[str]] = None) -> PCAResult:
        """
        Fit StandardScaler and PCA on score matrix.
        Retains principal components until cumulative variance >= variance_threshold.
        """
        if score_cols is None:
            score_cols = [c for c in score_matrix_df.columns if c in ["s_HSP", "s_chi", "s_desc", "s_GT", "s_lit"]]
            if not score_cols:
                score_cols = list(score_matrix_df.columns)
        raw_values = score_matrix_df[score_cols].values
        polymer_ids = score_matrix_df["polymer_id"].tolist() if "polymer_id" in score_matrix_df.columns else score_matrix_df.index.tolist()


        # Center and scale
        scaled_values = self.scaler.fit_transform(raw_values)

        # Fit full PCA first to determine retained components
        full_pca = PCA()
        full_pca.fit(scaled_values)
        cum_var = np.cumsum(full_pca.explained_variance_ratio_)
        
        k = int(np.argmax(cum_var >= self.variance_threshold) + 1)
        # Ensure k is bounded between 1 and min(N, 5)
        k = max(1, min(k, len(score_cols)))

        # Refit PCA with k components
        self.pca_model = PCA(n_components=k)
        t_matrix = self.pca_model.fit_transform(scaled_values)

        pc_cols = [f"PC{i+1}" for i in range(k)]
        df_scores_t = pd.DataFrame(t_matrix, columns=pc_cols, index=polymer_ids)


        df_loadings_p = pd.DataFrame(
            self.pca_model.components_.T, index=score_cols, columns=pc_cols
        )


        var_explained = self.pca_model.explained_variance_ratio_
        cum_var_retained = np.cumsum(var_explained)

        is_1d = (var_explained[0] >= 0.80) or (k == 1)

        # Generate interpretation text per PC
        interpretation = []
        for i in range(k):
            top_load = df_loadings_p[f"PC{i+1}"].abs().idxmax()
            pct = var_explained[i] * 100
            interpretation.append(
                f"PC{i+1} ({pct:.1f}% var): Dominated by {top_load} loading."
            )

        return PCAResult(
            scores_matrix_t=df_scores_t,
            loadings_matrix_p=df_loadings_p,
            explained_variance_ratio=var_explained,
            cumulative_variance_ratio=cum_var_retained,
            n_components_retained=k,
            is_effectively_one_dimensional=is_1d,
            interpretation=interpretation,
        )
