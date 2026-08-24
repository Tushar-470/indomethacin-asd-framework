"""
Pydantic schemas for API request/response models.
Maps to the existing asd_mcda domain objects without duplicating scientific logic.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime


# ── Drug Schemas ──────────────────────────────────────────────────────────────

class DrugProfileCreate(BaseModel):
    """Schema for creating a new drug profile."""
    drug_id: str = Field(..., description="Unique drug identifier")
    generic_name: str = Field(..., description="Generic drug name")
    canonical_smiles: str = Field(..., description="Canonical SMILES string")
    molecular_weight_g_mol: float = Field(..., gt=0)
    tm_k: float = Field(..., gt=0, description="Melting point in Kelvin")
    tg_k: Optional[float] = Field(None, description="Experimental Tg in Kelvin")
    tg_k_estimated: Optional[float] = None
    tg_source: str = "experimental"
    density_crystalline_g_cm3: float = Field(1.31, gt=0)
    density_amorphous_g_cm3: Optional[float] = None
    density_source: str = "literature"
    pka: Optional[float] = None
    logp: Optional[float] = None
    logd_ph74: Optional[float] = None
    hbd: Optional[int] = None
    hba: Optional[int] = None
    tpsa_angstrom2: Optional[float] = None
    rotatable_bonds: Optional[int] = None
    aromatic_rings: Optional[int] = None
    hsp_delta_d: float = Field(..., description="Hansen δD (MPa^0.5)")
    hsp_delta_p: float = Field(..., description="Hansen δP (MPa^0.5)")
    hsp_delta_h: float = Field(..., description="Hansen δH (MPa^0.5)")
    hsp_ro: float = Field(8.0, gt=0, description="Hansen interaction radius R₀")
    hsp_source: str = "literature"
    molar_volume_cm3_mol: float = Field(273.0, gt=0)
    delta_h_fus_kj_mol: Optional[float] = None
    bcs_class: str = "II"
    polymorphs: List[str] = ["gamma", "alpha"]
    ionisation_state: str = "neutral"
    reference_doi: Optional[str] = None
    reference_source: str = "user_entered"
    data_quality_score: float = Field(0.5, ge=0, le=1)
    validation_status: str = "draft"


class DrugProfileResponse(BaseModel):
    """Schema for drug profile API responses."""
    drug_id: str
    generic_name: str
    canonical_smiles: str
    inchi_key: Optional[str] = None
    molecular_weight_g_mol: float
    tm_k: float
    tg_k: Optional[float] = None
    tg_k_estimated: Optional[float] = None
    tg_source: str = ""
    density_crystalline_g_cm3: float = 0.0
    density_amorphous_g_cm3: Optional[float] = None
    density_source: str = ""
    pka: Optional[float] = None
    logp: Optional[float] = None
    logd_ph74: Optional[float] = None
    hbd: Optional[int] = None
    hba: Optional[int] = None
    tpsa_angstrom2: Optional[float] = None
    rotatable_bonds: Optional[int] = None
    aromatic_rings: Optional[int] = None
    hsp_delta_d: float = 0.0
    hsp_delta_p: float = 0.0
    hsp_delta_h: float = 0.0
    hsp_ro: float = 0.0
    hsp_source: str = ""
    molar_volume_cm3_mol: float = 0.0
    delta_h_fus_kj_mol: Optional[float] = None
    bcs_class: str = ""
    polymorphs: List[str] = []
    ionisation_state: str = ""
    reference_doi: Optional[str] = None
    reference_source: str = ""
    data_quality_score: float = 1.0
    validation_status: str = ""
    is_reference: bool = True


# ── Polymer Schemas ───────────────────────────────────────────────────────────

class PolymerCreate(BaseModel):
    """Schema for creating a new polymer."""
    polymer_id: str = Field(..., description="Unique polymer identifier")
    polymer_name: str = Field(..., description="Full polymer name")
    abbreviation: str = Field(..., description="Short abbreviation")
    polymer_family: str = "vinylic"
    polymer_class: str = "neutral"
    regulatory_status: str = "FDA_IID"
    supplier: str = ""
    catalog_number: str = ""
    batch_number: str = ""
    mn_da: float = Field(..., gt=0, description="Number-average MW (Da)")
    mw_da: Optional[float] = None
    pdi: float = Field(1.2, gt=0)
    tg_k: float = Field(..., gt=0, description="Glass transition temperature (K)")
    tg_source: str = "experimental_dsc"
    density_g_cm3: float = Field(1.20, gt=0)
    density_source: str = "literature"
    hsp_delta_d: float = Field(..., description="Hansen δD (MPa^0.5)")
    hsp_delta_p: float = Field(..., description="Hansen δP (MPa^0.5)")
    hsp_delta_h: float = Field(..., description="Hansen δH (MPa^0.5)")
    hsp_total: Optional[float] = None
    hsp_source: str = "hoftyzer_van_krevelen"
    functional_groups: str = ""
    monomer_smiles: str = Field(..., description="SMILES string(s), pipe-separated for copolymers")
    copolymer_mole_fractions: Optional[str] = None
    known_asd_applications: str = ""
    spray_drying_suitability: str = "good"
    hygroscopicity: str = "slightly"
    literature_dois: Optional[str] = None
    data_source: str = "user_entered"
    confidence_level: str = "moderate"
    validation_status: str = "draft"


class PolymerResponse(BaseModel):
    """Schema for polymer API responses."""
    polymer_id: str
    polymer_name: str
    abbreviation: str
    polymer_family: str = ""
    polymer_class: str = ""
    regulatory_status: str = ""
    mn_da: float = 0
    mw_da: Optional[float] = None
    pdi: float = 1.0
    tg_k: float = 0
    density_g_cm3: float = 0
    hsp_delta_d: float = 0
    hsp_delta_p: float = 0
    hsp_delta_h: float = 0
    hsp_total: float = 0
    literature_evidence_score: Optional[float] = None
    spray_drying_suitability: str = ""
    hygroscopicity: str = ""
    validation_status: str = ""
    is_reference: bool = True


# ── Screening Schemas ─────────────────────────────────────────────────────────

class ScreeningRequest(BaseModel):
    """Schema for running a screening analysis."""
    drug_id: str = Field(..., description="Drug profile ID to use")
    polymer_ids: List[str] = Field(..., min_length=2, description="Polymer IDs to screen (min 2)")
    mode: str = Field("exploratory", pattern="^(research|exploratory)$")
    drug_loading_ww: float = Field(0.30, gt=0, lt=1)
    random_seed: int = Field(42, ge=0)


class RankingRow(BaseModel):
    """Single row in the TOPSIS ranking table."""
    rank: int
    polymer_id: str
    polymer_name: str
    abbreviation: str
    topsis_cl: float
    topsis_ideal_distance: float
    topsis_anti_ideal_distance: float
    confidence_p_top1: Optional[float] = None




class ScreeningResponse(BaseModel):
    """Full screening results response."""
    analysis_id: str
    timestamp: str
    mode: str
    drug_id: str
    drug_name: str
    polymer_ids: List[str]
    ranking: List[RankingRow]
    selected_polymer: str
    selected_polymer_id: str
    topsis_cl: float
    confidence_tier: str
    confidence_p_top1: float
    predicted_tg_k: float
    tg_prediction_interval: List[float]
    predicted_chi: float
    chi_critical: float
    miscibility_class: str
    stability_tier: str
    gate1_passed: bool
    gate2_passed: bool
    pca_retained_k: int
    pca_variance_explained: List[float]
    pca_interpretation: List[str]
    uq_p_top1: Dict[str, float]
    uq_gelman_rubin: float
    uq_converged: bool
    oat_top1_stable: bool
    oat_stability_fraction: float
    morris_feature_names: List[str]
    morris_mu: List[float]
    morris_sigma: List[float]
    validation_spearman: float
    validation_classification: str
    baseline_outperforms: bool
    fbm_auc: float
    fbm_actionable: bool
    figures: List[str]
    reports: Dict[str, str]
    software_version: str
    warnings: List[str]


# ── History Schemas ───────────────────────────────────────────────────────────

class AnalysisHistoryEntry(BaseModel):
    """Schema for a single analysis history record."""
    analysis_id: str
    timestamp: str
    drug_id: str
    drug_name: str
    polymer_ids: List[str]
    mode: str
    top_polymer: str
    topsis_cl: float
    confidence_tier: str
    software_version: str
    config_checksum: str
    warnings: List[str] = []


class ValidationResult(BaseModel):
    """Schema for input validation results."""
    status: str = Field(..., pattern="^(VALID|WARNING|INVALID)$")
    errors: List[str] = []
    warnings: List[str] = []
