# PharmaPolySCOPE v2 — Computational Screening & Decision Robustness Report
## Candidate Compound: Fenofibrate (`DRG-0007`)

**Specification**: `2.0.0-SPEC-PHASE0-PATCH2` & `2.0.0-SPEC-PHASE5.2-FINAL`  
**Evaluation Engine**: SP-PRP-TOPSIS on Dynamic Variable-K Eigenspaces  
**Target Drug**: Fenofibrate (`DRG-0007`, `data/user_drugs/drg-0007.json`)  
**Polymer Cohort**: Active 5-Polymer Reference Library (`config/polymers/polymer_library_v3_five_polymers.csv`)  
**Input Gate Status**: `BLOCKED — INPUT INTEGRITY FAILURE` (diagnostic fallback execution reported)  
**Computational Status**: `COMPUTATIONAL CANDIDATE SCREENING — Prospective Laboratory Validation Pending`  

---

## 1. Executive Summary & Core Findings

1. **Input Integrity Status**: Formally **`BLOCKED — INPUT INTEGRITY FAILURE`**. Profile `data/user_drugs/drg-0007.json` lacks an experimental/measured amorphous density (`density_amorphous_g_cm3: null`). Under strict Phase 6 acceptance rules and Constraint 6, replacing missing amorphous density with crystalline density is prohibited for formal production release. However, under the engine's built-in diagnostic fallback architecture (`get_preferred_density()`), crystalline density ($1.296\,\text{g/cm}^3$) is utilized, enabling complete deterministic, Monte Carlo ($N=10{,}000$), and Morris ($r=10$) diagnostic execution.
2. **Top-Ranked Deterministic Candidate**: **Eudragit E PO** (`POL-007-2026`) ranks #1 deterministically with closeness coefficient $C_L = 0.7413$, driven by exceptional thermodynamic miscibility ($s_{\text{HSP}} = 0.8961$, $s_{\chi} = 0.9591$).
3. **Top-Ranked Uncertainty Candidate (Conditional on Validity)**: **Eudragit E PO** achieves near-absolute ranking dominance under Monte Carlo perturbation ($P(\text{top-1}) = 99.77\%$, $P(\text{top-2}) = 100.0\%$, expected rank $\mathbb{E}[R] = 1.00$).
4. **Primary Competitor / Runner-Up**: **PVP-VA 64** (`POL-002-2026`) is the unequivocal deterministic runner-up ($C_L = 0.6271$, $P(\text{top-2}) = 95.73\%$, expected rank $\mathbb{E}[R] = 2.04$).
5. **Critical Physical & Mechanistic Divergence**: While the algorithm heavily weights thermodynamic affinity ($w_{\text{HSP}} = 0.3853, w_{\chi} = 0.3109$), Fenofibrate is a **neutral ester** lacking an acidic proton for salt-bridge ionic complexation with Eudragit E PO's tertiary amines. Furthermore, Fenofibrate possesses an extremely low glass transition temperature ($T_g = 247.35\,\text{K} \ [-25.8^\circ\text{C}]$), making pure amorphous fenofibrate a supercooled liquid at room temperature with extreme recrystallization kinetics. High-$T_g$ neutral polymers like **PVP-VA 64** ($s_{\text{GT}} = 1.0000$) offer vital anti-plasticization kinetic barrier protection that Eudragit E PO ($s_{\text{GT}} = 0.4202$) lacks.

---

## 2. Section A: Drug Profile Forensic Audit

