"""Comprehensive Cheminformatics Integrity & RDKit Pipeline Test Suite for PharmaPolySCOPE v2.

Authoritative Specification: Controlled Cheminformatics Integrity Remediation.
Verifies all 17 mandatory requirements:
- Valid SMILES ingestion & sanitization
- Malformed, invalid, and impossible-valence SMILES rejection
- Fallback descriptor prohibition in production MCDA
- RDKit unavailable strict blocking
- Authoritative structure-derived descriptor synchronization (aspirin -> ethanol)
- Stale descriptor override prevention and provenance discrepancy auditing
- Tetrahedral stereocenter retention (@/@@) and InChIKey distinction
- Itraconazole stereochemical integrity (VHVPQPYKVGDNFY-ZPGVKDDISA-N)
- Canonical SMILES convergence (CCO vs OCC)
- Isotopic structure distinction (deuterated ethanol)
- Multi-component salt behavior preservation and documentation
- Complete descriptor provenance auditing
- Generalization to new valid drugs through VariableKEngine
- Defense-in-depth engine rejection of fallback provenance
- Absolute v1.5 isolation and zero monkey-patching
"""

import copy
import json
import os
from unittest.mock import patch
import numpy as np
import pytest

from asd_mcda.v2 import (
    VariableKEngine,
    ChemicalStructureError,
    InvalidSmilesError,
    ProductionFallbackProhibitedError,
    RDKitParseFailureError,
    RDKitSanitizationFailureError,
    RDKitUnavailableError,
    validate_chemical_structure,
    compute_production_descriptors,
    get_diagnostic_fallback_descriptors,
    resolve_validated_drug_snapshot,
    validate_polymer_repeat_units,
)
from asd_mcda.polymer.polymer_library import Polymer, PolymerLibrary

AHP_MATRIX = np.array([
    [1.0, 2.0, 3.0, 2.0],
    [0.5, 1.0, 5.0, 2.0],
    [1.0 / 3.0, 0.2, 1.0, 0.5],
    [0.5, 0.5, 2.0, 1.0]
], dtype=np.float64)

POL_IDS = ("POL-001-2026", "POL-002-2026", "POL-005-2026", "POL-006-2026", "POL-007-2026")


# =============================================================================
# TEST 1: Valid SMILES passes production validation
# =============================================================================
@pytest.mark.parametrize("smiles,name", [
    ("CC(=O)Oc1ccccc1C(=O)O", "Aspirin"),
    ("COc1ccc2c(c1)c(CC(=O)O)c(C)n2C(=O)c1ccc(Cl)cc1", "Indomethacin"),
    ("CC(C)Cc1ccc(C(C)C(=O)O)cc1", "Ibuprofen"),
    ("CCO", "Ethanol"),
])
def test_01_valid_smiles_passes_validation(smiles, name):
    mol = validate_chemical_structure(smiles)
    assert mol is not None

    desc = compute_production_descriptors(smiles)
    assert desc["descriptor_source"] == "RDKit"
    assert desc["fallback_used"] is False
    assert desc["validation_status"] == "VALID"
    assert desc["MolWt"] > 0
    assert len(desc["inchi_key"]) == 27


# =============================================================================
# TEST 2: Malformed SMILES is blocked
# =============================================================================
@pytest.mark.parametrize("bad_smiles", [
    "CC(=O",                             # Syntax error (unclosed paren)
    "C1CCCCC",                           # Unclosed ring
    "C[Xx]C",                            # Non-existent element
    "NOT_A_SMILES_12345",                # Arbitrary corrupt string
    "C---C",                             # Invalid bond specification
    "",                                  # Empty string
    "   ",                               # Whitespace only
])
def test_02_malformed_smiles_blocked(bad_smiles):
    with pytest.raises((InvalidSmilesError, RDKitParseFailureError)):
        validate_chemical_structure(bad_smiles)


def test_02b_non_string_smiles_blocked():
    with pytest.raises(InvalidSmilesError):
        validate_chemical_structure(12345)  # type: ignore
    with pytest.raises(InvalidSmilesError):
        validate_chemical_structure(None)   # type: ignore


# =============================================================================
# TEST 3: Impossible valence is blocked
# =============================================================================
@pytest.mark.parametrize("impossible_smiles", [
    "C=C=C=C=C(C)(C)(C)(C)",            # 5-valent carbon
    "[CH4+5]",                           # Impossible charge
])
def test_03_impossible_valence_blocked(impossible_smiles):
    with pytest.raises((RDKitParseFailureError, RDKitSanitizationFailureError)):
        validate_chemical_structure(impossible_smiles)


