# Scientific Reproducibility Guide

**Release**: v1.3.1-FREEZE  
**Python Target**: $\ge 3.11$  
**Random Seed**: 42  
**Dataset SHA-256**: `24cd6c4092788cb7266d2ea34e82b6dfe193b5cfb91e22c0dff66b0abc9088ff`  

---

## 1. Environment Setup

Clone the repository and install the production package in editable mode:

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
FINAL DATASET VALIDATION — v1.3.1-FREEZE
============================================================
  PASS: Library file exists: polymer_library_v3_five_polymers.csv
  PASS: Library SHA-256 matches expected (24cd6c4092788cb7...)
  PASS: Exactly 5 polymers (found 5)
  ...
Results: 22 passed, 0 failed
STATUS: PASS
```

---

## 3. Automated Test Suite Execution

Run the complete test suite across unit, integration, and API modules:

```bash
pytest tests/
```

Expected result: Complete test pass across all computational engine, physics, MCDA, and integration pipelines.

---

## 4. Pipeline Execution & Deterministic Output Reproduction

Execute the full 11-step computational screening pipeline via CLI:

```bash
python -m asd_mcda.cli --config config/workflow/workflow_config.yaml
```

The pipeline writes deterministic outputs to `results/reports/` and `results/figures/`.

### Expected Deterministic Ranking Table

| Rank | Polymer ID | Name | TOPSIS $C_L$ | $P(\text{top-1})$ |
| :---: | :--- | :--- | :---: | :---: |
| **1** | `POL-005-2026` | Soluplus | 0.736338 | 43.2% |
| **2** | `POL-006-2026` | Hydroxypropyl Methylcellulose E5 | 0.684063 | 31.0% |
| **3** | `POL-002-2026` | PVP-Vinyl Acetate 64 | 0.504982 | 5.8% |
| **4** | `POL-001-2026` | Polyvinylpyrrolidone K30 | 0.442917 | 14.4% |
| **5** | `POL-007-2026` | Eudragit E PO | 0.000000 | 5.6% |

---

## 5. Web Interface Execution

Launch the local-first web application interface (FastAPI backend + React frontend):

```bash
python start_app.py
```

- **Frontend Dashboard**: `http://localhost:5173`
- **FastAPI Documentation**: `http://localhost:8000/api/docs`
