"""
Regression test suite for RDKit integration and descriptor calculations.
Verifies software bug fixes, input data corrections, and preservation of frozen methodology invariants.
"""

import json
from pathlib import Path
import numpy as np
import pytest
import yaml

from asd_mcda.utils.rdkit_wrapper import (
    compute_2d_descriptors,
    get_inchi_key,
    canonicalize_smiles,
    _fallback_2d_descriptors,
    RDKIT_AVAILABLE,
)
from asd_mcda.utils.constants import DEFAULT_DESC_SUBWEIGHTS
from asd_mcda.integration.pca import PCAPreprocessor


PROJECT_ROOT = Path(__file__).parent.parent.parent
INDO_SMILES = "COc1ccc2c(c1)c(CC(=O)O)c(C)n2C(=O)c1ccc(Cl)cc1"


def test_a_lowercase_rdkit_inchi_import():
    """A: Verify correct lowercase RDKit inchi module import and function accessibility."""
    from rdkit.Chem import inchi
    assert hasattr(inchi, "MolToInchiKey"), "rdkit.Chem.inchi must expose MolToInchiKey"


def test_b_rdkit_available_is_true():
    """B: Verify that RDKit is detected as available in the runtime environment."""
    assert RDKIT_AVAILABLE is True, "RDKIT_AVAILABLE must be True in production test environment"


def test_c_real_ethanol_descriptors():
    """C: Verify real RDKit descriptor calculation for ethanol (CCO)."""
    desc = compute_2d_descriptors("CCO")
    assert pytest.approx(desc["MolWt"], abs=0.05) == 46.07
    assert desc["NumHDonors"] == 1
    assert desc["NumHAcceptors"] == 1
    assert desc["NumAromaticRings"] == 0
    assert desc["NumRotatableBonds"] == 0
    assert pytest.approx(desc["TPSA"], abs=0.1) == 20.23


def test_d_correct_indomethacin_inchikey():
    """D: Verify InChIKey generation from authoritative Indomethacin SMILES."""
    key = get_inchi_key(INDO_SMILES)
    assert key == "CGIGDMFJXJATDK-UHFFFAOYSA-N"