# =============================================================================
# TEST 4: Invalid SMILES cannot reach MCDA
# =============================================================================
def test_04_invalid_smiles_cannot_reach_mcda():
    bad_drug_data = {
        "drug_id": "DRG-INVALID-001",
        "generic_name": "CorruptDrug",
        "canonical_smiles": "NOT_A_VALID_SMILES_CORRUPT",
        "tm_k": 400.0,
        "density_crystalline_g_cm3": 1.3,
    }

    # 1. Attempting to resolve validated snapshot fails
    with pytest.raises(RDKitParseFailureError):
        resolve_validated_drug_snapshot(bad_drug_data)

    # 2. Attempting to evaluate VariableKEngine with corrupt drug data fails
    dummy_scores = np.full((5, 4), 0.5, dtype=np.float64)
    engine = VariableKEngine()
    with pytest.raises((RDKitParseFailureError, ChemicalStructureError)):
        engine.evaluate(dummy_scores, AHP_MATRIX, POL_IDS, drug_data=bad_drug_data)


# =============================================================================
# TEST 5: Fallback descriptors cannot reach production MCDA
# =============================================================================
def test_05_fallback_descriptors_blocked_from_production():
    # Diagnostic fallback can be generated in isolation
    diag_desc = get_diagnostic_fallback_descriptors("CC(=O")
    assert diag_desc["descriptor_source"] == "fallback"
    assert diag_desc["fallback_used"] is True

    # But VariableKEngine rejects any profile containing fallback descriptors
    contaminated_drug = {
        "drug_id": "DRG-CONTAMINATED",
        "name": "ContaminatedDrug",
        "canonical_smiles": "CC(=O",
        "descriptor_source": "fallback",
        "fallback_used": True,
    }
    dummy_scores = np.full((5, 4), 0.5, dtype=np.float64)
    engine = VariableKEngine()
    with pytest.raises(ProductionFallbackProhibitedError, match="Fallback descriptors are strictly prohibited"):
        engine.evaluate(dummy_scores, AHP_MATRIX, POL_IDS, drug_data=contaminated_drug)


# =============================================================================
# TEST 6: RDKit unavailable is blocked for production
# =============================================================================
def test_06_rdkit_unavailable_blocked():
    with patch("asd_mcda.v2.chemistry.is_rdkit_available", return_value=False):
        with pytest.raises(RDKitUnavailableError, match="RDKit is required for production"):
            validate_chemical_structure("CCO")


# =============================================================================
# TEST 7: Changing SMILES invalidates/recomputes descriptors (Aspirin -> Ethanol)
# =============================================================================
def test_07_changing_smiles_invalidates_descriptors():
    # Profile A: Aspirin
    aspirin_raw = {
        "drug_id": "DRG-ASPIRIN",
        "canonical_smiles": "CC(=O)Oc1ccccc1C(=O)O",
        "molecular_weight_g_mol": 180.16,
        "logp": 1.31,
        "tpsa_angstrom2": 63.60,
        "hbd": 1,
        "hba": 3,
        "rotatable_bonds": 2,
        "aromatic_rings": 1,
    }
    snap_a = resolve_validated_drug_snapshot(aspirin_raw)
    assert pytest.approx(snap_a["molecular_weight_g_mol"], abs=0.05) == 180.16
    assert snap_a["aromatic_rings"] == 1

    # Change ONLY canonical_smiles to Ethanol, leaving aspirin fields
    ethanol_raw = copy.deepcopy(aspirin_raw)
    ethanol_raw["canonical_smiles"] = "CCO"

    snap_b = resolve_validated_drug_snapshot(ethanol_raw)

    # Every single structure-derived descriptor must be recomputed for Ethanol!
    assert snap_b["canonical_smiles"] == "CCO"
    assert pytest.approx(snap_b["molecular_weight_g_mol"], abs=0.05) == 46.07
    assert pytest.approx(snap_b["logp"], abs=0.05) == -0.0014
    assert pytest.approx(snap_b["tpsa_angstrom2"], abs=0.1) == 20.23
    assert snap_b["hbd"] == 1
    assert snap_b["hba"] == 1
    assert snap_b["rotatable_bonds"] == 0
    assert snap_b["aromatic_rings"] == 0
    assert snap_b["inchi_key"] == "LFQSCWFLJHTTHZ-UHFFFAOYSA-N"

    # Zero aspirin-derived descriptors remain!
    assert snap_b["molecular_weight_g_mol"] != 180.16
    assert snap_b["aromatic_rings"] != 1
    assert len(snap_b["descriptor_discrepancies"]) > 0


