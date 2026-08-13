# Five-Polymer Computational Baseline Record (v1.2.0)

**Project**: Quality by Design-Driven Development of Indomethacin Immediate-Release Tablets from Spray-Dried Amorphous Solid Dispersions  
**Release Baseline**: `v1.2.0` (Five-Polymer Candidate Set for Immediate-Release Tablets)  
**Historical Baseline**: `v1.1.0` (Preserved intact)  
**Release Tag**: `v1.2.0`  
**Git Commit**: `4aeed7e`  
**Date**: August 13, 2026  
**Status**: COMPUTATIONALLY VERIFIED & LOCKED FIVE-POLYMER BASELINE  

---

## 1. Candidate Library Rationale & Composition

The candidate polymer library was updated from 6 to **5 polymers** specifically targeted for **immediate-release spray-dried tablet formulations**:
- **Included**: Soluplus, PVP-VA 64, Eudragit E PO, PVP K30, HPMC E5.
- **Excluded**:
  - `HPMCAS-LF` (`POL-003-2026`): Excluded because HPMCAS is an enteric (pH-dependent, soluble at $\text{pH} \ge 5.5$) polymer, which retards Indomethacin dissolution in acidic gastric media ($\text{pH } 1.2$), violating the immediate-release tablet target specification.
  - `Eudragit L100` (`POL-004-2026`): Excluded for the same enteric/pH-dependent dissolution mechanism.

---

## 2. Locked Five-Polymer Input Provenance Table

| Polymer ID | Polymer Name | Abbreviation | Family | Class | $M_n$ (Da) | $M_w$ (Da) | PDI | $T_g$ (K / °C) | Density ($\text{g/cm}^3$) | HSP ($\delta_D / \delta_P / \delta_H$) | Monomer SMILES | Literature Evidence Score | Primary Source |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| `POL-005-2026` | Soluplus | `SOLUPLUS` | acrylic | amphiphilic | 90,000 | 118,000 | 1.311 | 343.15 (70 °C) | 1.08 | 18.0 / 8.5 / 10.5 | `CC(=O)OCC(C)C\|...` | 1.0 | BASF CoA / J. Pharm. Sci. 2010 |
| `POL-002-2026` | PVP-Vinyl Acetate 64 | `PVP_VA_64` | vinylic | neutral | 45,000 | 57,500 | 1.278 | 378.15 (105 °C) | 1.20 | 17.0 / 8.0 / 10.0 | `C=CN1CCCC1=O\|CC(=O)OC` | 1.0 | BASF CoA / Int. J. Pharm. 2010 |
| `POL-007-2026` | Eudragit E PO | `EDR_EPO` | acrylic | cationic | 39,000 | 47,000 | 1.205 | 323.15 (50 °C) | 1.125 | 16.8 / 5.2 / 6.5 | `CCN(C)CCOC(=O)C...` | 1.0 | Evonik Specification / IJP 2008 |
| `POL-001-2026` | Polyvinylpyrrolidone K30 | `PVP_K30` | vinylic | neutral | 40,000 | 50,000 | 1.250 | 441.15 (168 °C) | 1.20 | 17.4 / 8.2 / 11.7 | `C=CN1CCCC1=O` | 1.0 | BASF CoA / J. Pharm. Sci. 2007 |
| `POL-006-2026` | Hydroxypropyl Methylcellulose E5 | `HPMC_E5` | cellulosic | neutral | 20,000 | 28,700 | 1.435 | 443.15 (170 °C) | 1.27 | 18.5 / 8.8 / 12.0 | `COCC1O[C@H](O)...` | 1.0 | Dow Technical Sheet / JPS 2007 |

---

## 3. Normalized Score Matrix $S$ ($5 \times 5$)

$$\mathbf{S} = \begin{bmatrix} s_{\text{HSP}} & s_{\chi} & s_{\text{desc}} & s_{\text{GT}} & s_{\text{lit}} \end{bmatrix}$$

| Polymer ID | Abbreviation | $s_{\text{HSP}}$ | $s_{\chi}$ | $s_{\text{desc}}$ | $s_{\text{GT}}$ | $s_{\text{lit}}$ |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `POL-005-2026` | `SOLUPLUS` | **0.7972** | **0.7735** | 0.2268 | 0.0000 | 1.0000 |
| `POL-006-2026` | `HPMC_E5` | 0.7521 | 0.5885 | 0.2268 | **0.9731** | 1.0000 |
| `POL-002-2026` | `PVP_VA_64` | 0.7073 | 0.6094 | 0.2268 | 0.2368 | 1.0000 |
| `POL-001-2026` | `PVP_K30` | 0.6942 | 0.4836 | 0.2268 | 0.9848 | 1.0000 |
| `POL-007-2026` | `EDR_EPO` | 0.6359 | 0.3193 | 0.2268 | 0.0000 | 1.0000 |

