# Controlled Cheminformatics Integrity Remediation Report

**Project**: PharmaPolySCOPE (Pharmaceutical Polymer Screening and Computational Optimization Platform)  
**Release Target**: v2.0.0 (Production Candidate)  
**Baseline Anchor**: Git Commit `31eee4d9bb1cc57b9185f9f958e225d51634c871` (v1.5 Protected Baseline)  
**Date**: September 13, 2026  
**Status**: REMEDIATION COMPLETE — ALL INTEGRITY GATES VERIFIED  

---

> [!IMPORTANT]
> **Methodological Invariance Statement**:
> This remediation changes input/structure integrity controls only and does not alter the PharmaPolySCOPE v2 scientific decision methodology.

---

## 1. Defects Discovered

A comprehensive forensic audit of the RDKit molecular-structure pipeline revealed two critical software/architectural defects:

1. **Defect 1 (Silent Invalid SMILES Penetration to MCDA)**:
   The legacy input validation schema checked only that `canonical_smiles` was a non-empty string. It did not invoke RDKit parsing or sanitization. If an unparseable or chemically nonsensical SMILES string was supplied, the wrapper caught the parse failure, silently injected hardcoded heuristic fallback constants ($M_w=111.14$, $\text{LogP}=0.5$, $\text{TPSA}=20.3$, etc.), and passed these synthetic descriptors into the compatibility matrix, PCA, AHP, and TOPSIS. An invalid string produced an apparently valid deterministic ranking with zero exceptions raised.
2. **Defect 2 (Stale Descriptor Persistence on Structure Change)**:
   In `Drug.from_dict()`, scalar fields in input dictionaries ($M_w, \text{LogP}, \text{TPSA}, \text{HBD}, \text{HBA}$) took precedence over dynamic calculation. If a user changed `canonical_smiles` (e.g., from Aspirin to Ethanol) while keeping the original dictionary keys, the Drug dataclass retained the old scalar numbers while `DescriptorEngine` computed new values from SMILES, causing severe internal data divergence.

---

## 2. Root Cause Analysis

- **Defect 1 Root Cause**: Absence of an explicit, unbypassable chemical structure validation gate in the production ingestion pipeline, coupled with a permissive `try...except` wrapper in `rdkit_wrapper.py` that automatically routed failed parses to `_fallback_2d_descriptors()`.
- **Defect 2 Root Cause**: Dictionary-first precedence in profile deserialization (`data.get("molecular_weight_g_mol") or descriptors_2d["MolWt"]`) rather than structure-first precedence.

---

## 3. Exact Code Changes

All changes were implemented strictly in the `v2` package space without modifying any of the 71 protected v1.5 files:

1. **`src/asd_mcda/v2/exceptions.py`**:
   - Introduced domain-specific chemical exception hierarchy inheriting from `PharmaPolyScopeV2Error` and standard exceptions:
     - `ChemicalStructureError(PharmaPolyScopeV2Error, ValueError)`
     - `RDKitUnavailableError(ChemicalStructureError, RuntimeError)`
     - `InvalidSmilesError(ChemicalStructureError)`
     - `RDKitParseFailureError(InvalidSmilesError)`
     - `RDKitSanitizationFailureError(ChemicalStructureError)`
     - `ProductionFallbackProhibitedError(ChemicalStructureError)`
2. **`src/asd_mcda/v2/phase5_models.py`**:
   - Expanded `CANONICAL_BLOCK_REASONS` with explicit chemical failure codes:
     `"INVALID_SMILES"`, `"RDKIT_PARSE_FAILURE"`, `"RDKIT_SANITIZATION_FAILURE"`, `"RDKIT_UNAVAILABLE"`, `"FALLBACK_PROHIBITED"`.
