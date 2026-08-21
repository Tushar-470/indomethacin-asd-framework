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
        "polymer_name": "Eudragit E PO",
        "abbreviation": "EDR_EPO",
        "mn_da": 39000,
        "tg_k": 323.15,
        "density_g_cm3": 1.125,
        "hsp_delta_d": 16.8,
        "hsp_delta_p": 5.2,
        "hsp_delta_h": 6.5,
        "monomer_smiles": "CCN(C)CCOC(=O)C(C)=C",
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


def test_flory_huggins_chi_critical_analytical_value(test_setup):
    """
    Verify chi_c follows classical binary Flory-Huggins equation: chi_c = 0.5 * (1/sqrt(r1) + 1/sqrt(r2))^2.
    For r1 = 1 and r2 = 100, chi_c must equal exactly 0.5 * (1 + 1/10)^2 = 0.605.
    (Under the old faulty extra +1 implementation, this gave 2.205).
    """
    drug, library, _ = test_setup
    # Construct synthetic polymer such that V_poly / V_drug = 100.0
    # V_drug = 273.0 cm3/mol -> V_poly = 27,300 cm3/mol. Density = 1.0 -> Mn = 27300 Da.
    poly_r100 = Polymer.from_dict({
        "polymer_id": "SYN_100",
        "polymer_name": "Synthetic Polymer r2=100",
        "mn_da": 27300.0,
        "tg_k": 350.0,
        "density_g_cm3": 1.0,
        "hsp_delta_d": 18.0,
        "hsp_delta_p": 8.0,
        "hsp_delta_h": 10.0,
        "monomer_smiles": "CCO",
    })
    fh = FloryHugginsModel(drug, PolymerLibrary([poly_r100], drug))
    chi_c = fh.compute_chi_critical(poly_r100)

    # Expected analytical value: 0.5 * (1.0 + 1/sqrt(100))^2 = 0.5 * (1.1)^2 = 0.605
    assert abs(chi_c - 0.605) < 1e-4


def test_flory_huggins_chi_critical_asymptotic_value(test_setup):
    """
    Verify that as r2 -> infinity (very high MW polymer), chi_c asymptotically approaches 0.500.
    (Under the old faulty extra +1 implementation, chi_c approached 2.000).
    """
    drug, library, _ = test_setup
    # Very high MW polymer -> r2 = 1,000,000
    poly_high_mw = Polymer.from_dict({
        "polymer_id": "SYN_HIGH",
        "polymer_name": "Synthetic Polymer High MW",
        "mn_da": 273000000.0,
        "tg_k": 400.0,
        "density_g_cm3": 1.0,
        "hsp_delta_d": 18.0,
        "hsp_delta_p": 8.0,
        "hsp_delta_h": 10.0,
        "monomer_smiles": "CCO",
    })
    fh = FloryHugginsModel(drug, PolymerLibrary([poly_high_mw], drug))
    chi_c = fh.compute_chi_critical(poly_high_mw)

    # Asymptotic value as r2 -> infinity: chi_c -> 0.500
    assert abs(chi_c - 0.500) < 1e-2


def test_flory_huggins_chi_critical_r2_10(test_setup):
    """Verify chi_c for r2 = 10 gives approx 0.866 (Task 2 verification)."""
    drug, _, _ = test_setup
    poly_r10 = Polymer.from_dict({
        "polymer_id": "SYN_10",
        "polymer_name": "Synthetic Polymer r2=10",
        "mn_da": 2730.0,
        "tg_k": 350.0,
        "density_g_cm3": 1.0,
        "hsp_delta_d": 18.0,
        "hsp_delta_p": 8.0,
        "hsp_delta_h": 10.0,
        "monomer_smiles": "CCO",
    })
    fh = FloryHugginsModel(drug, PolymerLibrary([poly_r10], drug))
    chi_c = fh.compute_chi_critical(poly_r10)
    expected = 0.5 * (1.0 + 1.0 / (10.0 ** 0.5)) ** 2
    assert chi_c == pytest.approx(expected, rel=1e-5)
    assert abs(chi_c - 0.866228) < 1e-4


def test_flory_huggins_lindvig_chi_hand_calculation(test_setup):
    """
    Verify Lindvig chi calculation against independent hand calculation (Task 3 verification):
    chi = alpha * (V_m / (R * T)) * [ 1.0*(dd)^2 + 0.25*(dp)^2 + 0.25*(dh)^2 ]
    For Indomethacin (19.2, 7.9, 8.4, Vm=273.0, T=298.15) + Soluplus (18.0, 8.5, 10.5):
    energy_diff = 1.0*(1.2)^2 + 0.25*(-0.6)^2 + 0.25*(-2.1)^2 = 1.44 + 0.09 + 1.1025 = 2.6325 MPa
    chi = 0.60 * (273e-6 / (8.314462618 * 298.15)) * (2.6325 * 1e6) = 0.1739455
    """
    drug, library, poly1 = test_setup
    fh = FloryHugginsModel(drug, library)
    chi = fh.compute_chi(poly1)
    expected_chi = 0.60 * (273.0e-6 / (8.314462618 * 298.15)) * (2.6325e6)
    assert chi == pytest.approx(expected_chi, rel=1e-5)
    assert abs(chi - 0.1739455) < 1e-5


def test_gordon_taylor(test_setup):

    drug, library, poly1 = test_setup
    gt = GordonTaylorModel(drug, library, drug_loading_ww=0.30)
    k, _ = gt.compute_k_simha_boyer(poly1)
    tg_mix = gt.compute_tg_mix(poly1)
    s_gt = gt.compute_s_gt(poly1)

    assert k > 0.0
    assert 300.0 < tg_mix < 450.0
    assert 0.0 <= s_gt <= 1.0
