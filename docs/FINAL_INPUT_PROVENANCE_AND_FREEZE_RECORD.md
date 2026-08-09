# Final Input Data Provenance and Freeze Record

**Project**: Indomethacin ASD Computational Polymer Screening Framework  
**Master Research Framework**: V2.0  
**Software Release**: `asd_mcda` v1.1.0  
**Status**: FROZEN COMPUTATIONAL BASELINE  
**Date**: August 9, 2026  

---

## 1. Executive Summary

This document establishes the official physical property provenance, input classification, and frozen data integrity record for the **Indomethacin Amorphous Solid Dispersion (ASD) Computational Screening Framework**. All physical property values for the active pharmaceutical ingredient (Indomethacin) and candidate polymeric carriers have been forensically audited, cross-referenced with peer-reviewed literature, supplier Certificates of Analysis (CoAs), and USP monographs, and locked for prospective experimental execution.

---

## 2. Indomethacin API Input Provenance

| Property Field | Value | Unit | Source / Reference | Data Type | Grade / State | Uncertainty |
| :--- | :---: | :---: | :--- | :---: | :---: | :---: |
| **Generic Name** | Indomethacin | - | USP Monograph | Reference | Pure API | - |
| **CAS Number** | 53-86-1 | - | Chemical Abstracts Service | Registry | Pure API | - |
| **Molecular Weight ($M_w$)** | 357.79 | g/mol | USP Monograph / IUPAC | Experimental | Pure API | $\pm 0.01$ |
| **Melting Point ($T_m$)** | 424.15 (151.0 °C) | K | Hancock et al., *J. Pharm. Sci.* 2007 | Experimental DSC | $\gamma$-Polymorph | $\pm 0.5$ |
| **Glass Transition ($T_g$)** | 315.15 (42.0 °C) | K | Hancock et al., *J. Pharm. Sci.* 2007 | Experimental DSC | Quenched Amorphous | $\pm 1.0$ |
| **Amorphous Density ($\rho_{\text{amorphous}}$)** | 1.22 | $\text{g/cm}^3$ | Hancock et al., *J. Pharm. Sci.* 2007 | Experimental Pycnometry | Amorphous | $\pm 0.02$ |
| **Crystalline Density ($\rho_{\text{crystalline}}$)** | 1.31 | $\text{g/cm}^3$ | Yalkowsky et al., *Solubility Data* | Experimental | $\gamma$-Form | $\pm 0.01$ |
| **HSP Dispersion ($\delta_D$)** | 19.2 | $\text{MPa}^{0.5}$ | Hancock et al., *J. Pharm. Sci.* 2007 | Experimental Sphere | Pure API | $\pm 0.5$ |
| **HSP Polar ($\delta_P$)** | 7.9 | $\text{MPa}^{0.5}$ | Hancock et al., *J. Pharm. Sci.* 2007 | Experimental Sphere | Pure API | $\pm 0.5$ |
| **HSP Hydrogen ($\delta_H$)** | 8.4 | $\text{MPa}^{0.5}$ | Hancock et al., *J. Pharm. Sci.* 2007 | Experimental Sphere | Pure API | $\pm 0.5$ |
| **HSP Total ($\delta_T$)** | 22.4 | $\text{MPa}^{0.5}$ | Calculated ($\sqrt{\delta_D^2 + \delta_P^2 + \delta_H^2}$) | Calculated | Pure API | $\pm 0.5$ |
| **Interaction Radius ($R_0$)** | 8.0 | $\text{MPa}^{0.5}$ | Hancock et al., *J. Pharm. Sci.* 2007 | Experimental | Pure API | $\pm 0.5$ |

---

## 3. Candidate Polymer Library Input Provenance

