# Archive Directory

## Purpose

This directory preserves development artifacts, superseded outputs, and historical documents from the computational framework development phase. Archived files are **NOT** part of the active scientific reproduction workflow.

## Structure

### `historical/`
Prior-version baseline records and superseded polymer libraries that document the evolution of the computational framework.
- `COMPUTATIONAL_FREEZE_RECORD_V1.0.md` — Original v1.0 baseline (superseded by v1.3.1)
- `FIVE_POLYMER_COMPUTATIONAL_BASELINE_RECORD_V1.2.md` — v1.2 baseline (superseded by v1.3.1)
- `polymer_library_v2.csv` — Six-polymer library including HPMCAS-L and Eudragit L100 (superseded by `polymer_library_v3_five_polymers.csv`)

### `superseded/`
Output reports and rankings from earlier computational iterations that have been replaced by the frozen v1.3.1-FREEZE baseline.
- `decision_report.*` — Pre-freeze decision reports
- `ranking.csv` — Pre-freeze ranking output
- `v130_prospective_validation_lock.json` — v1.3.0 validation lock (superseded by v1.3.1)

### `development/`
Development-phase scripts used for auditing, calibration, debugging, and one-time analyses. These scripts are preserved for provenance but are not required to reproduce the final computational baseline.

## Important

- **Active final results must NEVER depend on archived files.**
- All archived material remains accessible in Git history.
- The authoritative active outputs are in `results/final/`.
- The authoritative active polymer library is `config/polymers/polymer_library_v3_five_polymers.csv`.
