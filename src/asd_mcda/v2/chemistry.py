"""Cheminformatics Integrity and Chemical Structure Ingestion for PharmaPolySCOPE v2.

Authoritative Specification: Controlled Cheminformatics Integrity Remediation.
Implements:
1. Self-contained chemical structure validation gate (blocking invalid/malformed SMILES).
2. Authoritative RDKit molecular graph parsing and descriptor derivation.
3. Strict separation of production descriptor path from isolated diagnostic fallbacks.
4. Non-fatal stale descriptor synchronization with audit provenance recording.
5. Polymer repeat-unit structure integrity validation.

Zero global monkey-patching; zero modification to frozen v1.5 baseline.
"""

from copy import deepcopy
import logging
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple, Union
import numpy as np

# RDKit import
try:
    import rdkit
    from rdkit import Chem
    from rdkit.Chem import Descriptors, inchi, rdMolDescriptors
    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False
    rdkit = None
    Chem = None
    Descriptors = None
    inchi = None
    rdMolDescriptors = None

from asd_mcda.v2.exceptions import (
    ChemicalStructureError,
    InvalidSmilesError,
    ProductionFallbackProhibitedError,
    RDKitParseFailureError,
    RDKitSanitizationFailureError,
    RDKitUnavailableError,
)

logger = logging.getLogger(__name__)

STRUCTURE_DERIVED_FIELDS: Tuple[str, ...] = (
    "molecular_weight_g_mol",
    "logp",
    "tpsa_angstrom2",
    "hbd",
    "hba",
    "rotatable_bonds",
    "aromatic_rings",
    "fractional_tpsa",
    "inchi_key",
)


def is_rdkit_available() -> bool:
    """Return True if RDKit is operational in the runtime environment."""
    return bool(RDKIT_AVAILABLE and Chem is not None)


def validate_chemical_structure(smiles: str) -> Any:
    """Validate a chemical SMILES string for production execution.

    Parameters
    ----------
    smiles : str
        Input SMILES representation.

    Returns
    -------
    rdkit.Chem.Mol
        Sanitized, valid RDKit molecular graph.

    Raises
    ------
    InvalidSmilesError
        If smiles is not a non-empty string or contains whitespace-only characters.
    RDKitUnavailableError
        If RDKit is not installed or importable.
    RDKitParseFailureError
        If RDKit fails to parse the SMILES string into a chemical graph.
    RDKitSanitizationFailureError
        If RDKit sanitization (valency, aromaticity, kekulization) fails.
    """
    if not isinstance(smiles, str):
        raise InvalidSmilesError(f"SMILES must be a string, got {type(smiles).__name__}.")

    clean_smiles = smiles.strip()
    if not clean_smiles:
        raise InvalidSmilesError("SMILES string cannot be empty or whitespace-only.")

    if not is_rdkit_available():
        raise RDKitUnavailableError(
            "RDKit is required for production molecular-structure processing and descriptor calculation. "
            "Silent fallback descriptors are prohibited in production."
        )

    # Attempt parsing
    mol = Chem.MolFromSmiles(clean_smiles)
    if mol is None:
        raise RDKitParseFailureError(
            f"RDKit failed to parse chemical structure from SMILES: '{clean_smiles}'."
        )

    # Attempt sanitization
    sanitization_val = Chem.SanitizeMol(mol, catchErrors=True)
    if sanitization_val != Chem.SanitizeFlags.SANITIZE_NONE:
        raise RDKitSanitizationFailureError(
            f"RDKit sanitization failed for SMILES '{clean_smiles}' (error flag: {sanitization_val})."
        )

    return mol


