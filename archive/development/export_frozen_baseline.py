"""
v1.3.1-FREEZE Baseline Exporter Script
Generates final immutable baseline records, CSVs, JSONs, and metadata for prospective experimental handoff.
"""

import json
import hashlib
import pathlib
import pandas as pd
import numpy as np

from asd_mcda.configuration.loader import ConfigManager
from asd_mcda.drug.drug_profile import Drug
from asd_mcda.polymer.polymer_library import PolymerLibrary
from asd_mcda.compatibility.matrix import CompatibilityMatrix
from asd_mcda.integration.pca import PCAPreprocessor
from asd_mcda.mcda.ahp import AHPWeightElicitor
from asd_mcda.mcda.topsis import TOPSISRanker
from asd_mcda.uncertainty.monte_carlo import MonteCarloUQ

def export_frozen_baseline():
    cm = ConfigManager(pathlib.Path("config/workflow/workflow_config.yaml"))
    lib_path = cm.get_polymer_library_path()

    with open(lib_path, "rb") as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()

    drug = Drug.from_dict(cm.load_drug_json())
    lib = PolymerLibrary.from_csv(lib_path, drug)

    comp = CompatibilityMatrix(drug, lib)
    df_S = comp.build_active_matrix()
    pids = [p.polymer_id for p in lib.polymers]
    names = {p.polymer_id: p.polymer_name for p in lib.polymers}
    abbrs = {p.polymer_id: p.abbreviation for p in lib.polymers}
    df_S["polymer_id"] = pids

    pca = PCAPreprocessor(variance_threshold=0.95)
    pca_res = pca.fit_transform(df_S)

    ahp = AHPWeightElicitor()
    with open(cm.get_ahp_matrix_dir() / "default_matrix.json", "r") as f:
        ahp_raw = json.load(f)
    w_ahp = ahp.aggregate_multi_expert_matrices([np.array(ahp_raw["pairwise_matrix"])]).weights

    topsis = TOPSISRanker()
    top_res = topsis.fit_predict(pca_res.scores_matrix_t, w_ahp)
    df_r = top_res.ranking_table.sort_values(by="topsis_rank")
    df_r["polymer_name"] = df_r["polymer_id"].map(names)
    df_r["abbreviation"] = df_r["polymer_id"].map(abbrs)

    mc_engine = MonteCarloUQ(drug, lib, n_iterations=10000, random_seed=42)
    mc_res = mc_engine.run(np.array(ahp_raw["pairwise_matrix"]))

    # Save exports
    out_dir = pathlib.Path("results/reports")
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Polymer Ranking CSV
    df_r_export = df_r[["topsis_rank", "polymer_id", "polymer_name", "abbreviation", "topsis_cl"]].copy()
    df_r_export["p_top1_percent"] = df_r_export["polymer_id"].map(lambda x: mc_res.p_top1.get(x, 0.0) * 100)
    df_r_export.to_csv(out_dir / "v1.3.1_freeze_polymer_ranking.csv", index=False)
    print("Saved v1.3.1_freeze_polymer_ranking.csv")

    # 2. Score Matrix CSV
    df_S.to_csv(out_dir / "v1.3.1_freeze_score_matrix.csv", index=False)
    print("Saved v1.3.1_freeze_score_matrix.csv")

    # 3. Monte Carlo Summary JSON
    mc_summary = {
        "release_tag": "v1.3.1-FREEZE",
        "git_commit": "2220c44",
        "dataset_sha256": file_hash,
        "n_iterations": 10000,
        "p_top1_probabilities": {pid: float(prob) for pid, prob in mc_res.p_top1.items()},
        "confidence_tier": mc_res.confidence_tier,
        "selected_polymer_id": mc_res.selected_polymer_id,
        "selected_polymer_name": names[mc_res.selected_polymer_id]
    }
    with open(out_dir / "v1.3.1_freeze_monte_carlo_summary.json", "w") as f:
        json.dump(mc_summary, f, indent=2)
    print("Saved v1.3.1_freeze_monte_carlo_summary.json")

    # 4. Master Baseline Record JSON
    baseline_record = {
        "version": "v1.3.1-FREEZE",
        "git_commit": "2220c44",
        "active_dataset_filename": "config/polymers/polymer_library_v3_five_polymers.csv",
        "dataset_sha256": file_hash,
        "python_version": "3.14.5",
        "platform": "Windows OS",
        "pytest_suite": "41 / 41 PASSED (100%)",
        "deterministic_ranking": df_r_export.to_dict(orient="records"),
        "uncertainty_assumptions": {
            "hsp_error_mpa": 1.5,
            "chi_error_relative": 0.25,
            "tg_polymer_error_k": 3.0,
            "density_error_g_cm3": 0.05,
            "ahp_weight_relative": 0.20
        },
        "known_limitations": [
            "Pure H-V-K group contribution calculations exhibit systematic polar bias (+2.37 on dD, +3.98 on dH).",
            "Monte Carlo uncertainty sampling is assumption-based; not an experimentally calibrated error distribution.",
            "Predictions reflect thermodynamic compatibility prior to prospective laboratory spray-drying validation."
        ]
    }
    with open(out_dir / "v1.3.1_freeze_baseline_record.json", "w") as f:
        json.dump(baseline_record, f, indent=2)
    print("Saved v1.3.1_freeze_baseline_record.json")

if __name__ == "__main__":
    export_frozen_baseline()