3. **`src/asd_mcda/v2/chemistry.py` [NEW MODULE]**:
   - `validate_chemical_structure(smiles)`: Strict production gate requiring non-empty string, RDKit availability, successful `Chem.MolFromSmiles()`, and successful `Chem.SanitizeMol()`.
   - `compute_production_descriptors(smiles_or_mol)`: Authoritative RDKit calculation producing canonical SMILES, InChIKey, and 8 2D descriptors with `descriptor_source="RDKit"`, `fallback_used=False`, `validation_status="VALID"`.
   - `get_diagnostic_fallback_descriptors(smiles)`: Strictly isolated diagnostic estimator tagged with `descriptor_source="fallback"`, `fallback_used=True`.
   - `resolve_validated_drug_snapshot(raw_data)`: Authoritative structure-first resolution. Overrides stored scalars with RDKit values and logs discrepancies in `descriptor_discrepancies`.
   - `validate_polymer_repeat_units(polymer)`: Validates monomer/repeat-unit SMILES, raising `ChemicalStructureError` on invalid structures.
4. **`src/asd_mcda/v2/engine.py`**:
   - Added defense-in-depth validation in `VariableKEngine.evaluate()`: rejects any drug snapshot with `fallback_used=True` or `descriptor_source="fallback"`, and validates `canonical_smiles`.
5. **`src/asd_mcda/v2/__init__.py`**:
   - Cleanly exported all new chemical exceptions and functions without any global monkey-patching or side effects.
6. **`tests/v2/test_cheminformatics_integrity.py` [NEW TEST SUITE]**:
   - 29 comprehensive automated tests verifying all 17 mandatory requirements.

---

## 4. Production Behavior Before vs. After

| Scenario | Behavior Before Remediation | Behavior After Remediation |
|---|---|---|
| **Malformed SMILES** (e.g. `CC(=O`) | Ingested silently; fallback injected; MCDA ranking generated | **BLOCKED** immediately with `RDKitParseFailureError` before scoring |
| **Impossible Valence** (`C=C=C=C=C(C)(C)(C)(C)`) | Ingested silently; fallback injected; MCDA ranking generated | **BLOCKED** immediately with `RDKitParseFailureError` before scoring |
| **RDKit Missing in Production** | Silently used synthetic constants | **BLOCKED** with `RDKitUnavailableError` |
| **SMILES Changed (Aspirin $\to$ Ethanol)** | Retained stale Aspirin scalar fields in Drug object | **SYNCHRONIZED**: All structure-derived fields update to Ethanol |
| **Conflicting Scalar Inputs** | Stored scalar fields silently overrode RDKit calculation | **SYNCHRONIZED**: RDKit is authoritative; differences logged to provenance |
| **Fallback Reaching VariableKEngine** | Accepted and computed rankings silently | **BLOCKED**: VariableKEngine raises `ProductionFallbackProhibitedError` |
| **Polymer Monomer Corrupted** | Monomer fallback descriptors used silently | **BLOCKED**: `validate_polymer_repeat_units` raises `ChemicalStructureError` |

---

## 5. Fallback Behavior & Isolation

The fallback mechanism is now strictly isolated:
- `compute_production_descriptors()` has zero fallback branches; it requires an active RDKit installation and valid molecular graph.
- `get_diagnostic_fallback_descriptors()` is isolated to non-production testing and development diagnostics.
- Any drug snapshot carrying `fallback_used=True` or `descriptor_source="fallback"` is intercepted by `VariableKEngine` and blocked with `ProductionFallbackProhibitedError`.

---

## 6. Structure Invalidation Behavior

Under the remediated v2 architecture:
- Structure-derived properties ($M_w, \text{LogP}, \text{TPSA}, \text{HBD}, \text{HBA}, N_{\text{rot}}, N_{\text{arom}}, f_{\text{TPSA}}, \text{InChIKey}$) are derived deterministically from the parsed RDKit molecular graph.
- When an updated SMILES string is supplied, a new snapshot is constructed. 100% of structure-derived properties reflect the new SMILES. Zero stale properties survive.
- Discrepancies between stored inputs and authoritative values are non-fatal but permanently recorded in `descriptor_discrepancies` for auditability.

---

## 7. Descriptor Provenance

Every drug profile processed by v2 carries immutable provenance metadata:
```json
{
  "descriptor_source": "RDKit",
  "rdkit_version": "2026.03.5",
  "fallback_used": false,
  "validation_status": "VALID",
  "descriptor_discrepancies": {}
}
```
If discrepancies exist between user inputs and RDKit, they are recorded field-by-field with both `stored` and `authoritative` values.

