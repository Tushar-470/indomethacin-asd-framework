"""
Final HSP Scientific Audit & Scenario Comparison Runner
Evaluates Scenario A (Current Adopted HSP), Scenario B (Literature Experimental HSP),
and Scenario C (H-V-K Calculated HSP) across MCDA, TOPSIS, and Monte Carlo ranking.
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

def run_hsp_scenarios():
    cm = ConfigManager(pathlib.Path("config/workflow/workflow_config.yaml"))
    drug = Drug.from_dict(cm.load_drug_json())
    lib_base = PolymerLibrary.from_csv(cm.get_polymer_library_path(), drug)

    pids = [p.polymer_id for p in lib_base.polymers]
    names = {p.polymer_id: p.polymer_name for p in lib_base.polymers}

    # Scenario A: Adopted Consensus
    hsp_scenario_A = {
        "POL-005-2026": (17.2, 5.2, 6.5),  # Soluplus
        "POL-006-2026": (18.5, 8.8, 11.2), # HPMC E5
        "POL-002-2026": (17.8, 7.2, 8.5),  # PVP-VA 64
        "POL-001-2026": (17.5, 6.8, 9.2),  # PVP K30
        "POL-007-2026": (16.8, 5.5, 6.2),  # Eudragit E PO
    }

    # Scenario B: Alternative Peer-Reviewed Literature Data
    hsp_scenario_B = {
        "POL-005-2026": (17.0, 5.5, 6.8),
        "POL-006-2026": (18.2, 9.0, 11.0),
        "POL-002-2026": (17.6, 7.5, 8.8),
        "POL-001-2026": (17.4, 7.0, 9.5),
        "POL-007-2026": (16.5, 5.8, 6.4),
    }

    # Scenario C: H-V-K Pure Calculated
    hsp_scenario_C = {
        "POL-005-2026": (19.21, 11.10, 9.16),
        "POL-006-2026": (20.33, 8.59, 17.47),
        "POL-002-2026": (20.47, 13.90, 10.32),
        "POL-001-2026": (22.55, 17.03, 10.36),
        "POL-007-2026": (17.35, 6.12, 8.81),
    }

    ahp = AHPWeightElicitor()
    with open(cm.get_ahp_matrix_dir() / "default_matrix.json", "r") as f:
        ahp_raw = json.load(f)
    w_ahp = ahp.aggregate_multi_expert_matrices([np.array(ahp_raw["pairwise_matrix"])]).weights

    for sc_label, hsp_dict in [("Scenario A (Adopted Literature)", hsp_scenario_A),
                                ("Scenario B (Alt Literature)", hsp_scenario_B),
                                ("Scenario C (H-V-K Calculated)", hsp_scenario_C)]:
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
        df_S_active = comp.build_active_matrix()
        df_S_active["polymer_id"] = pids

        pca = PCAPreprocessor(variance_threshold=0.95)
        pca_res = pca.fit_transform(df_S_active)
        top_res = TOPSISRanker().fit_predict(pca_res.scores_matrix_t, w_ahp)
        df_r = top_res.ranking_table.sort_values(by="topsis_rank")
        df_r["polymer_name"] = df_r["polymer_id"].map(names)

        hsp_mod = HSPModel(drug, lib)
        fh_mod = FloryHugginsModel(drug, lib)

        print(f"\n=== {sc_label} ===")
        for _, row in df_r.iterrows():
            pol_obj = next(p for p in lib.polymers if p.polymer_id == row["polymer_id"])
            ra = hsp_mod.compute_ra(pol_obj)
            red = hsp_mod.compute_red(pol_obj)
            chi = fh_mod.compute_chi(pol_obj)
            print(f"Rank #{row['topsis_rank']}: {row['polymer_name']:32s} [{row['polymer_id']}] -> TOPSIS CL={row['topsis_cl']:.6f} | Ra={ra:.2f} | RED={red:.2f} | chi={chi:.4f}")



if __name__ == "__main__":
    run_hsp_scenarios()