def test_e_config_smiles_computes_correct_inchikey():
    """E: Verify that SMILES in config/drugs/indomethacin.json generates correct InChIKey."""
    config_file = PROJECT_ROOT / "config" / "drugs" / "indomethacin.json"
    with open(config_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    computed_key = get_inchi_key(data["canonical_smiles"])
    assert computed_key == "CGIGDMFJXJATDK-UHFFFAOYSA-N"


def test_f_config_inchikey_matches_computed_inchikey():
    """F: Verify that recorded inchi_key in config matches computed InChIKey exactly."""
    config_file = PROJECT_ROOT / "config" / "drugs" / "indomethacin.json"
    with open(config_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    computed_key = get_inchi_key(data["canonical_smiles"])
    assert data["inchi_key"] == computed_key


def test_g_indomethacin_molecular_weight():
    """G: Verify accurate molecular weight calculation for Indomethacin."""
    desc = compute_2d_descriptors(INDO_SMILES)
    assert pytest.approx(desc["MolWt"], abs=0.01) == 357.793


def test_h_real_indomethacin_descriptors():
    """
    H: Verify real Indomethacin descriptors.
    NumAromaticRings must be 3 (indole 6-ring, indole 5-ring, and 4-chlorophenyl ring).
    NumHDonors must be 1 (carboxylic acid -OH).
    In RDKit, Descriptors.NumHAcceptors evaluates to 3 via Daylight SMARTS definition
    (methoxy O, amide carbonyl O, carboxyl carbonyl O; carboxylic -OH is not counted as acceptor).
    Under broader hydrogen-bonding conventions counting all oxygen lone pairs, HBA is 4.
    """
    desc = compute_2d_descriptors(INDO_SMILES)
    assert desc["NumHDonors"] == 1
    assert desc["NumHAcceptors"] in (3, 4), f"HBA must be 3 (Daylight SMARTS) or 4 (literature convention), got {desc['NumHAcceptors']}"
    assert pytest.approx(desc["TPSA"], abs=0.1) == 68.53
    assert desc["NumAromaticRings"] == 3, "Indomethacin possesses 3 aromatic rings via Smallest Set of Smallest Rings (SSSR)"
    assert desc["NumRotatableBonds"] == 4


def test_i_fallback_distinguishable_from_real_rdkit():
    """I: Verify that historical fallback values are clearly distinguishable from real RDKit values."""
    fallback = _fallback_2d_descriptors("CC1=C(C=C")
    real = compute_2d_descriptors(INDO_SMILES)
    assert fallback["NumHDonors"] == 2
    assert real["NumHDonors"] == 1
    assert fallback["NumAromaticRings"] == 2
    assert real["NumAromaticRings"] == 3


def test_j_chemically_valid_descriptor_sensitivity():
    """
    J: Verify descriptor sensitivity across chemically valid reference pairs:
    1. Water vs hydrogen peroxide: HBA differs
    2. Benzene vs pyridine: HBA differs
    3. Acetic acid vs methyl acetate: HBD differs
    4. Benzene vs naphthalene: aromatic-ring count differs
    5. Methanol vs dimethyl ether: HBD differs
    """
    # 1. Water vs hydrogen peroxide (HBA)
    hba_water = compute_2d_descriptors("O")["NumHAcceptors"]
    hba_peroxide = compute_2d_descriptors("OO")["NumHAcceptors"]
    assert hba_water != hba_peroxide, "Water and hydrogen peroxide must differ in HBA"

    # 2. Benzene vs pyridine (HBA)
    hba_benzene = compute_2d_descriptors("c1ccccc1")["NumHAcceptors"]
    hba_pyridine = compute_2d_descriptors("c1ccncc1")["NumHAcceptors"]
    assert hba_benzene != hba_pyridine, "Benzene and pyridine must differ in HBA"

    # 3. Acetic acid vs methyl acetate (HBD)
    hbd_acetic = compute_2d_descriptors("CC(=O)O")["NumHDonors"]
    hbd_acetate = compute_2d_descriptors("CC(=O)OC")["NumHDonors"]
    assert hbd_acetic != hbd_acetate, "Acetic acid and methyl acetate must differ in HBD"

    # 4. Benzene vs naphthalene (Aromatic rings)
    arom_benzene = compute_2d_descriptors("c1ccccc1")["NumAromaticRings"]
    arom_naphth = compute_2d_descriptors("c1ccc2ccccc2c1")["NumAromaticRings"]
    assert arom_benzene != arom_naphth, "Benzene and naphthalene must differ in aromatic ring count"

    # 5. Methanol vs dimethyl ether (HBD)
    hbd_methanol = compute_2d_descriptors("CO")["NumHDonors"]
    hbd_ether = compute_2d_descriptors("COC")["NumHDonors"]
    assert hbd_methanol != hbd_ether, "Methanol and dimethyl ether must differ in HBD"


def test_k_frozen_s_desc_subweights():
    """K: Verify frozen s_desc internal subweights: HBD=0.30, HBA=0.30, TPSA=0.20, Aromatic=0.20."""
    assert pytest.approx(DEFAULT_DESC_SUBWEIGHTS["hbd"]) == 0.30
    assert pytest.approx(DEFAULT_DESC_SUBWEIGHTS["hba"]) == 0.30
    assert pytest.approx(DEFAULT_DESC_SUBWEIGHTS["tpsa"]) == 0.20
    assert pytest.approx(DEFAULT_DESC_SUBWEIGHTS["aromatic"]) == 0.20
    total_w = sum(DEFAULT_DESC_SUBWEIGHTS.values())
    assert pytest.approx(total_w) == 1.0


def test_l_frozen_pca_configuration():
    """L: Verify frozen PCA variance threshold remains exactly 0.95 (95%)."""
    wf_config = PROJECT_ROOT / "config" / "workflow" / "workflow_config.yaml"
    with open(wf_config, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    assert cfg["pca"]["variance_threshold"] == 0.95


def test_m_frozen_2x2_pc1_pc2_ahp():
    """M: Verify frozen 2x2 PC1/PC2 AHP matrix and expected weights."""
    ahp_file = PROJECT_ROOT / "config" / "ahp" / "default_matrix.json"
    with open(ahp_file, "r", encoding="utf-8") as f:
        ahp_cfg = json.load(f)
    assert ahp_cfg["criteria"] == ["PC1", "PC2"]
    mat = np.array(ahp_cfg["pairwise_matrix"])
    assert mat.shape == (2, 2)
    assert np.allclose(mat, [[1.0, 2.0], [0.5, 1.0]])


def test_n_historical_zero_variance_s_desc():
    """N: Verify that historical frozen score matrix recorded constant s_desc = 0.2268."""
    hist_score_file = PROJECT_ROOT / "results" / "final" / "final_score_matrix.csv"
    assert hist_score_file.exists(), "Historical score matrix must exist in results/final/"
    import pandas as pd
    df = pd.read_csv(hist_score_file)
    assert "s_desc" in df.columns
    unique_vals = df["s_desc"].unique()
    assert len(unique_vals) == 1, "Historical s_desc had exactly zero variance across reference polymers"
    assert pytest.approx(unique_vals[0], abs=1e-4) == 0.2268


def test_o_production_k_is_not_hardcoded_to_2():
    """O: Verify that PCAPreprocessor dynamically computes retained K from cumulative variance >= 95%."""
    pca = PCAPreprocessor(variance_threshold=0.95)
    import pandas as pd
    np.random.seed(123)
    synthetic_data = pd.DataFrame(
        np.random.randn(10, 4),
        columns=["s_HSP", "s_chi", "s_desc", "s_GT"],
        index=[f"POL_{i}" for i in range(10)],
    )
    res = pca.fit_transform(synthetic_data)
    assert res.cumulative_variance_ratio[-1] >= 0.95
    assert res.n_components_retained == len(res.cumulative_variance_ratio)
