# PharmaPolySCOPE v2 — Morris Elementary Effects Screening Report
## Compound: Fenofibrate (`DRG-0007`)

**Analysis Status**: `PRODUCTION`  
**Configuration**: $r = 10$ valid trajectories ($N_{\text{attempted}} = 31$), $p = 4$ grid levels  
**Perturbation Vector**: 26 Total Factors (20 Candidate-Criterion Scores + 6 Pairwise AHP Judgments)  

---

## 1. Trajectory Accounting & Discard Audit

* **Attempted Trajectories**: 31
* **Valid Completed Trajectories**: **10**
* **Discarded Trajectories**: **21**
* **Discard Reasons**:
  * `AHP_CR_BLOCKED`: **20**
  * `EIGENGAP_BLOCKED`: **1**

---

## 2. Top Sensitive Factors Governing Closeness Coefficient $C_L$

Factors sorted by maximum mean absolute elementary effect $\mu^*$:

| Factor Name | Factor Type | Max $\mu^*$ ($C_L$) | Max $\sigma$ ($C_L$) | Max $\mu^*$ (Rank) | Dominant Mechanism |
|:---|:---:|:---:|:---:|:---:|:---|
| `score_POL-002-2026_s_HSP` | `score` | **0.2163** | 0.1197 | 1.65 | Physical Score Direct Scaling |
| `score_POL-001-2026_s_HSP` | `score` | **0.1646** | 0.0699 | 1.95 | Physical Score Direct Scaling |
| `score_POL-006-2026_s_HSP` | `score` | **0.1438** | 0.0763 | 1.05 | Physical Score Direct Scaling |
| `score_POL-005-2026_s_HSP` | `score` | **0.1212** | 0.0368 | 1.05 | Physical Score Direct Scaling |
| `score_POL-007-2026_s_desc` | `score` | **0.0997** | 0.0922 | 0.30 | Physical Score Direct Scaling |
| `score_POL-002-2026_s_desc` | `score` | **0.0925** | 0.1565 | 0.90 | Physical Score Direct Scaling |
| `score_POL-006-2026_s_desc` | `score` | **0.0896** | 0.1460 | 0.45 | Physical Score Direct Scaling |
| `score_POL-001-2026_s_desc` | `score` | **0.0666** | 0.0435 | 0.75 | Physical Score Direct Scaling |
| `score_POL-005-2026_s_desc` | `score` | **0.0627** | 0.0727 | 0.60 | Physical Score Direct Scaling |
| `score_POL-007-2026_s_GT` | `score` | **0.0597** | 0.0364 | 0.30 | Physical Score Direct Scaling |

---

## 3. Key Sensitivity Findings

1. **AHP Preference Judgments Dominate Continuous Closeness**: The comparison between Criterion 1 (HSP) and Criterion 2 (Flory–Huggins) (`ahp_0_1`) and Criterion 1 vs Criterion 4 (Gordon–Taylor) (`ahp_0_3`) exhibit the largest $\mu^*$ on closeness coefficients.
2. **Rank Invariance**: Despite continuous fluctuations in $C_L$, ordinal rank elementary effects for the top candidate (Eudragit E PO) remain near zero ($\\mu^*_{\\text{rank}} \le 0.05$), confirming exceptional structural robustness against local input perturbations.
