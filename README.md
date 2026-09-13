<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/brand/logo-horizontal-dark.svg">
    <img alt="PharmaPolySCOPE" src="docs/brand/logo-horizontal-light.svg" width="360">
  </picture>
  <p><em>Pharmaceutical Polymer Screening and Computational Optimization Platform</em></p>
</div>

A computational decision-support framework for rational polymer screening in amorphous solid dispersion (ASD) formulation development.

**Current Software Release**: **PharmaPolySCOPE v2.0.0**<br>
**Frozen Scientific Baseline**: **`v1.5.0-FOUR-CRITERION-FREEZE`**

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Software Release](https://img.shields.io/badge/release-v2.0.0-blue.svg)](https://github.com/Tushar-470/indomethacin-asd-framework/releases/tag/v2.0.0)
[![Scientific Baseline](https://img.shields.io/badge/baseline-v1.5.0--FOUR--CRITERION--FREEZE-green.svg)](docs/v1.5.0_frozen_computational_baseline_record.md)
[![DOI](https://img.shields.io/badge/DOI-to__be__assigned-lightgrey.svg)](#12-citation--academic-license)

> **Release Note**: PharmaPolySCOPE v2.0.0 is the current production software release, providing an extensible Variable-$K$ architecture, dynamic AHP/TOPSIS projection, Morris sensitivity analysis, and authoritative RDKit cheminformatics. The `v1.5.0-FOUR-CRITERION-FREEZE` remains the protected scientific baseline used for historical reproducibility, regression isolation, and benchmark comparisons.

---

## 1. System Identity & Architecture

| Identity Layer | Designation | Description |
| :--- | :--- | :--- |
| **Product / Framework Name** | **PharmaPolySCOPE** | Public platform identity and software suite |
| **Subtitle** | *A Four-Criterion Computational Framework for Rational Polymer Selection in Amorphous Solid Dispersions* | Descriptive scientific designation |
| **Developer** | **Developed by Tushar Mathapati** | Software architecture, computational decision framework & web platform |
| **Current Software Release** | **`v2.0.0`** | Variable-$K$ production architecture, dynamic AHP/TOPSIS, Morris sensitivity, RDKit cheminformatics |
| **Frozen Scientific Baseline** | **`v1.5.0-FOUR-CRITERION-FREEZE`** | Historical four-criterion frozen computational baseline (commit `31eee4d`) |
| **Production Python Engine** | `asd_mcda.v2` | Extensible Variable-$K$ screening, uncertainty, sensitivity, and provenance engine |
| **Historical Engine Core** | `asd_mcda` | Frozen v1.5 computational baseline engine |

---

## 2. Scientific Objective

To replace empirical trial-and-error screening cascades with an integrated, four-criterion multi-criteria decision analysis (MCDA) workflow coupled to stochastic uncertainty quantification and global parameter sensitivity analysis.

---

## 3. Current Project Lifecycle Status

> **COMPUTATIONAL SCREENING FRAMEWORK; PROSPECTIVE EXPERIMENTAL VALIDATION REQUIRED.**
>
> The computational development phase is closed and frozen. The deterministic ranking and uncertainty quantification provide model-based decision support. Laboratory spray-drying, solid-state characterization (mDSC, PXRD, FTIR), and dissolution testing represent the required prospective experimental validation phase.

---

## 4. Active Five-Polymer Candidate Library

The active candidate set comprises five compendial polymers evaluated under the PharmaPolySCOPE computational framework:

| Polymer ID | Canonical Polymer Name | Abbreviation | Polymer Family | Polymer Class | Compendial Status |
| :--- | :--- | :---: | :---: | :---: | :---: |
| `POL-001-2026` | Polyvinylpyrrolidone K30 | PVP_K30 | vinylic | neutral | FDA_IID |
| `POL-002-2026` | PVP-Vinyl Acetate 64 | PVP_VA_64 | vinylic | neutral | FDA_IID |
| `POL-005-2026` | Soluplus | SOLUPLUS | acrylic | amphiphilic | FDA_IID |
| `POL-006-2026` | Hydroxypropyl Methylcellulose E5 | HPMC_E5 | cellulosic | neutral | USP_NF |
| `POL-007-2026` | Eudragit E PO | EDR_EPO | acrylic | cationic | Ph.Eur. |

*(Note: Enteric carriers HPMCAS-L and Eudragit L100 were retired from the active immediate-release library and are preserved in `archive/historical/`)*.

---

## 5. Computational Architecture: v2 Production vs. v1.5 Baseline

PharmaPolySCOPE maintains a strict architectural separation between the **v2 production engine** (`asd_mcda.v2`) and the **frozen v1.5 baseline** (`asd_mcda`):

### 5.1 Production v2 Architecture (`asd_mcda.v2`)

The v2 production architecture is designed for multi-drug extensibility without methodology redesign:

```
[Drug Profile (RDKit Validated) + Polymer Library]
                     │
                     ▼
[1. Compatibility Evaluation across 4 Criteria]
   - Hansen Solubility Parameters (Ra, RED, s_HSP)
   - Flory–Huggins Interaction Parameter (χ via Lindvig, s_chi)
   - Gordon–Taylor Anti-Plasticization (Tg,mix via Simha–Boyer, s_GT)
   - 2D Structural Descriptors (RDKit-derived match, s_desc)
                     │
                     ▼
[2. Population Standardization (Z-score, ddof=0)]
                     │
                     ▼
[3. Dynamic Variable-K PCA (min K for ≥95% Cumulative Variance)]
   - Eigengap Stability Guardrail (Δλ > 0.05)
                     │
                     ▼
[4. Eigenspace AHP Matrix (K × K Pairwise Comparison, CR ≤ 0.10)]
                     │
                     ▼
[5. SP-PRP-TOPSIS Ranking (Projected Metric Tensor M = V_K W_K V_K^T)]
                     │
                     ▼
[6. Joint-Distribution Monte Carlo UQ (N=10,000)]
   - Replicate-Specific Re-computation: S^(b) → Z^(b) → PCA^(b) → K^(b)
   - Outputs: Rank Distribution, Top-k, P(top-1), K Distribution, Stability
                     │
                     ▼
[7. Morris Elementary Effects Global Sensitivity Analysis (r=10, p=4)]
                     │
                     ▼
[8. Cryptographic Provenance Manifest & Immutable Snapshot Output]
```

**Key Features of v2 Architecture**:
- **Dynamic PCA ($K$ is not fixed)**: Automatically selects the minimum number of principal components $K \in \{1, 2, 3, 4\}$ explaining $\ge 95\%$ of cohort variance.
- **Eigengap Guardrails**: Validates that retained components are well-separated ($\lambda_K - \lambda_{K+1} > 0.05$) to prevent subspace instability.
- **Projected Metric TOPSIS**: Computes ideal and anti-ideal Euclidean distances under the metric tensor $\mathbf{M} = \mathbf{V}_K \mathbf{W}_K \mathbf{V}_K^T$.
- **Replicate-Specific Monte Carlo**: Each perturbation sample executes its own standardization, PCA, and $K$-selection, accurately propagating dimensionality uncertainty.
- **Authoritative RDKit Integration**: Validates chemical SMILES, detects valence and stereochemical errors, calculates 2D Lipinski/Crippen descriptors, and protects against silent fallback heuristic corruption.
- **Immutable Snapshots**: Freezes caller memory buffers to guarantee zero side-effects and deterministic provenance.

---

## 6. Production v2 Screening Results

Evaluated under the v2 Variable-$K$ production screening pipeline across multiple API chemical systems:

| Drug System | Top-Ranked Candidate | TOPSIS $C_L$ | Monte Carlo $P(	ext{top-1})$ | Retained Components ($K$) | Stability Status |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Fenofibrate** (`DRG-0002`) | **Eudragit E PO** | **0.741309** | **99.77%** | $K=2$ ($96.8\%$ var) | `STABLE` |
| **Ibuprofen** (`DRG-0001`) | **Eudragit E PO** | **0.550264** | **97.87%** | $K=2$ ($97.2\%$ var) | `STABLE` |
| **Itraconazole** (`ITR-001-2026`) | **Soluplus** | **0.610306** | **59.98%** | $K=2$ ($96.0\%$ var) | `STABLE` |
| **Indomethacin** (`IND-001-2026`, v2) | **Soluplus** | **0.686435** | **43.18%** | $K=3$ ($98.3\%$ var) | `STABLE` |

> [!IMPORTANT]
> **Scientific Interpretation of Model Outputs**:
> Computational closeness coefficients ($C_L$) and Monte Carlo selection probabilities ($P(	ext{top-1})$) quantify multi-criteria model suitability under assumed parameter distributions. **They do NOT represent probabilities of physical formulation success, experimental solubility enhancement, or clinical efficacy.** Prospective laboratory validation remains mandatory.

---

## 7. Frozen Scientific Baseline (`v1.5.0-FOUR-CRITERION-FREEZE`)

The `v1.5.0-FOUR-CRITERION-FREEZE` baseline is preserved as a permanent historical benchmark for Indomethacin. It utilizes a fixed-subspace projection (Policy A, $K=2$, $100\%$ cumulative variance across 2 PCs):

### 7.1 Frozen Deterministic Ranking (v1.5 Indomethacin Baseline)

| Rank | Candidate Polymer | TOPSIS $C_L$ | Gate 1 Status | Scientific Classification |
| :---: | :--- | :---: | :---: | :--- |
| **1** | **Hydroxypropyl Methylcellulose E5** (`POL-006-2026`) | **0.835911** | **PASS** | **Top-Ranked Computational Candidate** |
| 2 | Soluplus (`POL-005-2026`) | 0.694342 | **PASS** | High-Affinity Miscibility Candidate |
| 3 | Polyvinylpyrrolidone K30 (`POL-001-2026`) | 0.549368 | **PASS** | High-Tg Alternative Candidate |
| 4 | PVP-Vinyl Acetate 64 (`POL-002-2026`) | 0.470256 | **PASS** | Intermediate Affinity Candidate |
| 5 | Eudragit E PO (`POL-007-2026`) | 0.090501 | **FAIL** | Phase-Separation Risk under Model Diagnostic |

### 7.2 Frozen Monte Carlo UQ (v1.5 Indomethacin Baseline, $N=10{,}000$, Seed = 42)

- **HPMC E5**: $P(	ext{top-1}) = \mathbf{75.54\%}$
- **Soluplus**: $P(	ext{top-1}) = \mathbf{20.18\%}$
- **PVP K30**: $P(	ext{top-1}) = \mathbf{4.03\%}$
- **PVP-VA 64**: $P(	ext{top-1}) = \mathbf{0.25\%}$
- **Eudragit E PO**: $P(	ext{top-1}) = \mathbf{0.00\%}$
- **Convergence**: Gelman–Rubin $\hat{R} = 1.0050 < 1.01$
- **Classification**: **High Model Confidence** ($P(	ext{top-1}) \ge 0.70$)

*Baseline Cryptographic Guarantee*: Exactly 71 files representing the v1.5 computational core are cryptographically locked and verified against Git commit `31eee4d` via `tests/v2/test_v15_isolation_regression.py`.

---

## 8. Physical Compatibility Diagnostics

### 8.1 Hansen Solubility Parameters (HSP)
$$R_a = \sqrt{4(\Delta\delta_D)^2 + (\Delta\delta_P)^2 + (\Delta\delta_H)^2}, \quad \text{RED} = \frac{R_a}{R_0}, \quad s_{\text{HSP}} = \max\left(0, 1 - \frac{\text{RED}}{2}\right)$$
All polymer HSP values in the active library are calculated group-contribution estimates derived via the Hoftyzer–Van Krevelen (H-V-K) method from repeat-unit monomer SMILES.

### 8.2 Flory–Huggins Interaction Parameter ($\chi$)
$$\chi = \frac{V_m}{RT}\left[0.60(\Delta\delta_D)^2 + 0.25(\Delta\delta_P)^2 + 0.25(\Delta\delta_H)^2\right], \quad s_\chi = \max(0, 1 - \chi)$$
Calculated via the Lindvig solubility parameter conversion at $T = 298.15\text{ K}$, representing theoretical enthalpy of mixing.

### 8.3 Gordon–Taylor Anti-Plasticization ($T_{g,\text{mix}}$)
$$T_{g,\text{mix}} = \frac{w_1 T_{g,1} + K_{\text{SB}} w_2 T_{g,2}}{w_1 + K_{\text{SB}} w_2}, \quad K_{\text{SB}} = \frac{\rho_1 T_{g,1}}{\rho_2 T_{g,2}}, \quad s_{\text{GT}} = \text{clip}\left(\frac{T_{g,\text{mix}} - (T_{g,\text{drug}} + 30)}{50}, 0, 1\right)$$
Predicts glass-transition elevation of the amorphous mixture (at default $w_{\text{drug}} = 0.30$) to assess kinetic crystallization inhibition.

### 8.4 2D Structural Descriptors ($s_{\text{desc}}$)
Evaluates four normalized physicochemical descriptor matches derived from RDKit:
$$s_{\text{desc}} = 0.25 \cdot \text{match}_{\text{HBD}} + 0.25 \cdot \text{match}_{\text{HBA}} + 0.25 \cdot \text{match}_{\text{TPSA}} + 0.25 \cdot \text{match}_{\text{arom}}$$

---

## 9. Installation & Quick Start

### Prerequisites
- Python $\ge 3.11$ (compatible with Python 3.11 – 3.14)
- `uv` (recommended) or `pip`

### Installation

```bash
git clone https://github.com/Tushar-470/indomethacin-asd-framework.git
cd indomethacin-asd-framework

# Install package in editable mode with development dependencies
uv pip install -e .
uv pip install -r requirements-dev.txt
```

### Run Verification Test Suites

```bash
# 1. Run the primary v2 production regression suite (116 tests)
pytest tests/v2/ -v

# 2. Run the v1.5 baseline cryptographic isolation test (4 tests)
pytest tests/v2/test_v15_isolation_regression.py -v

# 3. Run the RDKit cheminformatics integrity suite (29 tests)
pytest tests/v2/test_cheminformatics_integrity.py -v
```

*(Note: Legacy tests in `tests/unit/` and `tests/integration/` reflect the historical fixed-$K=2$ environment for Indomethacin. The official release test gate is `tests/v2/`).*

### CLI Execution

```bash
# Run v2 Variable-K screening pipeline
python -m asd_mcda.v2.cli --drug data/user_drugs/itr-001-2026.json --polymers config/polymers/polymer_library_v3_five_polymers.csv

# Run legacy v1.5 Indomethacin screening
python -m asd_mcda.cli --config config/workflow/workflow_config.yaml
```

### Local Research Dashboard

```bash
python start_app.py
```
Access the interactive web UI at `http://localhost:5173` and the OpenAPI docs at `http://localhost:8000/api/docs`.

---

## 10. Repository Map

```text
asd_framework/
├── pyproject.toml              # Package configuration declaring rdkit>=2026.3.6
├── uv.lock                     # Pinned reproducible dependency lockfile
├── README.md                   # Project overview and documentation
├── LICENSE                     # MIT Open Source License
├── CITATION.cff                # Academic citation metadata
│
├── src/asd_mcda/               # Core computational engines
│   ├── v2/                     # Production Variable-K architecture (engine, AHP, TOPSIS, UQ, sensitivity)
│   ├── compatibility/          # Physical models (HSP, Flory-Huggins, Gordon-Taylor)
│   ├── mcda/                   # Legacy MCDA implementation
│   ├── uncertainty/            # Legacy Monte Carlo UQ implementation
│   └── ...                     # Supporting modules
│
├── tests/                      # Automated test suites
│   ├── v2/                     # Official v2 regression suite (116 tests)
│   ├── unit/                   # Unit test fixtures
│   └── integration/            # End-to-end integration fixtures
│
├── results/                    # Screening reports and datasets
│   ├── v2/                     # Authoritative v2 multi-drug screening results & reports
│   │   ├── fenofibrate/        # Fenofibrate screening outputs, UQ, and sensitivity data
│   │   ├── itraconazole/       # Itraconazole screening outputs, UQ, and sensitivity data
│   │   └── tables/             # Cross-cohort structured datasets (Ibuprofen, Indomethacin)
│   └── final/                  # Frozen v1.5 Indomethacin baseline artifacts
│
├── config/                     # Configuration inputs
│   ├── polymers/               # 5-polymer compendial library v3
│   ├── drugs/                  # Model drug profiles (Indomethacin)
│   └── workflow/               # Orchestration workflow configs
│
├── data/                       # Curated data profiles
│   └── user_drugs/             # Validated drug profiles (itr-001-2026.json)
│
├── backend/                    # FastAPI REST application
├── frontend/                   # React 18 + Vite interactive dashboard
└── docs/                       # Comprehensive documentation suite
```

---

## 11. Methodological Boundaries & Limitations

1. **Calculated HSP Input**: Polymer HSP values are Hoftyzer–Van Krevelen group-contribution predictions, not direct experimental solubility spheres. A documented polar overestimation bias exists ($\delta_D +2.37$, $\delta_H +3.98\text{ MPa}^{0.5}$).
2. **Enthalpy Approximation**: Flory–Huggins $\chi$ uses Lindvig HSP conversion rather than experimental melting-point depression DSC.
3. **Uncertainty Assumption Scope**: Monte Carlo perturbation distributions reflect assumed literature ranges rather than experimentally determined error covariance matrices.
4. **Pre-Laboratory Nature**: All computational outputs represent thermodynamic and kinetic **pre-laboratory predictions** intended to prioritize candidates, not guaranteed formulation outcomes.
5. **Failure Boundary Mapping Out of Scope**: Failure Boundary Mapping (FBM) is outside the validated v2.0.0 computational screening scope. The platform does not predict manufacturing process failure, define experimentally validated failure boundaries, or generate process design spaces; prospective experimental formulation and process data are required for downstream manufacturing modeling.

*For full technical details, see [`docs/limitations.md`](docs/limitations.md).*

---

## 12. Citation & Academic License

**PharmaPolySCOPE** was developed by **Tushar Mathapati**.

Distributed under the MIT Open Source License. See [`LICENSE`](LICENSE) for terms.

```bibtex
@software{pharmapolyscope_2026,
  title={PharmaPolySCOPE: Pharmaceutical Polymer Screening and Computational Optimization Platform},
  author={Mathapati, Tushar},
  year={2026},
  version={2.0.0},
  url={https://github.com/Tushar-470/indomethacin-asd-framework},
  note={DOI: to be assigned}
}
```