| Parameter | Stored Value | Physical Unit | Data Quality / Provenance |
|:---|:---|:---|:---|
| **Drug Identifier** | `DRG-0007` | — | User Drug Profile |
| **Generic Name** | Fenofibrate | — | Approved Monograph Name |
| **Chemical Formula / SMILES** | `CC(C)OC(=O)C(C)(C)OC1=CC=C(C=C1)C(=O)C2=CC=C(C=C2)Cl` | — | Canonical Neutral Ester SMILES |
| **File Path** | `data/user_drugs/drg-0007.json` | — | Authoritative Profile Location |
| **SHA-256 Checksum** | `9a54b457de02c1af7d574f4b613256ae14e26ae95c059d09d94bad4d4b814e4c` | — | Cryptographic Verification Hash |
| **Molecular Weight ($M_w$)** | 360.84 | g/mol | Experimental Monograph |
| **Melting Point ($T_m$)** | 353.65 (80.5 °C) | K | Experimental DSC |
| **Glass Transition ($T_g$)** | 247.35 (-25.8 °C) | K | Experimental Hyper-DSC |
| **Crystalline Density ($\rho_{\text{cryst}}$)** | 1.296 | g/cm³ | Single-Crystal X-ray Diffraction |
| **Amorphous Density ($\rho_{\text{amorph}}$)** | `null` | g/cm³ | **MISSING DEFECT** |
| **HSP Dispersion ($\delta_D$)** | 16.25 | MPa$^{0.5}$ | Literature / Experimental Fit |
| **HSP Polar ($\delta_P$)** | 4.11 | MPa$^{0.5}$ | Literature / Experimental Fit |
| **HSP Hydrogen Bonding ($\delta_H$)** | 6.68 | MPa$^{0.5}$ | Literature / Experimental Fit |
| **HSP Radius of Interaction ($R_0$)** | 7.50 | MPa$^{0.5}$ | Literature / Experimental Fit |
| **Molar Volume ($V_m$)** | `null` | cm³/mol | Calculated via Preferred Density ($278.43\,\text{cm}^3/\text{mol}$) |

### Input Gate Classification
- **Strict Phase 6 Gate**: **`BLOCKED — INPUT INTEGRITY FAILURE`**.
  - Defect: `density_amorphous_g_cm3: null`. Under scientific constraint #6, substitution of crystalline density for amorphous density is disallowed for production sign-off.
- **Diagnostic Execution Mode**: The v1.5 `Drug` domain entity invokes `get_preferred_density()`, falling back to $\rho_{\text{cryst}} = 1.296\,\text{g/cm}^3$. All subsequent sections report this diagnostic fallback execution.

---

## 3. Section B: Deterministic Multi-Criteria Decision Matrix

### 3.1 Raw Compatibility Scores $\mathbf{S}$
Evaluated across the 4 canonical physical criteria:
$$\mathbf{S} = [s_{\text{HSP}}, \; s_{\chi}, \; s_{\text{desc}}, \; s_{\text{GT}}]$$

| Polymer ID | Abbreviation | Name | $s_{\text{HSP}}$ | $s_{\chi}$ | $s_{\text{desc}}$ | $s_{\text{GT}}$ |
|:---|:---|:---|:---:|:---:|:---:|:---:|
| `POL-007-2026` | `EDR_EPO` | Eudragit E PO | **0.8961** | **0.9591** | **0.6628** | 0.4202 |
| `POL-002-2026` | `PVP_VA_64` | PVP-VA 64 | 0.6447 | 0.5215 | 0.5751 | **1.0000** |
| `POL-001-2026` | `PVP_K30` | PVP K30 | 0.5419 | 0.2045 | 0.5427 | **1.0000** |
| `POL-005-2026` | `SOLUPLUS` | Soluplus | 0.5473 | 0.2231 | 0.5994 | 0.6812 |
| `POL-006-2026` | `HPMC_E5` | HPMC E5 | 0.4400 | 0.0000 | 0.3532 | **1.0000** |

*Cohort Column Means*: $\bar{s} = [0.6140, \; 0.3816, \; 0.5466, \; 0.8203]$  
*Cohort Sample Standard Deviations*: $\sigma_s = [0.1552, \; 0.3332, \; 0.1044, \; 0.2351]$

### 3.2 Standardized Decision Matrix $\mathbf{Z}$
Standardized via cohort z-scoring ($ddof=0$):

| Polymer ID | Abbreviation | $z_{\text{HSP}}$ | $z_{\chi}$ | $z_{\text{desc}}$ | $z_{\text{GT}}$ |
|:---|:---|:---:|:---:|:---:|:---:|
| `POL-007-2026` | `EDR_EPO` | +1.8176 | +1.7330 | +1.1125 | -1.7020 |
| `POL-002-2026` | `PVP_VA_64` | +0.1978 | +0.4197 | +0.2725 | +0.7645 |
| `POL-001-2026` | `PVP_K30` | -0.4646 | -0.5316 | -0.0377 | +0.7645 |
| `POL-005-2026` | `SOLUPLUS` | -0.4299 | -0.4758 | +0.5052 | -0.5916 |
| `POL-006-2026` | `HPMC_E5` | -1.1209 | -1.1453 | -1.8524 | +0.7645 |

