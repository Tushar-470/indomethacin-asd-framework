"""Unit tests for Layer 4 Compatibility Prediction models."""

import pytest
from asd_mcda.drug.drug_profile import Drug
from asd_mcda.polymer.polymer_library import Polymer, PolymerLibrary
from asd_mcda.compatibility.hsp_model import HSPModel
from asd_mcda.compatibility.flory_huggins import FloryHugginsModel
from asd_mcda.compatibility.gordon_taylor import GordonTaylorModel


@pytest.fixture
def test_setup():
    drug = Drug.from_dict({
        "drug_id": "IND",
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
    })

    poly1 = Polymer.from_dict({
        "polymer_id": "SOL",
        "polymer_name": "Soluplus",
        "abbreviation": "SOLUPLUS",
        "mn_da": 90000,
        "tg_k": 343.0,
        "density_g_cm3": 1.15,
        "hsp_delta_d": 18.0,
        "hsp_delta_p": 8.5,
        "hsp_delta_h": 10.5,
        "monomer_smiles": "C=CN1CCCC1=O",
    })

    poly2 = Polymer.from_dict({
        "polymer_id": "EDR",
        "polymer_name": "Eudragit L100",
        "abbreviation": "EDR_L100",
        "mn_da": 125000,
        "tg_k": 438.0,
        "density_g_cm3": 1.25,
        "hsp_delta_d": 16.5,
        "hsp_delta_p": 7.5,
        "hsp_delta_h": 9.0,
        "monomer_smiles": "CC(C)C(=O)OC(C)C",
    })

    poly3 = Polymer.from_dict({
        "polymer_id": "PVP",
        "polymer_name": "PVP K30",
        "abbreviation": "PVP_K30",
        "mn_da": 40000,
        "tg_k": 443.0,
        "density_g_cm3": 1.20,
        "hsp_delta_d": 17.4,
        "hsp_delta_p": 8.2,
        "hsp_delta_h": 11.7,
        "monomer_smiles": "C=CN1CCCC1=O",
    })

    library = PolymerLibrary([poly1, poly2, poly3], drug)
    return drug, library, poly1


def test_hsp_model(test_setup):
    drug, library, poly1 = test_setup
    hsp = HSPModel(drug, library)
    ra = hsp.compute_ra(poly1)
    red = hsp.compute_red(poly1)
    s_hsp = hsp.compute_s_hsp(poly1)

    assert ra > 0.0
    assert 0.0 <= red <= 2.0
    assert 0.0 <= s_hsp <= 1.0


def test_flory_huggins(test_setup):
    drug, library, poly1 = test_setup
    fh = FloryHugginsModel(drug, library)
    chi = fh.compute_chi(poly1)
    chi_c = fh.compute_chi_critical(poly1)
    s_chi = fh.compute_s_chi(poly1)

    assert chi >= 0.0
    assert chi_c > 0.0
    assert 0.0 <= s_chi <= 1.0


def test_gordon_taylor(test_setup):
    drug, library, poly1 = test_setup
    gt = GordonTaylorModel(drug, library, drug_loading_ww=0.30)
    k, _ = gt.compute_k_simha_boyer(poly1)
    tg_mix = gt.compute_tg_mix(poly1)
    s_gt = gt.compute_s_gt(poly1)

    assert k > 0.0
    assert 300.0 < tg_mix < 450.0
    assert 0.0 <= s_gt <= 1.0
