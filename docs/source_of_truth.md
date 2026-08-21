# Source of Truth — Authoritative File Map

**Release**: v1.3.1-FREEZE  
**Git Commit**: 2220c44  
**Date**: August 2026  
**Status**: FROZEN COMPUTATIONAL BASELINE  

---

This document establishes the single, unambiguous authoritative file mapping for every scientific object in the active computational baseline.

## Authoritative File Map

| Scientific Object | Authoritative File | Version | Source | Generating Code | Status |
| :--- | :--- | :---: | :--- | :--- | :---: |
| **Final Polymer Library** | `config/polymers/polymer_library_v3_five_polymers.csv` | v3 (5 polymers) | Curated supplier CoA + H-V-K group contribution | Manual curation / Verification | **FROZEN** |
| **Final Workflow Configuration** | `config/workflow/workflow_config.yaml` | v1.0.0 | Master Research Framework V2.0 | Framework configuration | **FROZEN** |
| **Final Drug Profile (Indomethacin)** | `config/drugs/indomethacin.json` | IND-001-2026 | Hancock et al. (*J. Pharm. Sci.* 2007) | Literature curation | **FROZEN** |
| **Final AHP Matrices** | `config/ahp/default_matrix.json` | DEFAULT_AHP_V2 | Expert consensus pairwise comparisons | Multi-expert elicitation | **FROZEN** |
| **Final HSP Calculation Inputs** | `config/polymers/polymer_library_v3_five_polymers.csv` | H-V-K Group Contribution | Hoftyzer–Van Krevelen method | `src/asd_mcda/compatibility/hsp_model.py` | **FROZEN** |
| **Final Compatibility Score Matrix** | `results/final/final_score_matrix.csv` | v1.3.1-FREEZE | Computational engine | `src/asd_mcda/compatibility/matrix.py` | **FROZEN** |
| **Final Polymer Ranking** | `results/final/final_polymer_ranking.csv` | v1.3.1-FREEZE | Computational engine (PCA-AHP-TOPSIS) | `src/asd_mcda/mcda/topsis.py` | **FROZEN** |
| **Final Monte Carlo UQ Results** | `results/final/final_monte_carlo_summary.json` | v1.3.1-FREEZE | Stochastic simulation ($N=10,000$, seed=42) | `src/asd_mcda/uncertainty/monte_carlo.py` | **FROZEN** |
| **Final Computational Decision Report** | `results/final/final_computational_report.md` | v1.3.1-FREEZE | Synthesized decision artifact | Pipeline output | **FROZEN** |
| **Frozen Baseline Record** | `results/reports/v1.3.1_freeze_baseline_record.json` | v1.3.1-FREEZE | Export script | Frozen baseline lock | **FROZEN** |
| **Reproduction Environment** | `pyproject.toml`, `requirements.txt` | Python $\ge 3.11$ | Dependency specification | Package config | **FROZEN** |

---

## Active Polymer Library Integrity

- **Filename**: `config/polymers/polymer_library_v3_five_polymers.csv`
- **SHA-256 Checksum**: `24cd6c4092788cb7266d2ea34e82b6dfe193b5cfb91e22c0dff66b0abc9088ff`
- **Candidate Count**: Exactly 5 polymers

| Polymer ID | Canonical Name | Abbreviation | Polymer Family | Polymer Class | Regulatory Status |
| :--- | :--- | :---: | :---: | :---: | :---: |
| `POL-001-2026` | Polyvinylpyrrolidone K30 | PVP_K30 | vinylic | neutral | FDA_IID |
| `POL-002-2026` | PVP-Vinyl Acetate 64 | PVP_VA_64 | vinylic | neutral | FDA_IID |
| `POL-005-2026` | Soluplus | SOLUPLUS | acrylic | amphiphilic | FDA_IID |
| `POL-006-2026` | Hydroxypropyl Methylcellulose E5 | HPMC_E5 | cellulosic | neutral | USP_NF |
| `POL-007-2026` | Eudragit E PO | EDR_EPO | acrylic | cationic | Ph.Eur. |

---

## Excluded Historical Candidates

| Polymer ID | Canonical Name | Status | Justification |
| :--- | :--- | :---: | :--- |
| `POL-003-2026` | HPMCAS-L | EXCLUDED | Retired from 6-polymer screening; preserved in `archive/historical/` |
| `POL-004-2026` | Eudragit L100 | EXCLUDED | Retired from 6-polymer screening; preserved in `archive/historical/` |
