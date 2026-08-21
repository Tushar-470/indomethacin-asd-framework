# Pre-Cleanup Dependency and Safety Audit

**Date**: August 2026  
**Release**: v1.3.1-FREEZE  
**Framework**: Master Research Framework V2.0  

---

## 1. Executive Summary

Prior to executing any file moves or archival operations, a comprehensive repository-wide dependency and reference analysis was conducted. Every root-level script, temporary data file, legacy report, historical documentation record, and runtime artifact was inspected across all modules in `src/`, `tests/`, `backend/`, `config/`, `.github/`, and root.

---

## 2. Root-Level Scripts Dependency Audit

| File | Current Location | Active Dependency? | Used By | Safe to Archive? | Destination |
| :--- | :--- | :---: | :--- | :---: | :--- |
| `audit_suite.py` | Root | NO | None (standalone audit) | YES | `archive/development/` |
| `forensic_fbm_audit.py` | Root | NO | None (standalone audit) | YES | `archive/development/` |
| `run_corrected_calibration.py` | Root | NO | None (standalone research) | YES | `archive/development/` |
| `run_final_corrected_n10_calibration.py` | Root | NO | None (standalone research) | YES | `archive/development/` |
| `run_final_hsp_reconciliation.py` | Root | NO | None (standalone research) | YES | `archive/development/` |
| `run_hsp_audit_suite.py` | Root | NO | None (standalone research) | YES | `archive/development/` |
| `run_hvk_calibration_analysis.py` | Root | NO | None (standalone research) | YES | `archive/development/` |
| `run_provenance_audit.py` | Root | NO | None (standalone audit) | YES | `archive/development/` |
| `run_statistical_audit_fbm.py` | Root | NO | None (standalone audit) | YES | `archive/development/` |
| `run_v130_scientific_upgrade.py` | Root | NO* | `tests/unit/test_v130_upgrade.py` (*`wilson_score_ci` helper relocated to `src/asd_mcda/utils/helpers.py`) | YES | `archive/development/` |
| `run_v131_qc_audit.py` | Root | NO | None (standalone audit) | YES | `archive/development/` |
| `verify_exact_source_locations.py` | Root | NO | None (standalone audit) | YES | `archive/development/` |
| `verify_repository_pre_freeze.py` | Root | NO | None (pre-freeze dry run) | YES | `archive/development/` |
| `export_frozen_baseline.py` | Root | NO | None (one-time freeze exporter) | YES | `archive/development/` |
| `start_app.py` | Root | YES | `run_app.bat`, `README.md`, Web App workflow | NO (KEEP) | Root (Active launcher) |
| `run_app.bat` | Root | YES | Windows users / local launcher | NO (KEEP) | Root (Active launcher) |

---

## 3. Data Files and Runtime Artifacts Audit

| File / Directory | Current Location | Active Dependency? | Used By | Safe to Archive? | Destination |
| :--- | :--- | :---: | :--- | :---: | :--- |
| `scratch_temp_6polys.csv` | Root | NO | None (scratch exploratory data) | YES | `archive/development/` |
| `scratch_temp_clean.csv` | Root | NO | None (scratch exploratory data) | YES | `archive/development/` |
| `scratch_temp_polys.csv` | Root | NO | None (scratch exploratory data) | YES | `archive/development/` |
| `config/polymers/polymer_library_v2.csv` | `config/polymers/` | NO* | Legacy 6-polymer library (*test updated to v3 5-polymer library) | YES | `archive/historical/` |
| `data/analysis_history.db` | `data/` | NO (Historical) | Historical web UI runs (auto-created fresh on new runs) | YES | `archive/development/` |
| `data/analyses/` | `data/` | NO (Historical) | 89 past exploratory web UI analysis directories | YES | `archive/development/analyses/` |
| `data/user_polymers.csv` | `data/` | NO (Historical) | Historical custom user polymers (auto-created on new user additions) | YES | `archive/development/user_polymers.csv` |

---

## 4. Superseded Reports and Historical Documentation Audit

| File | Current Location | Active Dependency? | Used By | Safe to Archive? | Destination |
| :--- | :--- | :---: | :--- | :---: | :--- |
| `results/reports/decision_report.*` | `results/reports/` | NO | Superseded pre-freeze reports | YES | `archive/superseded/` |
| `results/reports/ranking.csv` | `results/reports/` | NO | Superseded pre-freeze ranking | YES | `archive/superseded/` |
| `results/reports/v130_prospective_validation_lock.json` | `results/reports/` | NO | Superseded v1.3.0 metadata lock | YES | `archive/superseded/` |
| `docs/COMPUTATIONAL_FREEZE_RECORD_V1.0.md` | `docs/` | NO | Historical baseline record | YES | `archive/historical/` |
| `docs/FIVE_POLYMER_COMPUTATIONAL_BASELINE_RECORD_V1.2.md` | `docs/` | NO | Historical baseline record | YES | `archive/historical/` |
| `docs/FINAL_INPUT_PROVENANCE_AND_FREEZE_RECORD.md` | `docs/` | NO | Historical 6-polymer provenance (v1.1.0) | YES | `archive/historical/` |
| `docs/FINAL_VERIFICATION_REPORT.md` | `docs/` | NO | Historical 36-test report (v1.1.0) | YES | `archive/historical/` |

---

## 5. Audit Decision & Verification

All archived items were moved using `git mv` (or file moves followed by staging) to guarantee 100% preservation in Git history. Active production tests were verified and decoupled from ad-hoc root scripts by embedding the required `wilson_score_ci` utility function into `src/asd_mcda/utils/helpers.py`. No active scientific model equations, parameters, or outputs were altered.
