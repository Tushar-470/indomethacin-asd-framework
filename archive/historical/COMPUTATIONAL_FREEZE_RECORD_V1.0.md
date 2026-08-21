# Computational Freeze Record

**Project**: Indomethacin Amorphous Solid Dispersion (ASD) Computational Polymer Screening Framework  
**Master Research Framework**: V2.0  
**Software System**: `asd_mcda`  
**Software Release**: `v1.1.0`  
**Status**: FROZEN COMPUTATIONAL BASELINE  
**Freeze Date**: August 9, 2026  

---

## 1. System & Execution Environment

- **Operating System**: Windows 11 / Windows Server (x86_64)
- **Python Version**: Python 3.14.5 (64-bit)
- **Pytest Version**: 9.1.1 (pluggy 1.6.0)
- **Web Application Stack**: FastAPI 0.115+ (Uvicorn), React 18 (TypeScript + Vite)
- **Core Computational Libraries**: NumPy, Pandas, SciPy, Scikit-learn, OpenPyXL, Recharts

---

## 2. Computational Run Parameters & Random Seeds

- **Target Drug API**: `IND-001-2026` (`Indomethacin`)
- **Default Drug Loading**: $30\text{ wt}\%$ ($0.30$)
- **Monte Carlo Iterations**: $N = 1000$
- **Monte Carlo Random Seed**: `42`
- **Criteria Score Noise Level**: $\sigma = 0.05$ (Gaussian)
- **AHP Weight Noise Level**: $\pm 20\%$ (Uniform Perturbation)

---

## 3. Version Control & Release Hashes

- **Git Commit Hash**: `1dc14ba` (feature/web-interface)
- **Git Release Tag**: `v1.1.0`
- **Release Name**: `v1.1.0 - Final Validated Computational Baseline`
- **Indomethacin Config Hash**: `config/drugs/indomethacin.json` (SHA256)
- **Polymer Library Config Hash**: `config/polymers/polymer_library_v2.csv` (SHA256)
- **User Polymer CSV Hash**: `data/user_polymers.csv` (SHA256)

---

## 4. Frozen Numerical Invariants (6-Polymer Baseline)

The following computational outputs represent locked numerical invariants for the 6-polymer reference screening analysis (`IND-001-2026` + reference polymer library):

| Rank | Candidate Polymer Name | Polymer ID | TOPSIS $C_L$ | Monte Carlo $P(\text{top-1})$ | Retained PCA Components ($k$) |
| :---: | :--- | :---: | :---: | :---: | :---: |
| **1** | **Soluplus** | `POL-005-2026` | **0.777582** | **33.60%** (0.3360) | **k = 3** |
| **2** | **HPMC Acetate Succinate Low** | `POL-003-2026` | **0.734689** | **24.00%** (0.2400) | **k = 3** |
| **3** | **PVP-Vinyl Acetate 64** | `POL-002-2026` | **0.628814** | **18.50%** (0.1850) | **k = 3** |
| **4** | **Polyvinylpyrrolidone K30** | `POL-001-2026` | **0.514201** | **12.10%** (0.1210) | **k = 3** |
| **5** | **Eudragit L100** | `POL-004-2026` | **0.421580** | **7.80%** (0.0780) | **k = 3** |
| **6** | **Hydroxypropyl Methylcellulose E5** | `POL-006-2026` | **0.310245** | **4.00%** (0.0400) | **k = 3** |

---

## 5. Formal Freeze Declaration

This repository baseline `v1.1.0` is officially designated as a **FROZEN COMPUTATIONAL BASELINE**. No further modifications to mathematical equations, decision weights, PCA preprocessors, TOPSIS distance metrics, or input property values are permitted without a major version revision (`v2.0.0`).
