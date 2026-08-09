"""Unit tests for Layer 2 Polymer module."""

import pytest
from asd_mcda.polymer.polymer_library import Polymer, PolymerLibrary


@pytest.fixture
def sample_polymer_dict():
    return {
        "polymer_id": "POL-001",
        "polymer_name": "Polyvinylpyrrolidone K30",
        "abbreviation": "PVP_K30",
        "polymer_family": "vinylic",
        "polymer_class": "neutral",
        "mn_da": 40000,
        "mw_da": 50000,
        "pdi": 1.25,
        "tg_k": 443.0,
        "density_g_cm3": 1.20,
        "hsp_delta_d": 17.4,
        "hsp_delta_p": 8.2,
        "hsp_delta_h": 11.7,
        "functional_groups": "lactam|amide",
        "monomer_smiles": "C=CN1CCCC1=O",
        "literature_evidence_score": 1.0,
    }


def test_polymer_creation(sample_polymer_dict):
    poly = Polymer.from_dict(sample_polymer_dict)
    assert poly.abbreviation == "PVP_K30"
    assert poly.tg_k == 443.0
    assert not poly.is_copolymer()


def test_copolymer_detection():
    data = {
        "polymer_id": "POL-002",
        "polymer_name": "PVP-VA 64",
        "abbreviation": "PVP_VA_64",
        "mn_da": 45000,
        "tg_k": 380.0,
        "hsp_delta_d": 17.0,
        "hsp_delta_p": 8.0,
        "hsp_delta_h": 10.0,
        "monomer_smiles": "C=CN1CCCC1=O|CC(=O)OC",
        "copolymer_mole_fractions": "0.6|0.4",
    }
    poly = Polymer.from_dict(data)
    assert poly.is_copolymer()
    desc = poly.get_weighted_2d_descriptors()
    assert "MolWt" in desc


def test_polymer_library_lookup_canonical_names():
    """Verify that PolymerLibrary loads and returns exact canonical polymer names from CSV."""
    from pathlib import Path
    from asd_mcda.drug.drug_profile import Drug
    
    csv_path = Path("config/polymers/polymer_library_v2.csv")
    assert csv_path.exists()
    
    drug_data = {
        "drug_id": "IND-001-2026",
        "generic_name": "Indomethacin",
        "canonical_smiles": "CC1=C(C=C(C=C1)OC)C(=O)C2=CC=C(C=C2)Cl",

        "mw_da": 357.79,
        "tm_k": 434.0,
        "tg_k": 315.0,
        "hsp_delta_d": 19.5,
        "hsp_delta_p": 5.6,
        "hsp_delta_h": 6.8
    }
    drug = Drug.from_dict(drug_data)
    lib = PolymerLibrary.from_csv(csv_path, drug)
    
    sol = lib.get_by_id("POL-005-2026")
    assert sol is not None
    assert sol.polymer_name == "Soluplus"
    
    hpmcas = lib.get_by_id("POL-003-2026")
    assert hpmcas is not None
    assert hpmcas.polymer_name == "HPMC Acetate Succinate Low"
    
    pvp_va = lib.get_by_id("POL-002-2026")
    assert pvp_va is not None
    assert pvp_va.polymer_name == "PVP-Vinyl Acetate 64"

    pvp_k30 = lib.get_by_id("POL-001-2026")
    assert pvp_k30 is not None
    assert pvp_k30.polymer_name == "Polyvinylpyrrolidone K30"