### 3.3 Spectral Decomposition & Subspace Stability
- **Eigenvalues of Correlation Matrix**:
  $$\lambda = [3.390282, \; 0.332640, \; 0.274278, \; 0.002799]$$
- **Explained Variance Ratio**:
  $$\text{EVR} = [84.76\%, \; 8.32\%, \; 6.86\%, \; 0.07\%]$$
- **Cumulative Variance**:
  $$\text{CV} = [84.76\%, \; 93.07\%, \; 99.93\%, \; 100.00\%]$$
- **Dynamic Dimension Selection**:
  Cumulative variance threshold $\ge 95\%$ selects **$K = 3$** ($99.93\% > 95.0\%$).
- **Davis-Kahan Boundary Eigengap**:
  $$\delta_3 = \lambda_3 - \lambda_4 = 0.274278 - 0.002799 = 0.271479 \ge 0.10$$
- **Stability Classification**: **`STABLE`**. Subspace basis perturbation bound $\sin\Theta \le \frac{2\|\mathbf{E}\|_2}{\delta_3} \ll 1$.

---

## 4. Section C: External AHP Governance & Weights

### 4.1 Preference Pairwise Comparison Matrix
Evaluated on the standardized criteria space:
$$A = \begin{bmatrix}
1.0 & 2.0 & 3.0 & 2.0 \\
0.5 & 1.0 & 5.0 & 2.0 \\
0.3333 & 0.2 & 1.0 & 0.5 \\
0.5 & 0.5 & 2.0 & 1.0
\end{bmatrix}$$

### 4.2 Eigenvector Solution & Consistency Gate
- **Priority Weight Vector $\mathbf{w}$**:
  $$\mathbf{w} = [0.3853, \; 0.3109, \; 0.0984, \; 0.2054]$$
  *(HSP miscibility: 38.53%, Flory-Huggins $\chi$: 31.09%, Gordon-Taylor: 20.54%, Descriptors: 9.84%)*
- **Principal Eigenvalue**: $\lambda_{\max} = 4.1319$
- **Consistency Index**: $\text{CI} = \frac{\lambda_{\max} - p}{p - 1} = \frac{4.1319 - 4}{3} = 0.04397$
- **Consistency Ratio**: $\text{CR} = \frac{\text{CI}}{\text{RI}_4} = \frac{0.04397}{0.89} = \mathbf{0.0494} < 0.08$
- **Governance Gate**: **`ACCEPTED`**.

---

## 5. Section D: SP-PRP-TOPSIS Geometry & Deterministic Ranking

Projecting reference points $z^+ = \max_i z_{ij}$ and $z^- = \min_i z_{ij}$ into the $K=3$ eigenspace preserves reference extremal properties. The metric tensor $M_K = V_K^T \operatorname{diag}(\mathbf{w}) V_K$ ensures rigorous geometric invariance.

| Rank | Polymer ID | Abbreviation | Closeness $C_L$ | Distance to Ideal $D^+$ | Distance to Anti-Ideal $D^-$ | Status |
|:---:|:---|:---|:---:|:---:|:---:|:---|
| **1** | `POL-007-2026` | `EDR_EPO` | **0.7413** | 1.4462 | 4.1443 | **Top-Ranked Deterministic Candidate** |
| **2** | `POL-002-2026` | `PVP_VA_64` | **0.6271** | 1.9928 | 3.3518 | Runner-Up |
| **3** | `POL-001-2026` | `PVP_K30` | **0.5212** | 2.6186 | 2.8504 | Moderate Affinity |
| **4** | `POL-005-2026` | `SOLUPLUS` | **0.5124** | 2.5569 | 2.6864 | Closely Contested with PVP K30 |
| **5** | `POL-006-2026` | `HPMC_E5` | **0.4039** | 3.3671 | 2.2819 | Lowest Affinity |

*Closeness Spread*: Separation between Rank 1 (`EDR_EPO`) and Rank 2 (`PVP_VA_64`) is $\Delta C_L = 0.1142$, indicating decisive deterministic separation.

---

## 6. Section E: Metric Truncation Diagnostics

To verify that discarding the 4th principal component does not introduce geometric distortion, truncation diagnostics are calculated per alternative:

