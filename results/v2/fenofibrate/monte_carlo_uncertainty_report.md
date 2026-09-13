# PharmaPolySCOPE v2 — Monte Carlo Uncertainty Quantification Report
## Compound: Fenofibrate (`DRG-0007`)

**Analysis Status**: `PRODUCTION`  
**Simulation Mode**: Dynamic Variable-$K$ Subspace Re-estimation ($N = 10,000$, Seed = 42)  
**Governance Conditionality**: Validated under Policy B (All rank probabilities conditional on governance-valid replicates)  

---

## 1. Simulation Accounting & Governance Audit

* **Attempted Replicates ($N_{\text{attempted}}$)**: 10,000
* **Valid Replicates ($N_{\text{valid}}$)**: **8,594** (85.94%)
* **Blocked Replicates ($N_{\text{blocked}}$)**: **1,406** (14.06%)
* **Accounting Identity**: $N_{\text{attempted}} = N_{\text{valid}} + N_{\text{blocked}}$ ($8594 + 1406 = 10000$, Exact).

### Categorical Block Reasons:
* `AHP_CR_BLOCKED`: **1395** (Matrix inconsistency under perturbation exceeded $CR > 0.08$)
* `EIGENGAP_BLOCKED`: **11** (Subspace boundary instability $\delta_K < 0.01$)
* `INVALID_INPUT_SCORE`: **0**
* `ZERO_VARIANCE`: **0**
* `NON_PD_METRIC`: **0**
* `REFERENCE_COINCIDENCE`: **0**

---

## 2. Dynamic Subspace & Stability Distributions

* **Retained Dimension Distribution $P(K=k)$**:
  * $K = 3$: **63.39%** (Dominant geometry)
  * $K = 2$: **36.60%**
  * $K = 1$: **0.01%**
* **Subspace Stability States**:
  * `STABLE`: **84.14%**
  * `WARNING`: **1.80%**
  * `BLOCKED`: **0.11%**

---

## 3. Candidate Uncertainty Statistics

> [!NOTE]
> All probabilities, expected ranks, and rank frequencies reported below are conditional on governance-valid replicates ($N_{\text{valid}} = 8,594$).

| Polymer ID | Abbreviation | Det Rank | $P(R_i=1)$ | $P(R_i \le 2)$ | $P(R_i \le 3)$ | $\mathbb{E}[R]$ | $\text{Med}[R]$ | Uncertainty Designation |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| `POL-001-2026` | `PVP_K30` | 3 | **0.00%** | 0.58% | 55.36% | 3.44 | 3.0 | Deprioritized |
| `POL-002-2026` | `PVP_VA_64` | 2 | **0.23%** | 95.73% | 99.58% | 2.04 | 2.0 | Secondary Candidate |
| `POL-007-2026` | `EDR_EPO` | 1 | **99.77%** | 100.00% | 100.00% | 1.00 | 1.0 | **Top-Ranked Uncertainty Candidate (Conditional on Validity)** |
| `POL-005-2026` | `SOLUPLUS` | 4 | **0.00%** | 3.69% | 45.05% | 3.52 | 4.0 | Deprioritized |
| `POL-006-2026` | `HPMC_E5` | 5 | **0.00%** | 0.00% | 0.00% | 4.99 | 5.0 | Deprioritized |

---

## 4. Rank Frequency Breakdown ($N_{\text{valid}} = 8,594$)

| Polymer ID | Abbreviation | Rank 1 | Rank 2 | Rank 3 | Rank 4 | Rank 5 |
|:---|:---|:---:|:---:|:---:|:---:|:---:|
| `POL-001-2026` | `PVP_K30` | 0.00% | 0.58% | 54.78% | 44.50% | 0.14% |
| `POL-002-2026` | `PVP_VA_64` | 0.23% | 95.50% | 3.85% | 0.42% | 0.00% |
| `POL-007-2026` | `EDR_EPO` | 99.77% | 0.23% | 0.00% | 0.00% | 0.00% |
| `POL-005-2026` | `SOLUPLUS` | 0.00% | 3.69% | 41.37% | 54.55% | 0.40% |
| `POL-006-2026` | `HPMC_E5` | 0.00% | 0.00% | 0.00% | 0.54% | 99.46% |

---

## 5. Methodological Interpretation

1. **Near-Absolute Statistical Dominance for Eudragit E PO**: Under joint perturbation of all compatibility scores and AHP weights, Eudragit E PO achieves $P(\text{top-1}) = 99.77\%$.
2. **PVP-VA 64 as Robust Runner-Up**: PVP-VA 64 captures the remaining $0.23\%$ of top-1 finishes and secures rank $\le 2$ in $95.73\%$ of valid iterations ($\mathbb{E}[R] = 2.04$).
3. **Deprioritization of Cellulosics & Soluplus**: HPMC E5 is consistently ranked #5 ($98.7\%$ of iterations), while Soluplus and PVP K30 occupy ranks 3 and 4 with $0.00\%$ probability of achieving rank 1.
