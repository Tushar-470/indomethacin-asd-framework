"""
TOPSIS (Technique for Order Preference by Similarity to Ideal Solution) ranker module.
Aligned with Master Research Framework V2.0 Section 8 and Equation 9.
"""

from dataclasses import dataclass
import numpy as np
import pandas as pd
from typing import List, Tuple


@dataclass
class TOPSISResult:
    ranking_table: pd.DataFrame
    ideal_distances_d_plus: np.ndarray
    anti_ideal_distances_d_minus: np.ndarray
    closeness_coefficients_cl: np.ndarray


class TOPSISRanker:
    """Ranks alternative polymers using Euclidean distances to ideal (A+) and anti-ideal (A-) solutions."""

    def fit_predict(
        self, decision_matrix_df: pd.DataFrame, weights: np.ndarray
    ) -> TOPSISResult:
        """
        Execute TOPSIS algorithm on decision matrix with given criterion weights.
        Equation 9 (Hwang & Yoon 1981).
        """
        polymer_ids = (
            decision_matrix_df["polymer_id"].tolist()
            if "polymer_id" in decision_matrix_df.columns
            else decision_matrix_df.index.tolist()
        )
        abbreviations = (
            decision_matrix_df["abbreviation"].tolist()
            if "abbreviation" in decision_matrix_df.columns
            else polymer_ids
        )

        score_cols = [
            c
            for c in decision_matrix_df.columns
            if c not in ["polymer_id", "abbreviation"]
        ]
        matrix = decision_matrix_df[score_cols].values.astype(float)

        n_samples, n_criteria = matrix.shape
        w = np.array(weights, dtype=float)
        w = w / np.sum(w)  # Ensure weights sum to 1

        # Step 1: Vector normalization
        norm_factors = np.sqrt(np.sum(matrix**2, axis=0))
        norm_factors[norm_factors == 0] = 1.0
        normalized_matrix = matrix / norm_factors

        # Step 2: Weighted normalized matrix
        weighted_matrix = normalized_matrix * w

        # Step 3: Determine ideal (A+) and anti-ideal (A-) solutions (assuming all criteria are benefit)
        ideal_a_plus = np.max(weighted_matrix, axis=0)
        anti_ideal_a_minus = np.min(weighted_matrix, axis=0)

        # Step 4: Calculate Euclidean distances D+ and D-
        d_plus = np.sqrt(np.sum((weighted_matrix - ideal_a_plus) ** 2, axis=1))
        d_minus = np.sqrt(np.sum((weighted_matrix - anti_ideal_a_minus) ** 2, axis=1))

        # Step 5: Closeness coefficient CL (Equation 9)
        denom = d_plus + d_minus
        denom[denom == 0] = 1e-9
        cl = d_minus / denom

        # Step 6: Rank determination (1 = highest CL)
        ranks = np.argsort(-cl).argsort() + 1

        df_result = pd.DataFrame(
            {
                "polymer_id": polymer_ids,
                "abbreviation": abbreviations,
                "topsis_ideal_distance": d_plus,
                "topsis_anti_ideal_distance": d_minus,
                "topsis_cl": cl,
                "topsis_rank": ranks,
            }
        )


        df_result.sort_values(by="topsis_rank", inplace=True)
        df_result.set_index("polymer_id", inplace=False)

        return TOPSISResult(
            ranking_table=df_result,
            ideal_distances_d_plus=d_plus,
            anti_ideal_distances_d_minus=d_minus,
            closeness_coefficients_cl=cl,
        )
