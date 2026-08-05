"""
Schema validation for YAML workflow configs, JSON drug profiles, polymer libraries, and AHP matrices.
"""

from typing import Dict, List, Any


def validate_workflow_config(config: Dict[str, Any]) -> List[str]:
    """Validate workflow configuration parameters, returning list of validation errors."""
    errors = []
    if "workflow" not in config:
        errors.append("Missing 'workflow' section in configuration.")
    if "gates" not in config:
        errors.append("Missing 'gates' section in configuration.")
    if "paths" not in config:
        errors.append("Missing 'paths' section in configuration.")
    
    if "gates" in config:
        gates = config["gates"]
        if gates.get("gate1_hsp_red_threshold", 0) <= 0:
            errors.append("gate1_hsp_red_threshold must be > 0.")
        if not (0 < gates.get("gate2_ahp_cr_max", 0) <= 0.10):
            errors.append("gate2_ahp_cr_max must be between 0 and 0.10.")
    return errors


def validate_drug_dict(drug_data: Dict[str, Any]) -> List[str]:
    """Validate drug profile dictionary against required fields and plausible ranges."""
    errors = []
    required_fields = [
        "drug_id", "generic_name", "canonical_smiles", "molecular_weight_g_mol",
        "tm_k", "hsp_delta_d", "hsp_delta_p", "hsp_delta_h", "hsp_ro"
    ]
    for field in required_fields:
        if field not in drug_data or drug_data[field] is None:
            errors.append(f"Drug profile missing required field: {field}")

    if "tm_k" in drug_data and drug_data["tm_k"] is not None:
        if not (300 < drug_data["tm_k"] < 800):
            errors.append(f"Melting point Tm ({drug_data['tm_k']} K) outside plausible range (300-800 K).")

    if "density_crystalline_g_cm3" in drug_data and drug_data["density_crystalline_g_cm3"] is not None:
        if not (0.8 < drug_data["density_crystalline_g_cm3"] < 2.0):
            errors.append("Density outside plausible range (0.8-2.0 g/cm3).")

    return errors