def compute_production_descriptors(smiles_or_mol: Union[str, Any]) -> Dict[str, Any]:
    """Compute authoritative 2D molecular descriptors using RDKit.

    Strict production path: requires a valid RDKit molecular graph.
    Never falls back to heuristic constants.

    Parameters
    ----------
    smiles_or_mol : Union[str, Chem.Mol]
        Input SMILES string or pre-validated RDKit Mol object.

    Returns
    -------
    Dict[str, Any]
        Authoritative descriptor dictionary with cryptographic/provenance metadata:
        - canonical_smiles: Canonical SMILES preserving tetrahedral stereocenters (@/@@)
        - inchi_key: Authoritative InChIKey
        - MolWt, MolLogP, TPSA, NumHDonors, NumHAcceptors, NumRotatableBonds, NumAromaticRings, FractionalTPSA
        - descriptor_source: "RDKit"
        - rdkit_version: installed RDKit version string
        - fallback_used: False
        - validation_status: "VALID"
    """
    if isinstance(smiles_or_mol, str):
        mol = validate_chemical_structure(smiles_or_mol)
    else:
        if smiles_or_mol is None:
            raise InvalidSmilesError("Cannot compute descriptors for None molecular graph.")
        mol = smiles_or_mol

    # Canonical SMILES preserving tetrahedral stereochemistry
    canonical_smiles = Chem.MolToSmiles(mol, canonical=True)

    # Authoritative InChIKey
    try:
        inchi_key = inchi.MolToInchiKey(mol)
    except Exception as exc:
        raise ChemicalStructureError(f"Failed to generate InChIKey from parsed molecule: {exc}") from exc

    if not inchi_key or inchi_key == "UNKNOWN_INCHI_KEY":
        raise ChemicalStructureError("Failed to generate a valid InChIKey from parsed molecule.")

    mw = float(Descriptors.MolWt(mol))
    logp = float(Descriptors.MolLogP(mol))
    tpsa = float(Descriptors.TPSA(mol))
    hbd = int(Descriptors.NumHDonors(mol))
    hba = int(Descriptors.NumHAcceptors(mol))
    rotb = int(Descriptors.NumRotatableBonds(mol))
    arom = int(rdMolDescriptors.CalcNumAromaticRings(mol))
    frac_tpsa = float(tpsa / mw if mw > 0.0 else 0.0)

    rdkit_ver = getattr(rdkit, "__version__", "unknown")

    return {
        "canonical_smiles": canonical_smiles,
        "inchi_key": inchi_key,
        "MolWt": mw,
        "MolLogP": logp,
        "TPSA": tpsa,
        "NumHDonors": hbd,
        "NumHAcceptors": hba,
        "NumRotatableBonds": rotb,
        "NumAromaticRings": arom,
        "FractionalTPSA": frac_tpsa,
        "descriptor_source": "RDKit",
        "rdkit_version": rdkit_ver,
        "fallback_used": False,
        "validation_status": "VALID",
    }


