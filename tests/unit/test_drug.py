"""Unit tests for Layer 1 Drug module."""

import pytest
from asd_mcda.drug.drug_profile import Drug


@pytest.fixture
def sample_drug_dict():
    return {
        "drug_id": "IND-TEST-001",
        "generic_name": "Indomethacin",
        "canonical_smiles": "CC1=C(C=C(C=C1)OC)C2=C(C3=CC=CC=C3N2CC(=O)O)C(=O)C4=CC=C(C=C4)Cl",
        "molecular_weight_g_mol": 357.79,
        "tm_k": 424.15,
        "tg_k": 315.15,
        "density_crystalline_g_cm3": 1.31,
        "density_amorphous_g_cm3": 1.22,
        "hsp_delta_d": 19.2,
        "hsp_delta_p": 7.9,
        "hsp_delta_h": 8.4,
        "hsp_ro": 8.0,
        "molar_volume_cm3_mol": 273.0,
    }


def test_drug_creation(sample_drug_dict):
    drug = Drug.from_dict(sample_drug_dict)
    assert drug.generic_name == "Indomethacin"
    assert drug.tm_k == 424.15
    assert drug.estimate_tg() == 315.15


def test_density_preference(sample_drug_dict):
    drug = Drug.from_dict(sample_drug_dict)
    dens, source = drug.get_preferred_density()
    assert dens == 1.22
    assert source == "amorphous"


def test_plausibility_validation(sample_drug_dict):
    drug = Drug.from_dict(sample_drug_dict)
    warnings = drug.validate_plausibility()
    assert len(warnings) == 0
