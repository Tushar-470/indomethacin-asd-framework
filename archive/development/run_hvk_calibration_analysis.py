"""
HSP Experimental vs H-V-K Calibration & Error Characterization Analysis
Executes temporary, read-only calibration calculations comparing ACS Omega 2026 experimental HSP
data against production Hoftyzer-Van Krevelen (H-V-K) group contribution estimates.
"""

import json
import math
import numpy as np
import pandas as pd
import pathlib


from asd_mcda.configuration.loader import ConfigManager
from asd_mcda.drug.drug_profile import Drug
from asd_mcda.polymer.polymer_library import PolymerLibrary, Polymer
from asd_mcda.compatibility.matrix import CompatibilityMatrix
from asd_mcda.compatibility.hsp_model import HSPModel
from asd_mcda.compatibility.flory_huggins import FloryHugginsModel
from asd_mcda.integration.pca import PCAPreprocessor
from asd_mcda.mcda.ahp import AHPWeightElicitor
from asd_mcda.mcda.topsis import TOPSISRanker

def run_calibration_audit():
    # 1. ACS Omega 2026 Experimental HSP Benchmark Data (Exact-Grade Overlap)
    exp_exact_data = [
        {"polymer": "Soluplus", "grade": "Soluplus", "dD_exp": 17.2, "dP_exp": 5.2, "dH_exp": 6.5, "R0_exp": 7.8, "family": "Graft Copolymer"},
        {"polymer": "PVP-VA 64", "grade": "Kollidon VA64", "dD_exp": 17.8, "dP_exp": 7.2, "dH_exp": 8.5, "R0_exp": 7.5, "family": "Copovidone"},
        {"polymer": "PVP K30", "grade": "Povidone K30", "dD_exp": 17.5, "dP_exp": 6.8, "dH_exp": 9.2, "R0_exp": 7.2, "family": "Povidone Homopolymer"},
        {"polymer": "Eudragit E PO", "grade": "Eudragit EPO", "dD_exp": 16.8, "dP_exp": 5.5, "dH_exp": 6.2, "R0_exp": 8.1, "family": "Methacrylate Copolymer"},
    ]

    # 2. Production H-V-K Calculated Values (from run_provenance_audit.py / group contribution)
    hvk_data = {
        "Soluplus": (19.21, 11.10, 9.16),
        "PVP-VA 64": (20.47, 13.90, 10.32),
        "PVP K30": (22.55, 17.03, 10.36),
        "Eudragit E PO": (17.35, 6.12, 8.81),
        "HPMC E5": (20.33, 8.59, 17.47), # H-V-K for substituted AGU
    }

    # 3. Compute Component Errors & Euclidean Distances for Exact-Grade Set
    records = []
    for item in exp_exact_data:
        p = item["polymer"]
        dD_exp, dP_exp, dH_exp = item["dD_exp"], item["dP_exp"], item["dH_exp"]
        dD_hvk, dP_hvk, dH_hvk = hvk_data[p]

        err_D = dD_hvk - dD_exp
        err_P = dP_hvk - dP_exp
        err_H = dH_hvk - dH_exp
        e_hsp = math.sqrt(err_D**2 + err_P**2 + err_H**2)

        records.append({
            "Polymer": p,
            "Grade": item["grade"],
            "dD_exp": dD_exp, "dP_exp": dP_exp, "dH_exp": dH_exp,
            "dD_hvk": dD_hvk, "dP_hvk": dP_hvk, "dH_hvk": dH_hvk,
            "err_D": err_D, "err_P": err_P, "err_H": err_H,
            "abs_err_D": abs(err_D), "abs_err_P": abs(err_P), "abs_err_H": abs(err_H),
            "Euclidean_Error": e_hsp
        })

    df_err = pd.DataFrame(records)
    print("=== EXACT-GRADE EXPERIMENTAL vs H-V-K ERROR TABLE (n=4) ===")
    print(df_err[["Polymer", "dD_exp", "dD_hvk", "err_D", "dP_exp", "dP_hvk", "err_P", "dH_exp", "dH_hvk", "err_H", "Euclidean_Error"]].to_string(index=False))

    # Calculate Component-wise Summary Statistics (n=4)
    n = len(df_err)
    bias_D = df_err["err_D"].mean()
    bias_P = df_err["err_P"].mean()
    bias_H = df_err["err_H"].mean()

    mae_D = df_err["abs_err_D"].mean()
    mae_P = df_err["abs_err_P"].mean()
    mae_H = df_err["abs_err_H"].mean()

    rmse_D = math.sqrt((df_err["err_D"]**2).mean())
    rmse_P = math.sqrt((df_err["err_P"]**2).mean())
    rmse_H = math.sqrt((df_err["err_H"]**2).mean())

    print("\n=== COMPONENT-WISE ERROR STATISTICS (n=4 Exact-Grade) ===")
    print(f"delta_D -> Bias: {bias_D:+.2f} | MAE: {mae_D:.2f} | RMSE: {rmse_D:.2f} | Range: [{df_err['err_D'].min():+.2f}, {df_err['err_D'].max():+.2f}]")
    print(f"delta_P -> Bias: {bias_P:+.2f} | MAE: {mae_P:.2f} | RMSE: {rmse_P:.2f} | Range: [{df_err['err_P'].min():+.2f}, {df_err['err_P'].max():+.2f}]")
    print(f"delta_H -> Bias: {bias_H:+.2f} | MAE: {mae_H:.2f} | RMSE: {rmse_H:.2f} | Range: [{df_err['err_H'].min():+.2f}, {df_err['err_H'].max():+.2f}]")
    print(f"Euclidean HSP Error -> Mean: {df_err['Euclidean_Error'].mean():.2f} | Min: {df_err['Euclidean_Error'].min():.2f} | Max: {df_err['Euclidean_Error'].max():.2f}")

    # 4. Expanded Calibration Dataset (Including Related/Other Excipients)
    exp_expanded_data = [
        {"polymer": "Eudragit RLPO", "grade": "Eudragit RLPO", "dD_exp": 17.1, "dP_exp": 6.0, "dH_exp": 6.8, "dD_hvk": 17.65, "dP_hvk": 6.85, "dH_hvk": 8.90, "family": "Methacrylate"},
        {"polymer": "HPMCAS-L", "grade": "HPMCAS LF", "dD_exp": 18.0, "dP_exp": 8.2, "dH_exp": 10.5, "dD_hvk": 19.85, "dP_hvk": 9.40, "dH_hvk": 14.80, "family": "Cellulosic Ester"},
        {"polymer": "HPMCAS-M", "grade": "HPMCAS MF", "dD_exp": 18.1, "dP_exp": 8.4, "dH_exp": 10.8, "dD_hvk": 19.90, "dP_hvk": 9.50, "dH_hvk": 14.90, "family": "Cellulosic Ester"},
        {"polymer": "HPMCAS-H", "grade": "HPMCAS HF", "dD_exp": 18.2, "dP_exp": 8.6, "dH_exp": 11.0, "dD_hvk": 19.95, "dP_hvk": 9.60, "dH_hvk": 15.00, "family": "Cellulosic Ester"},
        {"polymer": "HPC Klucel MXF", "grade": "HPC MXF", "dD_exp": 17.8, "dP_exp": 7.5, "dH_exp": 11.5, "dD_hvk": 19.50, "dP_hvk": 8.20, "dH_hvk": 16.20, "family": "Cellulosic Ether"},
        {"polymer": "HPMC K100M", "grade": "Methocel K100M", "dD_exp": 18.4, "dP_exp": 8.7, "dH_exp": 11.1, "dD_hvk": 20.33, "dP_hvk": 8.59, "dH_hvk": 17.47, "family": "Cellulosic Ether (Related Grade)"},
    ]

    exp_records = list(records) # start with exact
    for item in exp_expanded_data:
        err_D = item["dD_hvk"] - item["dD_exp"]
        err_P = item["dP_hvk"] - item["dP_exp"]
        err_H = item["dH_hvk"] - item["dH_exp"]
        e_hsp = math.sqrt(err_D**2 + err_P**2 + err_H**2)
        exp_records.append({
            "Polymer": item["polymer"], "Grade": item["grade"],
            "dD_exp": item["dD_exp"], "dP_exp": item["dP_exp"], "dH_exp": item["dH_exp"],
            "dD_hvk": item["dD_hvk"], "dP_hvk": item["dP_hvk"], "dH_hvk": item["dH_hvk"],
            "err_D": err_D, "err_P": err_P, "err_H": err_H,
            "abs_err_D": abs(err_D), "abs_err_P": abs(err_P), "abs_err_H": abs(err_H),
            "Euclidean_Error": e_hsp
        })

    df_exp_all = pd.DataFrame(exp_records)
    print("\n=== EXPANDED CALIBRATION DATASET (n=10) ===")
    print(df_exp_all[["Polymer", "Grade", "err_D", "err_P", "err_H", "Euclidean_Error"]].to_string(index=False))

    n_all = len(df_exp_all)
    print(f"\nExpanded (n=10) -> Mean Euclidean Error: {df_exp_all['Euclidean_Error'].mean():.2f} | MAE_D: {df_exp_all['abs_err_D'].mean():.2f} | MAE_P: {df_exp_all['abs_err_P'].mean():.2f} | MAE_H: {df_exp_all['abs_err_H'].mean():.2f}")

    # 5. Ranking Impact Analysis Across 3 Scenarios
    cm = ConfigManager(pathlib.Path("config/workflow/workflow_config.yaml"))
    drug = Drug.from_dict(cm.load_drug_json())
    lib_base = PolymerLibrary.from_csv(cm.get_polymer_library_path(), drug)

    # Scenarios for Five Candidate Polymers:
    # Scenario A: Current Adopted Literature HSP (Production baseline)
    # Scenario B: ACS Omega Experimental HSP (Exact grades for 4; HPMC E5 = 18.5, 8.8, 11.2)
    # Scenario C: Production H-V-K Calculated HSP
    hsp_sc_A = {
        "POL-005-2026": (17.2, 5.2, 6.5),  # Soluplus
        "POL-006-2026": (18.5, 8.8, 11.2), # HPMC E5
        "POL-002-2026": (17.8, 7.2, 8.5),  # PVP-VA 64
        "POL-001-2026": (17.5, 6.8, 9.2),  # PVP K30
        "POL-007-2026": (16.8, 5.5, 6.2),  # Eudragit E PO
    }
    hsp_sc_B = {
        "POL-005-2026": (17.2, 5.2, 6.5),  # Soluplus (Exact ACS Omega)
        "POL-006-2026": (18.5, 8.8, 11.2), # HPMC E5 (Adopted literature; K100M=18.4, 8.7, 11.1)
        "POL-002-2026": (17.8, 7.2, 8.5),  # PVP-VA 64 (Exact ACS Omega)
        "POL-001-2026": (17.5, 6.8, 9.2),  # PVP K30 (Exact ACS Omega)
        "POL-007-2026": (16.8, 5.5, 6.2),  # Eudragit E PO (Exact ACS Omega)
    }
    hsp_sc_C = {
        "POL-005-2026": (19.21, 11.10, 9.16),
        "POL-006-2026": (20.33, 8.59, 17.47),
        "POL-002-2026": (20.47, 13.90, 10.32),
        "POL-001-2026": (22.55, 17.03, 10.36),
        "POL-007-2026": (17.35, 6.12, 8.81),
    }

    print("\n=== SCENARIO RANKING COMPARISON ===")
    ahp = AHPWeightElicitor()
    with open(cm.get_ahp_matrix_dir() / "default_matrix.json", "r") as f:
        ahp_raw = json.load(f)
    w_ahp = ahp.aggregate_multi_expert_matrices([np.array(ahp_raw["pairwise_matrix"])]).weights

    for label, hsp_dict in [("Scenario A (Adopted Lit)", hsp_sc_A), ("Scenario B (ACS Omega Exp)", hsp_sc_B), ("Scenario C (Pure H-V-K)", hsp_sc_C)]:
        polys = []
        for p in lib_base.polymers:
            p_d = p.__dict__.copy()
            dD, dP, dH = hsp_dict[p.polymer_id]
            p_d["hsp_delta_d"] = dD
            p_d["hsp_delta_p"] = dP
            p_d["hsp_delta_h"] = dH
            polys.append(Polymer.from_dict(p_d))
        lib = PolymerLibrary(polys, drug)
        comp = CompatibilityMatrix(drug, lib)
        df_S = comp.build_active_matrix()
        df_S["polymer_id"] = [p.polymer_id for p in polys]

        pca_res = PCAPreprocessor(variance_threshold=0.95).fit_transform(df_S)
        top_res = TOPSISRanker().fit_predict(pca_res.scores_matrix_t, w_ahp)
        df_r = top_res.ranking_table.sort_values(by="topsis_rank")
        winner = df_r.iloc[0]["polymer_id"]
        w_name = next(p.polymer_name for p in polys if p.polymer_id == winner)
        print(f"{label:30s} -> Winner: {w_name:30s} | TOPSIS CL={df_r.iloc[0]['topsis_cl']:.6f} | Ranks: {df_r['polymer_id'].tolist()}")

if __name__ == "__main__":
    run_calibration_audit()
