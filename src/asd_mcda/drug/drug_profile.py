"""
Immutable Drug dataclass representing the physicochemical identity of the API.
Aligned with SAS V1.0 Section 6.1.
"""

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from asd_mcda.utils.constants import BOYER_BEAMAN_FACTOR
from asd_mcda.utils.helpers import generate_sha256
from asd_mcda.utils.rdkit_wrapper import canonicalize_smiles, get_inchi_key, compute_2d_descriptors


@dataclass(frozen=True)
class Drug:
    """Immutable value object representing an Active Pharmaceutical Ingredient (API)."""

    drug_id: str
    generic_name: str
    canonical_smiles: str
    inchi_key: str
    molecular_weight_g_mol: float
    tm_k: float
    tg_k: Optional[float]
    tg_k_estimated: float
    tg_source: str
    density_crystalline_g_cm3: float
    density_amorphous_g_cm3: Optional[float]
    density_source: str
    pka: Optional[float]
    logp: float
    logd_ph74: Optional[float]
    hbd: int
    hba: int
    tpsa_angstrom2: float
    rotatable_bonds: int
    aromatic_rings: int
    hsp_delta_d: float
    hsp_delta_p: float
    hsp_delta_h: float
    hsp_ro: float
    hsp_source: str
    molar_volume_cm3_mol: float
    delta_h_fus_kj_mol: Optional[float] = None
    bcs_class: str = "II"
    polymorphs: List[str] = field(default_factory=lambda: ["gamma", "alpha"])
    ionisation_state: str = "neutral"
    data_quality_score: float = 1.0
    validation_status: str = "validated"
    checksum_sha256: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Drug":
        """Factory method creating a Drug instance from dictionary with validation and automatic descriptor derivation."""
        smiles = canonicalize_smiles(data["canonical_smiles"])
        inchi_key = data.get("inchi_key") or get_inchi_key(smiles)

        # Compute 2D descriptors if missing
        descriptors_2d = compute_2d_descriptors(smiles)
        mw = data.get("molecular_weight_g_mol") or descriptors_2d["MolWt"]
        logp = data.get("logp") or descriptors_2d["MolLogP"]
        hbd = data.get("hbd") if data.get("hbd") is not None else descriptors_2d["NumHDonors"]
        hba = data.get("hba") if data.get("hba") is not None else descriptors_2d["NumHAcceptors"]
        tpsa = data.get("tpsa_angstrom2") or descriptors_2d["TPSA"]
        rotb = data.get("rotatable_bonds") if data.get("rotatable_bonds") is not None else descriptors_2d["NumRotatableBonds"]
        arom = data.get("aromatic_rings") if data.get("aromatic_rings") is not None else descriptors_2d["NumAromaticRings"]

        tm_k = float(data["tm_k"])
        tg_k_estimated = data.get("tg_k_estimated") or (tm_k * BOYER_BEAMAN_FACTOR)
        tg_k = float(data["tg_k"]) if data.get("tg_k") is not None else None

        checksum = generate_sha256(data)

        return cls(
            drug_id=str(data["drug_id"]),
            generic_name=str(data["generic_name"]),
            canonical_smiles=smiles,
            inchi_key=inchi_key,
            molecular_weight_g_mol=float(mw),
            tm_k=tm_k,
            tg_k=tg_k,
            tg_k_estimated=float(tg_k_estimated),
            tg_source=str(data.get("tg_source", "experimental" if tg_k else "boyer_beaman")),
            density_crystalline_g_cm3=float(data.get("density_crystalline_g_cm3", 1.31)),
            density_amorphous_g_cm3=float(data["density_amorphous_g_cm3"]) if data.get("density_amorphous_g_cm3") else None,
            density_source=str(data.get("density_source", "literature")),
            pka=float(data["pka"]) if data.get("pka") is not None else None,
            logp=float(logp),
            logd_ph74=float(data["logd_ph74"]) if data.get("logd_ph74") is not None else None,
            hbd=int(hbd),
            hba=int(hba),
            tpsa_angstrom2=float(tpsa),
            rotatable_bonds=int(rotb),
            aromatic_rings=int(arom),
            hsp_delta_d=float(data.get("hsp_delta_d", 19.2)),
            hsp_delta_p=float(data.get("hsp_delta_p", 7.9)),
            hsp_delta_h=float(data.get("hsp_delta_h", 8.4)),
            hsp_ro=float(data.get("hsp_ro", 8.0)),
            hsp_source=str(data.get("hsp_source", "literature")),
            molar_volume_cm3_mol=float(data.get("molar_volume_cm3_mol", 273.0)),
            delta_h_fus_kj_mol=float(data["delta_h_fus_kj_mol"]) if data.get("delta_h_fus_kj_mol") else None,
            bcs_class=str(data.get("bcs_class", "II")),
            polymorphs=data.get("polymorphs", ["gamma", "alpha"]),
            ionisation_state=str(data.get("ionisation_state", "neutral")),
            data_quality_score=float(data.get("data_quality_score", 1.0)),
            validation_status=str(data.get("validation_status", "validated")),
            checksum_sha256=checksum,
        )

    @classmethod
    def from_json(cls, path: Union[str, Path]) -> "Drug":
        """Load drug profile from JSON file."""
        path = Path(path)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)

    def estimate_tg(self) -> float:
        """Return experimental Tg if available, else Boyer-Beaman estimate."""
        return self.tg_k if self.tg_k is not None else self.tg_k_estimated

    def get_preferred_density(self) -> Tuple[float, str]:
        """Return amorphous density if available, else crystalline density with systematic bias flag."""
        if self.density_amorphous_g_cm3 is not None:
            return self.density_amorphous_g_cm3, "amorphous"
        return self.density_crystalline_g_cm3, "crystalline_systematic_bias_flag"

    def validate_plausibility(self) -> List[str]:
        """Check plausibility rules per SAS V1.0 Section 6.1."""
        warnings = []
        if not (300 < self.tm_k < 800):
            warnings.append(f"Melting point Tm ({self.tm_k} K) outside standard 300-800 K range.")
        dens, source = self.get_preferred_density()
        if not (0.8 < dens < 2.0):
            warnings.append(f"Density ({dens} g/cm3) outside standard 0.8-2.0 g/cm3 range.")
        return warnings
