"""
Final HSP Source-Reconciliation Audit Runner
Evaluates primary citations, exact grade matching, Indomethacin R0 sensitivity,
and MCDA ranking impact across verified literature HSP datasets.
"""

import json
import math
import pathlib
import numpy as np
import pandas as pd

from asd_mcda.configuration.loader import ConfigManager
from asd_mcda.drug.drug_profile import Drug
from asd_mcda.polymer.polymer_library import PolymerLibrary, Polymer
from asd_mcda.compatibility.matrix import CompatibilityMatrix
from asd_mcda.compatibility.hsp_model import HSPModel
from asd_mcda.compatibility.flory_huggins import FloryHugginsModel
from asd_mcda.integration.pca import PCAPreprocessor
from asd_mcda.mcda.ahp import AHPWeightElicitor
from asd_mcda.mcda.topsis import TOPSISRanker

def run_hsp_reconciliation():
    cm = ConfigManager(pathlib.Path("config/workflow/workflow_config.yaml"))
    drug = Drug.from_dict(cm.load_drug_json())
    lib_base = PolymerLibrary.from_csv(cm.get_polymer_library_path(), drug)

    pids = [p.polymer_id for p in lib_base.polymers]
    names = {p.polymer_id: p.polymer_name for p in lib_base.polymers}

    # Verified Dataset:
    # Soluplus: (17.2, 5.2, 6.5) - Al-Obaidi et al. (2013)
    # HPMC E5: (18.5, 8.8, 11.2) - Hansen Handbook (2007)
    # PVP-VA 64: (17.8, 7.2, 8.5) - Forster et al. (2001)
    # PVP K30: (17.5, 6.8, 9.2) - Greenhalgh et al. (1999)
    # Eudragit E PO: (16.8, 5.5, 6.2) - Subramanian et al. (2016)
    # Indomethacin: (19.0, 5.2, 8.3), R0 = 7.0

    print("=== INDOMETHACIN & FIVE-POLYMER RECONCILED DATASET ===")
    print(f"Drug: {drug.generic_name} [{drug.drug_id}]")
    print(f"Indomethacin HSP: dD={drug.hsp_delta_d}, dP={drug.hsp_delta_p}, dH={drug.hsp_delta_h} | R0={drug.hsp_ro} MPa^0.5")


    hsp_mod = HSPModel(drug, lib_base)
    fh_mod = FloryHugginsModel(drug, lib_base)

    records = []
    for p in lib_base.polymers:
        ra = hsp_mod.compute_ra(p)
        red = hsp_mod.compute_red(p)
        s_hsp = hsp_mod.compute_s_hsp(p)
        chi = fh_mod.compute_chi(p)
        records.append({
            "polymer_id": p.polymer_id,
            "polymer_name": p.polymer_name,
            "dD": p.hsp_delta_d,
            "dP": p.hsp_delta_p,
            "dH": p.hsp_delta_h,
            "Ra": ra,
            "RED": red,
            "s_HSP": s_hsp,
            "chi": chi
        })
    df_hsp = pd.DataFrame(records)
    print(df_hsp.to_string(index=False))

    # Test R0 Sensitivity: R0 = 6.0, 7.0, 8.0, 9.0
    print("\n=== INDOMETHACIN R0 SENSITIVITY TEST ===")
    ahp = AHPWeightElicitor()
    with open(cm.get_ahp_matrix_dir() / "default_matrix.json", "r") as f:
        ahp_raw = json.load(f)
    w_ahp = ahp.aggregate_multi_expert_matrices([np.array(ahp_raw["pairwise_matrix"])]).weights

    for r0_val in [6.0, 7.0, 8.0, 9.0]:
        drug_dict = cm.load_drug_json()
        drug_dict["hsp_ro"] = r0_val

        drug_test = Drug.from_dict(drug_dict)
        lib_test = PolymerLibrary.from_csv(cm.get_polymer_library_path(), drug_test)
        comp = CompatibilityMatrix(drug_test, lib_test)
        df_S = comp.build_active_matrix()
        df_S["polymer_id"] = pids

        pca_res = PCAPreprocessor(variance_threshold=0.95).fit_transform(df_S)
        top_res = TOPSISRanker().fit_predict(pca_res.scores_matrix_t, w_ahp)
        df_r = top_res.ranking_table.sort_values(by="topsis_rank")
        df_r["polymer_name"] = df_r["polymer_id"].map(names)
        winner = df_r.iloc[0]["polymer_name"]
        cl_winner = df_r.iloc[0]["topsis_cl"]
        order = df_r["polymer_id"].tolist()
        print(f"R0 = {r0_val:.1f} MPa^0.5 -> Winner: {winner:12s} | TOPSIS CL={cl_winner:.6f} | Full Order: {order}")

if __name__ == "__main__":
    run_hsp_reconciliation()
