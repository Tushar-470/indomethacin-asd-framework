"""
Gordon-Taylor glass transition temperature prediction engine.
Aligned with Master Research Framework V2.0 Section 6.1 (Eqs 6-7).
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple

from asd_mcda.drug.drug_profile import Drug
from asd_mcda.polymer.polymer_library import Polymer, PolymerLibrary


class GordonTaylorModel:
    """Calculates Gordon-Taylor Tg_mix, Simha-Boyer K, Kwei option, and s_GT score."""

    def __init__(
        self,
        drug: Drug,
        polymer_library: PolymerLibrary,
        drug_loading_ww: float = 0.30,
        kwei_q: Optional[float] = None,
    ):
        self.drug = drug
        self.polymer_library = polymer_library
        self.drug_loading_ww = drug_loading_ww
        self.kwei_q = kwei_q

    def compute_k_simha_boyer(self, polymer: Polymer) -> Tuple[float, str]:
        """
        Compute Simha-Boyer constant K (Equation 7, Simha & Boyer 1962).
        K = (rho_drug * Tg_drug) / (rho_polymer * Tg_polymer)
        """
        tg_drug = self.drug.estimate_tg()
        dens_drug, dens_source = self.drug.get_preferred_density()
        tg_poly = polymer.tg_k
        dens_poly = polymer.density_g_cm3

        k = (dens_drug * tg_drug) / (dens_poly * tg_poly)
        return float(k), dens_source

    def compute_tg_mix(self, polymer: Polymer, drug_loading: Optional[float] = None) -> float:
        """
        Compute predicted glass transition temperature Tg_mix (Equation 6, Gordon & Taylor 1952).
        Tg_mix = (w1 * Tg1 + K * w2 * Tg2) / (w1 + K * w2)
        where 1 = drug, 2 = polymer.
        """
        w1 = drug_loading if drug_loading is not None else self.drug_loading_ww
        w2 = 1.0 - w1

        tg1 = self.drug.estimate_tg()
        tg2 = polymer.tg_k
        k, _ = self.compute_k_simha_boyer(polymer)

        tg_mix = (w1 * tg1 + k * w2 * tg2) / (w1 + k * w2)
        return float(tg_mix)

    def compute_tg_mix_kwei(self, polymer: Polymer, drug_loading: Optional[float] = None) -> Optional[float]:
        """Compute Kwei-corrected Tg_mix = Tg_gt + q * w1 * w2 if q parameter is available."""
        if self.kwei_q is None:
            return None
        w1 = drug_loading if drug_loading is not None else self.drug_loading_ww
        w2 = 1.0 - w1
        tg_gt = self.compute_tg_mix(polymer, drug_loading)
        return float(tg_gt + self.kwei_q * w1 * w2)

    def compute_s_gt(self, polymer: Polymer, drug_loading: Optional[float] = None) -> float:
        """
        Compute normalized GT compatibility score s_GT.
        s_GT = clip( (Tg_mix - (Tg_drug + 30)) / 50.0, 0, 1 )
        """
        tg_mix = self.compute_tg_mix(polymer, drug_loading)
        tg_drug = self.drug.estimate_tg()
        s_gt = (tg_mix - (tg_drug + 30.0)) / 50.0
        return float(np.clip(s_gt, 0.0, 1.0))

    def build_gt_scores(self, drug_loading: Optional[float] = None) -> pd.DataFrame:
        """Build DataFrame with K, Tg_mix, Tg_kwei, and s_GT for all candidate polymers."""
        records = []
        w1 = drug_loading if drug_loading is not None else self.drug_loading_ww
        for polymer in self.polymer_library.polymers:
            k, dens_source = self.compute_k_simha_boyer(polymer)
            tg_mix = self.compute_tg_mix(polymer, w1)
            tg_kwei = self.compute_tg_mix_kwei(polymer, w1)
            s_gt = self.compute_s_gt(polymer, w1)
            records.append({
                "polymer_id": polymer.polymer_id,
                "abbreviation": polymer.abbreviation,
                "gordon_taylor_k": k,
                "density_source_used": dens_source,
                "predicted_tg_k": tg_mix,
                "predicted_tg_kwei_k": tg_kwei,
                "s_gt_score": s_gt,
            })
        df = pd.DataFrame(records)
        df.set_index("polymer_id", inplace=False)
        return df
