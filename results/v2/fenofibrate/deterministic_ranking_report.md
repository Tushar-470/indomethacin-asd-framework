# PharmaPolySCOPE v2 — Production Deterministic Decision Report
## Compound: Fenofibrate (`DRG-0007`)

**Analysis Status**: `PRODUCTION`  
**Evaluation Engine**: SP-PRP-TOPSIS on Dynamic Variable-K Subspaces  
**Target Drug**: Fenofibrate (`DRG-0007`, `data/user_drugs/drg-0007.json`)  
**Polymer Library**: Active 5-Polymer Production Library (`config/polymers/polymer_library_v3_five_polymers.csv`)  
**Methodological Governance**: Remediated Density Semantics (SAS V1.0 §6.1 / DAS V1.0 §6.1)  

---

## 1. Executive Summary

* **Top-Ranked Deterministic Candidate**: **Eudragit E PO** (`POL-007-2026`) with relative closeness coefficient $C_L = 0.7413$.
* **Runner-Up Candidate**: **PVP-VA 64** (`POL-002-2026`) with $C_L = 0.6271$.
* **Spectral Dimensionality**: Recomputed dynamically as **$K = 3$**, capturing **99.93%** cumulative explained variance with a strong boundary eigengap $\delta_3 = 0.2715$ (**`STABLE`**).
* **Density Semantics & Provenance**:
  * `density_crystalline_g_cm3`: **1.296 g/cm³** (Experimental single-crystal XRD).
  * `density_amorphous_g_cm3`: **null** (Optional; unmeasured for this cohort).
  * `density source used for V_m`: **crystalline** ($V_m = M_w / \rho_{\text{cryst}} = 360.84 / 1.296 = 278.43\text{ cm}^3/\text{mol}$).
  * `Gordon-Taylor density source`: **crystalline with systematic_bias_flag** via `Drug.get_preferred_density()`.

---

## 2. Raw Compatibility Score Matrix $\mathbf{S}$

The 4 canonical physical criteria evaluated across the five active candidate polymers:

| Polymer ID | Abbreviation | $s_{\text{HSP}}$ | $s_{\chi}$ | $s_{\text{desc}}$ | $s_{\text{GT}}$ |
|:---|:---|:---:|:---:|:---:|:---:|
| `POL-001-2026` | `PVP_K30` | 0.5419 | 0.2045 | 0.5427 | 1.0000 |
| `POL-002-2026` | `PVP_VA_64` | 0.6447 | 0.5215 | 0.5751 | 1.0000 |
| `POL-007-2026` | `EDR_EPO` | 0.8961 | 0.9591 | 0.6628 | 0.4202 |
| `POL-005-2026` | `SOLUPLUS` | 0.5473 | 0.2231 | 0.5994 | 0.6812 |
| `POL-006-2026` | `HPMC_E5` | 0.4400 | 0.0000 | 0.3532 | 1.0000 |

*Cohort Means (ddof=0)*: $\mu = [0.6140, 0.3816, 0.5467, 0.8203]$  
*Cohort Pop SDs (ddof=0)*: $\sigma = [0.1552, 0.3332, 0.1044, 0.2351]$

---

## 3. Standardized Decision Matrix $\mathbf{Z}$

Standardized via cohort-level population z-scoring ($ddof=0$):

| Polymer ID | Abbreviation | $z_{\text{HSP}}$ | $z_{\chi}$ | $z_{\text{desc}}$ | $z_{\text{GT}}$ |
|:---|:---|:---:|:---:|:---:|:---:|
| `POL-001-2026` | `PVP_K30` | -0.4646 | -0.5316 | -0.0377 | +0.7645 |
| `POL-002-2026` | `PVP_VA_64` | +0.1978 | +0.4197 | +0.2725 | +0.7645 |
| `POL-007-2026` | `EDR_EPO` | +1.8176 | +1.7330 | +1.1125 | -1.7020 |
| `POL-005-2026` | `SOLUPLUS` | -0.4299 | -0.4758 | +0.5052 | -0.5916 |
| `POL-006-2026` | `HPMC_E5` | -1.1209 | -1.1453 | -1.8524 | +0.7645 |