---

## 4. Thermodynamic & Phase-Boundary Diagnostics

| Polymer ID | Abbreviation | Flory–Huggins $\chi$ | Corrected $\chi_c$ | Spinodal Stability Margin ($\chi_c - \chi$) | Gordon–Taylor $T_{g,\text{mix}}$ ($30\text{ wt}\%$) | $T_g$ Margin above $25^\circ\text{C}$ | Phase Separation Risk |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `POL-005-2026` | `SOLUPLUS` | 0.2265 | 0.5589 | +0.3324 (Stable) | 335.0 K (61.8 °C) | +36.8 K | **Low** |
| `POL-006-2026` | `HPMC_E5` | 0.4115 | 0.6403 | +0.2288 (Stable) | 393.8 K (120.6 °C) | +95.7 K | **Low** |
| `POL-002-2026` | `PVP_VA_64` | 0.3906 | 0.5890 | +0.1984 (Stable) | 357.0 K (83.8 °C) | +58.8 K | **Low** |
| `POL-001-2026` | `PVP_K30` | 0.5164 | 0.5946 | +0.0782 (Stable) | 394.4 K (121.2 °C) | +96.2 K | **Low** |
| `POL-007-2026` | `EDR_EPO` | 0.6807 | 0.5927 | -0.0880 (Metastable) | 320.8 K (47.7 °C) | +22.7 K | **Moderate** |

---

## 5. Multi-Criteria Ranking & Monte Carlo Uncertainty Quantification

| Rank | Polymer Name | Polymer ID | TOPSIS Ideal Distance ($d^+$) | TOPSIS Anti-Ideal Distance ($d^-$) | TOPSIS Closeness ($C_L$) | Monte Carlo Top-1 Count ($N=10,000$) | Monte Carlo $P(\text{top-1})$ | Decision Confidence Tier |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | **Soluplus** | `POL-005-2026` | **0.323503** | **0.903459** | **0.736338** | **4,320** | **43.20%** | **Moderate Confidence** |
| **2** | **HPMC E5** | `POL-006-2026` | **0.311569** | **0.674606** | **0.684063** | **3,100** | **31.00%** | **Moderate Confidence** |
| **3** | **PVP-Vinyl Acetate 64** | `POL-002-2026` | **0.484853** | **0.494613** | **0.504982** | **580** | **5.80%** | **Low Confidence** |
| **4** | **PVP K30** | `POL-001-2026` | **0.577437** | **0.459099** | **0.442917** | **1,440** | **14.40%** | **Low Confidence** |
| **5** | **Eudragit E PO** | `POL-007-2026` | **0.959686** | **0.000000** | **0.000000** | **560** | **5.60%** | **Low Confidence** |

---

## 6. PCA & AHP Integration Results

- **Retained PCA Components**: $k = 3$ (explaining $> 95\%$ cumulative variance).
- **AHP Eigenvector Weights**: $w_1 = 0.6429, w_2 = 0.3571, w_3 = 0.0000$.
- **AHP Consistency Ratio**: $CR = 0.0421$ ($< 0.08$ Gate 2 threshold).

---

## 7. Recommended Final Shortlist for Immediate-Release Spray-Dried Tablets

1. **Soluplus** (`POL-005-2026`) — **Rank #1 ($C_L = 0.7363$, $P(\text{top-1}) = 43.2\%$)**: Outstanding solubility enhancement ($\chi = 0.2265$), amphiphilic micellar solubilization during dissolution.
2. **HPMC E5** (`POL-006-2026`) — **Rank #2 ($C_L = 0.6841$, $P(\text{top-1}) = 31.0\%$)**: High glass transition temperature margin ($T_{g,\text{mix}} = 120.6^\circ\text{C}$), strong crystallization inhibition.
3. **PVP-Vinyl Acetate 64** (`POL-002-2026`) — **Rank #3 ($C_L = 0.5050$, $P(\text{top-1}) = 5.8\%$)**: Excellent spray-drying processability, strong H-bonding acceptor capacity.
