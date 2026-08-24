# Scientific Reproducibility Guide

**Platform**: PharmaPolySCOPE (Pharmaceutical Polymer Screening and Computational Optimization Platform)  
**Release**: `v1.5.0-FOUR-CRITERION-FREEZE`  
**Python Target**: $\ge 3.11$  
**Random Seed**: 42  
**Dataset SHA-256**: `5497d606b64e081cac0274e4f5db8343c012fd84191b5ec413990614717c3ac2`  
**Developer Attribution**: Developed by Tushar Mathapati  

---

## 1. Environment Setup

Clone the repository and install dependencies:

```bash
git clone https://github.com/Tushar-470/indomethacin-asd-framework.git
cd indomethacin-asd-framework
pip install -e .
pip install -r requirements-dev.txt
```

---

## 2. Dataset Verification

Execute the automated dataset validator to confirm file integrity, active candidate count, column consistency, and SHA-256 checksums:

```bash
python scripts/validate_final_dataset.py
```

Expected output:
```text
============================================================
FINAL DATASET VALIDATION — v1.5.0-FOUR-CRITERION-FREEZE
============================================================
  PASS: Library file exists: polymer_library_v3_five_polymers.csv
  PASS: Library SHA-256 matches expected (5497d606b64e081c...)
  PASS: Exactly 5 polymers (found 5)
  ...
STATUS: PASS
```

---

## 3. Automated Test Suite Execution

Run the complete test suite across unit, integration, and API modules:

```bash
py -3 -m pytest tests/ -v
```

Expected result: 76 passed (100% pass rate).

---

## 4. Pipeline Execution & Deterministic Output Reproduction

Execute the full computational screening pipeline via CLI:

```bash
python -m asd_mcda.cli --config config/workflow/workflow_config.yaml
```

The pipeline writes deterministic outputs to `results/reports/` and `results/figures/`.

### Expected Deterministic Ranking Table (`v1.5.0-FOUR-CRITERION-FREEZE`)

| Rank | Polymer ID | Name | TOPSIS $C_L$ | $P(\text{top-1})$ | Model Selection Robustness Tier |
| :---: | :--- | :--- | :---: | :---: | :--- |
| **1** | `POL-006-2026` | Hydroxypropyl Methylcellulose E5 | 0.835911 | 75.54% | High Robustness ($P \ge 70\%$) |
| **2** | `POL-005-2026` | Soluplus | 0.694342 | 20.18% | Low Robustness ($P < 40\%$) |
| **3** | `POL-001-2026` | Polyvinylpyrrolidone K30 | 0.549368 | 4.03% | Low Robustness ($P < 40\%$) |
| **4** | `POL-002-2026` | PVP-Vinyl Acetate 64 | 0.470256 | 0.25% | Low Robustness ($P < 40\%$) |
| **5** | `POL-007-2026` | Eudragit E PO | 0.090501 | 0.00% | Low Robustness ($P < 40\%$) |

---

## 5. Web Interface Execution

Launch the local-first web application interface (FastAPI backend + React frontend):

```bash
python start_app.py
```

- **Frontend Dashboard**: `http://localhost:5173`
- **FastAPI Documentation**: `http://localhost:8000/api/docs`
