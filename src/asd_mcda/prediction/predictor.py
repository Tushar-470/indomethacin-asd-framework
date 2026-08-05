"""
FormulationPredictor assembling Layer 7 predictions: expected Tg interval, miscibility class,
stability risk tier, and Failure Boundary Map (FBM).
Aligned with SAS V1.0 Section 6.2.
"""

from dataclasses import dataclass
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple

from asd_mcda.compatibility.flory_huggins import FloryHugginsModel
from asd_mcda.compatibility.gordon_taylor import GordonTaylorModel
from asd_mcda.drug.drug_profile import Drug
from asd_mcda.polymer.polymer_library import Polymer, PolymerLibrary
from asd_mcda.prediction.fbm import FailureBoundaryMap, FBMResult


@dataclass
class PredictionReport:
    selected_polymer_id: str
    selected_polymer_name: str
    predicted_tg_k: float
    tg_prediction_interval: Tuple[float, float]
    flory_huggins_chi: float
    chi_critical: float
    miscibility_class: str
    stability_tier_25c_60rh: str
    stability_tier_40c_75rh: str
    risk_recrystallization: str
    risk_phase_separation: str
    risk_hygroscopicity: str
    fbm_result: FBMResult


class FormulationPredictor:
    """Generates complete Layer 7 performance predictions for top-ranked polymer."""

    def __init__(
        self,
        drug: Drug,
        polymer_library: PolymerLibrary,
        drug_loading_ww: float = 0.30,
    ):
        self.drug = drug
        self.polymer_library = polymer_library
        self.drug_loading_ww = drug_loading_ww
        self.gt_model = GordonTaylorModel(drug, polymer_library, drug_loading_ww)
        self.fh_model = FloryHugginsModel(drug, polymer_library)
        self.fbm = FailureBoundaryMap()

    def predict_for_polymer(self, polymer_id: str, rank: int = 1) -> PredictionReport:
        """Generate comprehensive prediction report for a specified polymer."""
        poly = next(p for p in self.polymer_library.polymers if p.polymer_id == polymer_id)

        tg_mix = self.gt_model.compute_tg_mix(poly, self.drug_loading_ww)
        tg_interval = (round(tg_mix - 5.0, 1), round(tg_mix + 5.0, 1))

        chi = self.fh_model.compute_chi(poly)
        chi_c = self.fh_model.compute_chi_critical(poly)

        # Miscibility classification
        if chi < 0.0:
            miscibility = "Miscible (Thermodynamically Favorable, chi < 0)"
        elif chi <= chi_c:
            miscibility = f"Miscible (Below Critical chi_c = {chi_c:.2f})"
        else:
            miscibility = f"Partially Miscible / Immiscible (Exceeds chi_c = {chi_c:.2f})"

        # Stability Tiers
        margin_25c = tg_mix - 298.15
        if margin_25c >= 50.0:
            tier_25c = "High Stability (Tg margin >= 50 K above 25°C)"
            risk_recryst = "Low"
        elif margin_25c >= 30.0:
            tier_25c = "Medium Stability (Tg margin 30-50 K above 25°C)"
            risk_recryst = "Moderate"
        else:
            tier_25c = "Low Stability (Tg margin < 30 K above 25°C)"
            risk_recryst = "High"

        margin_40c = tg_mix - 313.15
        if margin_40c >= 30.0:
            tier_40c = "Medium-High (40°C/75%RH)"
        else:
            tier_40c = "Medium-Low (40°C/75%RH)"

        risk_phase = "High" if chi > chi_c else "Low"
        risk_hygro = poly.hygroscopicity.capitalize()

        # Fit FBM on synthetic DoE
        X_doe, y_doe, _ = self.fbm.generate_synthetic_doe_dataset()
        fbm_res = self.fbm.fit(X_doe, y_doe)

        return PredictionReport(
            selected_polymer_id=poly.polymer_id,
            selected_polymer_name=poly.polymer_name,
            predicted_tg_k=round(tg_mix, 1),
            tg_prediction_interval=tg_interval,
            flory_huggins_chi=round(chi, 3),
            chi_critical=round(chi_c, 3),
            miscibility_class=miscibility,
            stability_tier_25c_60rh=tier_25c,
            stability_tier_40c_75rh=tier_40c,
            risk_recrystallization=risk_recryst,
            risk_phase_separation=risk_phase,
            risk_hygroscopicity=risk_hygro,
            fbm_result=fbm_res,
        )
