# Changelog

All notable computational and architectural milestones for **PharmaPolySCOPE** (formerly ASD MCDA Framework) are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [v1.5.0-FOUR-CRITERION-FREEZE] — August 2026

**Platform**: PharmaPolySCOPE (Pharmaceutical Polymer Screening and Computational Optimization Platform)  
**Developer**: Developed by Tushar Mathapati  
**Status**: COMPUTATIONAL PHASE CLOSED & FROZEN; PRE-EXPERIMENTATION  

### Four-Criterion Framework Baseline
- **Permanent Removal of $s_{\text{lit}}$**: The subjective Literature Evidence Score ($s_{\text{lit}}$) was permanently removed from active multi-criteria decision ranking $\mathbf{S} = [s_{\text{HSP}}, s_\chi, s_{\text{desc}}, s_{\text{GT}}]$. Literature citations and supplier quality grades are preserved strictly as provenance metadata.
- **Policy A Subspace Projection**: Established fixed baseline PCA decision subspace projection for Monte Carlo uncertainty quantification ($N=10,000$, seed=42) and global sensitivity analysis.
- **Orthogonal Variance Distribution**:
  - Retained Principal Components: $K=2$ ($100.0\%$ cumulative explained variance).
  - PC1 ($67.2\%$ variance): Thermodynamic interaction affinity ($s_\chi, s_{\text{HSP}}$).
  - PC2 ($32.8\%$ variance): Gordon–Taylor thermal anti-plasticization ($s_{\text{GT}}$).
- **Authoritative Frozen Five-Polymer Ranking**:
  1. **Hydroxypropyl Methylcellulose E5** (`POL-006-2026`): $C_L = 0.835911$, $P(\text{top-1}) = 75.54\%$ (High model-selection robustness).
  2. **Soluplus** (`POL-005-2026`): $C_L = 0.694342$, $P(\text{top-1}) = 20.18\%$.
  3. **Polyvinylpyrrolidone K30** (`POL-001-2026`): $C_L = 0.549368$, $P(\text{top-1}) = 4.03\%$.
  4. **PVP-Vinyl Acetate 64** (`POL-002-2026`): $C_L = 0.470256$, $P(\text{top-1}) = 0.25\%$.
  5. **Eudragit E PO** (`POL-007-2026`): $C_L = 0.090501$, $P(\text{top-1}) = 0.00\%$.
- **Full Screening Technical PDF Report**:
  - Publication-ready 14-page PDF generator dynamically bound to execution snapshots.
  - Section-numbered layout mirroring the 7 analytical views of the platform.
  - Strict candidate isolation and un-truncated configuration provenance dumps.
  - Aligned Lattice Lens brand lockup.
- **Software Suite & UI**:
  - React 18 + TypeScript + Vite interactive research dashboard with 0 build errors.
  - Full candidate isolation between exploratory and research runs.
  - Comprehensive 76-test automated verification suite (100% pass rate).

---

## [v1.4.0-CORRECTED-FREEZE] — August 2026

**Status**: HISTORICAL FROZEN BASELINE (Superseded by v1.5.0)

### Physics Engine Corrections
- **Indomethacin Melting Point Correction**: Updated $T_m$ from preliminary estimate ($424.15\text{ K}$) to experimental DSC exact value ($433.15\text{ K } / 160.0^\circ\text{C}$; Hancock et al., 2007).
- **Flory–Huggins Lindvig Scaling Calibration**: Calibrated global Lindvig factor $\alpha = 0.60$ and standardized $\chi_c$ calculation on number-average molecular weight ($M_n$).
- **Canonical AHP Eigenvector Priority**: Standardized AHP pairwise comparison matrix on $[PC_1:PC_2 = 2:1]$ with $\text{CR} = 0.000$.

---

## [v1.3.1-FREEZE] — August 2026

**Status**: HISTORICAL BASELINE (Superseded by v1.4.0)

### Final Baseline Architecture
- **Active Polymer Library**: Frozen 5-polymer candidate library (`config/polymers/polymer_library_v3_five_polymers.csv`, SHA-256: `24cd6c4092788cb7266d2ea34e82b6dfe193b5cfb91e22c0dff66b0abc9088ff`).
- **Physics Engine**: H-V-K group contribution for polymer HSP, Lindvig conversion for $\chi$, Simha–Boyer Gordon–Taylor $T_{g,\text{mix}}$.
- **Repository Curation**: Legacy scripts archived to `archive/development/`; superseded outputs moved to `archive/superseded/`.

---

## [v1.3.0] — August 2026

### Added
- Addition of compendial cationic carrier Eudragit E PO (`POL-007-2026`).
- Transition from 6-polymer library to active 5-polymer screening set.

### Changed
- Excluded enteric carriers HPMCAS-L (`POL-003-2026`) and Eudragit L100 (`POL-004-2026`) for prospective immediate-release tablet scope.

---

## [v1.2.0] — August 2026

### Added
- Multi-criteria decision analysis engine linking AHP and TOPSIS.
- Initial PCA pre-processing module for collinearity attenuation.

---

## [v1.1.0] — August 2026

### Added
- Core physics compatibility models: Hansen Solubility Parameters, Flory–Huggins $\chi$, Gordon–Taylor $T_g$.
- Preliminary 6-polymer library.
- Initial automated testing suite (36 tests).

---

## [v1.0.0] — August 2026

### Initial Release
- Project inception for computational screening of ASD polymer carriers for indomethacin.