---

## 8. Test Coverage & Verification

### Automated Test Results
1. **`tests/v2/test_cheminformatics_integrity.py`**:
   - **29 passed** out of 29 collected tests (100%).
   - All 15 required test categories (plus defense-in-depth, polymer repeat-unit, and v1.5 isolation) passed.
2. **`tests/unit/test_rdkit_integration.py`**:
   - **15 passed** out of 15 collected tests (100%).
3. **`tests/v2/test_v15_isolation_regression.py`**:
   - **4 passed** out of 4 collected tests (100%).
   - Confirms 71/71 baseline files byte-identical.
4. **Full v2 Suite (`tests/v2/`)**:
   - **116 passed** out of 116 collected tests (100%).
   - Previous baseline: 87 passed. New baseline: 116 passed. Zero failures.

---

## 9. v1.5 Integrity & Isolation

- **71/71 protected v1.5 files** remain 100% byte-identical against Git commit `31eee4d9bb1cc57b9185f9f958e225d51634c871`.
- **Zero global monkey-patching**: `Drug.from_dict()` remains unmodified in `src/asd_mcda/drug/drug_profile.py`.
- **Zero import-time side effects**: Importing `asd_mcda.v2` does not alter any class attributes, function signatures, or global states of v1.5 modules.

---

## 10. Scientific Methodology Integrity & Real-Drug Regression

The four active drug profiles were evaluated through the remediated v2 chemistry pipeline:

| Drug Profile | Validation Status | InChIKey | Stored $M_w$ | Authoritative $M_w$ | Stored TPSA | Authoritative TPSA | Discrepancies Logged | Deterministic Ranks & Closeness |
|---|---|---|---|---|---|---|---|---|
| **Indomethacin** (`IND-001-2026`) | VALID | `CGIGDMFJXJATDK-UHFFFAOYSA-N` | 357.79 | 357.793 | 68.50 | 68.53 | `['logp', 'hba', 'aromatic_rings']` | K=3, Var=99.96%, Stable; Ranks: (4, 3, 5, 1, 2) |
| **Ibuprofen** (`DRG-0001`) | VALID | `HEFNNWSXXWATRW-UHFFFAOYSA-N` | 206.28 | 206.285 | 37.30 | 37.30 | `['hba']` | K=2, Var=96.10%, Stable; Soluplus rank 1 ($C_L = 0.5503$) |
| **Itraconazole** (`ITR-001-2026`) | VALID | `VHVPQPYKVGDNFY-ZPGVKDDISA-N` | 705.60 | 705.647 | 104.70 | 104.70 | `[]` (None) | K=2, Var=96.19%, Stable; Soluplus rank 1 ($C_L = 0.6106$) |
| **Fenofibrate** (`DRG-0007`) | VALID | `YMTINGFKWWXKFG-UHFFFAOYSA-N` | 360.84 | 360.837 | 52.60 | 52.60 | `[]` (None) | Blocked from experimental translation (absent amorphous density) |

*Key Result*: The production recommendation for Itraconazole (**Soluplus rank 1**) is mathematically unchanged and verified.

---

## 11. Remaining Documented Limitations

1. **Multi-Component Salts & Solvates**: Disconnected SMILES (e.g. `CC(=O)[O-].[Na+]`) are parsed as the full molecular complex without counterion stripping or fragment selection. This behavior is documented and preserved.
2. **Tautomerism & Protonation**: Tautomer canonicalization and pH-dependent ionization modeling are not implemented, pending a dedicated future chemical standardization policy.

---

## 12. Future Maintenance Recommendations

1. Implement a dedicated `ChemicalStandardizer` in v2.1 to provide optional salt stripping, neutralization, and major microspecies protonation at pH 6.8.
2. When the v1.5 codebase undergoes formal version retirement, migrate `Drug.from_dict()` to use `resolve_validated_drug_snapshot()` natively.

---

## 13. Attestation & Final Verdict

The RDKit/SMILES integrity layer is ready for final computational release review, subject to the documented limitations.

CHEMINFORMATICS REMEDIATION PASSED
