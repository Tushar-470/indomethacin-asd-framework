"""
DescriptorEngine class generating 2D RDKit molecular descriptors and group-contribution HSP values.
Aligned with SAS V1.0 Section 6.2.
"""

import pandas as pd
from typing import Dict, Any

from asd_mcda.drug.drug_profile import Drug
from asd_mcda.polymer.polymer_library import Polymer, PolymerLibrary
from asd_mcda.utils.rdkit_wrapper import compute_2d_descriptors


class DescriptorEngine:
    """Computes 2D molecular descriptors and group-contribution HSP for drug and candidate polymers."""

    def __init__(self, drug: Drug, polymer_library: PolymerLibrary):
        self.drug = drug
        self.polymer_library = polymer_library

    def compute_drug_descriptors(self) -> Dict[str, float]:
        """Compute 2D molecular descriptors for the active pharmaceutical ingredient."""
        desc = compute_2d_descriptors(self.drug.canonical_smiles)
        desc.update({
            "HSP_delta_D": self.drug.hsp_delta_d,
            "HSP_delta_P": self.drug.hsp_delta_p,
            "HSP_delta_H": self.drug.hsp_delta_h,
        })
        return desc

    def compute_polymer_descriptors(self, polymer: Polymer) -> Dict[str, float]:
        """Compute 2D molecular descriptors for a polymer (copolymer mole-fraction weighted)."""
        desc = polymer.get_weighted_2d_descriptors()
        desc.update({
            "HSP_delta_D": polymer.hsp_delta_d,
            "HSP_delta_P": polymer.hsp_delta_p,
            "HSP_delta_H": polymer.hsp_delta_h,
        })
        return desc

    def build_descriptor_matrix(self) -> pd.DataFrame:
        """Build N x k DataFrame of descriptors for all polymers in library."""
        records = []
        for polymer in self.polymer_library.polymers:
            desc = self.compute_polymer_descriptors(polymer)
            desc["polymer_id"] = polymer.polymer_id
            desc["abbreviation"] = polymer.abbreviation
            records.append(desc)

        df = pd.DataFrame(records)
        df.set_index("polymer_id", inplace=True)
        return df
