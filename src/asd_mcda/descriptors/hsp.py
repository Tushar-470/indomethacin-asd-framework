"""
Hansen Solubility Parameter (HSP) estimation via Hoftyzer-Van Krevelen group contribution method.
"""

from typing import Tuple, Optional
from asd_mcda.utils.rdkit_wrapper import hoftyzer_van_krevelen_hsp


def compute_hsp_hoftyzer_van_krevelen(
    smiles: str, molar_volume: Optional[float] = None
) -> Tuple[float, float, float]:
    """
    Compute HSP (delta_D, delta_P, delta_H) in MPa^0.5 via Hoftyzer-Van Krevelen group contribution.
    """
    return hoftyzer_van_krevelen_hsp(smiles, molar_volume)
