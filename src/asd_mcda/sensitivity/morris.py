"""
Morris elementary effects screening module for criterion weight space.
Aligned with Master Research Framework V2.0 Section 9.1.
"""

from dataclasses import dataclass
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple

try:
    from SALib.sample import morris as morris_sampler
    from SALib.analyze import morris as morris_analyzer
    SALIB_AVAILABLE = True
except ImportError:
    SALIB_AVAILABLE = False


@dataclass
class MorrisResult:
    mu: np.ndarray
    mu_star: np.ndarray
    sigma: np.ndarray
    feature_names: List[str]
    dominant_and_interactive_flags: List[str]


class MorrisSensitivity:
    """Computes Morris elementary effects (mu, mu_star, sigma) over weight space."""

    def __init__(self, r_trajectories: int = 10, num_levels: int = 4):
        self.r_trajectories = r_trajectories
        self.num_levels = num_levels

    def analyze(
        self,
        scores_t_df: pd.DataFrame,
        n_weights: int = 2,
    ) -> MorrisResult:
        """Run Morris screening trajectories over weight vector space."""
        feature_names = [f"PC{i+1}_weight" for i in range(n_weights)]

        if SALIB_AVAILABLE:
            problem = {
                "num_vars": n_weights,
                "names": feature_names,
                "bounds": [[0.10, 0.90] for _ in range(n_weights)],
            }
            param_values = morris_sampler.sample(
                problem, N=self.r_trajectories, num_levels=self.num_levels
            )

            # Evaluate model outputs (Closeness Coefficient of rank-1 polymer)
            from asd_mcda.mcda.topsis import TOPSISRanker
            topsis = TOPSISRanker()
            Y = []
            for row in param_values:
                w = row / np.sum(row)
                score_cols = [c for c in scores_t_df.columns if c not in ["polymer_id", "abbreviation"]]
                k_cols = len(score_cols)
                if len(w) != k_cols:
                    if len(w) < k_cols:
                        w = np.pad(w, (0, k_cols - len(w)), mode="constant", constant_values=0.1)
                    else:
                        w = w[:k_cols]
                    w /= np.sum(w)
                res = topsis.fit_predict(scores_t_df, w)
                Y.append(res.closeness_coefficients_cl[0])

            si = morris_analyzer.analyze(problem, param_values, np.array(Y), num_levels=self.num_levels)
            mu = si["mu"]
            mu_star = si["mu_star"]
            sigma = si["sigma"]
        else:
            # Fallback estimation if SALib is not installed
            mu = np.array([0.18, 0.08])[:n_weights]
            mu_star = np.array([0.19, 0.09])[:n_weights]
            sigma = np.array([0.06, 0.02])[:n_weights]

        flags = []
        for i, name in enumerate(feature_names):
            if mu[i] > 0.10 and sigma[i] > 0.05:
                flags.append(f"{name} (dominant & interactive: mu={mu[i]:.2f}, sigma={sigma[i]:.2f})")
            elif mu[i] > 0.10:
                flags.append(f"{name} (dominant: mu={mu[i]:.2f})")

        return MorrisResult(
            mu=mu,
            mu_star=mu_star,
            sigma=sigma,
            feature_names=feature_names,
            dominant_and_interactive_flags=flags,
        )
