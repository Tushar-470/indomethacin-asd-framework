# Changelog

All notable computational and architectural milestones for the ASD Computational Polymer Screening Framework are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [v1.3.1-FREEZE] — August 2026

**Status**: FROZEN COMPUTATIONAL BASELINE; PRE-EXPERIMENTATION

### Final Baseline Architecture
- **Active Polymer Library**: Frozen 5-polymer candidate library (`config/polymers/polymer_library_v3_five_polymers.csv`, SHA-256: `24cd6c4092788cb7266d2ea34e82b6dfe193b5cfb91e22c0dff66b0abc9088ff`).
- **Deterministic Ranking**:
  1. Soluplus ($C_L = 0.736338$) — Top-Ranked Computational Candidate
  2. Hydroxypropyl Methylcellulose E5 ($C_L = 0.684063$)
  3. PVP-Vinyl Acetate 64 ($C_L = 0.504982$)
  4. Polyvinylpyrrolidone K30 ($C_L = 0.442917$)
  5. Eudragit E PO ($C_L = 0.000000$)
- **Monte Carlo Uncertainty Quantification ($N=10{,}000$, seed=42)**:
  - Soluplus: $P(\text{top-1}) = 43.2\%$
  - HPMC E5: $P(\text{top-1}) = 31.0\%$
  - PVP K30: $P(\text{top-1}) = 14.4\%$
  - PVP-VA 64: $P(\text{top-1}) = 5.8\%$
  - Eudragit E PO: $P(\text{top-1}) = 5.6\%$
  - Confidence Tier: Moderate Confidence ($0.40 \le P(\text{top-1}) < 0.70$).
- **Physics Engine**:
  - H-V-K group contribution for polymer HSP.
  - Lindvig conversion for Flory–Huggins $\chi$.
  - Simha–Boyer $K$ and Gordon–Taylor for composite $T_{g,\text{mix}}$.
  - PCA pre-processing ($k=2$ retained components, $95\%$ cumulative variance threshold).
  - AHP geometric-mean weight elicitation and TOPSIS closeness coefficient ($C_L$).

### Repository Curation
- Moved legacy and superseded development scripts to `archive/development/`.
- Moved legacy 6-polymer library and historical documentation to `archive/historical/`.
- Moved superseded decision reports to `archive/superseded/`.
- Created authoritative `results/final/` baseline artifact directory.
- Created complete documentation suite (`source_of_truth.md`, `computational_method.md`, `data_provenance.md`, `data_dictionary.md`, `study_overview.md`, `reproducibility.md`, `limitations.md`, `repository_map.md`).
- Added automated dataset integrity validator `scripts/validate_final_dataset.py`.

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
