"""
Input validation service for drug and polymer data.
Provides plausibility checks before data is saved or used in screening.
Does NOT duplicate scientific calculations — only checks data integrity.
"""

from typing import Dict, Any, List, Tuple


def validate_drug_input(data: Dict[str, Any]) -> Tuple[str, List[str], List[str]]:
    """Validate drug profile input data. Returns (status, errors, warnings)."""
    errors: List[str] = []
    warnings: List[str] = []

    # Required fields
    required = ["drug_id", "generic_name", "canonical_smiles", "molecular_weight_g_mol",
                "tm_k", "hsp_delta_d", "hsp_delta_p", "hsp_delta_h"]
    for field in required:
        val = data.get(field)
        if val is None or (isinstance(val, str) and val.strip() == ""):
            errors.append(f"Missing required field: {field}")

    # Plausibility checks
    tm = data.get("tm_k")
    if tm is not None and isinstance(tm, (int, float)):
        if not (300 < tm < 800):
            errors.append(f"Melting point Tm ({tm} K) outside plausible range 300–800 K.")

    tg = data.get("tg_k")
    if tg is not None and isinstance(tg, (int, float)):
        if not (200 < tg < 600):
            warnings.append(f"Tg ({tg} K) outside typical range 200–600 K.")
        if tm is not None and tg >= tm:
            errors.append(f"Tg ({tg} K) ≥ Tm ({tm} K): physically impossible for crystallisable drug.")

    mw = data.get("molecular_weight_g_mol")
    if mw is not None and isinstance(mw, (int, float)):
        if mw <= 0:
            errors.append("Molecular weight must be > 0.")
        if mw > 2000:
            warnings.append(f"Molecular weight ({mw} g/mol) unusually high for small molecule drug.")

    dens = data.get("density_crystalline_g_cm3")
    if dens is not None and isinstance(dens, (int, float)):
        if not (0.8 < dens < 2.0):
            warnings.append(f"Crystalline density ({dens} g/cm³) outside standard range 0.8–2.0.")

    for hsp_field in ["hsp_delta_d", "hsp_delta_p", "hsp_delta_h"]:
        val = data.get(hsp_field)
        if val is not None and isinstance(val, (int, float)):
            if val < 0:
                errors.append(f"{hsp_field} cannot be negative.")
            if val > 30:
                warnings.append(f"{hsp_field} ({val}) unusually high (>30 MPa^0.5).")

    ro = data.get("hsp_ro")
    if ro is not None and isinstance(ro, (int, float)):
        if ro <= 0:
            errors.append("HSP interaction radius R₀ must be > 0.")

    smiles = data.get("canonical_smiles", "")
    if isinstance(smiles, str) and len(smiles) > 0:
        invalid_chars = set(smiles) - set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789()[]=#@+-./%\\")
        if invalid_chars:
            warnings.append(f"SMILES contains unusual characters: {invalid_chars}")

    # Reference traceability
    doi = data.get("reference_doi")
    source = data.get("reference_source", "")
    if not doi and source != "user_entered":
        warnings.append("No DOI reference provided. Data provenance incomplete.")

    if errors:
        return "INVALID", errors, warnings
    elif warnings:
        return "WARNING", errors, warnings
    return "VALID", errors, warnings


def validate_polymer_input(data: Dict[str, Any], existing_ids: List[str] = None) -> Tuple[str, List[str], List[str]]:
    """Validate polymer input data. Returns (status, errors, warnings)."""
    errors: List[str] = []
    warnings: List[str] = []
    existing_ids = existing_ids or []

    # Required fields
    required = ["polymer_id", "polymer_name", "abbreviation", "mn_da", "tg_k",
                "hsp_delta_d", "hsp_delta_p", "hsp_delta_h", "monomer_smiles"]
    for field in required:
        val = data.get(field)
        if val is None or (isinstance(val, str) and val.strip() == ""):
            errors.append(f"Missing required field: {field}")

    # Duplicate checks
    pid = data.get("polymer_id", "")
    if pid in existing_ids:
        errors.append(f"Duplicate polymer_id: {pid}")

    # Plausibility
    mn = data.get("mn_da")
    if mn is not None and isinstance(mn, (int, float)):
        if mn <= 0:
            errors.append("Mn must be > 0.")
        if mn < 1000:
            warnings.append(f"Mn ({mn} Da) unusually low for pharmaceutical polymer.")

    tg = data.get("tg_k")
    if tg is not None and isinstance(tg, (int, float)):
        if not (200 < tg < 600):
            warnings.append(f"Tg ({tg} K) outside typical range 200–600 K.")

    dens = data.get("density_g_cm3")
    if dens is not None and isinstance(dens, (int, float)):
        if not (0.8 < dens < 2.0):
            warnings.append(f"Density ({dens} g/cm³) outside standard range 0.8–2.0.")

    for hsp_field in ["hsp_delta_d", "hsp_delta_p", "hsp_delta_h"]:
        val = data.get(hsp_field)
        if val is not None and isinstance(val, (int, float)):
            if val < 0:
                errors.append(f"{hsp_field} cannot be negative.")
            if val > 30:
                warnings.append(f"{hsp_field} ({val}) unusually high (>30 MPa^0.5).")

    lit = data.get("literature_evidence_score")
    if lit is not None and isinstance(lit, (int, float)):
        if not (0 <= lit <= 1):
            errors.append("literature_evidence_score must be between 0 and 1.")

    if errors:
        return "INVALID", errors, warnings
    elif warnings:
        return "WARNING", errors, warnings
    return "VALID", errors, warnings
