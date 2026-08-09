"""
CompatibilityMatrix assembler creating the normalized N x 5 score matrix S.
Aligned with SAS V1.0 Section 6.2.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional

from asd_mcda.compatibility.flory_huggins import FloryHugginsModel
from asd_mcda.compatibility.gordon_taylor import GordonTaylorModel
from asd_mcda.compatibility.hsp_model import HSPModel
from asd_mcda.descriptors.engine import DescriptorEngine
from asd_mcda.drug.drug_profile import Drug
from asd_mcda.polymer.polymer_library import PolymerLibrary
from asd_mcda.utils.constants import DEFAULT_DESC_SUBWEIGHTS


class CompatibilityMatrix:
    """Assembles and validates the N x 5 normalized compatibility score matrix S."""

    def __init__(
        self,
        drug: Drug,
        polymer_library: PolymerLibrary,
        drug_loading_ww: float = 0.30,
        desc_subweights: Optional[Dict[str, float]] = None,
    ):
        self.drug = drug
        self.polymer_library = polymer_library
        self.drug_loading_ww = drug_loading_ww
        self.desc_subweights = desc_subweights or DEFAULT_DESC_SUBWEIGHTS

        self.hsp_model = HSPModel(drug, polymer_library)
        self.fh_model = FloryHugginsModel(drug, polymer_library)
        self.gt_model = GordonTaylorModel(drug, polymer_library, drug_loading_ww)
        self.desc_engine = DescriptorEngine(drug, polymer_library)

    def compute_s_desc(self, polymer_id: str) -> float:
        """
        Compute weighted descriptor compatibility score s_desc.
        s_desc = w_hbd * match_hbd + w_hba * match_hba + w_tpsa * prox_tpsa + w_arom * ratio_arom
        """
        poly = next(p for p in self.polymer_library.polymers if p.polymer_id == polymer_id)
        p_desc = self.desc_engine.compute_polymer_descriptors(poly)
        d_desc = self.desc_engine.compute_drug_descriptors()

        # HBD match: 1 - |HBD_d - HBD_p| / max(HBD_d, HBD_p, 1)
        hbd_diff = abs(d_desc["NumHDonors"] - p_desc["NumHDonors"])
        hbd_max = max(d_desc["NumHDonors"], p_desc["NumHDonors"], 1)
        match_hbd = max(0.0, 1.0 - hbd_diff / hbd_max)

        # HBA match
        hba_diff = abs(d_desc["NumHAcceptors"] - p_desc["NumHAcceptors"])
        hba_max = max(d_desc["NumHAcceptors"], p_desc["NumHAcceptors"], 1)
        match_hba = max(0.0, 1.0 - hba_diff / hba_max)

        # TPSA proximity: 1 - |TPSA_d - TPSA_p| / 200.0
        tpsa_diff = abs(d_desc["TPSA"] - p_desc["TPSA"])
        prox_tpsa = max(0.0, 1.0 - tpsa_diff / 200.0)

        # Aromatic ratio
        arom_d = d_desc["NumAromaticRings"]
        arom_p = p_desc["NumAromaticRings"]
        ratio_arom = min(arom_d, arom_p) / max(arom_d, arom_p, 1)

        w = self.desc_subweights
        score = (
            w.get("hbd", 0.3) * match_hbd
            + w.get("hba", 0.3) * match_hba
            + w.get("tpsa", 0.2) * prox_tpsa
            + w.get("aromatic", 0.2) * ratio_arom
        )
        return float(np.clip(score, 0.0, 1.0))

    def build_matrix(self) -> pd.DataFrame:
        """Build full N x 5 normalized compatibility matrix S."""
        df_hsp = self.hsp_model.build_hsp_scores()
        df_fh = self.fh_model.build_chi_scores()
        df_gt = self.gt_model.build_gt_scores(self.drug_loading_ww)

        records = []
        for poly in self.polymer_library.polymers:
            pid = poly.polymer_id
            s_hsp = float(df_hsp.loc[df_hsp["polymer_id"] == pid, "s_hsp_score"].values[0])
            s_chi = float(df_fh.loc[df_fh["polymer_id"] == pid, "s_chi_score"].values[0])
            s_gt = float(df_gt.loc[df_gt["polymer_id"] == pid, "s_gt_score"].values[0])
            s_desc = self.compute_s_desc(pid)
            s_lit = float(poly.literature_evidence_score)

            records.append({
                "polymer_id": pid,
                "polymer_name": poly.polymer_name,
                "abbreviation": poly.abbreviation,
                "s_HSP": s_hsp,
                "s_chi": s_chi,
                "s_desc": s_desc,
                "s_GT": s_gt,
                "s_lit": s_lit,
            })


        df = pd.DataFrame(records)
        df.set_index("polymer_id", inplace=False)
        return df

    def get_correlation_matrix(self) -> pd.DataFrame:
        """Return Spearman rank correlation matrix of the 5 raw compatibility scores."""
        df = self.build_matrix()
        score_cols = ["s_HSP", "s_chi", "s_desc", "s_GT", "s_lit"]
        return df[score_cols].corr(method="spearman")
