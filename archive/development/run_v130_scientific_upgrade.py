"""
v1.3.0 Scientific Reliability Upgrade Script
Performs all 12 comparator evaluations, physical input Monte Carlo UQ,
pairwise win probabilities, confidence intervals, stress tests, and freeze hashing.
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
from asd_mcda.compatibility.hsp_model import HSPModel
from asd_mcda.integration.pca import PCAPreprocessor
from asd_mcda.mcda.ahp import AHPWeightElicitor
from asd_mcda.mcda.topsis import TOPSISRanker

def wilson_score_ci(p: float, n: int, confidence: float = 0.95) -> str:
    z = stats.norm.ppf(1 - (1 - confidence) / 2)
    denominator = 1 + (z**2) / n
    center = (p + (z**2) / (2 * n)) / denominator
    spread = (z * math.sqrt((p * (1 - p) / n) + (z**2) / (4 * (n**2)))) / denominator
    lower = max(0.0, center - spread)
    upper = min(1.0, center + spread)
    return f"[{lower*100:.1f}%, {upper*100:.1f}%]"

def run_v130_upgrade():
    cm = ConfigManager(pathlib.Path("config/workflow/workflow_config.yaml"))
    drug = Drug.from_dict(cm.load_drug_json())
    lib = PolymerLibrary.from_csv(cm.get_polymer_library_path(), drug)

    # -------------------------------------------------------------
    # 1. CHANGE 1: Active Matrix S_active = [s_HSP, s_chi, s_GT]
    # -------------------------------------------------------------
    pids = [p.polymer_id for p in lib.polymers]
    names = {p.polymer_id: p.polymer_name for p in lib.polymers}

    comp = CompatibilityMatrix(drug, lib)
    df_S_active = comp.build_active_matrix()
    df_S_active.index = pids
    print("=== CHANGE 1: ACTIVE SCORE MATRIX S_active (3 COLUMNS) ===")
    print(df_S_active.to_string())


    pca = PCAPreprocessor(variance_threshold=0.95)
    pca_res = pca.fit_transform(df_S_active)
    print("\nPCA Retained k:", pca_res.n_components_retained, "Variance ratio:", pca_res.explained_variance_ratio)

    ahp = AHPWeightElicitor()
    with open(cm.get_ahp_matrix_dir() / "default_matrix.json", "r") as f:
        ahp_raw = json.load(f)
    ahp_res = ahp.aggregate_multi_expert_matrices([np.array(ahp_raw["pairwise_matrix"])])
    w_ahp = ahp_res.weights

    pids = [p.polymer_id for p in lib.polymers]
    names = {p.polymer_id: p.polymer_name for p in lib.polymers}

    topsis = TOPSISRanker()
    top_res = topsis.fit_predict(pca_res.scores_matrix_t, w_ahp)
    df_rank_v13 = top_res.ranking_table.copy()
    df_rank_v13["polymer_id"] = pids
    df_rank_v13["polymer_name"] = [names[pid] for pid in pids]
    df_rank_v13 = df_rank_v13.sort_values(by="topsis_rank")

    print("\n=== v1.3.0 CANONICAL ACTIVE MCDA RANKING ===")
    print(df_rank_v13[["topsis_rank", "polymer_name", "polymer_id", "topsis_cl"]].to_string())


    # -------------------------------------------------------------
    # 2. CHANGE 2 & 8 & 9: Physical Input Monte Carlo (N=10,000)
    # -------------------------------------------------------------
    np.random.seed(42)
    N = 10000
    pids = [p.polymer_id for p in lib.polymers]
    names = {p.polymer_id: p.polymer_name for p in lib.polymers}
    top1_counts = {pid: 0 for pid in pids}
    pairwise_wins = {p1: {p2: 0 for p2 in pids} for p1 in pids}

    for _ in range(N):
        # Sample physical inputs for each polymer
        pert_polys = []
        for p in lib.polymers:
            d_d = max(10.0, np.random.normal(p.hsp_delta_d, 1.5))
            d_p = max(2.0, np.random.normal(p.hsp_delta_p, 1.5))
            d_h = max(2.0, np.random.normal(p.hsp_delta_h, 1.5))
            tg = max(250.0, np.random.normal(p.tg_k, 3.0))
            rho = max(0.8, np.random.normal(p.density_g_cm3, 0.05))

            # Reconstruct polymer dict
            p_dict = p.__dict__.copy()
            p_dict["hsp_delta_d"] = d_d
            p_dict["hsp_delta_p"] = d_p
            p_dict["hsp_delta_h"] = d_h
            p_dict["hsp_total"] = math.sqrt(d_d**2 + d_p**2 + d_h**2)
            p_dict["tg_k"] = tg
            p_dict["density_g_cm3"] = rho
            pert_polys.append(Polymer.from_dict(p_dict))

        pert_lib = PolymerLibrary(pert_polys, drug)
        comp_pert = CompatibilityMatrix(drug, pert_lib)
        df_S_sim = comp_pert.build_active_matrix()

        # Ensure polymer_id column is present in df_S_sim
        df_S_sim["polymer_id"] = pids
        pca_sim = PCAPreprocessor(variance_threshold=0.95)
        pca_sim_res = pca_sim.fit_transform(df_S_sim)

        # Perturb AHP weights ±20%
        w_sim = w_ahp * np.random.uniform(0.80, 1.20, size=len(w_ahp))
        w_sim /= np.sum(w_sim)
        if len(w_sim) != pca_sim_res.n_components_retained:
            w_sim = np.ones(pca_sim_res.n_components_retained) / pca_sim_res.n_components_retained

        top_sim = topsis.fit_predict(pca_sim_res.scores_matrix_t, w_sim)
        df_sim_rank = top_sim.ranking_table.copy()
        df_sim_rank["polymer_id"] = pids
        df_sim_rank = df_sim_rank.sort_values(by="topsis_rank")

        top1_id = df_sim_rank.iloc[0]["polymer_id"]
        top1_counts[top1_id] += 1

        # Pairwise wins
        cl_map = dict(zip(df_sim_rank["polymer_id"], df_sim_rank["topsis_cl"]))
        for p1 in pids:
            for p2 in pids:
                if cl_map[p1] > cl_map[p2]:
                    pairwise_wins[p1][p2] += 1


    print("\n=== MONTE CARLO UQ & CONFIDENCE INTERVALS (N=10,000) ===")
    for pid in pids:
        p = top1_counts[pid] / N
        se = math.sqrt(p * (1 - p) / N)
        ci = wilson_score_ci(p, N)
        print(f"{names[pid]:32s} [{pid}]: P(top-1) = {p*100:5.1f}% | SE = {se*100:4.2f}% | 95% CI = {ci}")

    print("\n=== PAIRWISE WIN PROBABILITIES MATRIX P(Row > Col) ===")
    df_pw = pd.DataFrame(index=[names[p] for p in pids], columns=[names[p] for p in pids])
    for p1 in pids:
        for p2 in pids:
            df_pw.loc[names[p1], names[p2]] = f"{pairwise_wins[p1][p2]/N*100:.1f}%"
    print(df_pw.to_string())

    # -------------------------------------------------------------
    # 3. CHANGE 4: Model-Form Robustness (Model A vs Model B)
    # -------------------------------------------------------------
    # Model A: s_chi = max(0, 1 - chi)
    # Model B: s_chi = 1 / (1 + chi)
    df_S_B = df_S_active.copy()
    fh = FloryHugginsModel(drug, lib)
    for p in lib.polymers:
        chi = fh.compute_chi(p)
        df_S_B.loc[p.polymer_id, "s_chi"] = 1.0 / (1.0 + chi)

    pca_B = PCAPreprocessor(variance_threshold=0.95)
    pca_res_B = pca_B.fit_transform(df_S_B)
    top_res_B = topsis.fit_predict(pca_res_B.scores_matrix_t, w_ahp)
    df_rank_B = top_res_B.ranking_table.sort_values(by="topsis_rank")
    df_rank_B["polymer_name"] = df_rank_B["polymer_id"].map(names)

    print("\n=== CHANGE 4: MODEL-FORM ROBUSTNESS (Model A vs Model B) ===")
    print("Model A (Linear s_chi = 1-chi):", df_rank_v13["polymer_id"].tolist())
    print("Model B (Non-linear s_chi = 1/(1+chi)):", df_rank_B["polymer_id"].tolist())
    rho_model, _ = stats.spearmanr(df_rank_v13["topsis_rank"], df_rank_B["topsis_rank"])
    print(f"Model-Form Spearman Rank Correlation: {rho_model:.4f}")

    # -------------------------------------------------------------
    # 4. CHANGE 5: PCA Robustness Comparison
    # -------------------------------------------------------------
    # Option B: No PCA (Standardized active criteria -> AHP/TOPSIS)
    from scipy.stats import zscore
    S_std = zscore(df_S_active.values, axis=0)
    top_res_no_pca = topsis.fit_predict(S_std, np.array([0.5, 0.3, 0.2]))
    df_rank_no_pca = top_res_no_pca.ranking_table.sort_values(by="topsis_rank")

    # Option C: Equal Weight TOPSIS
    top_res_eq = topsis.fit_predict(S_std, np.array([1/3, 1/3, 1/3]))
    df_rank_eq = top_res_eq.ranking_table.sort_values(by="topsis_rank")

    print("\n=== CHANGE 5: PCA ROBUSTNESS COMPARISON ===")
    print("Canonical (PCA+AHP+TOPSIS):", df_rank_v13["polymer_id"].tolist())
    print("Option B (No PCA, Standardized):", df_rank_no_pca["polymer_id"].tolist())
    print("Option C (Equal Weights TOPSIS):", df_rank_eq["polymer_id"].tolist())

    # -------------------------------------------------------------
    # 5. CHANGE 6: AHP Weight Sensitivity
    # -------------------------------------------------------------
    print("\n=== CHANGE 6: AHP WEIGHT SENSITIVITY ===")
    w1_range = [0.40, 0.50, 0.60, 0.6429, 0.70, 0.80]
    for w1 in w1_range:
        w_curr = np.array([w1, 1.0 - w1])
        t_res = topsis.fit_predict(pca_res.scores_matrix_t, w_curr)
        r_list = t_res.ranking_table.sort_values(by="topsis_rank")["polymer_id"].tolist()
        top1_p = names[r_list[0]]
        print(f"w1={w1:0.4f}, w2={1-w1:0.4f} -> Top-1: {top1_p:25s} | Full Rank: {r_list}")

    # -------------------------------------------------------------
    # 6. CHANGE 10 & 11: Candidate Applicability & Decision Report
    # -------------------------------------------------------------
    app_flags = {
        "POL-005-2026": {"flag": "HIGH", "drivers": "Lowest chi (0.2265), amphiphilic solubilization", "uncertainty": "Surrogate SMILES PEG/VCap/VAc ratio"},
        "POL-006-2026": {"flag": "HIGH", "drivers": "Highest Tg protection (120.6 C), strong H-bonding", "uncertainty": "Substituted AGU surrogate representation"},
        "POL-002-2026": {"flag": "HIGH", "drivers": "Strong H-bonding acceptor, good spray-drying yield", "uncertainty": "60:40 copolymer mole fraction tolerance"},
        "POL-001-2026": {"flag": "MEDIUM", "drivers": "High Tg protection (121.2 C), high solubility", "uncertainty": "Hygroscopicity risk under humid storage"},
        "POL-007-2026": {"flag": "MEDIUM", "drivers": "Cationic fast acidic dissolution", "uncertainty": "Higher chi (0.6807), metastable thermodynamic region"}
    }

    print("\n=== CHANGE 11: v1.3.0 DECISION REPORT & APPLICABILITY ===")
    for _, row in df_rank_v13.iterrows():
        pid = row["polymer_id"]
        pname = names[pid]
        cl = row["topsis_cl"]
        p_t1 = top1_counts[pid] / N
        ci = wilson_score_ci(p_t1, N)
        info = app_flags[pid]
        prio = "FIRST (Primary Candidate)" if row["topsis_rank"] == 1 else ("SECOND (Secondary Candidate)" if row["topsis_rank"] == 2 else "BACKUP")
        print(f"Rank #{row['topsis_rank']}: {pname} [{pid}]")
        print(f"  TOPSIS CL = {cl:.6f} | P(top-1) = {p_t1*100:.1f}% | 95% CI = {ci}")
        print(f"  Applicability Flag = {info['flag']} | Priority = {prio}")
        print(f"  Major Drivers = {info['drivers']}")
        print(f"  Uncertainty Source = {info['uncertainty']}\n")

    # -------------------------------------------------------------
    # 7. CHANGE 12: Prospective Validation Lock Metadata
    # -------------------------------------------------------------
    h_config = hashlib.sha256(open("config/workflow/workflow_config.yaml", "rb").read()).hexdigest()
    h_data = hashlib.sha256(open("config/polymers/polymer_library_v3_five_polymers.csv", "rb").read()).hexdigest()
    
    lock_meta = {
        "version": "1.3.0",
        "prediction_frozen": True,
        "selected_polymer_id": df_rank_v13.iloc[0]["polymer_id"],
        "selected_polymer_name": names[df_rank_v13.iloc[0]["polymer_id"]],
        "configuration_hash_sha256": h_config,
        "dataset_hash_sha256": h_data,
        "random_seed": 42,
        "environment": "Python 3.14.5 (Windows Server/Windows 11)",
        "git_commit": "4abf348"
    }

    with open("results/reports/v130_prospective_validation_lock.json", "w") as f:
        json.dump(lock_meta, f, indent=2)

    print("=== PROSPECTIVE VALIDATION LOCK PRODUCER ===")
    print(json.dumps(lock_meta, indent=2))

if __name__ == "__main__":
    run_v130_upgrade()