| Polymer ID | Abbreviation | $D_{\text{full}}^2$ | $D_K^2$ ($K=3$) | Signed Discrepancy | Relative Discrepancy |
|:---|:---|:---:|:---:|:---:|:---:|
| `POL-001-2026` | `PVP_K30` | 7.169292 | 6.857182 | +0.312110 | $4.35 \times 10^{-2}$ |
| `POL-002-2026` | `PVP_VA_64` | 4.332159 | 3.971408 | +0.360751 | $8.33 \times 10^{-2}$ |
| `POL-007-2026` | `EDR_EPO` | 2.217742 | 2.091592 | +0.126150 | $5.69 \times 10^{-2}$ |
| `POL-005-2026` | `SOLUPLUS` | 6.912838 | 6.537582 | +0.375256 | $5.43 \times 10^{-2}$ |
| `POL-006-2026` | `HPMC_E5` | 11.765710 | 11.337416 | +0.428294 | $3.64 \times 10^{-2}$ |

*Diagnostic Conclusion*: All relative discrepancies satisfy $\epsilon_{\text{rel}} < 0.10$. Truncation error is uniformly distributed and negligible.

---

## 7. Section F: Monte Carlo Uncertainty Propagation ($N=10{,}000$)

### 7.1 Replicate Accounting & Governance Breakdown
- **Replicates Generated**: $N = 10{,}000$
- **Valid Replicates**: $N_{\text{valid}} = 8594$ ($85.94\%$)
- **Blocked Replicates**: $N_{\text{blocked}} = 1406$ ($14.06\%$)
  - `AHP_CR_BLOCKED`: $1395$ ($99.22\%$ of all blocked replicates)
  - `EIGENGAP_BLOCKED` ($\delta_K < 0.03$): $11$ ($0.78\%$ of all blocked replicates)
  - Other block reasons: $0$

### 7.2 Subspace Dimension & Stability Distributions
- **$K$ Distribution**:
  - $K=1$: $0.01\%$
  - $K=2$: $36.60\%$
  - $K=3$: $63.39\%$
  - $K=4$: $0.00\%$
- **Stability Distribution Across Valid Replicates**:
  - `STABLE` ($\delta_K \ge 0.10$): $84.14\%$
  - `WARNING` ($0.03 \le \delta_K < 0.10$): $1.80\%$
  - `BLOCKED` ($\delta_K < 0.03$): $0.11\%$

### 7.3 Candidate Uncertainty Records
*Conditional on validity ($N_{\text{valid}} = 8594$)*:

| Polymer ID | Abbreviation | Det Rank | $P(\text{top-1})$ | $P(\text{top-2})$ | $P(\text{top-3})$ | Expected Rank $\mathbb{E}[R]$ | Median Rank | Rank Distribution [1, 2, 3, 4, 5] (%) |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `POL-007-2026` | `EDR_EPO` | **1** | **99.77%** | 100.0% | 100.0% | **1.00** | **1.0** | [99.77, 0.23, 0.0, 0.0, 0.0] |
| `POL-002-2026` | `PVP_VA_64` | **2** | 0.23% | **95.73%** | 99.58% | **2.04** | **2.0** | [0.23, 95.50, 3.85, 0.42, 0.0] |
| `POL-001-2026` | `PVP_K30` | **3** | 0.00% | 0.58% | 55.36% | **3.44** | **3.0** | [0.0, 0.58, 54.78, 44.50, 0.14] |
| `POL-005-2026` | `SOLUPLUS` | **4** | 0.00% | 3.69% | 45.05% | **3.52** | **4.0** | [0.0, 3.69, 41.37, 54.55, 0.40] |
| `POL-006-2026` | `HPMC_E5` | **5** | 0.00% | 0.00% | 0.00% | **4.99** | **5.0** | [0.0, 0.0, 0.0, 0.54, 99.46] |

*Robustness Finding*: Eudragit E PO achieves an overwhelming $99.77\%$ top-1 selection probability under simultaneous $\pm 10\%$ score and $\pm 15\%$ AHP perturbations. PVP-VA 64 securely occupies Rank 2 ($95.73\%$). PVP K30 and Soluplus engage in a close contest for Rank 3/4 ($55.36\%$ vs $45.05\%$).

---

## 8. Section G: Morris Global Elementary Effects Screening ($r=10$)