# =============================================================================
# TEST 8: Stored stale descriptors cannot override RDKit-derived descriptors
# =============================================================================
def test_08_stored_stale_descriptors_cannot_override():
    stale_profile = {
        "drug_id": "DRG-STALE",
        "canonical_smiles": "CCO",
        "molecular_weight_g_mol": 999.99,      # Grossly incorrect
        "logp": 15.0,                          # Grossly incorrect
        "tpsa_angstrom2": 450.0,               # Grossly incorrect
        "hbd": 8,                              # Grossly incorrect
        "hba": 12,                             # Grossly incorrect
        "rotatable_bonds": 9,                  # Grossly incorrect
        "aromatic_rings": 5,                   # Grossly incorrect
        "inchi_key": "FAKE-INCHI-KEY-N",
    }

    snap = resolve_validated_drug_snapshot(stale_profile)

    # Authoritative RDKit values must overwrite all stale inputs
    assert pytest.approx(snap["molecular_weight_g_mol"], abs=0.05) == 46.07
    assert pytest.approx(snap["logp"], abs=0.05) == -0.0014
    assert pytest.approx(snap["tpsa_angstrom2"], abs=0.1) == 20.23
    assert snap["hbd"] == 1
    assert snap["hba"] == 1
    assert snap["rotatable_bonds"] == 0
    assert snap["aromatic_rings"] == 0
    assert snap["inchi_key"] == "LFQSCWFLJHTTHZ-UHFFFAOYSA-N"

    # Stale inputs must be captured in discrepancy audit
    disc = snap["descriptor_discrepancies"]
    assert "molecular_weight_g_mol" in disc
    assert disc["molecular_weight_g_mol"]["stored"] == 999.99
    assert pytest.approx(disc["molecular_weight_g_mol"]["authoritative"], abs=0.05) == 46.07


# =============================================================================
# TEST 9: Valid stereochemical SMILES preserves stereochemistry
# =============================================================================
def test_09_stereochemistry_preserved():
    smiles_r = "O=C1CC[C@H](N2C(=O)c3ccccc3C2=O)C(=O)N1"
    smiles_s = "O=C1CC[C@@H](N2C(=O)c3ccccc3C2=O)C(=O)N1"

    desc_r = compute_production_descriptors(smiles_r)
    desc_s = compute_production_descriptors(smiles_s)

    # Stereocenters preserved in canonical smiles
    assert "@" in desc_r["canonical_smiles"]
    assert "@" in desc_s["canonical_smiles"]

    # InChIKeys distinguish enantiomers
    assert desc_r["inchi_key"] == "UEJJHQNACJXSKW-VIFPVBQESA-N"
    assert desc_s["inchi_key"] == "UEJJHQNACJXSKW-SECBINFHSA-N"
    assert desc_r["inchi_key"] != desc_s["inchi_key"]


# =============================================================================
# TEST 10: Itraconazole stereochemistry and InChIKey remain correct
# =============================================================================
def test_10_itraconazole_stereochemistry_inchikey():
    itr_smiles = "CCC(C)n1ncn(-c2ccc(N3CCN(c4ccc(OC[C@H]5CO[C@](Cn6cncn6)(c6ccc(Cl)cc6Cl)O5)cc4)CC3)cc2)c1=O"
    desc = compute_production_descriptors(itr_smiles)

    assert "@" in desc["canonical_smiles"]
    assert desc["inchi_key"] == "VHVPQPYKVGDNFY-ZPGVKDDISA-N"
    assert pytest.approx(desc["MolWt"], abs=0.05) == 705.65


# =============================================================================
# TEST 11: Canonical-equivalent SMILES produce equivalent structure identity
# =============================================================================
def test_11_canonical_equivalent_smiles_converge():
    desc_1 = compute_production_descriptors("CCO")
    desc_2 = compute_production_descriptors("OCC")

    assert desc_1["canonical_smiles"] == desc_2["canonical_smiles"] == "CCO"
    assert desc_1["inchi_key"] == desc_2["inchi_key"]
    assert desc_1["MolWt"] == desc_2["MolWt"]
    assert desc_1["TPSA"] == desc_2["TPSA"]


# =============================================================================
# TEST 12: Isotopic structure remains distinguishable
# =============================================================================
def test_12_isotopic_structure_distinguishable():
    desc_normal = compute_production_descriptors("CCO")
    desc_deut = compute_production_descriptors("[2H]C([2H])([2H])C([2H])([2H])O")

    assert desc_deut["MolWt"] > desc_normal["MolWt"]
    assert pytest.approx(desc_deut["MolWt"], abs=0.05) == 51.10
    assert desc_deut["inchi_key"] != desc_normal["inchi_key"]


