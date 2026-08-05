"""Unit tests for Uncertainty Quantification module."""

import numpy as np
import pytest

from asd_mcda.drug.drug_profile import Drug
from asd_mcda.polymer.polymer_library import Polymer, PolymerLibrary
from asd_mcda.uncertainty.monte_carlo import MonteCarloUQ


def test_monte_carlo_uq():
    drug = Drug.from_dict({
        "drug_id": "IND",
        "generic_name": "Indomethacin",
        "canonical_smiles": "CC1=C(C=C(C=C1)OC)C2=C(C3=CC=CC=C3N2CC(=O)O)C(=O)C4=CC=C(C=C4)Cl",
        "molecular_weight_g_mol": 357.79,
        "tm_k": 424.15,
        "tg_k": 315.15,
        "density_crystalline_g_cm3": 1.31,
        "hsp_delta_d": 19.2,
        "hsp_delta_p": 7.9,
        "hsp_delta_h": 8.4,
    })

    poly1 = Polymer.from_dict({
        "polymer_id": "POL1",
        "polymer_name": "P1",
        "abbreviation": "P1",
        "mn_da": 40000,
        "tg_k": 443.0,
        "hsp_delta_d": 17.4,
        "hsp_delta_p": 8.2,
        "hsp_delta_h": 11.7,
        "monomer_smiles": "C=CN1CCCC1=O",
    })

    poly2 = Polymer.from_dict({
        "polymer_id": "POL2",
        "polymer_name": "P2",
        "abbreviation": "P2",
        "mn_da": 90000,
        "tg_k": 343.0,
        "hsp_delta_d": 18.0,
        "hsp_delta_p": 8.5,
        "hsp_delta_h": 10.5,
        "monomer_smiles": "C=CN1CCCC1=O",
    })

    library = PolymerLibrary([poly1, poly2], drug)
    uq = MonteCarloUQ(drug, library, n_iterations=50, random_seed=42)

    ahp_m = np.array([[1.0, 2.0], [0.5, 1.0]])
    res = uq.run(ahp_m)

    assert len(res.p_top1) == 2
    assert res.selected_polymer_id in ["POL1", "POL2"]
    assert res.converged