| Polymer ID | Canonical Polymer Name | Abbreviation | Polymer Family | MW ($M_n / M_w$) | $T_g$ (K) | Density ($\text{g/cm}^3$) | HSP ($\delta_D/\delta_P/\delta_H$) | Monomer SMILES | Literature Evidence | Primary Source |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| `POL-001-2026` | Polyvinylpyrrolidone K30 | PVP_K30 | vinylic | 40k / 50k | 443.0 | 1.20 | 17.4 / 8.2 / 11.7 | `C=CN1CCCC1=O` | 1.0 | BASF CoA / J. Pharm. Sci. 2007 |
| `POL-002-2026` | PVP-Vinyl Acetate 64 | PVP_VA_64 | vinylic | 45k / 54k | 380.0 | 1.20 | 17.0 / 8.0 / 10.0 | `C=CN1CCCC1=O\|CC(=O)OC` | 1.0 | BASF CoA / Int. J. Pharm. 2010 |
| `POL-003-2026` | HPMC Acetate Succinate Low | HPMCAS_L | cellulosic | 100k / 120k | 394.0 | 1.28 | 18.0 / 8.2 / 10.5 | `COCC1O[C@H](O)...` | 1.0 | Shin-Etsu CoA / Int. J. Pharm. 2014 |
| `POL-004-2026` | Eudragit L100 | EDR_L100 | acrylic | 125k / 150k | 438.0 | 1.25 | 16.5 / 7.5 / 9.0 | `CC(C)C(=O)OC(C)C\|...` | 0.5 | Evonik Technical Specification |
| `POL-005-2026` | Soluplus | SOLUPLUS | acrylic | 90k / 118.8k | 343.0 | 1.15 | 18.0 / 8.5 / 10.5 | `CC(=O)OCC(C)C\|...` | 1.0 | BASF CoA / Int. J. Pharm. 2010 |
| `POL-006-2026` | Hydroxypropyl Methylcellulose E5 | HPMC_E5 | cellulosic | 20k / 26k | 438.0 | 1.33 | 18.5 / 8.8 / 12.0 | `COCC1O[C@H](O)...` | 0.5 | Dow Technical Brochure |
| `POL-PEG-50K-2026`| Poly(ethylene glycol) 50000 | PEG_50K | polyether | 50k / 50k | 200.0 | 1.20 | 16.5 / 5.0 / 8.0 | `CCO` | 0.5 | Polymer Handbook / DSC |

---

## 4. Documentation of Database Correction (PEG 50K)

- **Affected Polymer ID**: `POL-PEG-50K-2026` (`Poly(ethylene glycol) 50000`)
- **Affected Target File**: `data/user_polymers.csv`
- **Correction Date**: August 9, 2026
- **Correction Details**:
  - `monomer_smiles`: `C=COC` $\longrightarrow$ `CCO`
  - `polymer_family`: `vinylic` $\longrightarrow$ `polyether`
- **Scientific Justification**: Poly(ethylene glycol) / Poly(ethylene oxide) is a polyether composed of repeating ethylene oxide units `-[CH2-CH2-O]-_n`. The previous entry `C=COC` represented vinyl methyl ether, which is structurally inaccurate.
- **Verification & Numerical Impact**: Re-execution of the computational screening engine confirms **zero numerical change** in TOPSIS Closeness Coefficients ($C_L$), AHP criteria weights, PCA component loadings, or Monte Carlo top-1 probabilities ($P(\text{top-1})$). Candidate selection and ranking order remain 100% invariant.

---

## 5. Definition of Literature Evidence Scoring Protocol

The Literature Evidence Score ($s_{\text{lit}} \in [0, 1]$) quantifies validated formulation precedent for stabilizing the target API in an amorphous solid dispersion:
- `1.0`: Peer-reviewed experimental literature demonstrating successful spray-drying or melt-extrusion ASD formulation of Indomethacin with physical stability $\ge 6\text{ months}$.
- `0.5`: General ASD literature precedent with structurally related APIs or general carrier application, without specific Indomethacin clinical benchmarking.
- `0.0`: Novel carrier with zero published ASD formulation precedent.

---

## 6. Known Framework Limitations & Prospective Experimental Requirements

1. **Semicrystallinity**: High MW PEG 50K exhibits thermal melting ($T_m \approx 65^\circ\text{C}$), which is evaluated under amorphous Flory-Huggins theory.
2. **Moisture Sensitivity**: $T_g$ values reflect dry state conditions. Spray-dried powders must be stored under desiccated conditions.
3. **Prospective Validation Requirement**: The computational framework provides a **computationally verified, internally reproducible screening baseline**. Final candidate validation requires prospective experimental spray-drying, powder X-ray diffraction (PXRD), differential scanning calorimetry (DSC), and dissolution testing.
