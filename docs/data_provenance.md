# Data Provenance and Parameter Lineage

**Release**: v1.3.1-FREEZE  
**Status**: Frozen Baseline  

---

## 1. Active Pharmaceutical Ingredient: Indomethacin

**Primary Configuration File**: `config/drugs/indomethacin.json`  
**Drug Identifier**: `IND-001-2026`  

| Property Field | Numerical Value | Unit | Data Type | Primary Source | Experimental State / Grade |
| :--- | :---: | :---: | :---: | :--- | :--- |
| **Generic Name** | Indomethacin | — | Reference | USP Monograph | Pure API |
| **CAS Number** | 53-86-1 | — | Registry | Chemical Abstracts Service | Pure API |
| **Molecular Weight ($M_w$)** | 357.79 | g/mol | Literature | USP Monograph / IUPAC | Pure API |
| **Melting Temperature ($T_m$)** | 424.15 (151.0 °C) | K | Experimental DSC | Hancock et al., *J. Pharm. Sci.* 2007 | $\gamma$-Polymorph |
| **Glass Transition ($T_g$)** | 315.15 (42.0 °C) | K | Experimental DSC | Hancock et al., *J. Pharm. Sci.* 2007 | Quenched Amorphous |
| **Amorphous Density ($\rho_{\text{amorphous}}$)** | 1.22 | $\text{g/cm}^3$ | Experimental Pycnometry | Hancock et al., *J. Pharm. Sci.* 2007 | Amorphous |
| **Crystalline Density ($\rho_{\text{crystalline}}$)** | 1.31 | $\text{g/cm}^3$ | Experimental | Yalkowsky et al., *Solubility Data* | $\gamma$-Form |
| **HSP Dispersion ($\delta_D$)** | 19.2 | $\text{MPa}^{0.5}$ | Experimental Sphere | Hancock et al., *J. Pharm. Sci.* 2007 | Pure API |
| **HSP Polar ($\delta_P$)** | 7.9 | $\text{MPa}^{0.5}$ | Experimental Sphere | Hancock et al., *J. Pharm. Sci.* 2007 | Pure API |
| **HSP Hydrogen Bonding ($\delta_H$)** | 8.4 | $\text{MPa}^{0.5}$ | Experimental Sphere | Hancock et al., *J. Pharm. Sci.* 2007 | Pure API |
| **Total HSP ($\delta_T$)** | 22.4 | $\text{MPa}^{0.5}$ | Calculated ($\sqrt{\delta_D^2+\delta_P^2+\delta_H^2}$) | Derived | Pure API |
| **Interaction Radius ($R_0$)** | 8.0 | $\text{MPa}^{0.5}$ | Experimental Sphere | Hancock et al., *J. Pharm. Sci.* 2007 | Pure API |
| **Molar Volume ($V_m$)** | 273.0 | $\text{cm}^3/\text{mol}$ | Calculated ($M_w/\rho_{\text{crystalline}}$) | Derived | Pure API |
| **$\text{Log}P$** | 4.27 | — | Experimental | Hansch & Leo Literature Database | Pure API |
| **BCS Class** | II | — | Regulatory Classification | FDA BCS Database | Poorly Soluble / Permeable |

---

## 2. Active Polymer Carrier Library ($N=5$)

**Primary Configuration File**: `config/polymers/polymer_library_v3_five_polymers.csv`  
**Library SHA-256**: `24cd6c4092788cb7266d2ea34e82b6dfe193b5cfb91e22c0dff66b0abc9088ff`  

All polymer Hansen Solubility Parameters were computed using the **Hoftyzer–Van Krevelen (H-V-K) group contribution method** from repeat-unit monomer SMILES representations. These are **calculated group-contribution values**, not experimentally measured solubility spheres.

| Polymer ID | Canonical Polymer Name | Abbreviation | Family | Class | $M_n$ (Da) | $M_w$ (Da) | $T_g$ (K) | Density ($\text{g/cm}^3$) | HSP ($\delta_D/\delta_P/\delta_H$) | HSP Method |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| `POL-001-2026` | Polyvinylpyrrolidone K30 | PVP_K30 | vinylic | neutral | 40,000 | 50,000 | 441.15 | 1.20 | 17.4 / 8.2 / 11.7 | H-V-K Calculated |
| `POL-002-2026` | PVP-Vinyl Acetate 64 | PVP_VA_64 | vinylic | neutral | 45,000 | 57,500 | 378.15 | 1.20 | 17.0 / 8.0 / 10.0 | H-V-K Calculated |
| `POL-005-2026` | Soluplus | SOLUPLUS | acrylic | amphiphilic | 90,000 | 118,000 | 343.15 | 1.08 | 18.0 / 8.5 / 10.5 | H-V-K Calculated |
| `POL-006-2026` | Hydroxypropyl Methylcellulose E5 | HPMC_E5 | cellulosic | neutral | 20,000 | 28,700 | 443.15 | 1.27 | 18.5 / 8.8 / 12.0 | H-V-K Calculated |
| `POL-007-2026` | Eudragit E PO | EDR_EPO | acrylic | cationic | 39,000 | 47,000 | 323.15 | 1.125 | 16.8 / 5.2 / 6.5 | H-V-K Calculated |

---

## 3. Molecular Weight Distinction ($M_n$ vs $M_w$)

Both number-average molecular weight ($M_n$) and weight-average molecular weight ($M_w$) are recorded from manufacturer technical certificates:
- **Number-Average Molecular Weight ($M_n$)**: Used in the Flory–Huggins critical interaction parameter calculation ($\chi_c$) for segment-length ratio ($r_2 = V_{\text{polymer}}/V_{\text{drug}}$ where $V_{\text{polymer}} = M_n / \rho_{\text{polymer}}$).
- **Weight-Average Molecular Weight ($M_w$)**: Recorded for regulatory and polymer characterization completeness. $M_w$ does not enter the primary deterministic MCDA ranking.

---

## 4. Multi-Expert AHP Comparison Matrices

**Directory**: `config/ahp/`  
- `default_matrix.json`: Baseline $2 \times 2$ pairwise comparison matrix for retained Principal Components ($PC_1:PC_2 = 2.0:1.0, CR = 0.00$).
- `expert_001.json`, `expert_002.json`, `expert_003.json`: Elicited domain-expert matrices.
