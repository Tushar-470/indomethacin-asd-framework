"""
v1.3.1 Scientific QC and Pre-Lab Reliability Audit Script
Performs GT threshold sensitivity sweeps, leave-one-out candidate analysis,
consolidated robustness matrix calculations, and pairwise logic validation.
"""

import json
import math
import pathlib
import hashlib
import numpy as np
import pandas as pd
from scipy import stats

from asd_mcda.configuration.loader import ConfigManager
from asd_mcda.drug.drug_profile import Drug
from asd_mcda.polymer.polymer_library import PolymerLibrary, Polymer
from asd_mcda.compatibility.matrix import CompatibilityMatrix
from asd_mcda.compatibility.flory_huggins import FloryHugginsModel
from asd_mcda.compatibility.gordon_taylor import GordonTaylorModel
from asd_mcda.integration.pca import PCAPreprocessor
from asd_mcda.mcda.ahp import AHPWeightElicitor
from asd_mcda.mcda.topsis import TOPSISRanker

def get_ranking_order(df_active, pids, weights=None):
    if weights is None:
        cm_inst = ConfigManager(pathlib.Path("config/workflow/workflow_config.yaml"))
        ahp = AHPWeightElicitor()
        with open(cm_inst.get_ahp_matrix_dir() / "default_matrix.json", "r") as f:
            ahp_raw = json.load(f)
        ahp_res = ahp.aggregate_multi_expert_matrices([np.array(ahp_raw["pairwise_matrix"])])
        weights = ahp_res.weights


    df_in = df_active.copy()
    if "polymer_id" not in df_in.columns:
        df_in["polymer_id"] = pids

    pca = PCAPreprocessor(variance_threshold=0.95)
    pca_res = pca.fit_transform(df_in)

    topsis = TOPSISRanker()
    top_res = topsis.fit_predict(pca_res.scores_matrix_t, weights)
    df_rank = top_res.ranking_table.sort_values(by="topsis_rank")
    return df_rank["polymer_id"].tolist(), df_rank

