"""
Hansen Solubility Parameter (HSP) distance and RED number calculation engine.
Aligned with Master Research Framework V2.0 Section 6.1 (Eqs 1-2).
"""

import numpy as np
import pandas as pd
from typing import Dict, List, NamedTuple

from asd_mcda.drug.drug_profile import Drug
from asd_mcda.polymer.polymer_library import Polymer, PolymerLibrary


class GateResult(NamedTuple):
    passed: bool
    n_passing: int
    threshold: float
    message: str


class HSPModel:
    """Calculates Hansen Solubility Parameter distance Ra, RED number, and s_HSP compatibility score."""

    def __init__(self, drug: Drug, polymer_library: PolymerLibrary, temperature_k: float = 298.15):
        self.drug = drug
        self.polymer_library = polymer_library
        self.temperature_k = temperature_k

    def compute_ra(self, polymer: Polymer) -> float:
        """
        Compute HSP distance Ra (Equation 1, Hansen 2007).
        Ra = sqrt( 4*(delta_D1 - delta_D2)^2 + (delta_P1 - delta_P2)^2 + (delta_H1 - delta_H2)^2 )
        """
        dd = self.drug.hsp_delta_d - polymer.hsp_delta_d
        dp = self.drug.hsp_delta_p - polymer.hsp_delta_p
        dh = self.drug.hsp_delta_h - polymer.hsp_delta_h
        return float(np.sqrt(4.0 * (dd**2) + (dp**2) + (dh**2)))

    def compute_red(self, polymer: Polymer) -> float:
        """
        Compute Relative Energy Difference RED number (Equation 2).
        RED = Ra / R_o
        """
        ra = self.compute_ra(polymer)
        r_o = self.drug.hsp_ro if self.drug.hsp_ro > 0 else 8.0
        return float(ra / r_o)

    def compute_s_hsp(self, polymer: Polymer) -> float:
        """
        Compute normalized HSP compatibility score s_HSP.
        s_HSP = max(0, 1 - RED / 2)
        """
        red = self.compute_red(polymer)
        return float(max(0.0, 1.0 - red / 2.0))

    def build_hsp_scores(self) -> pd.DataFrame:
        """Build DataFrame with HSP distance Ra, RED number, and s_HSP for all candidate polymers."""
        records = []
        for polymer in self.polymer_library.polymers:
            ra = self.compute_ra(polymer)
            red = self.compute_red(polymer)
            s_hsp = self.compute_s_hsp(polymer)
            records.append({
                "polymer_id": polymer.polymer_id,
                "abbreviation": polymer.abbreviation,
                "hsp_distance_ra": ra,
                "hsp_red": red,
                "s_hsp_score": s_hsp,
            })
        df = pd.DataFrame(records)
        df.set_index("polymer_id", inplace=False)
        return df

    def check_gate1(self, red_threshold: float = 1.0, min_passing: int = 3) -> GateResult:
        """Gate 1 (HSP Filter): Check if at least min_passing polymers pass RED <= threshold."""
        df = self.build_hsp_scores()
        passing = df[df["hsp_red"] <= red_threshold]
        n_passing = len(passing)
        passed = n_passing >= min_passing
        msg = f"Gate 1 {'PASSED' if passed else 'FAILED'}: {n_passing}/{len(df)} polymers have RED <= {red_threshold} (minimum required: {min_passing})."
        return GateResult(passed=passed, n_passing=n_passing, threshold=red_threshold, message=msg)