def get_diagnostic_fallback_descriptors(smiles: str) -> Dict[str, Any]:
    """Isolated diagnostic fallback estimator for development and non-production testing.

    WARNING: This function MUST NEVER be used in the production decision engine.
    Any profile carrying these descriptors is blocked by VariableKEngine.
    """
    length = len(smiles) if smiles else 0
    clean = smiles if smiles else ""
    return {
        "canonical_smiles": clean,
        "inchi_key": "UNKNOWN_INCHI_KEY",
        "MolWt": round(length * 5.5 + 50.0, 2),
        "MolLogP": round(0.5 + (clean.count("c") + clean.count("C")) * 0.1, 2),
        "TPSA": round((clean.count("O") + clean.count("N")) * 10.0 + 10.3, 2),
        "NumHDonors": clean.count("O") // 2,
        "NumHAcceptors": clean.count("O") + clean.count("N"),
        "NumRotatableBonds": max(1, length // 10),
        "NumAromaticRings": 1 if "c" in clean else 0,
        "FractionalTPSA": 0.25,
        "descriptor_source": "fallback",
        "rdkit_version": None,
        "fallback_used": True,
        "validation_status": "FALLBACK_DIAGNOSTIC",
    }


def resolve_validated_drug_snapshot(raw_data: Mapping[str, Any]) -> Dict[str, Any]:
    """Ingest a raw drug dictionary, validate chemical structure, and resolve authoritative descriptors.

    Enforces the Stale Descriptor Policy:
    - Chemical structure (canonical_smiles) parsed by RDKit is authoritative.
    - All structure-derived fields are overwritten with RDKit-derived values.
    - Any discrepancies between stored scalar values and authoritative RDKit values
      are preserved in the provenance audit log under 'descriptor_discrepancies'.
    - Stale values are non-fatal: production continues with authoritative values.

    Parameters
    ----------
    raw_data : Mapping[str, Any]
        Raw dictionary loaded from JSON or user submission.

    Returns
    -------
    Dict[str, Any]
        Validated, immutable-ready drug snapshot with synchronized descriptors.

    Raises
    ------
    InvalidSmilesError, RDKitParseFailureError, RDKitSanitizationFailureError, RDKitUnavailableError
        If chemical structure validation fails.
    """
    if "canonical_smiles" not in raw_data:
        raise InvalidSmilesError("Drug profile missing required field 'canonical_smiles'.")

    smiles = raw_data["canonical_smiles"]
    authoritative = compute_production_descriptors(smiles)

    snapshot = dict(deepcopy(raw_data))

    # Detect discrepancies between stored scalar inputs and authoritative RDKit descriptors
    discrepancies: Dict[str, Dict[str, Any]] = {}

    mapping_pairs = [
        ("molecular_weight_g_mol", authoritative["MolWt"], 0.05),
        ("logp", authoritative["MolLogP"], 0.05),
        ("tpsa_angstrom2", authoritative["TPSA"], 0.1),
        ("hbd", authoritative["NumHDonors"], 0),
        ("hba", authoritative["NumHAcceptors"], 0),
        ("rotatable_bonds", authoritative["NumRotatableBonds"], 0),
        ("aromatic_rings", authoritative["NumAromaticRings"], 0),
    ]

    for field_name, auth_val, tol in mapping_pairs:
        if field_name in snapshot and snapshot[field_name] is not None:
            stored_val = snapshot[field_name]
            is_different = False
            if tol == 0:
                is_different = int(stored_val) != int(auth_val)
            else:
                is_different = abs(float(stored_val) - float(auth_val)) > tol

            if is_different:
                discrepancies[field_name] = {
                    "stored": stored_val,
                    "authoritative": auth_val,
                }

    stored_inchi = snapshot.get("inchi_key")
    if stored_inchi and stored_inchi != authoritative["inchi_key"]:
        discrepancies["inchi_key"] = {
            "stored": stored_inchi,
            "authoritative": authoritative["inchi_key"],
        }

    # Authoritative Overwrite: Structure-derived properties synchronize to RDKit
    snapshot["canonical_smiles"] = authoritative["canonical_smiles"]
    snapshot["inchi_key"] = authoritative["inchi_key"]
    snapshot["molecular_weight_g_mol"] = authoritative["MolWt"]
    snapshot["logp"] = authoritative["MolLogP"]
    snapshot["tpsa_angstrom2"] = authoritative["TPSA"]
    snapshot["hbd"] = authoritative["NumHDonors"]
    snapshot["hba"] = authoritative["NumHAcceptors"]
    snapshot["rotatable_bonds"] = authoritative["NumRotatableBonds"]
    snapshot["aromatic_rings"] = authoritative["NumAromaticRings"]
    snapshot["fractional_tpsa"] = authoritative["FractionalTPSA"]

    # Ingestion and provenance stamps
    snapshot["descriptor_source"] = authoritative["descriptor_source"]
    snapshot["rdkit_version"] = authoritative["rdkit_version"]
    snapshot["fallback_used"] = False
    snapshot["validation_status"] = "VALID"
    snapshot["descriptor_discrepancies"] = discrepancies

    return snapshot


def validate_polymer_repeat_units(polymer: Any) -> None:
    """Validate all monomer/repeat-unit SMILES in a polymer candidate.

    Raises
    ------
    ChemicalStructureError
        If any monomer SMILES string is unparseable or chemically invalid.
    """
    monomer_smiles = getattr(polymer, "monomer_smiles", None)
    if not monomer_smiles or not isinstance(monomer_smiles, str):
        return

    sub_smiles = [s.strip() for s in monomer_smiles.split("|") if s.strip()]
    for s in sub_smiles:
        try:
            validate_chemical_structure(s)
        except ChemicalStructureError as exc:
            poly_id = getattr(polymer, "polymer_id", "UNKNOWN_POLYMER")
            raise ChemicalStructureError(
                f"Polymer '{poly_id}' contains invalid monomer SMILES '{s}': {exc}"
            ) from exc