def run_qc_audit():
    cm = ConfigManager(pathlib.Path("config/workflow/workflow_config.yaml"))
    drug = Drug.from_dict(cm.load_drug_json())
    lib = PolymerLibrary.from_csv(cm.get_polymer_library_path(), drug)

    pids = [p.polymer_id for p in lib.polymers]
    names = {p.polymer_id: p.polymer_name for p in lib.polymers}

    # 1. Canonical v1.3.0 Run
    comp = CompatibilityMatrix(drug, lib)
    df_S_active = comp.build_active_matrix()
    df_S_active["polymer_id"] = pids

    canonical_order, df_rank_v13 = get_ranking_order(df_S_active, pids)
    df_rank_v13["polymer_name"] = df_rank_v13["polymer_id"].map(names)

    print("=== CANONICAL v1.3.0 DETERMINISTIC ORDER ===")
    for _, r in df_rank_v13.iterrows():
        print(f"Rank #{r['topsis_rank']}: {r['polymer_name']} [{r['polymer_id']}] -> TOPSIS CL = {r['topsis_cl']:.6f}")

    # -------------------------------------------------------------
    # CRITICAL AUDIT #3: s_GT Threshold Sensitivity
    # -------------------------------------------------------------
    print("\n=== CRITICAL AUDIT #3: s_GT THRESHOLD SENSITIVITY ===")
    gt_offsets = [10.0, 20.0, 30.0, 40.0, 50.0]
    gt_scales = [30.0, 50.0, 70.0]

    for offset in gt_offsets:
        for scale in gt_scales:
            df_S_gt = df_S_active.copy()
            gt_model = GordonTaylorModel(drug, lib, 0.30)
            tg_drug = drug.estimate_tg()
            for i, p in enumerate(lib.polymers):
                tg_mix = gt_model.compute_tg_mix(p)
                s_gt_cust = float(np.clip((tg_mix - (tg_drug + offset)) / scale, 0.0, 1.0))
                df_S_gt.iloc[i, df_S_gt.columns.get_loc("s_GT")] = s_gt_cust

            r_gt_list, df_r_gt = get_ranking_order(df_S_gt, pids)
            rho_gt, _ = stats.spearmanr(df_rank_v13["topsis_rank"], df_r_gt.sort_values(by="polymer_id")["topsis_rank"])
            top1 = names[r_gt_list[0]]
            top2 = names[r_gt_list[1]]
            print(f"GT Offset +{offset:2.0f} K, Scale {scale:2.0f} K -> Top-1: {top1:12s} | Top-2: {top2:32s} | rho = {rho_gt:.4f}")

    # -------------------------------------------------------------
    # CRITICAL AUDIT #17: Leave-One-Out Candidate Analysis
    # -------------------------------------------------------------
    print("\n=== CRITICAL AUDIT #17: LEAVE-ONE-OUT CANDIDATE ANALYSIS ===")
    for remove_pid in pids:
        sub_polys = [p for p in lib.polymers if p.polymer_id != remove_pid]
        sub_lib = PolymerLibrary(sub_polys, drug)
        sub_comp = CompatibilityMatrix(drug, sub_lib)
        df_S_sub = sub_comp.build_active_matrix()
        sub_pids = [p.polymer_id for p in sub_polys]
        df_S_sub["polymer_id"] = sub_pids

        sub_order, _ = get_ranking_order(df_S_sub, sub_pids)
        print(f"Remove {names[remove_pid]:32s} [{remove_pid}]: Winner = {names[sub_order[0]]:12s} | Order = {sub_order}")

    # -------------------------------------------------------------
    # CRITICAL AUDIT #16: Consolidated Robustness Matrix (15 Scenarios)
    # -------------------------------------------------------------
    print("\n=== CRITICAL AUDIT #16: CONSOLIDATED ROBUSTNESS MATRIX ===")
    scenarios = []

    # Scenario 1: Canonical
    scenarios.append(("01. Canonical v1.3.0", canonical_order))

    # Scenario 2-3: HSP perturbation
    for delta in [+1.5, -1.5]:
        pert_polys = []
        for p in lib.polymers:
            p_d = p.__dict__.copy()
            p_d["hsp_delta_d"] += delta
            pert_polys.append(Polymer.from_dict(p_d))
        df_s_p = CompatibilityMatrix(drug, PolymerLibrary(pert_polys, drug)).build_active_matrix()
        df_s_p["polymer_id"] = pids
        r_list, _ = get_ranking_order(df_s_p, pids)
        scenarios.append((f"HSP Delta_D {delta:+1.1f}", r_list))

    # Scenario 4-5: Tg perturbation
    for dtg in [+10.0, -10.0]:
        pert_polys = []
        for p in lib.polymers:
            p_d = p.__dict__.copy()
            p_d["tg_k"] += dtg
            pert_polys.append(Polymer.from_dict(p_d))
        df_s_p = CompatibilityMatrix(drug, PolymerLibrary(pert_polys, drug)).build_active_matrix()
        df_s_p["polymer_id"] = pids
        r_list, _ = get_ranking_order(df_s_p, pids)
        scenarios.append((f"Tg Shift {dtg:+2.0f} K", r_list))

    # Scenario 6-7: Density perturbation
    for drho in [+0.10, -0.10]:
        pert_polys = []
        for p in lib.polymers:
            p_d = p.__dict__.copy()
            p_d["density_g_cm3"] += drho
            pert_polys.append(Polymer.from_dict(p_d))
        df_s_p = CompatibilityMatrix(drug, PolymerLibrary(pert_polys, drug)).build_active_matrix()
        df_s_p["polymer_id"] = pids
        r_list, _ = get_ranking_order(df_s_p, pids)
        scenarios.append((f"Density Shift {drho:+1.2f}", r_list))

    # Scenario 8-10: AHP Weight Sweeps
    for w1 in [0.40, 0.60, 0.80]:
        r_list, _ = get_ranking_order(df_S_active, pids, np.array([w1, 1.0 - w1]))
        scenarios.append((f"AHP w1={w1:.2f}", r_list))

    # Scenario 11: Model B (s_chi = 1/(1+chi))
    df_S_B = df_S_active.copy()
    fh = FloryHugginsModel(drug, lib)
    for i, p in enumerate(lib.polymers):
        df_S_B.iloc[i, df_S_B.columns.get_loc("s_chi")] = 1.0 / (1.0 + fh.compute_chi(p))
    r_list_B, _ = get_ranking_order(df_S_B, pids)
    scenarios.append(("Model B s_chi=1/(1+chi)", r_list_B))

    # Scenario 12: Equal-Weight TOPSIS
    from scipy.stats import zscore
    S_num = df_S_active[["s_HSP", "s_chi", "s_GT"]].values
    S_std = pd.DataFrame(zscore(S_num, axis=0), columns=["s_HSP", "s_chi", "s_GT"])
    S_std["polymer_id"] = pids
    t_res_eq = TOPSISRanker().fit_predict(S_std, np.array([1/3, 1/3, 1/3]))
    r_list_eq = t_res_eq.ranking_table.sort_values(by="topsis_rank")["polymer_id"].tolist()
    scenarios.append(("Equal-Weight TOPSIS", r_list_eq))

    # Scenario 13-14: No PCA (Standardized active criteria)
    t_res_nopca = TOPSISRanker().fit_predict(S_std, np.array([0.5, 0.3, 0.2]))
    r_list_nopca = t_res_nopca.ranking_table.sort_values(by="topsis_rank")["polymer_id"].tolist()
    scenarios.append(("No-PCA Standardized TOPSIS", r_list_nopca))

    soluplus_top1_count = 0
    soluplus_top2_count = 0
    hpmc_top2_count = 0

    print(f"\n{'Scenario':32s} | Top-1 Candidate | Full Rank Order")
    print("-" * 90)
    for sc_name, sc_order in scenarios:
        top1 = sc_order[0]
        top2 = sc_order[:2]
        if top1 == "POL-005-2026":
            soluplus_top1_count += 1
        if "POL-005-2026" in top2:
            soluplus_top2_count += 1
        if "POL-006-2026" in top2:
            hpmc_top2_count += 1
        print(f"{sc_name:32s} | {names[top1]:15s} | {sc_order}")

    n_sc = len(scenarios)
    print("\n=== ROBUSTNESS SUMMARY METRICS ===")
    print(f"Soluplus Rank #1 Frequency: {soluplus_top1_count}/{n_sc} ({soluplus_top1_count/n_sc*100:.1f}%)")
    print(f"Soluplus Top-2 Frequency  : {soluplus_top2_count}/{n_sc} ({soluplus_top2_count/n_sc*100:.1f}%)")
    print(f"HPMC E5 Top-2 Frequency   : {hpmc_top2_count}/{n_sc} ({hpmc_top2_count/n_sc*100:.1f}%)")

if __name__ == "__main__":
    run_qc_audit()