# =============================================================================
# TEST 13: Multi-component salt behavior remains unchanged and explicitly documented
# =============================================================================
def test_13_multi_component_salt_behavior_documented():
    # Sodium acetate salt: CC(=O)[O-].[Na+]
    desc = compute_production_descriptors("CC(=O)[O-].[Na+]")

    # Confirms current behavior: salt is parsed as full complex without stripping
    assert pytest.approx(desc["MolWt"], abs=0.05) == 82.03
    assert desc["inchi_key"] == "VMHLLURERBWHNL-UHFFFAOYSA-M"
    assert desc["validation_status"] == "VALID"


# =============================================================================
# TEST 14: Production descriptor provenance identifies RDKit as source
# =============================================================================
def test_14_descriptor_provenance_rdkit():
    snap = resolve_validated_drug_snapshot({"canonical_smiles": "CC(=O)Oc1ccccc1C(=O)O"})
    assert snap["descriptor_source"] == "RDKit"
    assert snap["fallback_used"] is False
    assert snap["validation_status"] == "VALID"
    assert snap["rdkit_version"] is not None


# =============================================================================
# TEST 15: A completely new valid drug can still propagate through v2
# =============================================================================
def test_15_new_valid_drug_propagates_generalized():
    # Paracetamol
    paracetamol_raw = {
        "drug_id": "DRG-PARA-001",
        "generic_name": "Paracetamol",
        "canonical_smiles": "CC(=O)Nc1ccc(O)cc1",
        "tm_k": 443.0,
        "tg_k": 296.0,
        "density_crystalline_g_cm3": 1.29,
        "hsp_delta_d": 18.0,
        "hsp_delta_p": 12.0,
        "hsp_delta_h": 14.0,
        "hsp_ro": 8.0,
        "molar_volume_cm3_mol": 117.1,
    }

    validated_snap = resolve_validated_drug_snapshot(paracetamol_raw)
    assert validated_snap["validation_status"] == "VALID"
    assert validated_snap["descriptor_source"] == "RDKit"

    # Evaluate through VariableKEngine
    synthetic_scores = np.array([
        [0.85, 0.80, 0.75, 0.70],
        [0.60, 0.65, 0.70, 0.75],
        [0.90, 0.88, 0.82, 0.80],
        [0.40, 0.45, 0.50, 0.55],
        [0.70, 0.72, 0.68, 0.65],
    ], dtype=np.float64)

    engine = VariableKEngine()
    result = engine.evaluate(synthetic_scores, AHP_MATRIX, POL_IDS, drug_data=validated_snap)

    assert result.analysis_id is not None
    assert result.retained_k in (1, 2, 3, 4)
    assert result.cumulative_variance >= 0.95
    assert result.stability_status in ("STABLE", "WARNING")
    assert len(result.metrics.closeness_coefficients) == 5


# =============================================================================
# TEST 16: Defense-in-depth engine rejects fallback provenance
# =============================================================================
def test_16_defense_in_depth_engine_rejects_fallback():
    contaminated_drug_snapshot = {
        "drug_id": "DRG-CONTAMINATED",
        "canonical_smiles": "CCO",
        "descriptor_source": "fallback",
        "fallback_used": True,
    }
    dummy_scores = np.full((5, 4), 0.5, dtype=np.float64)
    engine = VariableKEngine()

    with pytest.raises(ProductionFallbackProhibitedError):
        engine.evaluate(dummy_scores, AHP_MATRIX, POL_IDS, drug_data=contaminated_drug_snapshot)


# =============================================================================
# TEST 17: Polymer repeat unit validation prevents corrupted monomer SMILES
# =============================================================================
def test_17_polymer_repeat_unit_validation():
    class DummyPolymer:
        def __init__(self, pid, monomer_smiles):
            self.polymer_id = pid
            self.monomer_smiles = monomer_smiles

    # Valid monomer passes
    valid_poly = DummyPolymer("POL-VALID", "C1CCN(C1=O)C=C|CC(=O)OC=C")
    validate_polymer_repeat_units(valid_poly)  # Should not raise

    # Invalid monomer raises ChemicalStructureError
    corrupt_poly = DummyPolymer("POL-CORRUPT", "C1CCN(C1=O)C=C|NOT_A_VALID_MONOMER")
    with pytest.raises(ChemicalStructureError, match="contains invalid monomer SMILES"):
        validate_polymer_repeat_units(corrupt_poly)


# =============================================================================
# TEST 18: v1.5 isolation unaffected by v2 chemistry import
# =============================================================================
def test_18_v15_isolation_unaffected_by_v2_import():
    # Verify importing v2 does not modify Drug classmethod or v1.5 classes
    from asd_mcda.drug.drug_profile import Drug
    # Drug class itself is frozen and untouched
    assert hasattr(Drug, "from_dict")
    # Verify no monkey-patch was applied
    assert Drug.from_dict.__module__ == "asd_mcda.drug.drug_profile"
