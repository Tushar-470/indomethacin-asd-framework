"""
Engine Adapter: Bridge between FastAPI API layer and frozen asd_mcda computational engine.

CRITICAL: This module IMPORTS and CALLS the existing asd_mcda package.
It does NOT duplicate any scientific calculations.
All thermodynamic models, MCDA algorithms, and statistical methods
come exclusively from src/asd_mcda/.
"""

import json
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import yaml

# Direct imports from the FROZEN scientific engine
from asd_mcda.__version__ import __version__ as ENGINE_VERSION
from asd_mcda.configuration.loader import ConfigManager
from asd_mcda.drug.drug_profile import Drug
from asd_mcda.polymer.polymer_library import Polymer, PolymerLibrary
from asd_mcda.compatibility.hsp_model import HSPModel
from asd_mcda.compatibility.matrix import CompatibilityMatrix
from asd_mcda.integration.pca import PCAPreprocessor
from asd_mcda.mcda.ahp import AHPWeightElicitor
from asd_mcda.mcda.topsis import TOPSISRanker
from asd_mcda.prediction.predictor import FormulationPredictor
from asd_mcda.validation.validator import FrameworkValidator
from asd_mcda.uncertainty.monte_carlo import MonteCarloUQ
from asd_mcda.sensitivity.oat import OATSensitivity
from asd_mcda.sensitivity.morris import MorrisSensitivity
from asd_mcda.reporting.report_generator import ReportGenerator
from asd_mcda.visualization.plotters import FigureGenerator
from asd_mcda.utils.helpers import generate_sha256

from backend.services import history_db


# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
ANALYSES_DIR = PROJECT_ROOT / "data" / "analyses"
CONFIG_DIR = PROJECT_ROOT / "config"
REFERENCE_DRUG_DIR = CONFIG_DIR / "drugs"
USER_DRUG_DIR = PROJECT_ROOT / "data" / "user_drugs"
REFERENCE_POLYMER_CSV = CONFIG_DIR / "polymers" / "polymer_library_v3_five_polymers.csv"

USER_POLYMER_CSV = PROJECT_ROOT / "data" / "user_polymers.csv"
AHP_MATRIX_DIR = CONFIG_DIR / "ahp"
BASE_WORKFLOW_CONFIG = CONFIG_DIR / "workflow" / "workflow_config.yaml"


def get_engine_version() -> str:
    """Return the frozen engine version string."""
    return ENGINE_VERSION


# ── Drug Management ───────────────────────────────────────────────────────────

def list_drugs() -> List[Dict[str, Any]]:
    """List all available drug profiles from reference and user directories."""
    drugs = []
    # Reference drugs
    if REFERENCE_DRUG_DIR.exists():
        for f in REFERENCE_DRUG_DIR.glob("*.json"):
            with open(f, "r", encoding="utf-8") as fp:
                data = json.load(fp)
                data["is_reference"] = True
                drugs.append(data)
    # User drugs
    USER_DRUG_DIR.mkdir(parents=True, exist_ok=True)
    for f in USER_DRUG_DIR.glob("*.json"):
        with open(f, "r", encoding="utf-8") as fp:
            data = json.load(fp)
            data["is_reference"] = False
            drugs.append(data)
    return drugs


def get_drug(drug_id: str) -> Optional[Dict[str, Any]]:
    """Get a single drug profile by ID."""
    for d in list_drugs():
        if d.get("drug_id") == drug_id:
            return d
    return None


def save_drug(data: Dict[str, Any]) -> Dict[str, Any]:
    """Save a new user drug profile."""
    USER_DRUG_DIR.mkdir(parents=True, exist_ok=True)
    drug_id = data["drug_id"]
    filename = f"{drug_id.lower().replace(' ', '_')}.json"
    path = USER_DRUG_DIR / filename
    data["validation_status"] = data.get("validation_status", "draft")
    data["reference_source"] = data.get("reference_source", "user_entered")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    data["is_reference"] = False
    return data


