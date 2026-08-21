# Computational Polymer Screening Framework for Indomethacin SD-ASDs (`asd_mcda`)

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Baseline Release](https://img.shields.io/badge/release-v1.3.1--FREEZE-green.svg)](FINAL_COMPUTATIONAL_BASELINE_MANIFEST.yaml)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.1234567.svg)](https://doi.org/10.5281/zenodo.1234567)

---

## 1. Project Title & Overview

**Quality by Design–Driven Development of Indomethacin Immediate-Release Tablets from Spray-Dried Amorphous Solid Dispersions: A Computational–Experimental Framework for Polymer Selection, Predictive Formulation Design, and Failure Boundary Mapping**

The `asd_mcda` package provides a rigorous, reproducible, open-source computational decision framework for rational polymeric carrier selection in spray-dried amorphous solid dispersions (SD-ASDs), demonstrated using indomethacin (BCS Class II) as a model drug.

---

## 2. Scientific Objective

To replace empirical trial-and-error screening cascades with an integrated, multi-physics, multi-criteria decision analysis (MCDA) workflow coupled to stochastic uncertainty quantification and failure boundary mapping.

---

## 3. Current Project Lifecycle Status

> **COMPUTATIONAL BASELINE FROZEN; PROSPECTIVE EXPERIMENTAL VALIDATION PENDING.**
>
> The computational development phase is complete. The deterministic five-polymer ranking and Monte Carlo uncertainty quantification are **frozen at release `v1.3.1-FREEZE` (Git commit: `2220c44`)**. Laboratory spray-drying, solid-state characterization (mDSC, PXRD, FTIR), and dissolution testing represent the prospective experimental phase.

---

## 4. Active Five-Polymer Candidate Library

The active candidate set comprises five compendial polymers evaluated under the Master Research Framework V2.0:

| Polymer ID | Canonical Polymer Name | Abbreviation | Polymer Family | Polymer Class | Compendial Status |
| :--- | :--- | :---: | :---: | :---: | :---: |
| `POL-001-2026` | Polyvinylpyrrolidone K30 | PVP_K30 | vinylic | neutral | FDA_IID |
| `POL-002-2026` | PVP-Vinyl Acetate 64 | PVP_VA_64 | vinylic | neutral | FDA_IID |
| `POL-005-2026` | Soluplus | SOLUPLUS | acrylic | amphiphilic | FDA_IID |
| `POL-006-2026` | Hydroxypropyl Methylcellulose E5 | HPMC_E5 | cellulosic | neutral | USP_NF |
| `POL-007-2026` | Eudragit E PO | EDR_EPO | acrylic | cationic | Ph.Eur. |

*(Note: Enteric carriers HPMCAS-L and Eudragit L100 were retired from the active immediate-release library and are preserved in `archive/historical/`)*.

---

## 5. Computational Workflow Architecture

The computational screening engine integrates an 11-step pipeline:

```
[Drug Profile + Polymer Library]
              │
              ▼
[1. Hansen Solubility Parameters (Ra, RED, s_HSP)]
[2. Flory–Huggins Interaction Parameter (χ via Lindvig, s_chi)]
[3. Gordon–Taylor Anti-Plasticization (Tg,mix via Simha–Boyer, s_GT)]
              │
              ▼
[4. Active Compatibility Score Matrix S_active]
              │
              ▼
[5. Principal Component Analysis (PCA, 95% Variance Retention)]
              │
              ▼
[6. Multi-Expert Analytic Hierarchy Process (AHP Eigenvector)]
              │
              ▼
[7. TOPSIS Multi-Criteria Decision Ranking (Closeness Coefficient CL)]
              │
              ▼
[8. Joint-Distribution Monte Carlo Uncertainty Quantification (N=10,000)]
              │
              ▼
[9. Morris Elementary Effects Global Sensitivity Analysis]
[10. Logistic Failure Boundary Mapping (FBM)]
[11. Publication-Ready Report & Figure Generation (300 DPI)]
```

---

## 6. Frozen Deterministic Ranking Results (v1.4.0-CORRECTED-FREEZE)

| Rank | Candidate Polymer | TOPSIS $C_L$ | Scientific Classification |
| :---: | :--- | :---: | :--- |
| **1** | **Hydroxypropyl Methylcellulose E5** (`POL-006-2026`) | **0.835911** | **Top-Ranked Computational Candidate** |
| 2 | Soluplus (`POL-005-2026`) | 0.694342 | High-Affinity Miscibility Candidate |
| 3 | Polyvinylpyrrolidone K30 (`POL-001-2026`) | 0.549368 | High-Tg Alternative Candidate |
| 4 | PVP-Vinyl Acetate 64 (`POL-002-2026`) | 0.470256 | Intermediate Affinity Candidate |
| 5 | Eudragit E PO (`POL-007-2026`) | 0.090501 | Boundary Anti-Ideal Candidate |

---

## 7. Monte Carlo Top-1 Selection Probabilities ($N=10{,}000$, Seed = 42)

Simultaneous joint perturbation of 7 input parameters (HSP $\pm 1.5\text{ MPa}^{0.5}$, $\chi \pm 25\%$, $\text{Log}P \pm 0.7$, $T_{g,\text{drug}} \pm 10\text{ K}$, $T_{g,\text{poly}} \pm 3\text{ K}$, density $\pm 0.05\text{ g/cm}^3$, AHP weights $\pm 20\%$) yields:

- **HPMC E5**: $P(\text{top-1}) = \mathbf{42.4\%}$
- **Soluplus**: $P(\text{top-1}) = \mathbf{35.0\%}$
- **PVP K30**: $P(\text{top-1}) = \mathbf{13.3\%}$
- **Eudragit E PO**: $P(\text{top-1}) = \mathbf{6.1\%}$
- **PVP-VA 64**: $P(\text{top-1}) = \mathbf{3.2\%}$
- **Confidence Classification**: **Moderate Confidence** ($0.40 \le P(\text{top-1}) < 0.70$)

---

## 8. Scientific Interpretation of Probabilities

- **HPMC E5** is the **top-ranked computational candidate** ($C_L = 0.8359, P(\text{top-1}) = 42.4\%$), combining favorable enthalpy of mixing ($\chi = 0.2598$) with superior glass transition anti-plasticization ($T_{g,\text{mix}} = 404.9\text{ K}, s_{\text{GT}} = 0.9731$).
- **Soluplus** is the **second-ranked candidate** ($C_L = 0.6943, P(\text{top-1}) = 35.0\%$), exhibiting the highest individual cohesive energy matching ($s_{\text{HSP}} = 0.7972, s_\chi = 0.8261$) but lower $T_g$ elevation ($T_{g,\text{mix}} = 334.5\text{ K}$).
- **Monte Carlo Top-1 Selection Probability** represents computational model stability under assumed input parameter uncertainty; it is **NOT** a probability of clinical or experimental manufacturing success.


---

## 9. Hansen Solubility Parameter (HSP) Provenance

All polymer HSP values in the active library are **calculated group-contribution estimates** derived via the Hoftyzer–Van Krevelen (H-V-K) method from repeat-unit monomer SMILES. An external calibration against experimental polymer solubility spheres ($n=10$, Osakwe & Le, *ACS Omega* 2026) revealed a systematic polar overestimation bias ($\delta_D$ bias: $+2.37\text{ MPa}^{0.5}$, $\delta_H$ bias: $+3.98\text{ MPa}^{0.5}$). This is documented as a known methodological boundary (see [`docs/limitations.md`](docs/limitations.md)).

---

## 10. Flory–Huggins Interaction Parameter ($\chi$) Methodology

The Flory–Huggins interaction parameter $\chi$ is calculated via the **Lindvig solubility parameter conversion** ($0.60\,\Delta\delta_D^2 + 0.25\,\Delta\delta_P^2 + 0.25\,\Delta\delta_H^2$) at $T = 298.15\text{ K}$, representing theoretical enthalpy of mixing prior to experimental melting-point depression verification.

---

## 11. Quick Start & Reproduction

### Installation

```bash
git clone https://github.com/Tushar-470/indomethacin-asd-framework.git
cd indomethacin-asd-framework
pip install -e .
pip install -r requirements-dev.txt
```

### Dataset Integrity Check

```bash
python scripts/validate_final_dataset.py
```

### Run Test Suite

```bash
pytest tests/
```

### CLI Execution

```bash
python -m asd_mcda.cli --config config/workflow/workflow_config.yaml
```

### Local Web Application Dashboard

```bash
python start_app.py
```

Access at `http://localhost:5173` (UI) and `http://localhost:8000/api/docs` (API).

---

## 12. Repository Architectural Structure

```
asd_framework/
├── config/             # Authoritative configuration inputs (5-polymer library v3, indomethacin.json, AHP)
├── src/asd_mcda/       # Frozen core computational engine (physics, MCDA, PCA, UQ, reporting)
├── results/final/      # Authoritative frozen outputs (ranking CSV, score matrix, Monte Carlo summary)
├── results/figures/    # Generated publication-quality 300 DPI figures
├── scripts/            # Dataset integrity validator (validate_final_dataset.py)
├── tests/              # Automated test suite (unit, integration, API regression)
├── backend/            # FastAPI REST application
├── frontend/           # React 18 + Vite local dashboard
├── docs/               # Full documentation suite (source of truth, methods, provenance, limitations)
└── archive/            # Preserved research history (historical baselines, superseded reports, audit scripts)
```

---

## 13. Methodological Limitations

1. Polymer HSP values are H-V-K group-contribution predictions, not direct experimental solubility spheres.
2. Flory–Huggins $\chi$ uses Lindvig HSP conversion rather than experimental melting-point depression DSC.
3. Monte Carlo uncertainty distributions reflect assumed literature ranges rather than empirically measured error covariances.
4. All computational outputs represent **pre-laboratory predictions** requiring prospective physical validation.

*For full technical details, see [`docs/limitations.md`](docs/limitations.md).*

---

## 14. Citation & Academic License

Distributed under the MIT Open Source License. See [`LICENSE`](LICENSE) for terms.

```bibtex
@article{indomethacin_asd_mcda_2026,
  title={Quality by Design--Driven Development of Indomethacin Immediate-Release Tablets from Spray-Dried Amorphous Solid Dispersions: A Computational--Experimental Framework for Polymer Selection, Predictive Formulation Design, and Failure Boundary Mapping},
  author={Computational Pharmaceutics Research Consortium},
  year={2026},
  doi={10.5281/zenodo.1234567}
}
```