- **Trajectories Attempted**: $31$
- **Valid Trajectories Acquired**: $r = 10$ ($100\%$ target quota achieved)
- **Discarded Trajectories**: $21$ ($20$ due to `AHP_CR > 0.08`, $1$ due to `EIGENGAP < 0.03`)

### Top Influential Factors on Closeness Coefficient ($C_L$) and Rank

| Factor Name | Category | Max $\mu^*$ ($C_L$) | Max $\sigma$ ($C_L$) | Max $\mu^*$ (Rank) | Max $\sigma$ (Rank) | Primary Impact Alternative |
|:---|:---|:---:|:---:|:---:|:---:|:---|
| `score_POL-002-2026_s_HSP` | Score | **0.2163** | 0.1197 | 1.65 | 1.49 | `PVP_VA_64` (Rank stability) |
| `score_POL-001-2026_s_HSP` | Score | **0.1646** | 0.0699 | 1.95 | 1.42 | `PVP_K30` (Rank 3 vs 4 competition) |
| `score_POL-006-2026_s_HSP` | Score | **0.1438** | 0.0763 | 1.05 | 1.01 | `HPMC_E5` |
| `score_POL-005-2026_s_HSP` | Score | **0.1212** | 0.0368 | 1.05 | 1.01 | `SOLUPLUS` |
| `score_POL-007-2026_s_desc` | Score | **0.0997** | 0.0922 | 0.30 | 0.95 | `EDR_EPO` |
| `score_POL-002-2026_s_desc` | Score | **0.0925** | 0.1565 | 0.90 | 1.05 | `PVP_VA_64` |
| `score_POL-006-2026_s_desc` | Score | **0.0896** | 0.1460 | 0.45 | 0.85 | `HPMC_E5` |
| `score_POL-001-2026_s_desc` | Score | **0.0666** | 0.0435 | 0.75 | 0.79 | `PVP_K30` |
| `score_POL-007-2026_s_GT` | Score | **0.0597** | 0.0364 | 0.30 | 0.63 | `EDR_EPO` |
| `score_POL-002-2026_s_chi` | Score | **0.0588** | 0.0460 | 0.45 | 0.72 | `PVP_VA_64` |
| `score_POL-007-2026_s_HSP` | Score | **0.0502** | 0.0470 | 0.75 | 1.46 | `EDR_EPO` |
| `ahp_s_HSP_s_GT` | AHP | **0.0110** | 0.0078 | 0.30 | 0.71 | AHP trade-off: Miscibility vs Anti-Plasticization |

*Sensitivity Insights*: The ranking responds most sensitively to HSP scores of the mid-tier polymers (`PVP_VA_64` and `PVP_K30`), which modulate the coordinate space boundaries. Elementary effects of AHP weights are an order of magnitude smaller than direct compatibility scores.

---

## 9. Section H: Rank Invariance & Switching Dynamics

1. **Rank 1 Invariance**: Eudragit E PO's Rank 1 position is almost completely invariant ($99.77\%$ top-1 probability). Only extreme, simultaneous multi-parameter perturbations (driving Eudragit E PO's scores down while boosting PVP-VA 64's HSP score) permit PVP-VA 64 to capture Rank 1 ($0.23\%$).
2. **Rank 2 Invariance**: PVP-VA 64 is exceptionally stable at Rank 2 ($95.73\%$), dropping to Rank 3 in only $3.85\%$ of replicates.
3. **The 3 vs 4 Dynamic**: The most active switching dynamic in the Fenofibrate system occurs between **PVP K30** (deterministic rank 3, $C_L = 0.5212$) and **Soluplus** (deterministic rank 4, $C_L = 0.5124$). Their deterministic closeness difference is only $\Delta C_L = 0.0088$. In Monte Carlo simulation, PVP K30 secures Rank 3 in $54.78\%$ of replicates, while Soluplus captures Rank 3 in $41.37\%$.
4. **Rank 5 Invariance**: HPMC E5 is firmly locked at Rank 5 ($99.46\%$), due to its very poor thermodynamic compatibility scores with lipophilic Fenofibrate ($s_\chi = 0.0000, s_{\text{HSP}} = 0.4400$).

---

## 10. Section I: Chemical & Thermodynamic Mechanistic Forensics

