# Computational Polymer Screening Framework (`asd_mcda`)

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Build Status](https://github.com/pharmaceutics/asd_mcda/workflows/CI/badge.svg)](https://github.com/pharmaceutics/asd_mcda/actions)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.1234567.svg)](https://doi.org/10.5281/zenodo.1234567)

Production-quality, open-source Python computational framework for rational polymer selection and Quality by Design (QbD)–driven formulation development of spray-dried amorphous solid dispersions (SD-ASDs), demonstrated with indomethacin as a BCS Class II model drug.

---

## 📌 Executive Summary

The selection of polymer carriers for amorphous solid dispersions has traditionally relied on empirical trial-and-error screening cascades. The `asd_mcda` package operationalizes the **Master Research Framework Version 2.0 (Frozen)**, integrating:

1. **Hansen Solubility Parameters (HSP)** distance ($R_a$) and Relative Energy Difference (RED)
2. **Flory-Huggins Enthalpy of Mixing** ($\chi$) via Lindvig conversion
3. **Gordon-Taylor Glass Transition Temperature** ($T_{g,\text{mix}}$) with Simha-Boyer $K$
4. **2D RDKit Structural Descriptors** ($s_{\text{desc}}$)
5. **Mandatory Principal Component Analysis (PCA)** pre-processing (Equation 10, revised)
6. **Multi-Expert Analytic Hierarchy Process (AHP)** weight derivation with geometric-mean aggregation and Kendall's $W$ concordance
7. **Technique for Order Preference by Similarity to Ideal Solution (TOPSIS)** ranking
8. **Joint-Distribution Monte Carlo Uncertainty Quantification ($N=10,000$)**
9. **Morris Elementary Effects Sensitivity Analysis** ($\mu$ vs $\sigma$)
10. **Logistic-Regression Failure Boundary Map (FBM)** with bootstrap 95% confidence intervals

---

## 🚀 Quick Start

### 1. Installation

Clone the repository and install in editable mode:

```bash
git clone https://github.com/pharmaceutics/asd_mcda.git
cd asd_mcda
pip install -e .
```

For developer & testing dependencies:

```bash
pip install -r requirements-dev.txt
```

### 2. Execution

Run the complete 11-step computational pipeline from the command line:

```bash
python -m asd_mcda.cli --config config/workflow/workflow_config.yaml
```

### 3. Web Application (Local-First Dashboard)

Launch the integrated FastAPI backend and React frontend dashboard:

```bash
python start_app.py
```

Access the interface at:
- **Frontend Dashboard**: `http://127.0.0.1:5173`
- **FastAPI Backend**: `http://127.0.0.1:8000`
- **Interactive API Docs**: `http://127.0.0.1:8000/api/docs`

---


## 📊 Outputs & Reports

The framework outputs reproducible, bit-for-bit deterministic artifacts to `results/`:

- `results/reports/decision_report.json` — Complete machine-readable report conforming to Table 12.1
- `results/reports/decision_report.xlsx` — 3-sheet formatted Excel workbook (Summary, Ranking, Sensitivity)
- `results/reports/ranking.csv` — Full candidate polymer ranking table with closeness coefficients ($CL$)
- `results/figures/` — 5 publication-ready 300 DPI figures:
  - `fig06_ahp_topsis_ranking.png`
  - `fig07_morris_sensitivity.png`
  - `fig08_uncertainty_propagation.png`
  - `fig11_pca_scree_plot.png`
  - `fig12_fbm_contour.png`

---

## 🧪 Running Tests

Execute the complete pytest suite:

```bash
pytest tests/
```

Run unit tests only:

```bash
pytest tests/unit/
```

Run integration pipeline test:

```bash
pytest tests/integration/
```

---

## 📚 Documentation

- [Installation Guide](docs/INSTALLATION.md)
- [User Guide](docs/USER_GUIDE.md)
- [Developer Guide](docs/DEVELOPER_GUIDE.md)
- [API Reference](docs/API.md)

---

## 📄 License & Citation

Distributed under the MIT License. See `LICENSE` for details.

If you use this software in your research, please cite:

```bibtex
@article{asd_mcda_2026,
  title={Quality by Design--Driven Development of Indomethacin Immediate-Release Tablets from Spray-Dried Amorphous Solid Dispersions Using an Integrated Computational Polymer Screening and Failure Mapping Framework},
  author={Interdisciplinary Computational Pharmaceutics Team},
  journal={AAPS PharmSciTech},
  year={2026},
  doi={10.5281/zenodo.1234567}
}
```
