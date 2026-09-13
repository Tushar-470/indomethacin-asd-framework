# PharmaPolySCOPE v2 — Monte Carlo Uncertainty Report
## Stochastic Uncertainty Propagation Envelope ($N=10,000$ Replicates)

**Specification**: `2.0.0-SPEC-PHASE5.2-FINAL`  
**Outer Layer Design**: Exact `VariableKEngine.evaluate(...)` on every replicate  
**Perturbation Parameters**:
- Pre-truncation Latent Gaussian Score Standard Deviation: $\sigma_{\text{score}} = 0.05$ (Domain $[0, 1]$)
- Analytical Log-Space AHP Perturbation: $\sigma_{\text{AHP}} = 0.15$ with exact reciprocity ($|a_{ji} a_{ij} - 1| < 10^{-12}$)
**Pseudorandom Generator**: PCG64 (`numpy.random.default_rng(42)`)  
**Status**: COMPUTATIONAL CANDIDATE SCREENING  

---

## 1. Executive Summary

Monte Carlo uncertainty quantification propagates joint score uncertainty and expert preference perturbation through the complete variable-dimension eigensystem and SP-PRP-TOPSIS pipeline. In accordance with `2.0.0-SPEC-PHASE5.2-FINAL`, every replicate solves fresh cohort moments and eigensystems.

Strict replicate accounting conservation:
$$N_{\text{generated}} \equiv N_{\text{valid}} + N_{\text{blocked}}$$

> [!IMPORTANT]
> **Methodological Statement on Conditional Sample Space**:  
> All candidate selection probabilities ($P(\text{top-1})$, $P(\text{top-k})$), rank frequencies, expected ranks ($\mathbb{E}[R]$), and median ranks reported herein are **conditional on governance-valid Monte Carlo replicates**:
> $$P(R_i = k \mid \text{Governance-Valid Replicate})$$
> Inconsistent expert states ($\text{CR} \ge 0.08$) and near-degenerate subspaces ($\delta_K < 0.03$) are screened out by the governance gates and do not constitute valid decision scenarios.


---

## 2. Cohort 1: Indomethacin (`IND-001-2026`)

### 2.1 Replicate Accounting & Governance Histogram
- **Generated Replicates**: $N_{\text{gen}} = 10,000$
- **Valid Replicates**: $N_{\text{valid}} = 8604$ ($86.04\%$)
- **Blocked Replicates**: $N_{\text{blocked}} = 1396$ ($13.96\%$)
- **Canonical Block Reasons**:
  - `AHP_CR_BLOCKED`: **1396** replicates (CR $\ge 0.08$)
  - `EIGENGAP_BLOCKED`: **0** replicates
  - `ZERO_VARIANCE`: **0** replicates
  - `INVALID_INPUT_SCORE`: **0** replicates
  - `NON_PD_METRIC`: **0** replicates
  - `REFERENCE_COINCIDENCE`: **0** replicates

### 2.2 Dynamic Subspace Dimension Distribution $P(K=k)$
- $K=1$: **0.00\%**
- $K=2$: **2.32\%** (200 replicates)
- $K=3$: **90.19\%** (7760 replicates)
- $K=4$: **7.48\%** (644 replicates)

### 2.3 Candidate Selection Probabilities & Rank Statistics
| Candidate | Abbreviation | Det Rank | $P(\text{top-1})$ | $P(\text{top-2})$ | Expected Rank $\mathbb{E}[R]$ | Median Rank | Rank 1 Freq | Rank 2 Freq | Rank 3 Freq |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `POL-005-2026` | **SOLUPLUS** | 1 | **57.05%** | 94.57% | 1.50 | 1 | 57.05% | 37.52% | 4.01% |
| `POL-006-2026` | **HPMC_E5** | 2 | **40.24%** | 92.27% | 1.70 | 2 | 40.24% | 52.03% | 5.70% |
| `POL-002-2026` | **PVP_VA_64** | 3 | **1.39%** | 7.74% | 3.36 | 3 | 1.39% | 6.35% | 54.65% |
| `POL-001-2026` | **PVP_K30** | 4 | **0.87%** | 4.03% | 3.80 | 4 | 0.87% | 3.16% | 28.91% |
| `POL-007-2026` | **EDR_EPO** | 5 | **0.44%** | 1.38% | 4.64 | 5 | 0.44% | 0.94% | 6.74% |

### 2.4 Conditioned Closeness Summary $C_L \mid K$
> [!NOTE]
> Dimensionless closeness coefficients $C_L$ are conditioned strictly by retained dimension $K$. Cross-$K$ pooled statistics are descriptive only.