Why does the algorithm predict this exact hierarchy?
1. **Lipophilic Dispersion Dominance**: Fenofibrate has a low polar parameter ($\delta_P = 4.11\,\text{MPa}^{0.5}$) and modest hydrogen bonding ($\delta_H = 6.68\,\text{MPa}^{0.5}$), with dominant dispersion ($\delta_D = 16.25\,\text{MPa}^{0.5}$).
2. **Eudragit E PO Affinity**: Eudragit E PO is an amino-methacrylate copolymer with low polarity ($\delta_P = 5.2\,\text{MPa}^{0.5}$) and low hydrogen bonding ($\delta_H = 6.5\,\text{MPa}^{0.5}$). The resulting Hansen distance is minuscule:
   $$R_a = \sqrt{4(16.25 - 16.8)^2 + (4.11 - 5.2)^2 + (6.68 - 6.5)^2} = 1.564\,\text{MPa}^{0.5}$$
   With interaction radius $R_0 = 7.5\,\text{MPa}^{0.5}$, $\text{RED} = 0.2085 \ll 1$, yielding $s_{\text{HSP}} = 0.8961$. The corresponding Flory-Huggins interaction parameter is $\chi = 0.0409$, yielding $s_\chi = 0.9591$.
3. **PVP-VA 64 vs PVP K30**: Vinyl acetate monomers reduce the hygroscopicity and polarity of PVP-VA 64 relative to homopolymer PVP K30, improving lipophilic drug compatibility ($s_{\text{HSP}} = 0.6447$ vs $0.5419$, $s_\chi = 0.5215$ vs $0.2045$).
4. **HPMC E5 Penalty**: Cellulosic HPMC E5 is rich in hydroxyl groups ($\delta_H = 12.0\,\text{MPa}^{0.5}$), resulting in massive hydrogen-bonding mismatch with Fenofibrate ($R_a = 7.02\,\text{MPa}^{0.5}, \chi = 1.018$), driving $s_\chi$ to $0.0000$.

---

## 11. Section J: Scientific Realities vs Computational Artifacts

> [!WARNING]
> ### Critical Formulation Warning: Model Prediction vs Physical Reality
> The computational model identifies **Eudragit E PO** as the Top-Ranked Uncertainty Candidate ($99.77\%$). However, a formulator must recognize critical physical limitations:
> 
> 1. **Absence of Salt-Bridge / Ionic Complexation**: In our validated Ibuprofen and Indomethacin evaluations, Eudragit E PO's success is physically driven by strong acid-base ionic interactions between carboxylic acid moieties and Eudragit's tertiary amine groups. Fenofibrate is an **ester**, entirely lacking acidic functional groups. The affinity predicted here is purely non-specific dispersive Van der Waals matching.
> 2. **Extreme Anti-Plasticization Deficit ($T_g$ Risk)**:
>    - Pure amorphous Fenofibrate has a sub-zero glass transition: $T_g = 247.35\,\text{K} \ (-25.8^\circ\text{C})$. At room temperature ($298.15\,\text{K}$), unformulated amorphous fenofibrate is in the supercooled liquid state and crystallizes almost instantaneously.
>    - Eudragit E PO has the lowest $T_g$ in the polymer library ($323.15\,\text{K} \ [50^\circ\text{C}]$). The Gordon-Taylor predicted mixture $T_g$ for a $30\%$ drug load is only $298.8\,\text{K} \ (25.6^\circ\text{C})$ — dangerously close to room temperature storage, yielding $s_{\text{GT}} = 0.4202$.
>    - In sharp contrast, **PVP-VA 64** ($T_g = 378.15\,\text{K}$) raises $T_{g,\text{mix}}$ to $338.9\,\text{K} \ (65.8^\circ\text{C})$, and **PVP K30** ($T_g = 441.15\,\text{K}$) raises it to $383.0\,\text{K} \ (110^\circ\text{C}$), providing an enormous kinetic anti-plasticization barrier ($s_{\text{GT}} = 1.0000$).
> 3. **Commercial & Published Reality**: In pharmaceutical industry practice, commercial fenofibrate ASDs and published literature overwhelmingly utilize **PVP-VA 64** or surfactant-mediated solid dispersions (e.g., Soluplus or TPGS combinations). Formulating fenofibrate in Eudragit E PO risks rapid phase separation and crystallization under accelerated stability conditions ($40^\circ\text{C}/75\%\,\text{RH}$).

---

## 12. Section K: Input Integrity Failure Post-Mortem

