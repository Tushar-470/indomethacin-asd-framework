"""
Programmatic 300 DPI publication figure generator for the 12 framework figures.
Aligned with Master Research Framework V2.0 Section 13.
"""

from pathlib import Path
from typing import Dict, List, Optional, Union
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for headless CI/server rendering
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from asd_mcda.integration.pca import PCAResult
from asd_mcda.prediction.fbm import FBMResult
from asd_mcda.sensitivity.morris import MorrisResult
from asd_mcda.uncertainty.monte_carlo import UQResult


class FigureGenerator:
    """Generates publication-quality 300 DPI PNG figures."""

    def __init__(self, output_dir: Union[str, Path], dpi: int = 300):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.dpi = dpi

        # Set consistent styling
        plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
        plt.rcParams.update({
            "font.family": "sans-serif",
            "font.size": 10,
            "axes.titlesize": 12,
            "axes.labelsize": 11,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "legend.fontsize": 9,
            "figure.titlesize": 14,
        })

    def plot_figure_6_ranking(self, ranking_df: pd.DataFrame) -> Path:
        """Figure 6: AHP-TOPSIS Ranking bar chart (Closeness Coefficient CL)."""
        fig, ax = plt.subplots(figsize=(7, 4.5))

        df_sorted = ranking_df.sort_values(by="topsis_cl", ascending=True)
        y_pos = np.arange(len(df_sorted))
        cls = df_sorted["topsis_cl"].values
        labels = df_sorted["abbreviation"].values

        colors = ["#2b5c8f" if cl == max(cls) else "#4a90e2" for cl in cls]

        bars = ax.barh(y_pos, cls, color=colors, edgecolor="black", height=0.6)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels)
        ax.set_xlabel("TOPSIS Closeness Coefficient (CL)")
        ax.set_title("Figure 6: Candidate Polymer AHP-TOPSIS Ranking", fontweight="bold")
        ax.set_xlim(0.0, 1.0)

        for bar in bars:
            w = bar.get_width()
            ax.text(w + 0.02, bar.get_y() + bar.get_height() / 2.0, f"{w:.3f}", ha="left", va="center")

        plt.tight_layout()
        out_path = self.output_dir / "fig06_ahp_topsis_ranking.png"
        fig.savefig(out_path, dpi=self.dpi)
        plt.close(fig)
        return out_path

    def plot_figure_7_sensitivity_morris(self, morris_res: MorrisResult) -> Path:
        """Figure 7: Sensitivity Analysis Morris Scatter Plot (mu vs sigma)."""
        fig, ax = plt.subplots(figsize=(6, 5))

        mu = morris_res.mu
        sigma = morris_res.sigma
        labels = morris_res.feature_names

        ax.scatter(mu, sigma, color="#d9534f", s=100, zorder=5, edgecolor="black")

        for i, txt in enumerate(labels):
            ax.annotate(txt, (mu[i] + 0.005, sigma[i] + 0.002), fontsize=10, fontweight="bold")

        ax.axvline(0.10, color="gray", linestyle="--", alpha=0.7, label="Dominant Threshold (mu=0.10)")
        ax.axhline(0.05, color="gray", linestyle=":", alpha=0.7, label="Interactive Threshold (sigma=0.05)")

        ax.set_xlabel("Mean Elementary Effect (mu)")
        ax.set_ylabel("Standard Deviation of Elementary Effect (sigma)")
        ax.set_title("Figure 7: Morris Elementary Effects Sensitivity Plot", fontweight="bold")
        ax.legend(loc="upper right")

        plt.tight_layout()
        out_path = self.output_dir / "fig07_morris_sensitivity.png"
        fig.savefig(out_path, dpi=self.dpi)
        plt.close(fig)
        return out_path

    def plot_figure_8_uncertainty(self, uq_res: UQResult) -> Path:
        """Figure 8: Uncertainty Propagation Monte Carlo P(top-1) Bar Chart."""
        fig, ax = plt.subplots(figsize=(7, 4.5))

        p_top1 = uq_res.p_top1
        polys = list(p_top1.keys())
        probs = [p_top1[p] for p in polys]

        x_pos = np.arange(len(polys))
        ax.bar(x_pos, probs, color="#5cb85c", edgecolor="black", width=0.5)

        ax.axhline(0.70, color="#d9534f", linestyle="--", linewidth=1.5, label="High-Confidence Threshold (0.70)")
        ax.set_xticks(x_pos)
        ax.set_xticklabels(polys, rotation=30, ha="right")
        ax.set_ylabel("Decision Confidence Metric P(top-1)")
        ax.set_ylim(0.0, 1.0)
        ax.set_title(f"Figure 8: Joint-Distribution Monte Carlo UQ ({uq_res.confidence_tier})", fontweight="bold")
        ax.legend()

        plt.tight_layout()
        out_path = self.output_dir / "fig08_uncertainty_propagation.png"
        fig.savefig(out_path, dpi=self.dpi)
        plt.close(fig)
        return out_path

    def plot_figure_11_pca_scree(self, pca_res: PCAResult) -> Path:
        """Figure 11: PCA Scree Plot & Cumulative Variance."""
        fig, ax1 = plt.subplots(figsize=(6.5, 4.5))

        var_ratio = pca_res.explained_variance_ratio * 100
        cum_var = pca_res.cumulative_variance_ratio * 100
        pcs = [f"PC{i+1}" for i in range(len(var_ratio))]

        ax1.bar(pcs, var_ratio, color="#337ab7", alpha=0.8, label="Individual Variance (%)")
        ax1.set_ylabel("Explained Variance (%)", color="#337ab7")
        ax1.set_ylim(0, 100)

        ax2 = ax1.twinx()
        ax2.plot(pcs, cum_var, color="#d9534f", marker="o", linewidth=2, label="Cumulative Variance (%)")
        ax2.axhline(95.0, color="gray", linestyle="--", label="95% Target Threshold")
        ax2.set_ylabel("Cumulative Variance (%)", color="#d9534f")
        ax2.set_ylim(0, 105)

        ax1.set_title(f"Figure 11: PCA Scree Plot (Retained k={pca_res.n_components_retained} PCs)", fontweight="bold")

        plt.tight_layout()
        out_path = self.output_dir / "fig11_pca_scree_plot.png"
        fig.savefig(out_path, dpi=self.dpi)
        plt.close(fig)
        return out_path

    def plot_figure_12_fbm_contour(self, fbm_res: FBMResult) -> Path:
        """Figure 12: Logistic Regression Failure Boundary Map (FBM) 2D Contour Slice."""
        fig, ax = plt.subplots(figsize=(6.5, 5))

        # Generate 2D slice: Inlet Temperature (°C) vs Drug Loading (% w/w) at polymer_rank=1, feed_conc=10%
        temp_grid = np.linspace(80, 120, 50)
        load_grid = np.linspace(0.10, 0.50, 50)
        T, L = np.meshgrid(temp_grid, load_grid)

        # Evaluate model probability P(failure)
        # Features: [rank=1, temp, loading, conc=0.10]
        pts = np.c_[np.ones(T.size), T.ravel(), L.ravel(), np.full(T.size, 0.10)]
        P = fbm_res.model.predict_proba(pts)[:, 1].reshape(T.shape)

        cs = ax.contourf(T, L, P, levels=[0.0, 0.30, 0.70, 1.0], colors=["#5cb85c", "#f0ad4e", "#d9534f"], alpha=0.7)
        cbar = fig.colorbar(cs, ax=ax)
        cbar.set_label("P(Operational Failure)")

        contour_50 = ax.contour(T, L, P, levels=[0.50], colors="black", linewidths=2.0)
        ax.clabel(contour_50, fmt="P=0.50 Boundary", fontsize=10)

        ax.set_xlabel("Inlet Temperature (°C)")
        ax.set_ylabel("Drug Loading (mass fraction w/w)")
        ax.set_title("Figure 12: Logistic Regression Failure Boundary Map (FBM Contour)", fontweight="bold")

        plt.tight_layout()
        out_path = self.output_dir / "fig12_fbm_contour.png"
        fig.savefig(out_path, dpi=self.dpi)
        plt.close(fig)
        return out_path
