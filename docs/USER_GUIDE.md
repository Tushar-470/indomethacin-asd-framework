# User Guide

## Overview

The `asd_mcda` package executes an 11-step computational polymer screening workflow for amorphous solid dispersions.

## Workflow Pipeline Steps

1. **Input**: Ingestion of drug JSON, polymer library CSV, and AHP matrices.
2. **Preprocessing**: SMILES canonicalization and structural verification.
3. **Descriptor Calculation**: 2D RDKit molecular descriptors and Hoftyzer-Van Krevelen HSP estimation.
4. **HSP Scoring**: $R_a$, RED number, $s_{\text{HSP}}$, and Gate 1 evaluation ($RED \le 1.0$).
5. **Flory-Huggins Scoring**: Enthalpic interaction parameter $\chi$, critical $\chi_c$, and $s_{\chi}$.
6. **Gordon-Taylor Scoring**: Mixture $T_{g,\text{mix}}$ via Simha-Boyer $K$, Kwei correction option, and $s_{GT}$.
7. **Evidence Integration**: MANDATORY PCA pre-processing on score matrix $S$, retaining PCs explaining $\ge 95\%$ cumulative variance.
8. **MCDA Decision**: Multi-expert AHP weight derivation ($CR < 0.08$ Gate 2 check, geometric-mean aggregation) and TOPSIS ranking ($CL$).
9. **UQ & Sensitivity**: Monte Carlo joint distribution propagation ($N=10,000$), OAT weight perturbation, and Morris elementary effects screening.
10. **Prediction & FBM**: Logistic-regression Failure Boundary Mapping ($\text{logit}(P(\text{failure})) = \beta \cdot X$) with bootstrap 95% CIs.
11. **Validation & Output**: LOO-CV, held-out test sets, negative controls, baseline comparisons ($\Delta \rho \ge 0.10$), and multi-format report generation.

## Command Line Flags

- `-c, --config`: Path to workflow YAML configuration file (default: `config/workflow/workflow_config.yaml`).
- `-v, --version`: Print package version string.

## Customizing Polymer Library

Edit `config/polymers/polymer_library_v2.csv` to add candidate polymers, specifying monomer SMILES, $M_n$, $T_g$, density, and Hansen solubility parameters.
