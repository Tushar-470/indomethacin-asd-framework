"""
Final Corrected n=10 HSP Calibration Runner
Computes exact model errors, summary statistics, exploratory bias-correction impact,
and ranking sensitivity using the verified 2026 ACS Omega Table 2 experimental HSP values.
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
from asd_mcda.integration.pca import PCAPreprocessor
from asd_mcda.mcda.ahp import AHPWeightElicitor
from asd_mcda.mcda.topsis import TOPSISRanker

def run_n10_calibration():
    # 1. VERIFIED ACS 2026 Table 2 Experimental Data (10 Systems)
    acs_n10 = [
        {"polymer": "Soluplus", "grade": "Soluplus", "dD_exp": 17.4, "dP_exp": 10.0, "dH_exp": 4.9, "hvk": (19.21, 11.10, 9.16), "type": "Exact"},
        {"polymer": "Kollidon VA64", "grade": "Kollidon VA64", "dD_exp": 16.5, "dP_exp": 10.2, "dH_exp": 10.4, "hvk": (20.47, 13.90, 10.32), "type": "Exact"},
        {"polymer": "Povidone K30", "grade": "Povidone K30", "dD_exp": 16.9, "dP_exp": 9.3, "dH_exp": 11.3, "hvk": (22.55, 17.03, 10.36), "type": "Exact"},
        {"polymer": "Eudragit EPO", "grade": "Eudragit EPO", "dD_exp": 17.2, "dP_exp": 5.3, "dH_exp": 8.6, "hvk": (17.35, 6.12, 8.81), "type": "Exact"},
        {"polymer": "Eudragit RLPO", "grade": "Eudragit RLPO", "dD_exp": 17.4, "dP_exp": 9.2, "dH_exp": 8.6, "hvk": (17.65, 6.85, 8.90), "type": "External"},
        {"polymer": "HPMCAS-L", "grade": "HPMCAS LF", "dD_exp": 17.4, "dP_exp": 10.4, "dH_exp": 9.2, "hvk": (19.85, 9.40, 14.80), "type": "External"},
        {"polymer": "HPMCAS-M", "grade": "HPMCAS MF", "dD_exp": 17.1, "dP_exp": 12.6, "dH_exp": 6.7, "hvk": (19.90, 9.50, 14.90), "type": "External"},
        {"polymer": "HPMCAS-H", "grade": "HPMCAS HF", "dD_exp": 16.5, "dP_exp": 8.8, "dH_exp": 7.5, "hvk": (19.95, 9.60, 15.00), "type": "External"},
        {"polymer": "HPC Klucel MXF", "grade": "HPC MXF", "dD_exp": 18.4, "dP_exp": 12.4, "dH_exp": 8.4, "hvk": (19.50, 8.20, 16.20), "type": "External"},
        {"polymer": "HPMC K100M", "grade": "Methocel K100M", "dD_exp": 18.3, "dP_exp": 6.6, "dH_exp": 10.5, "hvk": (20.33, 8.59, 17.47), "type": "External"},
    ]

    records = []
    for item in acs_n10:
        dD_exp, dP_exp, dH_exp = item["dD_exp"], item["dP_exp"], item["dH_exp"]
        dD_hvk, dP_hvk, dH_hvk = item["hvk"]
        err_D = dD_hvk - dD_exp
        err_P = dP_hvk - dP_exp
        err_H = dH_hvk - dH_exp
        e_hsp = math.sqrt(err_D**2 + err_P**2 + err_H**2)

        records.append({
            "Polymer": item["polymer"], "Grade": item["grade"], "Type": item["type"],
            "dD_exp": dD_exp, "dP_exp": dP_exp, "dH_exp": dH_exp,
            "dD_hvk": dD_hvk, "dP_hvk": dP_hvk, "dH_hvk": dH_hvk,
            "err_D": err_D, "err_P": err_P, "err_H": err_H,
            "abs_err_D": abs(err_D), "abs_err_P": abs(err_P), "abs_err_H": abs(err_H),
            "Euclidean_Error": e_hsp
        })

    df = pd.DataFrame(records)
    print("=== FULL VERIFIED n=10 CALIBRATION DATASET ===")
    print(df[["Polymer", "Grade", "dD_exp", "dD_hvk", "err_D", "dP_exp", "dP_hvk", "err_P", "dH_exp", "dH_hvk", "err_H", "Euclidean_Error"]].to_string(index=False))

    # Exact n=4 subset
    df_exact = df.query("Type == 'Exact'")
    print("\n=== EXACT-GRADE SUBSET STATISTICS (n=4) ===")
    print(f"delta_D -> Bias: {df_exact['err_D'].mean():+.2f} | MAE: {df_exact['abs_err_D'].mean():.2f} | MedAE: {df_exact['abs_err_D'].median():.2f} | RMSE: {math.sqrt((df_exact['err_D']**2).mean()):.2f}")
    print(f"delta_P -> Bias: {df_exact['err_P'].mean():+.2f} | MAE: {df_exact['abs_err_P'].mean():.2f} | MedAE: {df_exact['abs_err_P'].median():.2f} | RMSE: {math.sqrt((df_exact['err_P']**2).mean()):.2f}")
    print(f"delta_H -> Bias: {df_exact['err_H'].mean():+.2f} | MAE: {df_exact['abs_err_H'].mean():.2f} | MedAE: {df_exact['abs_err_H'].median():.2f} | RMSE: {math.sqrt((df_exact['err_H']**2).mean()):.2f}")
    print(f"Euclidean Error -> Mean: {df_exact['Euclidean_Error'].mean():.2f} | Median: {df_exact['Euclidean_Error'].median():.2f} | Min: {df_exact['Euclidean_Error'].min():.2f} | Max: {df_exact['Euclidean_Error'].max():.2f}")

    # Full n=10 dataset statistics
    print("\n=== EXPANDED n=10 DATASET STATISTICS ===")
    b_D, b_P, b_H = df['err_D'].mean(), df['err_P'].mean(), df['err_H'].mean()
    m_D, m_P, m_H = df['abs_err_D'].mean(), df['abs_err_P'].mean(), df['abs_err_H'].mean()
    med_D, med_P, med_H = df['abs_err_D'].median(), df['abs_err_P'].median(), df['abs_err_H'].median()
    r_D, r_P, r_H = math.sqrt((df['err_D']**2).mean()), math.sqrt((df['err_P']**2).mean()), math.sqrt((df['err_H']**2).mean())

    print(f"delta_D -> Bias: {b_D:+.2f} | MAE: {m_D:.2f} | MedAE: {med_D:.2f} | RMSE: {r_D:.2f}")
    print(f"delta_P -> Bias: {b_P:+.2f} | MAE: {m_P:.2f} | MedAE: {med_P:.2f} | RMSE: {r_P:.2f}")
    print(f"delta_H -> Bias: {b_H:+.2f} | MAE: {m_H:.2f} | MedAE: {med_H:.2f} | RMSE: {r_H:.2f}")
    print(f"Euclidean Error -> Mean: {df['Euclidean_Error'].mean():.2f} | Median: {df['Euclidean_Error'].median():.2f} | Min: {df['Euclidean_Error'].min():.2f} | Max: {df['Euclidean_Error'].max():.2f}")

    # Exploratory Bias Correction Test
    print("\n=== EXPLORATORY BIAS-CORRECTION TEST ===")
    df["corr_err_D"] = df["err_D"] - b_D
    df["corr_err_P"] = df["err_P"] - b_P
    df["corr_err_H"] = df["err_H"] - b_H
    df["corr_E_HSP"] = np.sqrt(df["corr_err_D"]**2 + df["corr_err_P"]**2 + df["corr_err_H"]**2)

    mean_euc_before = df["Euclidean_Error"].mean()
    mean_euc_after = df["corr_E_HSP"].mean()
    print(f"Mean Euclidean Error BEFORE bias correction: {mean_euc_before:.2f} MPa^0.5")
    print(f"Mean Euclidean Error AFTER bias correction:  {mean_euc_after:.2f} MPa^0.5")
    print(f"Euclidean Error Reduction: {((mean_euc_before - mean_euc_after)/mean_euc_before)*100:.1f}%")

    # Ranking Sensitivity Analysis
    cm = ConfigManager(pathlib.Path("config/workflow/workflow_config.yaml"))
    drug = Drug.from_dict(cm.load_drug_json())
    lib_base = PolymerLibrary.from_csv(cm.get_polymer_library_path(), drug)

    # Scenarios for Prospective Polymers:
    # Scenario A: Current Adopted Literature HSP (Production Baseline)
    # Scenario B: ACS 2026 Hybrid (Exact ACS 2026 values for 4 exact polymers; HPMC E5 = 18.5, 8.8, 11.2)
    hsp_sc_A = {
        "POL-005-2026": (17.2, 5.2, 6.5),  # Soluplus
        "POL-006-2026": (18.5, 8.8, 11.2), # HPMC E5
        "POL-002-2026": (17.8, 7.2, 8.5),  # PVP-VA 64
        "POL-001-2026": (17.5, 6.8, 9.2),  # PVP K30
        "POL-007-2026": (16.8, 5.5, 6.2),  # Eudragit E PO
    }
    hsp_sc_B = {
        "POL-005-2026": (17.4, 10.0, 4.9), # Soluplus ACS 2026
        "POL-006-2026": (18.5, 8.8, 11.2), # HPMC E5 (Adopted; K100M is not E5)
        "POL-002-2026": (16.5, 10.2, 10.4),# Kollidon VA64 ACS 2026
        "POL-001-2026": (16.9, 9.3, 11.3), # Povidone K30 ACS 2026
        "POL-007-2026": (17.2, 5.3, 8.6),  # Eudragit EPO ACS 2026
    }

    ahp = AHPWeightElicitor()
    with open(cm.get_ahp_matrix_dir() / "default_matrix.json", "r") as f:
        ahp_raw = json.load(f)
    w_ahp = ahp.aggregate_multi_expert_matrices([np.array(ahp_raw["pairwise_matrix"])]).weights

    print("\n=== RANKING SENSITIVITY (Scenario A vs Scenario B) ===")
    for label, hsp_dict in [("Scenario A (Production Baseline)", hsp_sc_A), ("Scenario B (Experimental ACS Hybrid)", hsp_sc_B)]:
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
        print(f"\n--- {label} ---")
        for _, row in df_r.iterrows():
            p_name = next(p.polymer_name for p in polys if p.polymer_id == row["polymer_id"])
            print(f"Rank #{row['topsis_rank']}: {p_name:32s} | TOPSIS CL={row['topsis_cl']:.6f}")

if __name__ == "__main__":
    run_n10_calibration()
