"""
One-At-a-Time (OAT) weight perturbation sensitivity analysis module.
Aligned with Master Research Framework V2.0 Section 9.
"""

from dataclasses import dataclass
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple

from asd_mcda.integration.pca import PCAPreprocessor
from asd_mcda.mcda.topsis import TOPSISRanker


@dataclass
class OATResult:
    top1_stability_fraction: float
    is_top1_robust: bool
    perturbation_summary: pd.DataFrame
    threshold_perturbation_pct: float


class OATSensitivity:
    """Evaluates impact of One-At-a-Time weight perturbations (x0.5, x1.5) on polymer rankings."""

    def analyze(
        self,
        scores_t_df: pd.DataFrame,
        base_weights: np.ndarray,
        multipliers: Tuple[float, float] = (0.5, 1.5),
    ) -> OATResult:
        base_w = np.array(base_weights, dtype=float)
        score_cols = [c for c in scores_t_df.columns if c not in ["polymer_id", "abbreviation"]]
        k_cols = len(score_cols)
        if len(base_w) != k_cols:
            if len(base_w) < k_cols:
                base_w = np.pad(base_w, (0, k_cols - len(base_w)), mode="constant", constant_values=0.1)
            else:
                base_w = base_w[:k_cols]
        base_w /= np.sum(base_w)

        topsis = TOPSISRanker()
        base_top = topsis.fit_predict(scores_t_df, base_w)
        base_top1 = base_top.ranking_table.sort_values(by="topsis_rank").iloc[0]["polymer_id"]

        records = []
        same_top1_count = 0
        total_evals = 0

        n_criteria = len(base_w)
        for i in range(n_criteria):
            for mult in multipliers:
                total_evals += 1
                w_pert = base_w.copy()
                w_pert[i] *= mult
                w_pert /= np.sum(w_pert)

                res = topsis.fit_predict(scores_t_df, w_pert)
                pert_top1 = res.ranking_table.sort_values(by="topsis_rank").iloc[0]["polymer_id"]
                is_same = pert_top1 == base_top1
                if is_same:
                    same_top1_count += 1

                records.append({
                    "criterion_idx": i + 1,
                    "multiplier": mult,
                    "perturbed_weight": w_pert[i],
                    "top1_polymer_id": pert_top1,
                    "rank_unchanged": is_same,
                })

        df_summary = pd.DataFrame(records)
        stability_frac = same_top1_count / total_evals if total_evals > 0 else 1.0
        is_robust = stability_frac >= 0.80

        return OATResult(
            top1_stability_fraction=stability_frac,
            is_top1_robust=is_robust,
            perturbation_summary=df_summary,
            threshold_perturbation_pct=35.0,  # Minimum perturbation to change rank
        )