| Polymer ID | Abbreviation | $K=2$ Median (IQR) | $K=3$ Median (IQR) | $K=4$ Median (IQR) | Descriptive Pooled Median |
| :--- | :--- | :---: | :---: | :---: | :---: |
| `POL-005-2026` | SOLUPLUS | 0.6707 (0.1588) | 0.6767 (0.0739) | 0.6956 (0.0618) | **0.6785** |
| `POL-006-2026` | HPMC_E5 | 0.6313 (0.1267) | 0.6696 (0.0650) | 0.6859 (0.0591) | **0.6704** |
| `POL-002-2026` | PVP_VA_64 | 0.6087 (0.1576) | 0.5957 (0.0736) | 0.6222 (0.0771) | **0.5978** |
| `POL-001-2026` | PVP_K30 | 0.5726 (0.1495) | 0.5773 (0.0740) | 0.6312 (0.0773) | **0.5807** |
| `POL-007-2026` | EDR_EPO | 0.5510 (0.1298) | 0.5347 (0.0699) | 0.5977 (0.0844) | **0.5380** |

*Mandatory Warning Label*: `DESCRIPTIVE SUMMARY ONLY — NOT GEOMETRICALLY INVARIANT ACROSS VARIABLE-K SPACES`

---

## 3. Cohort 2: Ibuprofen (`DRG-0001`)

### 3.1 Replicate Accounting & Governance Histogram
- **Generated Replicates**: $N_{\text{gen}} = 10,000$
- **Valid Replicates**: $N_{\text{valid}} = 8579$ ($85.79\%$)
- **Blocked Replicates**: $N_{\text{blocked}} = 1421$ ($14.21\%$)
- **Canonical Block Reasons**:
  - `AHP_CR_BLOCKED`: **1393** replicates
  - `EIGENGAP_BLOCKED`: **28** replicates (boundary gap $\delta_K < 0.03$)

### 3.2 Dynamic Subspace Dimension Distribution $P(K=k)$
- $K=1$: **0.00\%**
- $K=2$: **50.78\%** (4356 replicates)
- $K=3$: **49.17\%** (4218 replicates)
- $K=4$: **0.06\%** (5 replicates)

### 3.3 Candidate Selection Probabilities & Rank Statistics
| Candidate | Abbreviation | Det Rank | $P(\text{top-1})$ | $P(\text{top-2})$ | Expected Rank $\mathbb{E}[R]$ | Median Rank | Rank 1 Freq | Rank 2 Freq | Rank 3 Freq |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `POL-007-2026` | **EDR_EPO** | 1 | **97.87%** | 99.71% | 1.03 | 1 | 97.87% | 1.84% | 0.19% |
| `POL-002-2026` | **PVP_VA_64** | 2 | **1.38%** | 58.13% | 2.57 | 2 | 1.38% | 56.75% | 26.41% |
| `POL-001-2026` | **PVP_K30** | 3 | **0.48%** | 25.92% | 2.98 | 3 | 0.48% | 25.45% | 50.40% |
| `POL-005-2026` | **SOLUPLUS** | 4 | **0.24%** | 16.11% | 3.51 | 4 | 0.24% | 15.86% | 22.29% |
| `POL-006-2026` | **HPMC_E5** | 5 | **0.03%** | 0.13% | 4.92 | 5 | 0.03% | 0.09% | 0.71% |

### 3.4 Conditioned Closeness Summary $C_L \mid K$
> [!NOTE]
> Dimensionless closeness coefficients $C_L$ are conditioned strictly by retained dimension $K$. Cross-$K$ pooled statistics are descriptive only.

| Polymer ID | Abbreviation | $K=2$ Median (IQR) | $K=3$ Median (IQR) | $K=4$ Median (IQR) | Descriptive Pooled Median |
| :--- | :--- | :---: | :---: | :---: | :---: |
| `POL-007-2026` | EDR_EPO | 0.5542 (0.0649) | 0.6049 (0.0572) | 0.6032 (0.0213) | **0.5786** |
| `POL-002-2026` | PVP_VA_64 | 0.4178 (0.0696) | 0.5192 (0.0603) | 0.4918 (0.0537) | **0.4661** |
| `POL-001-2026` | PVP_K30 | 0.4092 (0.0549) | 0.4854 (0.0498) | 0.5196 (0.0167) | **0.4474** |
| `POL-005-2026` | SOLUPLUS | 0.4016 (0.0522) | 0.4495 (0.0435) | 0.4692 (0.0134) | **0.4275** |
| `POL-006-2026` | HPMC_E5 | 0.2525 (0.0710) | 0.3946 (0.0589) | 0.4355 (0.0263) | **0.3223** |

*Mandatory Warning Label*: `DESCRIPTIVE SUMMARY ONLY — NOT GEOMETRICALLY INVARIANT ACROSS VARIABLE-K SPACES`
