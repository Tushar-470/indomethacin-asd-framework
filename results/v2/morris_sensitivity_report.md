# PharmaPolySCOPE v2 — Morris Elementary Effects Sensitivity Report
## Global Factor Screening ($r=10$ Trajectories, $d=26$ Factors)

**Specification**: `2.0.0-SPEC-PHASE5.2-FINAL`  
**Screening Design**: Radial $(d+1)$-point OAT trajectories on hypercube  
**Factor Screening Bounds**: $[s_{\text{base}} - 0.15, s_{\text{base}} + 0.15] \cap [0, 1]$  
**AHP Screening Bounds**: $\pm 0.30$ in log space  
**Responses**: Continuous Closeness $C_L$ (Primary) and Discrete Ordinal Rank (Secondary)  
**Status**: COMPUTATIONAL CANDIDATE SCREENING  

---

## 1. Executive Summary & Interpretation Guidance

Morris elementary effects screening evaluates global factor influence and non-linear/interactive effects across the multidimensional input domain.

> [!IMPORTANT]
> **Scientific Interpretation Guardrail & Conditional Sensitivity Domain**:  
> 1. Morris sensitivity indices ($\mu^*$, $\sigma$) quantify **decision output responsiveness** to parameter variations. **They must NOT be interpreted as AHP preference weights or subjective importance.**  
> 2. Morris elementary-effect indices characterize sensitivity **conditional on trajectories surviving the $\text{CR} < 0.08$ governance screen**. Discarded trajectories violating the Saaty consistency criterion are screened out via whole-trajectory replacement, ensuring all gradients reflect consistent, admissible preference manifolds.


---

## 2. Cohort 1: Indomethacin (`IND-001-2026`)

### 2.1 Trajectory Discard & Governance Accounting
- **Requested Trajectories**: $r = 10$
- **Total Trajectories Attempted**: 31
- **Valid Trajectories Realized**: 10
- **Discarded Trajectories**: 21
- **Discard Reasons**:
  - `AHP_CR_BLOCKED`: 21
  - `EIGENGAP_BLOCKED`: 0

### 2.2 Top-10 Most Influential Factors (Continuous Closeness Response)
| Rank | Factor Name | Factor Type | Max $\mu^*(C_L)$ | Max $\sigma(C_L)$ | Max $\mu^*(\text{Rank})$ | Primary Sensitive Candidates |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| 1 | `score_POL-007-2026_s_HSP` | score | **0.2110** | 0.0953 | 1.95 | POL-007, POL-005, POL-006 |
| 2 | `score_POL-007-2026_s_desc` | score | **0.1907** | 0.1340 | 1.05 | POL-007, POL-005, POL-006 |
| 3 | `score_POL-005-2026_s_HSP` | score | **0.1665** | 0.1716 | 1.65 | POL-007, POL-005, POL-006 |
| 4 | `score_POL-002-2026_s_HSP` | score | **0.1365** | 0.0900 | 1.80 | POL-007, POL-005, POL-006 |
| 5 | `score_POL-006-2026_s_desc` | score | **0.1265** | 0.1224 | 1.20 | POL-007, POL-005, POL-006 |
| 6 | `score_POL-001-2026_s_desc` | score | **0.1181** | 0.1115 | 1.50 | POL-007, POL-005, POL-006 |
| 7 | `score_POL-006-2026_s_HSP` | score | **0.1147** | 0.1344 | 2.25 | POL-007, POL-005, POL-006 |
| 8 | `score_POL-001-2026_s_HSP` | score | **0.1010** | 0.1135 | 1.95 | POL-007, POL-005, POL-006 |
| 9 | `score_POL-005-2026_s_desc` | score | **0.0987** | 0.1080 | 1.80 | POL-007, POL-005, POL-006 |
| 10 | `score_POL-002-2026_s_desc` | score | **0.0889** | 0.0888 | 0.90 | POL-007, POL-005, POL-006 |

---

## 3. Cohort 2: Ibuprofen (`DRG-0001`)

### 3.1 Trajectory Discard & Governance Accounting
- **Requested Trajectories**: $r = 10$
- **Total Trajectories Attempted**: 31
- **Valid Trajectories Realized**: 10
- **Discarded Trajectories**: 21
- **Discard Reasons**:
  - `AHP_CR_BLOCKED`: 21
  - `EIGENGAP_BLOCKED`: 0

### 3.2 Top-10 Most Influential Factors (Continuous Closeness Response)
| Rank | Factor Name | Factor Type | Max $\mu^*(C_L)$ | Max $\sigma(C_L)$ | Max $\mu^*(\text{Rank})$ | Primary Sensitive Candidates |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| 1 | `score_POL-002-2026_s_HSP` | score | **0.2478** | 0.0527 | 2.10 | POL-002, POL-001, POL-007 |
| 2 | `score_POL-001-2026_s_HSP` | score | **0.2429** | 0.1081 | 2.85 | POL-002, POL-001, POL-007 |
| 3 | `score_POL-005-2026_s_HSP` | score | **0.1791** | 0.0379 | 1.80 | POL-002, POL-001, POL-007 |
| 4 | `score_POL-006-2026_s_HSP` | score | **0.1771** | 0.0288 | 1.05 | POL-002, POL-001, POL-007 |
| 5 | `score_POL-002-2026_s_desc` | score | **0.1168** | 0.0884 | 0.60 | POL-002, POL-001, POL-007 |
| 6 | `score_POL-007-2026_s_HSP` | score | **0.0942** | 0.0855 | 1.80 | POL-002, POL-001, POL-007 |
| 7 | `score_POL-001-2026_s_desc` | score | **0.0891** | 0.0679 | 0.60 | POL-002, POL-001, POL-007 |
| 8 | `score_POL-006-2026_s_desc` | score | **0.0820** | 0.0796 | 0.60 | POL-002, POL-001, POL-007 |
| 9 | `score_POL-002-2026_s_chi` | score | **0.0801** | 0.0443 | 0.90 | POL-002, POL-001, POL-007 |
| 10 | `score_POL-005-2026_s_desc` | score | **0.0616** | 0.0254 | 0.30 | POL-002, POL-001, POL-007 |