def delete_drug(drug_id: str) -> bool:
    """Delete a user-created drug (never deletes reference drugs)."""
    for f in USER_DRUG_DIR.glob("*.json"):
        with open(f, "r", encoding="utf-8") as fp:
            data = json.load(fp)
            if data.get("drug_id") == drug_id:
                f.unlink()
                return True
    return False


# ── Polymer Management ────────────────────────────────────────────────────────

def _read_reference_polymers() -> pd.DataFrame:
    """Read the authoritative reference polymer library CSV."""
    if REFERENCE_POLYMER_CSV.exists():
        return pd.read_csv(REFERENCE_POLYMER_CSV)
    return pd.DataFrame()


def _read_user_polymers() -> pd.DataFrame:
    """Read user-added polymers CSV."""
    if USER_POLYMER_CSV.exists():
        return pd.read_csv(USER_POLYMER_CSV)
    return pd.DataFrame()


def _save_user_polymers(df: pd.DataFrame) -> None:
    """Save user polymers CSV."""
    USER_POLYMER_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(USER_POLYMER_CSV, index=False)


def list_polymers() -> List[Dict[str, Any]]:
    """List all polymers from reference and user libraries."""
    polymers = []
    ref_df = _read_reference_polymers()
    for _, row in ref_df.iterrows():
        d = row.to_dict()
        d["is_reference"] = True
        # Convert NaN to None
        d = {k: (None if pd.isna(v) else v) for k, v in d.items()}
        polymers.append(d)

    user_df = _read_user_polymers()
    for _, row in user_df.iterrows():
        d = row.to_dict()
        d["is_reference"] = False
        d = {k: (None if pd.isna(v) else v) for k, v in d.items()}
        polymers.append(d)

    return polymers


def get_polymer(polymer_id: str) -> Optional[Dict[str, Any]]:
    """Get a single polymer by ID."""
    for p in list_polymers():
        if p.get("polymer_id") == polymer_id:
            return p
    return None


def save_polymer(data: Dict[str, Any]) -> Dict[str, Any]:
    """Save a new user polymer (appends to user CSV, never modifies reference CSV)."""
    user_df = _read_user_polymers()

    # Compute hsp_total if not provided
    dd = float(data.get("hsp_delta_d", 0))
    dp = float(data.get("hsp_delta_p", 0))
    dh = float(data.get("hsp_delta_h", 0))
    if not data.get("hsp_total"):
        data["hsp_total"] = round((dd**2 + dp**2 + dh**2) ** 0.5, 1)

    new_row = pd.DataFrame([data])
    user_df = pd.concat([user_df, new_row], ignore_index=True)
    _save_user_polymers(user_df)
    data["is_reference"] = False
    return data


def delete_polymer(polymer_id: str) -> bool:
    """Delete a user-created polymer (never deletes reference polymers)."""
    user_df = _read_user_polymers()
    if user_df.empty:
        return False
    mask = user_df["polymer_id"] == polymer_id
    if mask.any():
        user_df = user_df[~mask]
        _save_user_polymers(user_df)
        return True
    return False


# ── Screening Engine ──────────────────────────────────────────────────────────

