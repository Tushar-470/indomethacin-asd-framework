"""
Composite Compatibility Index (CCI) calculation engine.
Aligned with Master Research Framework V2.0 Section 7 and Equation 10 (revised).
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple

from asd_mcda.integration.pca import PCAResult


class CompositeCompatibilityIndex:
    """Computes Composite Compatibility Index (CCI) and justification trace on retained principal components."""

    def __init__(self, pca_result: PCAResult, ahp_weights: np.ndarray):
        self.pca_result = pca_result
        self.ahp_weights = np.array(ahp_weights, dtype=float)

        if len(self.ahp_weights) != pca_result.n_components_retained:
            # Normalize or resize weights if dimension mismatch occurs
            if len(self.ahp_weights) > pca_result.n_components_retained:
                self.ahp_weights = self.ahp_weights[: pca_result.n_components_retained]
            else:
                self.ahp_weights = np.pad(
                    self.ahp_weights,
                    (0, pca_result.n_components_retained - len(self.ahp_weights)),
                    mode="constant",
                    constant_values=1.0 / pca_result.n_components_retained,
                )

        # Normalize weights to sum to 1
        w_sum = np.sum(self.ahp_weights)
        if w_sum > 0:
            self.ahp_weights /= w_sum

    def compute_cci(self) -> pd.DataFrame:
        """
        Compute CCI for each polymer as weighted sum of retained PC scores.
        Normalizes final CCI to [0, 1] range via min-max scaling for interpretability.
        """
        t_matrix = self.pca_result.scores_matrix_t
        raw_cci = t_matrix.values @ self.ahp_weights

        # Min-max scale raw CCI to [0, 1]
        c_min, c_max = np.min(raw_cci), np.max(raw_cci)
        if c_max > c_min:
            cci_norm = (raw_cci - c_min) / (c_max - c_min)
        else:
            cci_norm = np.full_like(raw_cci, 0.5)

        df = pd.DataFrame(
            {
                "polymer_id": t_matrix.index,
                "raw_cci_score": raw_cci,
                "cci_value": cci_norm,
            }
        )

        # Append per-PC contributions
        for j, col in enumerate(t_matrix.columns):
            df[f"cci_contrib_{col}"] = t_matrix[col].values * self.ahp_weights[j]

        df.set_index("polymer_id", inplace=False)
        return df

    def get_justification_trace(self) -> pd.DataFrame:
        """Return breakdown of per-PC contributions to CCI per polymer."""
        df = self.compute_cci()
        contrib_cols = [c for c in df.columns if c.startswith("cci_contrib_")]
        return df[["cci_value"] + contrib_cols]
