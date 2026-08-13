"""
Flory-Huggins interaction parameter chi estimation via Lindvig conversion.
Aligned with Master Research Framework V2.0 Section 6.1 (Eq 5).
"""

import numpy as np
import pandas as pd
from typing import Dict, List

from asd_mcda.drug.drug_profile import Drug
from asd_mcda.polymer.polymer_library import Polymer, PolymerLibrary
from asd_mcda.utils.constants import GAS_CONSTANT_R, LINDVIG_WEIGHTS


class FloryHugginsModel:
    """Calculates Flory-Huggins chi interaction parameter, critical chi_c, and s_chi score."""

    def __init__(
        self,
        drug: Drug,
        polymer_library: PolymerLibrary,
        temperature_k: float = 298.15,
        chi_uncertainty_relative: float = 0.25,
    ):
        self.drug = drug
        self.polymer_library = polymer_library
        self.temperature_k = temperature_k
        self.chi_uncertainty_relative = chi_uncertainty_relative

    def compute_chi(self, polymer: Polymer) -> float:
        """
        Compute Flory-Huggins chi via Lindvig conversion (Equation 5, Lindvig et al. 2002).
        chi = (V_m / (R * T)) * [ 0.60*(dd)^2 + 0.25*(dp)^2 + 0.25*(dh)^2 ]
        """
        w_d, w_p, w_h = LINDVIG_WEIGHTS
        dd = self.drug.hsp_delta_d - polymer.hsp_delta_d
        dp = self.drug.hsp_delta_p - polymer.hsp_delta_p
        dh = self.drug.hsp_delta_h - polymer.hsp_delta_h

        v_m = self.drug.molar_volume_cm3_mol * 1e-6  # m^3/mol
        rt = GAS_CONSTANT_R * self.temperature_k  # J/mol

        # Sum of weighted energy density differences in Pa (1 MPa^0.5 = 1e3 Pa^0.5)
        energy_diff = (w_d * (dd**2) + w_p * (dp**2) + w_h * (dh**2)) * 1e6  # J/m^3

        chi = (v_m / rt) * energy_diff
        return float(chi)

    def compute_chi_critical(self, polymer: Polymer) -> float:
        """
        Compute classical binary Flory-Huggins critical interaction parameter chi_c for phase separation.
        chi_c = 0.5 * (1/sqrt(r1) + 1/sqrt(r2))^2
        where:
          - r1 = 1.0 (small-molecule drug reference component)
          - r2 = V_polymer / V_drug (relative molar volume ratio)
          - V_polymer is derived from number-average molecular weight Mn and density rho.
        Note: chi_c is a secondary phase-boundary/criticality diagnostic and is NOT used as an MCDA ranking score.
        """
        r1 = 1.0
        v_drug = self.drug.molar_volume_cm3_mol
        v_poly = polymer.mn_da / polymer.density_g_cm3 if polymer.density_g_cm3 > 0 else 1000.0
        r2 = v_poly / v_drug if v_drug > 0 else 10.0

        chi_c = 0.5 * (1.0 / np.sqrt(r1) + 1.0 / np.sqrt(r2)) ** 2
        return float(chi_c)


    def compute_s_chi(self, polymer: Polymer) -> float:
        """
        Compute normalized chi compatibility score s_chi.
        s_chi = max(0, 1 - chi)
        """
        chi = self.compute_chi(polymer)
        return float(max(0.0, 1.0 - chi))

    def build_chi_scores(self) -> pd.DataFrame:
        """Build DataFrame with chi, chi_c, and s_chi for all candidate polymers."""
        records = []
        for polymer in self.polymer_library.polymers:
            chi = self.compute_chi(polymer)
            chi_c = self.compute_chi_critical(polymer)
            s_chi = self.compute_s_chi(polymer)
            records.append({
                "polymer_id": polymer.polymer_id,
                "abbreviation": polymer.abbreviation,
                "flory_huggins_chi": chi,
                "chi_critical": chi_c,
                "s_chi_score": s_chi,
            })
        df = pd.DataFrame(records)
        df.set_index("polymer_id", inplace=False)
        return df
