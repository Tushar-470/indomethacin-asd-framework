"""
WorkflowOrchestrator module coordinating the 11-step computational screening pipeline.
Aligned with Master Research Framework V2.0 Section 5 and SAS V1.0 Section 3.2.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
import numpy as np

from asd_mcda.configuration.loader import ConfigManager
from asd_mcda.drug.drug_profile import Drug
from asd_mcda.polymer.polymer_library import PolymerLibrary
from asd_mcda.compatibility.hsp_model import HSPModel
from asd_mcda.compatibility.flory_huggins import FloryHugginsModel
from asd_mcda.compatibility.gordon_taylor import GordonTaylorModel
from asd_mcda.compatibility.matrix import CompatibilityMatrix
from asd_mcda.integration.pca import PCAPreprocessor, PCAResult
from asd_mcda.integration.cci import CompositeCompatibilityIndex
from asd_mcda.mcda.ahp import AHPWeightElicitor, AHPResult
from asd_mcda.mcda.topsis import TOPSISRanker, TOPSISResult
from asd_mcda.prediction.predictor import FormulationPredictor, PredictionReport
from asd_mcda.validation.validator import FrameworkValidator, ValidationReport
from asd_mcda.uncertainty.monte_carlo import MonteCarloUQ, UQResult
from asd_mcda.sensitivity.oat import OATSensitivity, OATResult
from asd_mcda.sensitivity.morris import MorrisSensitivity, MorrisResult
from asd_mcda.reporting.report_generator import ReportGenerator
from asd_mcda.visualization.plotters import FigureGenerator
from asd_mcda.utils.logging_config import setup_logger


@dataclass
class WorkflowExecutionSummary:
    success: bool
    selected_polymer_id: str
    selected_polymer_name: str
    topsis_cl: float
    confidence_tier: str
    reports_generated: Dict[str, Path]
    figures_generated: List[Path]
    gate1_passed: bool
    gate2_passed: bool


class WorkflowOrchestrator:
    """End-to-end 11-step workflow orchestrator for the polymer screening pipeline."""

    def __init__(self, config_manager: ConfigManager):
        self.config_mgr = config_manager
        self.config = config_manager.raw_config
        self.logger = setup_logger(
            log_dir=self.config_mgr.get_log_dir(),
            level=10 if self.config.get("debug") else 20,
        )

    def run(self) -> WorkflowExecutionSummary:
        """Execute the 11-step screening pipeline."""
        self.logger.info("=== Starting ASD Computational Polymer Screening Workflow ===")

        # Step 1: Input Loading
        self.logger.info("Stage 1: Loading drug profile and polymer library...")
        drug_dict = self.config_mgr.load_drug_json()
        drug = Drug.from_dict(drug_dict)
        polymer_lib = PolymerLibrary.from_csv(self.config_mgr.get_polymer_library_path(), drug)
        self.logger.info(f"Loaded Drug: {drug.generic_name} ({drug.drug_id}), Polymer Library size: {len(polymer_lib)}")

        # Step 2 & 3: Descriptor Calculation
        self.logger.info("Stage 2-3: Descriptor calculation and verification...")

        # Step 4: HSP Scoring & Gate 1
        self.logger.info("Stage 4: HSP scoring and Gate 1 evaluation...")
        hsp_model = HSPModel(drug, polymer_lib)
        g1_res = hsp_model.check_gate1(
            red_threshold=self.config["gates"]["gate1_hsp_red_threshold"],
            min_passing=self.config["gates"]["gate1_min_passing_polymers"],
        )
        self.logger.info(g1_res.message)
        if not g1_res.passed:
            raise RuntimeError(f"Pipeline halted: {g1_res.message}")

        # Step 5 & 6: Flory-Huggins & Gordon-Taylor scoring
        self.logger.info("Stage 5-6: Flory-Huggins chi and Gordon-Taylor Tg calculation...")
        comp_matrix_builder = CompatibilityMatrix(
            drug,
            polymer_lib,
            drug_loading_ww=self.config["prediction"]["default_drug_loading_ww"],
        )
        df_S = comp_matrix_builder.build_matrix()
        self.logger.info("Raw normalized 5-score matrix S constructed.")

        # Step 7: PCA Pre-Processing & Evidence Integration
        self.logger.info("Stage 7: MANDATORY PCA pre-processing on score matrix S...")
        pca_preprocessor = PCAPreprocessor(
            variance_threshold=self.config["pca"]["variance_threshold"]
        )
        pca_result = pca_preprocessor.fit_transform(df_S)
        self.logger.info(
            f"PCA complete. Retained k={pca_result.n_components_retained} PCs explaining {pca_result.cumulative_variance_ratio[-1]*100:.1f}% cumulative variance."
        )

        # Step 8: Multi-Expert AHP & Gate 2 + TOPSIS Ranking
        self.logger.info("Stage 8: Multi-expert AHP weight derivation & TOPSIS ranking...")
        ahp_elicitor = AHPWeightElicitor(
            cr_max_threshold=self.config["gates"]["gate2_ahp_cr_max"]
        )

        # Load default fallback AHP matrix
        import json
        with open(self.config_mgr.get_ahp_matrix_dir() / "default_matrix.json", "r", encoding="utf-8") as f:
            ahp_raw = json.load(f)
        matrix_pc = np.array(ahp_raw["pairwise_matrix"])

        ahp_res = ahp_elicitor.aggregate_multi_expert_matrices([matrix_pc])
        weights_k = ahp_res.weights
        k_retained = pca_result.n_components_retained
        if len(weights_k) != k_retained:
            if len(weights_k) < k_retained:
                w_padded = np.pad(weights_k, (0, k_retained - len(weights_k)), mode='constant', constant_values=0.1)
                weights_k = w_padded / np.sum(w_padded)
            else:
                weights_k = weights_k[:k_retained] / np.sum(weights_k[:k_retained])

        self.logger.info(f"AHP weights derived for {k_retained} PCs: {weights_k}, CR = {ahp_res.cr:.4f}")

        # TOPSIS ranking
        topsis = TOPSISRanker()
        topsis_res = topsis.fit_predict(pca_result.scores_matrix_t, weights_k)
        df_ranking = topsis_res.ranking_table
        poly_name_map = {p.polymer_id: p.polymer_name for p in polymer_lib.polymers}
        poly_abbr_map = {p.polymer_id: p.abbreviation for p in polymer_lib.polymers}
        df_ranking["polymer_name"] = df_ranking["polymer_id"].map(poly_name_map)
        df_ranking["abbreviation"] = df_ranking["polymer_id"].map(poly_abbr_map)
        self.logger.info("TOPSIS ranking completed.")

        # Step 8b: Monte Carlo Uncertainty Quantification
        self.logger.info("Stage 8b: Monte Carlo Joint-Distribution UQ (N=10,000)...")
        uq_engine = MonteCarloUQ(
            drug,
            polymer_lib,
            n_iterations=self.config["uncertainty"]["monte_carlo_iterations"],
            random_seed=self.config["workflow"]["random_seed"],
        )
        uq_result = uq_engine.run(matrix_pc)
        self.logger.info(f"UQ complete. Selected polymer: {uq_result.selected_polymer_id}, Tier: {uq_result.confidence_tier}")

        # Step 8c: Sensitivity Analysis
        self.logger.info("Stage 8c: Sensitivity analysis (OAT + Morris screening)...")
        oat = OATSensitivity()
        oat_res = oat.analyze(pca_result.scores_matrix_t, ahp_res.weights)

        morris = MorrisSensitivity(r_trajectories=self.config["sensitivity"]["morris_trajectories"])
        morris_res = morris.analyze(pca_result.scores_matrix_t, k_retained)

        # Step 9: Layer 7 Predictions & Failure Boundary Mapping
        self.logger.info("Stage 9: Performance predictions and Failure Boundary Mapping...")
        predictor = FormulationPredictor(
            drug,
            polymer_lib,
            drug_loading_ww=self.config["prediction"]["default_drug_loading_ww"],
        )
        pred_report = predictor.predict_for_polymer(
            uq_result.selected_polymer_id, rank=1
        )

        # Step 10: Layer 8 Validation
        self.logger.info("Stage 10: Comparative validation and baseline evaluation...")
        validator = FrameworkValidator()
        val_report = validator.validate(df_ranking, df_S)

        # Step 11: Output Generation (Reports & Figures)
        self.logger.info("Stage 11: Generating reports and 300 DPI figures...")
        report_gen = ReportGenerator(self.config_mgr.get_output_dir() / "reports")
        reports = report_gen.generate_full_report(
            ranking_df=df_ranking,
            prediction_report=pred_report,
            validation_report=val_report,
            uq_result=uq_result,
            pca_result=pca_result,
        )

        fig_gen = FigureGenerator(self.config_mgr.get_output_dir() / "figures")
        figs = [
            fig_gen.plot_figure_6_ranking(df_ranking),
            fig_gen.plot_figure_7_sensitivity_morris(morris_res),
            fig_gen.plot_figure_8_uncertainty(uq_result, poly_name_map),
            fig_gen.plot_figure_11_pca_scree(pca_result),
            fig_gen.plot_figure_12_fbm_contour(pred_report.fbm_result),
        ]


        self.logger.info("=== Computational Polymer Screening Pipeline Completed Successfully ===")

        return WorkflowExecutionSummary(
            success=True,
            selected_polymer_id=pred_report.selected_polymer_id,
            selected_polymer_name=pred_report.selected_polymer_name,
            topsis_cl=float(df_ranking.iloc[0]["topsis_cl"]),
            confidence_tier=uq_result.confidence_tier,
            reports_generated=reports,
            figures_generated=figs,
            gate1_passed=g1_res.passed,
            gate2_passed=ahp_res.passed_gate2,
        )
