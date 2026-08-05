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
