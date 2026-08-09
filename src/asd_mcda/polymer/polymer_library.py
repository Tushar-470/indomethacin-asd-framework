"""
Polymer dataclass and PolymerLibrary collection container.
Aligned with SAS V1.0 Section 6.1 and DAS V1.0 Section 4.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Union
import pandas as pd

from asd_mcda.drug.drug_profile import Drug
from asd_mcda.utils.helpers import generate_sha256
from asd_mcda.utils.rdkit_wrapper import canonicalize_smiles, compute_2d_descriptors


@dataclass(frozen=True)
class Polymer:
    """Immutable value object representing a candidate polymeric carrier."""

    polymer_id: str
    polymer_name: str
    abbreviation: str
    polymer_family: str
    polymer_class: str
    regulatory_status: str
    mn_da: float
    mw_da: Optional[float]
    pdi: float
    tg_k: float
    density_g_cm3: float
    hsp_delta_d: float
    hsp_delta_p: float
    hsp_delta_h: float
    hsp_total: float
    functional_groups: List[str]
    monomer_smiles: Union[str, List[str]]
    copolymer_mole_fractions: Optional[List[float]] = None
    literature_evidence_score: float = 0.5
    spray_drying_suitability: str = "good"
    hygroscopicity: str = "slightly"
    validation_status: str = "validated"
    checksum_sha256: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Polymer":
        """Factory method to parse dictionary into Polymer dataclass."""
        raw_smiles = str(data["monomer_smiles"])
        if "|" in raw_smiles:
            monomer_smiles = [canonicalize_smiles(s) for s in raw_smiles.split("|")]
        else:
            monomer_smiles = canonicalize_smiles(raw_smiles)

        fractions_raw = data.get("copolymer_mole_fractions")
        if isinstance(fractions_raw, str) and "|" in fractions_raw:
            mole_fractions = [float(x) for x in fractions_raw.split("|")]
        elif isinstance(fractions_raw, list):
            mole_fractions = [float(x) for x in fractions_raw]
        else:
            mole_fractions = None

        fg_raw = data.get("functional_groups", "")
        fg_list = fg_raw.split("|") if isinstance(fg_raw, str) else fg_raw

        checksum = generate_sha256(data)

        d_d = float(data["hsp_delta_d"])
        d_p = float(data["hsp_delta_p"])
        d_h = float(data["hsp_delta_h"])
        hsp_total = float(data.get("hsp_total") or (d_d**2 + d_p**2 + d_h**2) ** 0.5)

        return cls(
            polymer_id=str(data["polymer_id"]),
            polymer_name=str(data["polymer_name"]),
            abbreviation=str(data.get("abbreviation", data["polymer_name"])),
            polymer_family=str(data.get("polymer_family", "vinylic")),
            polymer_class=str(data.get("polymer_class", "neutral")),
            regulatory_status=str(data.get("regulatory_status", "FDA_IID")),
            mn_da=float(data["mn_da"]),
            mw_da=float(data["mw_da"]) if (data.get("mw_da") is not None and not pd.isna(data.get("mw_da"))) else None,
            pdi=float(data.get("pdi", 1.2)),
            tg_k=float(data["tg_k"]),
            density_g_cm3=float(data.get("density_g_cm3", 1.20)),
            hsp_delta_d=d_d,
            hsp_delta_p=d_p,
            hsp_delta_h=d_h,
            hsp_total=hsp_total,
            functional_groups=fg_list if isinstance(fg_list, list) else [],
            monomer_smiles=monomer_smiles,
            copolymer_mole_fractions=mole_fractions,
            literature_evidence_score=float(data.get("literature_evidence_score", 0.5)),
            spray_drying_suitability=str(data.get("spray_drying_suitability", "good")),
            hygroscopicity=str(data.get("hygroscopicity", "slightly")),
            validation_status=str(data.get("validation_status", "validated")),
            checksum_sha256=checksum,
        )


    def is_copolymer(self) -> bool:
        """Return True if polymer is a copolymer with multiple monomer SMILES."""
        return isinstance(self.monomer_smiles, list) and len(self.monomer_smiles) > 1

    def get_weighted_2d_descriptors(self) -> Dict[str, float]:
        """Compute polymer repeat unit 2D descriptors (weighted average for copolymers)."""
        if not self.is_copolymer():
            smiles = self.monomer_smiles if isinstance(self.monomer_smiles, str) else self.monomer_smiles[0]
            return compute_2d_descriptors(smiles)

        # Copolymer weighted average
        smiles_list = self.monomer_smiles
        weights = self.copolymer_mole_fractions or [1.0 / len(smiles_list)] * len(smiles_list)
        
        aggregated: Dict[str, float] = {}
        for sm, w in zip(smiles_list, weights):
            desc = compute_2d_descriptors(sm)
            for k, v in desc.items():
                aggregated[k] = aggregated.get(k, 0.0) + w * float(v)
        return aggregated


class PolymerLibrary:
    """Container collection for candidate polymers in screening library."""

    def __init__(self, polymers: List[Polymer], drug: Optional[Drug] = None):
        self.polymers = polymers
        self.drug = drug

    def __len__(self) -> int:
        return len(self.polymers)

    def __getitem__(self, idx: int) -> Polymer:
        return self.polymers[idx]

    @classmethod
    def from_csv(cls, path: Union[str, Path], drug: Optional[Drug] = None) -> "PolymerLibrary":
        """Load polymer library from CSV file."""
        df = pd.read_csv(Path(path))
        polymers = [Polymer.from_dict(row.to_dict()) for _, row in df.iterrows()]
        return cls(polymers=polymers, drug=drug)

    def get_by_id(self, polymer_id: str) -> Optional[Polymer]:
        """Get polymer by polymer_id."""
        for p in self.polymers:
            if p.polymer_id == polymer_id:
                return p
        return None

    def get_polymer(self, polymer_id: str) -> Optional[Polymer]:
        """Alias for get_by_id."""
        return self.get_by_id(polymer_id)

    def to_dataframe(self) -> pd.DataFrame:

        """Convert polymer library attributes into pandas DataFrame."""
        records = []
        for p in self.polymers:
            records.append({
                "polymer_id": p.polymer_id,
                "polymer_name": p.polymer_name,
                "abbreviation": p.abbreviation,
                "polymer_class": p.polymer_class,
                "mn_da": p.mn_da,
                "pdi": p.pdi,
                "tg_k": p.tg_k,
                "density_g_cm3": p.density_g_cm3,
                "hsp_delta_d": p.hsp_delta_d,
                "hsp_delta_p": p.hsp_delta_p,
                "hsp_delta_h": p.hsp_delta_h,
                "hsp_total": p.hsp_total,
                "literature_evidence_score": p.literature_evidence_score,
            })
        return pd.DataFrame(records)