def run_screening(
    drug_id: str,
    polymer_ids: List[str],
    mode: str = "exploratory",
    drug_loading_ww: float = 0.30,
    random_seed: int = 42,
) -> Dict[str, Any]:
    """
    Execute the full asd_mcda computational screening pipeline.

    This function:
    1. Loads drug and selected polymers from config/data files
    2. Creates a temporary workspace with proper config files
    3. Calls the existing WorkflowOrchestrator or runs the pipeline steps directly
    4. Collects all results into a structured response
    5. Saves analysis to history for provenance tracking
    """
    analysis_id = f"ANA-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"
    warnings_list: List[str] = []

    # 1. Load drug profile
    drug_data = get_drug(drug_id)
    if drug_data is None:
        raise ValueError(f"Drug profile not found: {drug_id}")

    # Remove non-standard fields before passing to engine
    drug_data_clean = {k: v for k, v in drug_data.items() if k != "is_reference"}
    drug = Drug.from_dict(drug_data_clean)

    # 2. Build filtered polymer library from selected IDs
    all_polymers = list_polymers()
    selected_polymer_dicts = [p for p in all_polymers if p.get("polymer_id") in polymer_ids]

    if len(selected_polymer_dicts) < 2:
        raise ValueError(f"Need at least 2 polymers, found {len(selected_polymer_dicts)} matching IDs.")

    # Check for unvalidated data in research mode
    if mode == "research":
        for p in selected_polymer_dicts:
            if p.get("validation_status") != "validated":
                raise ValueError(
                    f"Research mode requires validated polymers. "
                    f"Polymer {p.get('polymer_id')} has status '{p.get('validation_status')}'."
                )
        if drug_data.get("validation_status") != "validated":
            raise ValueError(
                f"Research mode requires validated drug profile. "
                f"Drug {drug_id} has status '{drug_data.get('validation_status')}'."
            )

    # Create temporary polymer CSV for the engine
    analysis_dir = ANALYSES_DIR / analysis_id
    analysis_dir.mkdir(parents=True, exist_ok=True)

    # Write selected polymers to temp CSV
    clean_dicts = []
    for pd_dict in selected_polymer_dicts:
        clean = {}
        for k, v in pd_dict.items():
            if k == "is_reference":
                continue
            if v is None or (isinstance(v, float) and np.isnan(v)) or str(v) == "nan":
                continue
            clean[k] = v
        clean.setdefault("polymer_family", "vinylic")
        clean.setdefault("polymer_class", "neutral")
        clean.setdefault("regulatory_status", "FDA_IID")
        clean.setdefault("pdi", 1.2)
        clean.setdefault("density_g_cm3", 1.20)
        clean.setdefault("spray_drying_suitability", "good")
        clean.setdefault("hygroscopicity", "slightly")
        clean.setdefault("validation_status", "validated")
        clean_dicts.append(clean)
    temp_polymer_df = pd.DataFrame(clean_dicts)
    temp_polymer_csv = analysis_dir / "polymers.csv"
    temp_polymer_df.to_csv(temp_polymer_csv, index=False)


    # Write drug JSON
    temp_drug_json = analysis_dir / "drug.json"
    with open(temp_drug_json, "w", encoding="utf-8") as f:
        json.dump(drug_data_clean, f, indent=2)

    # Create analysis-specific output dirs
    reports_dir = analysis_dir / "reports"
    figures_dir = analysis_dir / "figures"
    logs_dir = analysis_dir / "logs"
    reports_dir.mkdir(exist_ok=True)
    figures_dir.mkdir(exist_ok=True)
    logs_dir.mkdir(exist_ok=True)

    # 3. Load base workflow config
    with open(BASE_WORKFLOW_CONFIG, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    config["prediction"]["default_drug_loading_ww"] = drug_loading_ww
    config["workflow"]["random_seed"] = random_seed
    config_checksum = generate_sha256(config)

    # 4. Run the pipeline steps (same as WorkflowOrchestrator.run())
    polymer_lib = PolymerLibrary.from_csv(temp_polymer_csv, drug)

    # Step 4: HSP scoring & Gate 1
    hsp_model = HSPModel(drug, polymer_lib)
    g1_res = hsp_model.check_gate1(
        red_threshold=config["gates"]["gate1_hsp_red_threshold"],
        min_passing=config["gates"]["gate1_min_passing_polymers"],
    )
    if not g1_res.passed:
        warnings_list.append(f"Gate 1 FAILED: {g1_res.message}")

    # Steps 5-6: Build compatibility matrix
    comp_matrix_builder = CompatibilityMatrix(
        drug, polymer_lib,
        drug_loading_ww=drug_loading_ww,
    )
    df_S = comp_matrix_builder.build_matrix()

    # Step 7: PCA
    pca_preprocessor = PCAPreprocessor(
        variance_threshold=config["pca"]["variance_threshold"]
    )
    pca_result = pca_preprocessor.fit_transform(df_S)

    # Step 8: AHP + TOPSIS
    ahp_elicitor = AHPWeightElicitor(
        cr_max_threshold=config["gates"]["gate2_ahp_cr_max"]
    )
    with open(AHP_MATRIX_DIR / "default_matrix.json", "r", encoding="utf-8") as f:
        ahp_raw = json.load(f)
    matrix_pc = np.array(ahp_raw["pairwise_matrix"])

    ahp_res = ahp_elicitor.aggregate_multi_expert_matrices([matrix_pc])
    weights_k = ahp_res.weights
    k_retained = pca_result.n_components_retained
    if len(weights_k) != k_retained:
        if len(weights_k) < k_retained:
            w_padded = np.pad(weights_k, (0, k_retained - len(weights_k)),
                              mode="constant", constant_values=0.1)
            weights_k = w_padded / np.sum(w_padded)
        else:
            weights_k = weights_k[:k_retained] / np.sum(weights_k[:k_retained])

    topsis = TOPSISRanker()
    topsis_res = topsis.fit_predict(pca_result.scores_matrix_t, weights_k)
    df_ranking = topsis_res.ranking_table
    poly_name_map = {p["polymer_id"]: p.get("polymer_name", p["polymer_id"]) for p in selected_polymer_dicts}
    poly_abbr_map = {p["polymer_id"]: p.get("abbreviation", p["polymer_id"]) for p in selected_polymer_dicts}
    df_ranking["polymer_name"] = df_ranking["polymer_id"].map(poly_name_map)
    df_ranking["abbreviation"] = df_ranking["polymer_id"].map(poly_abbr_map)


    # Step 8b: Monte Carlo UQ
    uq_engine = MonteCarloUQ(
        drug, polymer_lib,
        n_iterations=config["uncertainty"]["monte_carlo_iterations"],
        random_seed=random_seed,
    )
    uq_result = uq_engine.run(matrix_pc)

    # Step 8c: Sensitivity
    oat = OATSensitivity()
    oat_res = oat.analyze(pca_result.scores_matrix_t, ahp_res.weights)

    morris = MorrisSensitivity(r_trajectories=config["sensitivity"]["morris_trajectories"])
    morris_res = morris.analyze(pca_result.scores_matrix_t, k_retained)

    # Step 9: Predictions
    predictor = FormulationPredictor(drug, polymer_lib, drug_loading_ww=drug_loading_ww)
    pred_report = predictor.predict_for_polymer(uq_result.selected_polymer_id, rank=1)

    # Step 10: Validation
    validator = FrameworkValidator()
    val_report = validator.validate(df_ranking, df_S)

    # Step 11: Generate reports and figures
    report_gen = ReportGenerator(reports_dir)
    reports = report_gen.generate_full_report(
        ranking_df=df_ranking,
        prediction_report=pred_report,
        validation_report=val_report,
        uq_result=uq_result,
        pca_result=pca_result,
    )

    poly_name_map = {p["polymer_id"]: p.get("polymer_name", p.get("abbreviation", p["polymer_id"])) for p in selected_polymer_dicts}

    fig_gen = FigureGenerator(figures_dir)
    figs = [
        fig_gen.plot_figure_6_ranking(df_ranking),
        fig_gen.plot_figure_7_sensitivity_morris(morris_res),
        fig_gen.plot_figure_8_uncertainty(uq_result, poly_name_map),
        fig_gen.plot_figure_11_pca_scree(pca_result),
        fig_gen.plot_figure_12_fbm_contour(pred_report.fbm_result),
    ]


    # Save input snapshot for reproducibility
    input_snapshot = {
        "drug_id": drug_id,
        "drug_data": drug_data_clean,
        "polymer_ids": polymer_ids,
        "mode": mode,
        "drug_loading_ww": drug_loading_ww,
        "random_seed": random_seed,
        "config": config,
    }
    with open(analysis_dir / "input_snapshot.json", "w", encoding="utf-8") as f:
        json.dump(input_snapshot, f, indent=2, default=str)

    # Build ranking list with dynamic polymer_name resolution and UQ P(top-1) confidence
    poly_map = {p["polymer_id"]: p for p in selected_polymer_dicts}
    ranking_list = []
    for _, row in df_ranking.iterrows():
        pid = row["polymer_id"]
        p_info = poly_map.get(pid, {})
        p_name = p_info.get("polymer_name", pid)
        p_top1 = float(uq_result.p_top1.get(pid, 0.0))
        ranking_list.append({
            "rank": int(row["topsis_rank"]),
            "polymer_id": pid,
            "polymer_name": p_name,
            "abbreviation": row.get("abbreviation", pid),
            "topsis_cl": float(row["topsis_cl"]),
            "topsis_ideal_distance": float(row["topsis_ideal_distance"]),
            "topsis_anti_ideal_distance": float(row["topsis_anti_ideal_distance"]),
            "confidence_p_top1": p_top1,
        })



    # Build figure URLs (relative to API)
    figure_names = [p.name for p in figs]
    report_formats = {k: str(v.name) for k, v in reports.items()}

    # Add mode warning for exploratory
    if mode == "exploratory":
        warnings_list.append("EXPLORATORY PREDICTION — NOT EXPERIMENTALLY VALIDATED")

    # 5. Save to history
    drug_name = drug.generic_name
    top_polymer_name = pred_report.selected_polymer_name
    history_db.save_analysis(
        analysis_id=analysis_id,
        drug_id=drug_id,
        drug_name=drug_name,
        polymer_ids=polymer_ids,
        mode=mode,
        top_polymer=top_polymer_name,
        topsis_cl=float(df_ranking.iloc[0]["topsis_cl"]),
        confidence_tier=uq_result.confidence_tier,
        software_version=ENGINE_VERSION,
        config_checksum=config_checksum,
        random_seed=random_seed,
        input_snapshot=input_snapshot,
        result_dir=str(analysis_dir),
        warnings=warnings_list,
    )

    # 6. Build response
    return {
        "analysis_id": analysis_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mode": mode,
        "drug_id": drug_id,
        "drug_name": drug_name,
        "polymer_ids": polymer_ids,
        "ranking": ranking_list,
        "selected_polymer": top_polymer_name,
        "selected_polymer_id": pred_report.selected_polymer_id,
        "topsis_cl": float(df_ranking.iloc[0]["topsis_cl"]),
        "confidence_tier": uq_result.confidence_tier,
        "confidence_p_top1": uq_result.p_top1.get(pred_report.selected_polymer_id, 0.0),
        "predicted_tg_k": pred_report.predicted_tg_k,
        "tg_prediction_interval": list(pred_report.tg_prediction_interval),
        "predicted_chi": pred_report.flory_huggins_chi,
        "chi_critical": pred_report.chi_critical,
        "miscibility_class": pred_report.miscibility_class,
        "stability_tier": f"{pred_report.stability_tier_25c_60rh}; {pred_report.stability_tier_40c_75rh}",
        "gate1_passed": bool(g1_res.passed),
        "gate2_passed": bool(ahp_res.passed_gate2),
        "pca_retained_k": int(pca_result.n_components_retained),
        "pca_variance_explained": [float(x) for x in pca_result.explained_variance_ratio],
        "pca_interpretation": pca_result.interpretation,
        "uq_p_top1": {k: float(v) for k, v in uq_result.p_top1.items()},
        "uq_gelman_rubin": float(uq_result.gelman_rubin_rhat),
        "uq_converged": bool(uq_result.converged),
        "oat_top1_stable": bool(oat_res.is_top1_robust),
        "oat_stability_fraction": float(oat_res.top1_stability_fraction),
        "morris_feature_names": morris_res.feature_names,
        "morris_mu": [float(x) for x in morris_res.mu],
        "morris_sigma": [float(x) for x in morris_res.sigma],
        "validation_spearman": float(val_report.spearman_rho),
        "validation_classification": val_report.classification,
        "baseline_outperforms": bool(val_report.baseline_result.outperforms_baselines),
        "fbm_auc": float(pred_report.fbm_result.auc_roc),

        "fbm_actionable": bool(pred_report.fbm_result.is_actionable),

        "figures": figure_names,
        "reports": report_formats,
        "software_version": ENGINE_VERSION,
        "warnings": warnings_list,
    }


def get_screening_result(analysis_id: str) -> Optional[Dict[str, Any]]:
    """Load a stored screening result by analysis ID."""
    record = history_db.get_analysis(analysis_id)
    if record is None:
        return None

    analysis_dir = ANALYSES_DIR / analysis_id
    result_json = analysis_dir / "reports" / "decision_report.json"
    if result_json.exists():
        with open(result_json, "r", encoding="utf-8") as f:
            report_data = json.load(f)
            record["report_data"] = report_data

            # Populate top-level fields for frontend UI rendering
            if "ranking" in report_data:
                record["ranking"] = report_data["ranking"]
            if "selected_polymer" in report_data:
                record["selected_polymer"] = report_data["selected_polymer"]
            if "selected_polymer_id" in report_data:
                record["selected_polymer_id"] = report_data["selected_polymer_id"]
            if "topsis_CL" in report_data:
                record["topsis_cl"] = report_data["topsis_CL"]
            if "confidence_tier" in report_data:
                record["confidence_tier"] = report_data["confidence_tier"]
            if "predicted_Tg_K" in report_data:
                record["predicted_tg_k"] = report_data["predicted_Tg_K"]
            if "predicted_chi" in report_data:
                record["predicted_chi"] = report_data["predicted_chi"]
            if "chi_critical" in report_data:
                record["chi_critical"] = report_data["chi_critical"]
            if "miscibility_class" in report_data:
                record["miscibility_class"] = report_data["miscibility_class"]

    # Fallback to reading ranking.csv if ranking is missing (e.g. older analysis runs)
    if "ranking" not in record or not record["ranking"]:
        ranking_csv = analysis_dir / "reports" / "ranking.csv"
        if ranking_csv.exists():
            import csv
            ranking_list = []
            with open(ranking_csv, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    rank_val = int(float(row.get("topsis_rank", 0))) if row.get("topsis_rank") else 0
                    pid = row.get("polymer_id", "").strip()
                    pname = row.get("polymer_name", row.get("abbreviation", pid)).strip()
                    abbr = row.get("abbreviation", pid).strip()
                    cl_val = float(row.get("topsis_cl", 0.0)) if row.get("topsis_cl") else 0.0
                    ideal_d = float(row.get("topsis_ideal_distance", 0.0)) if row.get("topsis_ideal_distance") else 0.0
                    anti_d = float(row.get("topsis_anti_ideal_distance", 0.0)) if row.get("topsis_anti_ideal_distance") else 0.0

                    ranking_list.append({
                        "rank": rank_val,
                        "polymer_id": pid,
                        "polymer_name": pname if pname != pid else pid,
                        "abbreviation": abbr,
                        "topsis_cl": cl_val,
                        "topsis_ideal_distance": ideal_d,
                        "topsis_anti_ideal_distance": anti_d,
                    })
            ranking_list.sort(key=lambda x: x["rank"])
            record["ranking"] = ranking_list



    # List available figures
    figures_dir = analysis_dir / "figures"
    if figures_dir.exists():
        record["figures"] = [f.name for f in figures_dir.glob("*.png")]
    else:
        record["figures"] = []

    # List available reports
    reports_dir = analysis_dir / "reports"
    if reports_dir.exists():
        record["report_files"] = {
            f.suffix.lstrip("."): f.name for f in reports_dir.iterdir() if f.is_file()
        }
    else:
        record["report_files"] = {}

    return record


def get_figure_path(analysis_id: str, figure_name: str) -> Optional[Path]:
    """Get the absolute path to a generated figure file."""
    path = ANALYSES_DIR / analysis_id / "figures" / figure_name
    if path.exists() and path.is_file():
        return path
    return None


def get_report_path(analysis_id: str, filename: str) -> Optional[Path]:
    """Get the absolute path to a generated report file."""
    path = ANALYSES_DIR / analysis_id / "reports" / filename
    if path.exists() and path.is_file():
        return path
    return None
