# Computational Method Documentation

**Platform**: PharmaPolySCOPE (Pharmaceutical Polymer Screening and Computational Optimization Platform)  
**Release**: `v1.5.0-FOUR-CRITERION-FREEZE`  
**Framework**: Master Research Framework V2.0  
**Implementation Package**: `asd_mcda`  
**Developer Attribution**: Developed by Tushar Mathapati  

---

## 1. Hansen Solubility Parameter (HSP) Distance and RED

**Implementation**: [`src/asd_mcda/compatibility/hsp_model.py`](file:///src/asd_mcda/compatibility/hsp_model.py)

### Equation 1 — Hansen Solubility Parameter Distance ($R_a$)

$$R_a = \sqrt{4(\delta_{D,\text{drug}} - \delta_{D,\text{polymer}})^2 + (\delta_{P,\text{drug}} - \delta_{P,\text{polymer}})^2 + (\delta_{H,\text{drug}} - \delta_{H,\text{polymer}})^2}$$

| Variable | Definition | Unit | Value (Indomethacin) |
| :--- | :--- | :---: | :---: |
| $\delta_D$ | Dispersion component | $\text{MPa}^{0.5}$ | 19.2 |
| $\delta_P$ | Polar component | $\text{MPa}^{0.5}$ | 7.9 |
| $\delta_H$ | Hydrogen bonding component | $\text{MPa}^{0.5}$ | 8.4 |
| $R_a$ | HSP Euclidean distance | $\text{MPa}^{0.5}$ | — |

**Reference**: Hansen CM. *Hansen Solubility Parameters: A User's Handbook*. 2nd ed. CRC Press; 2007.

### Equation 2 — Relative Energy Difference (RED)

$$\text{RED} = \frac{R_a}{R_0}$$

| Variable | Definition | Unit | Value (Indomethacin) |
| :--- | :--- | :---: | :---: |
| $R_0$ | Interaction radius of drug solubility sphere | $\text{MPa}^{0.5}$ | 8.0 |
| $\text{RED}$ | Relative Energy Difference | Dimensionless | — |

**Interpretation**: $\text{RED} \le 1.0$ indicates favorable HSP compatibility under the model criterion (Diagnostic 1); $\text{RED} > 1.0$ indicates progressively lower thermodynamic affinity.

### Equation 3 — Normalized HSP Compatibility Score ($s_{\text{HSP}}$)

$$s_{\text{HSP}} = \max\left(0,\; 1 - \frac{\text{RED}}{2}\right)$$

---

## 2. Flory–Huggins Interaction Parameter ($\chi$)

**Implementation**: [`src/asd_mcda/compatibility/flory_huggins.py`](file:///src/asd_mcda/compatibility/flory_huggins.py)

### Equation 4 — Lindvig Conversion for $\chi$

$$\chi = \alpha \cdot \frac{V_m}{RT}\left[(\delta_{D,\text{drug}} - \delta_{D,\text{polymer}})^2 + 0.25(\delta_{P,\text{drug}} - \delta_{P,\text{polymer}})^2 + 0.25(\delta_{H,\text{drug}} - \delta_{H,\text{polymer}})^2\right]$$

where $\alpha = 0.60$ is the global multiplicative correction factor applied to the bracketed sum (Lindvig et al. 2002).

| Variable | Definition | Unit | Value / Constant |
| :--- | :--- | :---: | :---: |
| $\alpha$ | Global Lindvig multiplicative correction factor | Dimensionless | 0.60 |
| $V_m$ | Drug molar volume | $\text{cm}^3/\text{mol}$ | 273.0 (Indomethacin) |
| $R$ | Universal gas constant | $\text{J}/(\text{mol}\cdot\text{K})$ | 8.314463 |
| $T$ | System reference temperature | $\text{K}$ | 298.15 |
| $\chi$ | Flory–Huggins interaction parameter | Dimensionless | — |

**Reference**: Lindvig T, Michelsen ML, Kontogeorgis GM. *Fluid Phase Equilib.* 2002;203:247–260.

### Equation 5 — Binary Critical Interaction Parameter ($\chi_c$)

$$\chi_c = \frac{1}{2}\left(1 + \frac{1}{\sqrt{r_2}}\right)^2$$

where:
- $r_1 = 1.0$ (small-molecule drug reference component, absorbed into the leading 1 term)
- $r_2 = V_{\text{polymer}} / V_{\text{drug}}$ (relative molar volume ratio)
- $V_{\text{polymer}} = M_n / \rho_{\text{polymer}}$ (derived from number-average molecular weight $M_n$ and density $\rho$)

**Scientific Diagnostic Role**: $\chi_c$ is evaluated at $T = 298.15\text{ K}$ as a secondary phase-boundary diagnostic ($\chi < \chi_c$; Diagnostic 2) and is **NOT** included in the MCDA score matrix $\mathbf{S}$.

### Equation 6 — Normalized Chi Compatibility Score ($s_\chi$)

$$s_\chi = \max(0,\; 1 - \chi)$$

---

## 3. Gordon–Taylor Glass Transition Temperature Prediction

**Implementation**: [`src/asd_mcda/compatibility/gordon_taylor.py`](file:///src/asd_mcda/compatibility/gordon_taylor.py)

### Equation 7 — Simha–Boyer Constant ($K$)

$$K = \frac{\rho_{\text{drug}} \cdot T_{g,\text{drug}}}{\rho_{\text{polymer}} \cdot T_{g,\text{polymer}}}$$

| Variable | Definition | Unit | Value (Indomethacin) |
| :--- | :--- | :---: | :---: |
| $\rho_{\text{drug}}$ | Amorphous density of drug | $\text{g/cm}^3$ | 1.22 |
| $T_{g,\text{drug}}$ | Glass transition temperature of drug | $\text{K}$ | 315.15 |
| $\rho_{\text{polymer}}$ | Polymer density | $\text{g/cm}^3$ | Carrier-specific |
| $T_{g,\text{polymer}}$ | Polymer glass transition temperature | $\text{K}$ | Carrier-specific |

**Reference**: Simha R, Boyer RF. *J. Chem. Phys.* 1962;37:1003–1007.

### Equation 8 — Gordon–Taylor Binary Composite $T_{g,\text{mix}}$

$$T_{g,\text{mix}} = \frac{w_1 T_{g,1} + K w_2 T_{g,2}}{w_1 + K w_2}$$

where subscript 1 denotes drug, subscript 2 denotes polymer, $w_1$ is drug weight fraction (default $w_1 = 0.30$), and $w_2 = 1 - w_1$.

**Reference**: Gordon M, Taylor JS. *J. Appl. Chem.* 1952;2:493–500.

### Equation 9 — Normalized Gordon–Taylor Compatibility Score ($s_{\text{GT}}$)

$$s_{\text{GT}} = \text{clip}\left(\frac{T_{g,\text{mix}} - (T_{g,\text{drug}} + 30)}{50},\; 0.0,\; 1.0\right)$$

*Higher predicted $T_{g,\text{mix}}$ indicates a larger glass-transition margin under the model assumptions; physical stability and recrystallization resistance require experimental confirmation.*

---

## 4. Four-Criterion Multi-Criteria Score Matrix ($\mathbf{S}$)

**Implementation**: [`src/asd_mcda/compatibility/matrix.py`](file:///src/asd_mcda/compatibility/matrix.py)

The compatibility score matrix integrates exactly four computationally-evaluated criteria:
$$\mathbf{S} = [s_{\text{HSP}},\; s_\chi,\; s_{\text{desc}},\; s_{\text{GT}}] \in [0, 1]^{N \times 4}$$

- Literature/evidence information ($s_{\text{lit}}$) is permanently excluded from MCDA and preserved strictly as provenance metadata.
- 2D molecular descriptor score ($s_{\text{desc}} = 0.2268$) is invariant across the reference 5-polymer set and retained for library generalizability.

---

## 5. Principal Component Analysis (PCA) & Policy A Subspace

**Implementation**: [`src/asd_mcda/integration/pca.py`](file:///src/asd_mcda/integration/pca.py)

To prevent collinearity distortion across thermodynamic criteria, PCA is applied to the column-standardized active score matrix $\mathbf{S}$:
1. Columns are standardized to zero mean and unit variance using `StandardScaler`.
2. Principal components are retained until cumulative explained variance ratio $\ge 95\%$ ($K=2$ retained components, explaining 100.0% variance).
3. **Policy A (Fixed Subspace Projection)**: Monte Carlo realization vectors $\mathbf{S}_{\text{sim}}$ are projected onto the established baseline PCA axes ($\mathbf{T}_{\text{sim}} = \mathbf{S}_{\text{sim}} \cdot \mathbf{P}_{\text{baseline}}$).

---

## 6. Analytic Hierarchy Process (AHP) Weight Elicitation

**Implementation**: [`src/asd_mcda/mcda/ahp.py`](file:///src/asd_mcda/mcda/ahp.py)

1. Pairwise comparison matrices $\mathbf{A}$ are elicited across retained components ($[PC_1:PC_2 = 2:1]$).
2. Priority weight vector $\mathbf{w} = [0.6667, 0.3333]$ is calculated via the principal eigenvector method ($\mathbf{A}\mathbf{w} = \lambda_{\max}\mathbf{w}$).
3. Consistency Ratio $\text{CR} = 0.0000 < 0.0800$ assesses the internal consistency of the expert pairwise comparison matrix (Diagnostic 3: PASS).

---

## 7. TOPSIS Multi-Criteria Decision Ranking

**Implementation**: [`src/asd_mcda/mcda/topsis.py`](file:///src/asd_mcda/mcda/topsis.py)

### Equation 10 — TOPSIS Closeness Coefficient ($C_L$)

$$C_L = \frac{D^-}{D^+ + D^-}$$

where $D^+$ is the Euclidean distance to the positive ideal solution ($\mathbf{A}^+$) and $D^-$ is the Euclidean distance to the negative ideal solution ($\mathbf{A}^-$).

---

## 8. Joint-Distribution Monte Carlo Uncertainty Quantification

**Implementation**: [`src/asd_mcda/uncertainty/monte_carlo.py`](file:///src/asd_mcda/uncertainty/monte_carlo.py)

Simultaneously perturbs 7 parameter uncertainty sources across $N = 10{,}000$ iterations (seed = 42) under Policy A:
- HSP components: $\pm 1.5\text{ MPa}^{0.5}$
- Flory–Huggins $\chi$: $\pm 25\%$
- $\text{Log}P$: $\pm 0.7$
- $T_{g,\text{drug}}$: $\pm 10.0\text{ K}$
- $T_{g,\text{polymer}}$: $\pm 3.0\text{ K}$
- Density $\rho$: $\pm 0.05\text{ g/cm}^3$
- AHP weights: $\pm 20\%$

**Output Metric**: Model-selection probability $P(\text{top-1})$, reflecting numerical ranking stability under assumed parameter uncertainty (not an experimental probability of success).
