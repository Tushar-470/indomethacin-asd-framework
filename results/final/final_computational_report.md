# Final Computational Decision Report

**Release**: v1.3.1-FREEZE  
**Git Commit**: 2220c44  
**Dataset SHA-256**: `24cd6c4092788cb7266d2ea34e82b6dfe193b5cfb91e22c0dff66b0abc9088ff`  
**Status**: FROZEN COMPUTATIONAL BASELINE; PRE-LABORATORY PREDICTION  

---

## 1. Study Objective

This report documents the frozen computational baseline for rational polymeric carrier selection for spray-dried amorphous solid dispersions (SD-ASDs) of indomethacin (BCS Class II). The framework couples multi-property thermodynamic modeling, Principal Component Analysis (PCA), Analytic Hierarchy Process (AHP), and TOPSIS multi-criteria decision analysis with Monte Carlo Uncertainty Quantification ($N=10{,}000$).

---

## 2. Active Polymer Carrier Library ($N=5$)

| Polymer ID | Canonical Polymer Name | Abbreviation | Family | Class | $M_n$ (Da) | $T_g$ (K) | Density ($\text{g/cm}^3$) | HSP ($\delta_D/\delta_P/\delta_H$) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `POL-001-2026` | Polyvinylpyrrolidone K30 | PVP_K30 | vinylic | neutral | 40,000 | 441.15 | 1.20 | 17.4 / 8.2 / 11.7 |
| `POL-002-2026` | PVP-Vinyl Acetate 64 | PVP_VA_64 | vinylic | neutral | 45,000 | 378.15 | 1.20 | 17.0 / 8.0 / 10.0 |
| `POL-005-2026` | Soluplus | SOLUPLUS | acrylic | amphiphilic | 90,000 | 343.15 | 1.08 | 18.0 / 8.5 / 10.5 |
| `POL-006-2026` | Hydroxypropyl Methylcellulose E5 | HPMC_E5 | cellulosic | neutral | 20,000 | 443.15 | 1.27 | 18.5 / 8.8 / 12.0 |
| `POL-007-2026` | Eudragit E PO | EDR_EPO | acrylic | cationic | 39,000 | 323.15 | 1.125 | 16.8 / 5.2 / 6.5 |

---

## 3. Compatibility Score Matrix ($\mathbf{S}_{\text{active}}$)

| Polymer ID | Abbreviation | $s_{\text{HSP}}$ | $s_\chi$ | $s_{\text{GT}}$ |
| :--- | :---: | :---: | :---: | :---: |
| `POL-001-2026` | PVP_K30 | 0.694197 | 0.483615 | 0.984822 |
| `POL-002-2026` | PVP_VA_64 | 0.707316 | 0.609435 | 0.236756 |
| `POL-007-2026` | EDR_EPO | 0.635887 | 0.319305 | 0.000000 |
| `POL-005-2026` | SOLUPLUS | 0.797188 | 0.773524 | 0.000000 |
| `POL-006-2026` | HPMC_E5 | 0.752118 | 0.588511 | 0.973123 |

---

## 4. Deterministic TOPSIS Ranking

| Rank | Polymer ID | Canonical Name | Abbreviation | TOPSIS $C_L$ | Model Designation |
| :---: | :--- | :--- | :---: | :---: | :--- |
| **1** | `POL-005-2026` | **Soluplus** | **SOLUPLUS** | **0.736338** | **Top-Ranked Computational Candidate** |
| 2 | `POL-006-2026` | Hydroxypropyl Methylcellulose E5 | HPMC_E5 | 0.684063 | High-Affinity Alternative |
| 3 | `POL-002-2026` | PVP-Vinyl Acetate 64 | PVP_VA_64 | 0.504982 | Intermediate Miscibility Candidate |
| 4 | `POL-001-2026` | Polyvinylpyrrolidone K30 | PVP_K30 | 0.442917 | Moderate Affinity Candidate |
| 5 | `POL-007-2026` | Eudragit E PO | EDR_EPO | 0.000000 | Boundary Anti-Ideal Candidate |

---

## 5. Joint-Distribution Monte Carlo Uncertainty Quantification ($N=10{,}000$)

- **Soluplus (`POL-005-2026`)**: $P(\text{top-1}) = \mathbf{43.2\%}$
- **HPMC E5 (`POL-006-2026`)**: $P(\text{top-1}) = \mathbf{31.0\%}$
- **PVP K30 (`POL-001-2026`)**: $P(\text{top-1}) = \mathbf{14.4\%}$
- **PVP-VA 64 (`POL-002-2026`)**: $P(\text{top-1}) = \mathbf{5.8\%}$
- **Eudragit E PO (`POL-007-2026`)**: $P(\text{top-1}) = \mathbf{5.6\%}$
- **Confidence Tier**: **Moderate Confidence** ($0.40 \le P(\text{top-1}) < 0.70$)

---

## 6. Scientific Interpretation & Formulation Guidance

1. **Soluplus** emerges as the top-ranked computational candidate with the highest closeness coefficient ($C_L = 0.7363$) and the highest Monte Carlo top-1 selection probability ($43.2\%$), driven by favorable cohesive energy balance ($s_{\text{HSP}} = 0.7972$) and low estimated interaction parameter ($\chi = 0.2265, s_\chi = 0.7735$).
2. **HPMC E5** represents a strong competitive alternative ($C_L = 0.6841, P(\text{top-1}) = 31.0\%$), combining favorable thermodynamic miscibility with high anti-plasticization capability ($s_{\text{GT}} = 0.9731, T_{g,\text{mix}} = 404.9\text{ K}$).
3. **PVP K30** provides superior anti-plasticization ($T_g = 441.15\text{ K}$) but lower cohesive compatibility with indomethacin, leading to a rank 4 placement ($C_L = 0.4429$).
4. **Eudragit E PO** serves as the empirical anti-ideal anchor ($C_L = 0.0000$) due to low glass transition temperature and lower cohesive density matching.

**Statement of Status**: These findings are pre-laboratory computational predictions. Prospective experimental spray-drying and physical stability testing are required before clinical development decisions.