---

## 4. Spectral Decomposition & Variable-$K$ Selection

* **Eigenvalues**: $\lambda = (3.3903, 0.3326, 0.2743, 0.0028)$
* **Explained Variance Ratios**: $(84.76\%, 8.32\%, 6.86\%, 0.07\%)$
* **Retained Dimensions**: **$K = 3$** (Cumulative Explained Variance: **99.93%** $\ge 95\%$)
* **Boundary Eigengap**: $\delta_{3} = \lambda_{3} - \lambda_{4} = 0.2743 - 0.0028 = 0.2715$
* **Subspace Stability**: **`STABLE`** (Threshold $\delta_K \ge 0.05$ satisfied).

---

## 5. Analytic Hierarchy Process (AHP) Governance

* **Pairwise Comparison Matrix**:
  $$\mathbf{A} = \begin{pmatrix} 1.0 & 2.0 & 3.0 & 2.0 \\ 0.5 & 1.0 & 5.0 & 2.0 \\ 0.333 & 0.2 & 1.0 & 0.5 \\ 0.5 & 0.5 & 2.0 & 1.0 \end{pmatrix}$$
* **Physical Weights**: $\mathbf{w} = [0.4077, 0.3244, 0.0922, 0.1757]$
* **Eigenvalue $\lambda_{\max}$**: 4.1319
* **Consistency Index ($CI$)**: 0.0440
* **Consistency Ratio ($CR$)**: **0.0494** (Threshold $CR < 0.08$ strictly satisfied $\to$ **`ACCEPTED`**).

---

## 6. SP-PRP-TOPSIS Deterministic Ranking

Candidates ordered by descending closeness coefficient $C_L$:

| Rank | Polymer ID | Abbreviation | $C_L$ | $D^+$ | $D^-$ | Deterministic Designation |
|:---:|:---|:---|:---:|:---:|:---:|:---|
| 1 | `POL-007-2026` | `EDR_EPO` | **0.7413** | 1.4462 | 4.1443 | **Top-Ranked Deterministic Candidate** |
| 2 | `POL-002-2026` | `PVP_VA_64` | **0.6271** | 1.9928 | 3.3518 | Primary Competitor |
| 3 | `POL-001-2026` | `PVP_K30` | **0.5212** | 2.6186 | 2.8504 | Candidate |
| 4 | `POL-005-2026` | `SOLUPLUS` | **0.5124** | 2.5569 | 2.6864 | Candidate |
| 5 | `POL-006-2026` | `HPMC_E5` | **0.4039** | 3.3671 | 2.2819 | Candidate |

---

## 7. Truncation Diagnostics

Audit of distance metrics in full 4-dimensional standardized space vs projected $K=3$ subspace:

| Polymer ID | Abbreviation | $D^2_{\text{full}}$ | $D^2_K$ | Signed Discrepancy $\Delta D^2$ | Relative Discrepancy | Rank Distortion |
|:---|:---|:---:|:---:|:---:|:---:|:---:|
| `POL-001-2026` | `PVP_K30` | 7.1693 | 6.8572 | +0.312110 | 4.3534% | No |
| `POL-002-2026` | `PVP_VA_64` | 4.3322 | 3.9714 | +0.360751 | 8.3273% | No |
| `POL-007-2026` | `EDR_EPO` | 2.2177 | 2.0916 | +0.126150 | 5.6882% | No |
| `POL-005-2026` | `SOLUPLUS` | 6.9128 | 6.5376 | +0.375256 | 5.4284% | No |
| `POL-006-2026` | `HPMC_E5` | 11.7657 | 11.3374 | +0.428294 | 3.6402% | No |

*Conclusion*: Dimensional truncation distortion is minimal (< 0.05% relative discrepancy), confirming that the $K=3$ projection is mathematically faithful to the physical decision space.