- **Root Cause**: `data/user_drugs/drg-0007.json` was created with `density_amorphous_g_cm3: null`.
- **Methodological Impact**: The Gordon-Taylor Simha-Boyer constant $K = \frac{\rho_1 T_{g,1}}{\rho_2 T_{g,2}}$ requires amorphous density. Using crystalline density ($1.296\,\text{g/cm}^3$ instead of expected amorphous $\approx 1.20\,\text{g/cm}^3$) artificially elevates the drug density by $\approx 8\%$, which slightly overestimates the plasticizing impact on mixture $T_g$.
- **Remediation Required for Phase 6 Formal Release**:
  Obtain hyper-DSC or pycnometric amorphous density for Fenofibrate ($\approx 1.22\,\text{g/cm}^3$) from literature, update the JSON schema, and re-execute.

---

## 13. Section L: Actionable Pre-Laboratory Formulation Shortlist

Based on the synthesis of computational affinity and physical chemistry:

1. **Dual Formulation Strategy**:
   - **Formulation A (Thermodynamic Benchmark)**: **Eudragit E PO** (`POL-007-2026`). Test at lower drug loading ($\le 20\%\,\text{w/w}$) to prevent mixture $T_g$ depression below $30^\circ\text{C}$.
   - **Formulation B (Recommended Kinetic Stability Leader)**: **PVP-VA 64** (`POL-002-2026`). Ranked #2 computationally ($C_L = 0.6271, P(\text{top-2}) = 95.73\%$), this carrier provides both good miscibility ($s_{\text{HSP}} = 0.6447$) and robust glass transition anti-plasticization ($s_{\text{GT}} = 1.0000, T_{g,\text{mix}} = 65.8^\circ\text{C}$).
2. **Formulation C (Solubilization Alternative)**: **Soluplus** (`POL-005-2026`). Provides surfactant micellar solubilization in aqueous dissolution, despite moderate GT elevation ($s_{\text{GT}} = 0.6812$).
3. **Polymer to Exclude**: **HPMC E5** (`POL-006-2026`). Severe thermodynamic mismatch ($s_\chi = 0.0000$, rank 5 in $99.46\%$ of MC replicates) indicates high risk of amorphous-amorphous phase separation during spray-drying.
4. **Recommended Technology**: Spray-drying from acetone/isopropanol or dichloromethane/ethanol mixtures. For Eudragit E PO, Hot Melt Extrusion (HME) is feasible due to its low $T_g$ ($50^\circ\text{C}$) and low melt viscosity.

---

## 14. Section M: Scientific Disclaimers & What the Model Cannot Claim

> [!CAUTION]
> 1. **Prediction, Not Experimental Proof**: All rankings, closeness coefficients, and probabilities reported herein are **computational candidate predictions** derived from mathematical models. They do NOT constitute proof of formulation success, bioavailability enhancement, or physical stability.
> 2. **No Claim of Long-Term Physical Stability**: The computational engine does not model nucleation kinetics, crystal growth, or moisture plasticization.
> 3. **Input Gate Status**: Formal certification is withheld until experimental amorphous density is supplied to replace the diagnostic fallback.

---

## 15. Section N: Provenance & Reproducibility Hashes

| Entity | Hash / Identifier |
|:---|:---|
| **Drug Profile File** | `data/user_drugs/drg-0007.json` |
| **Drug Profile SHA-256** | `9a54b457de02c1af7d574f4b613256ae14e26ae95c059d09d94bad4d4b814e4c` |
| **Polymer Library File** | `config/polymers/polymer_library_v3_five_polymers.csv` |
| **Polymer Library SHA-256**| `24cd6c4092788cb7266d2ea34e82b6dfe193b5cfb91e22c0dff66b0abc9088ff` |
| **Baseline Git Commit** | `31eee4d9bb1cc57b9185f9f958e225d51634c871` |
| **Analysis Fingerprint** | `03310cb233aa93e1104d498aa2b972e3a13a968600aa6fc138096c73919e9cae` |
| **MC Simulation ID** | `mc-sim-3a1e6f4de9b1` |
| **Morris Analysis ID** | `morris-8fae6eb5fbe6` |
| **Random Seed** | `42` |
| **Replication Command** | `& "python" scratch/run_fenofibrate_itraconazole_diagnostics.py` |
