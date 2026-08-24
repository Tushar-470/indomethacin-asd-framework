# Source of Truth — Authoritative File Map

**Platform**: PharmaPolySCOPE (Pharmaceutical Polymer Screening and Computational Optimization Platform)  
**Scientific Baseline**: `v1.5.0-FOUR-CRITERION-FREEZE`  
**Developer Attribution**: Developed by Tushar Mathapati  
**Date**: August 2026  
**Status**: COMPUTATIONAL PHASE CLOSED & FROZEN  

---

This document establishes the single, unambiguous authoritative file mapping for every scientific object in the active computational baseline.

## Authoritative File Map

| Scientific Object | Authoritative File | Version / Baseline | Generating Module / Source | Computational Status |
| :--- | :--- | :---: | :--- | :---: |
| **Model Drug Profile (Indomethacin)** | `config/drugs/indomethacin.json` | IND-001-2026 | Hancock et al. (*J. Pharm. Sci.* 2007) / Curated | **FROZEN** |
| **Active Polymer Library (5 Candidates)** | `config/polymers/polymer_library_v3_five_polymers.csv` | v3 (5 polymers) | Curated supplier CoA + H-V-K group contribution | **FROZEN** |
| **Workflow Configuration** | `config/workflow/workflow_config.yaml` | v1.0.0 | Master Research Framework V2.0 | **FROZEN** |
| **AHP Expert Matrix** | `config/ahp/default_matrix.json` | DEFAULT_AHP_V2 | Expert consensus pairwise comparisons (PC1:PC2 = 2:1) | **FROZEN** |
| **Polymer HSP Inputs** | `config/polymers/polymer_library_v3_five_polymers.csv` | H-V-K Calculated | Hoftyzer–Van Krevelen method | **FROZEN** |
| **Compatibility Score Matrix ($\mathbf{S}$)** | `results/final/final_score_matrix.csv` | `v1.5.0-FOUR-CRITERION-FREEZE` | `src/asd_mcda/compatibility/matrix.py` | **FROZEN** |
| **Polymer Ranking Table** | `results/final/final_polymer_ranking.csv` | `v1.5.0-FOUR-CRITERION-FREEZE` | `src/asd_mcda/mcda/topsis.py` | **FROZEN** |
| **Monte Carlo UQ Summary** | `results/final/final_monte_carlo_summary.json` | `v1.5.0-FOUR-CRITERION-FREEZE` | `src/asd_mcda/uncertainty/monte_carlo.py` ($N=10\text{k}$, seed=42) | **FROZEN** |
| **Frozen Baseline Record (JSON)** | `results/reports/v1.5.0_freeze_baseline_record.json` | `v1.5.0-FOUR-CRITERION-FREEZE` | `results/final/final_baseline_record.json` | **FROZEN** |
| **Frozen Baseline Record (Doc)** | `docs/v1.5.0_frozen_computational_baseline_record.md` | `v1.5.0-FOUR-CRITERION-FREEZE` | Research documentation record | **FROZEN** |
| **Baseline Release Manifest** | `FINAL_COMPUTATIONAL_BASELINE_MANIFEST.yaml` | `v1.5.0-FOUR-CRITERION-FREEZE` | Framework release manifest | **FROZEN** |
| **Full PDF Screening Report** | `backend/services/pdf_report_generator.py` | `v1.5.0-FOUR-CRITERION-FREEZE` | Dynamic 14-page ReportLab PDF export generator | **FROZEN** |
| **Automated Test Suite** | `tests/` (76 test functions) | pytest $\ge 9.0$ | Automated integrity, unit, integration & web tests | **FROZEN** |
| **Reproduction Environment** | `pyproject.toml`, `requirements.txt` | Python $\ge 3.11$ | Framework dependency specification | **FROZEN** |

---

## Active Polymer Library Integrity

- **Filename**: `config/polymers/polymer_library_v3_five_polymers.csv`
- **SHA-256 Checksum**: `5497d606b64e081cac0274e4f5db8343c012fd84191b5ec413990614717c3ac2`
- **Candidate Count**: Exactly 5 polymers

| Polymer ID | Canonical Name | Abbreviation | Polymer Family | Polymer Class | Compendial Status |
| :--- | :--- | :---: | :---: | :---: | :---: |
| `POL-001-2026` | Polyvinylpyrrolidone K30 | PVP_K30 | vinylic | neutral | FDA_IID |
| `POL-002-2026` | PVP-Vinyl Acetate 64 | PVP_VA_64 | vinylic | neutral | FDA_IID |
| `POL-005-2026` | Soluplus | SOLUPLUS | acrylic | amphiphilic | FDA_IID |
| `POL-006-2026` | Hydroxypropyl Methylcellulose E5 | HPMC_E5 | cellulosic | neutral | USP_NF |
| `POL-007-2026` | Eudragit E PO | EDR_EPO | acrylic | cationic | Ph.Eur. |

---

## Excluded Historical Candidates

| Polymer ID | Canonical Name | Historical Status | Archival Location & Justification |
| :--- | :--- | :---: | :--- |
| `POL-003-2026` | HPMCAS-L | EXCLUDED | Retired from 6-polymer screening; preserved in `archive/historical/` |
| `POL-004-2026` | Eudragit L100 | EXCLUDED | Retired from 6-polymer screening; preserved in `archive/historical/` |

---

## Historical vs. Active Version Lineage

| Version / Release | Decision Criteria ($\mathbf{S}$) | Candidate Library | Status | Key Distinction |
| :--- | :--- | :--- | :---: | :--- |
| **v1.0 – v1.2** | 3–5 criteria | 6 polymers | HISTORICAL | Early development prototypes |
| **v1.3.1-FREEZE** | 5 criteria ($s_{\text{HSP}}, s_\chi, s_{\text{desc}}, s_{\text{GT}}, s_{\text{lit}}$) | 5 polymers | HISTORICAL | Included uncalibrated $T_m$ and legacy $s_{\text{lit}}$ |
| **v1.4.0-CORRECTED-FREEZE** | 5 criteria ($s_{\text{HSP}}, s_\chi, s_{\text{desc}}, s_{\text{GT}}, s_{\text{lit}}$) | 5 polymers | HISTORICAL | Corrected $T_m = 433.15\text{ K}$ and Lindvig scaling |
| **v1.5.0-FOUR-CRITERION-FREEZE** | **4 criteria ($s_{\text{HSP}}, s_\chi, s_{\text{desc}}, s_{\text{GT}}$)** | **5 polymers** | **AUTHORITATIVE ACTIVE** | **$s_{\text{lit}}$ removed from MCDA; Policy A fixed-subspace UQ** |
