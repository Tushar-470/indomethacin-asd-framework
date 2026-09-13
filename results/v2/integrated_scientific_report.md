# PharmaPolySCOPE v2 — Integrated Scientific Synthesis Report
## Comprehensive Multi-Criteria Polymer Screening & Decision Robustness Analysis

**Specification**: `2.0.0-SPEC-PHASE0-PATCH2` & `2.0.0-SPEC-PHASE5.2-FINAL`  
**Core Framework**: SP-PRP-TOPSIS on Dynamic Variable-K Eigenspaces  
**Scope**: Publication-Grade Scientific Evaluation of Approved Cohorts  
**Status**: COMPUTATIONAL CANDIDATE SCREENING — Prospective Laboratory Validation Pending  
**Phase 6 Status**: PHASE 6 STATUS: FORMALLY CLOSED  


---

## 1. Executive Scientific Summary

PharmaPolySCOPE v2 integrates multi-criteria compatibility modeling (HSP, Flory-Huggins $\chi$, RDKit chemical descriptors, and Gordon-Taylor glass transition elevation) with data-driven dimension selection ($CV_K \ge 95\%$), Davis-Kahan subspace stability, external 4×4 physical-space AHP weighting, metric-tensor distance geometry, and stochastic uncertainty propagation.

Across both model BCS Class II compounds evaluated:
1. **Drug-Specific Geometries**: Each compound induces an independent, distinct decision geometry:
   - **Indomethacin** spans a 3-dimensional subspace ($K=3$, $CV = 99.96\%$).
   - **Ibuprofen** spans a 2-dimensional subspace ($K=2$, $CV = 96.10\%$).
2. **Deterministic and Robust Selection**:
   - For **Indomethacin**, **Soluplus** is the top **COMPUTATIONAL CANDIDATE** (Deterministic Rank 1, $C_L = 0.6864$; Monte Carlo $P(\text{top-1}) = 57.05\%$, $P(\text{top-2}) = 94.57\%$), closely contested by **HPMC E5** (Deterministic Rank 2, $C_L = 0.6731$; $P(\text{top-1}) = 40.24\%$, $P(\text{top-2}) = 92.27\%$).
   - For **Ibuprofen**, **Eudragit E PO** is the overwhelmingly dominant **COMPUTATIONAL CANDIDATE** (Deterministic Rank 1, $C_L = 0.5503$; Monte Carlo $P(\text{top-1}) = 97.87\%$).

---

## 2. In-Depth Scientific Answers (Step 8 Mandatory Taxonomy)

### 2.1 Cohort 1: Indomethacin (`IND-001-2026`)

1. **Top-Ranked Deterministic Candidate**:
   **Soluplus** (`POL-005-2026`) achieves deterministic rank 1 with closeness coefficient $C_L = 0.6864$, driven by high thermodynamic affinity ($s_{\text{HSP}} = 0.7972$, $s_{\chi} = 0.8261$).
2. **Top-Ranked Uncertainty Candidate (Conditional on Validity)**:
   **Soluplus** (`POL-005-2026`) is the Top-Ranked Uncertainty Candidate, achieving the highest top-1 selection probability: $P(\text{top-1}) = 57.05\%$ and expected rank $\mathbb{E}[R] = 1.50$.
3. **Competing Candidates**:
   **HPMC E5** (`POL-006-2026`) is a potent competitor (deterministic rank 2, $C_L = 0.6731$, $P(\text{top-1}) = 40.24\%$). Together, Soluplus and HPMC E5 account for **$97.29\%$ of all top-1 outcomes**.
4. **Ranking-Switching Behavior**:
   A strong two-candidate pairwise switching dynamic exists between Soluplus and HPMC E5. Soluplus leads in thermodynamic miscibility, while HPMC E5 leads in glass transition elevation ($s_{\text{GT}} = 0.9731$ vs $0.0000$). When score perturbations elevate anti-plasticization importance, HPMC E5 overtakes Soluplus.
5. **K Distribution**:
   $K=3$ dominates with **$90.19\%$** of valid replicates, while $K=4$ accounts for **$7.48\%$**, and $K=2$ accounts for **$2.32\%$**. $K=1$ is never selected ($0.0\%$).
6. **Eigengap & Stability Behavior**:
   The baseline boundary eigengap is wide ($\delta_3 = 0.7383 \ge 0.10$), classifying the subspace as `STABLE`. Across the $10,000$ MC replicates, **$85.62\%$** of valid replicates remain `STABLE`, and **$0.42\%$** trigger `WARNING`.
7. **Blocked Replicate Fraction**:
   $13.96\%$ of generated replicates are blocked ($N_{\text{blocked}} = 1396$). Exactly $100\%$ of blocks are caused by `AHP_CR_BLOCKED` (expert preference inconsistency under $\sigma_{\text{AHP}} = 0.15$), confirming the protective rigor of the Saaty $CR < 0.08$ gate.
8. **Most Influential Morris Factors**:
   The primary drivers of closeness response are:
   - `score_POL-007-2026_s_HSP` (max $\mu^* = 0.2110$)
   - `score_POL-007-2026_s_desc` (max $\mu^* = 0.1907$)
   - `score_POL-005-2026_s_HSP` (max $\mu^* = 0.1665$)
   - `score_POL-002-2026_s_HSP` (max $\mu^* = 0.1365$)
9. **Experimental Validation Shortlist**:
   - Primary: **Soluplus** (`POL-005-2026`) — formulation candidate for thermodynamic miscibility and solubilization.
   - Secondary / Dual-Carrier: **HPMC E5** (`POL-006-2026`) — formulation candidate for kinetic anti-plasticization and recrystallization inhibition.

---

### 2.2 Cohort 2: Ibuprofen (`DRG-0001`)

1. **Top-Ranked Deterministic Candidate**:
   **Eudragit E PO** (`POL-007-2026`) achieves deterministic rank 1 with $C_L = 0.5503$, driven by exceptional thermodynamic compatibility ($s_{\text{HSP}} = 0.7517$, $s_{\chi} = 0.8359$).
2. **Top-Ranked Uncertainty Candidate (Conditional on Validity)**:
   **Eudragit E PO** (`POL-007-2026`) is the Top-Ranked Uncertainty Candidate with $P(\text{top-1}) = 97.87\%$, $P(\text{top-2}) = 99.71\%$, and expected rank $\mathbb{E}[R] = 1.03$.
3. **Competing Candidates**:
   **PVP-VA 64** (`POL-002-2026`) is the distant runner-up (deterministic rank 2, $C_L = 0.4168$, $P(\text{top-1}) = 1.38\%$, $P(\text{top-2}) = 58.13\%$).
4. **Ranking-Switching Behavior**:
   Minimal top-1 switching occurs. The dominance of Eudragit E PO is structurally anchored by the chemical acid-base interaction between ibuprofen's carboxylic acid moiety and Eudragit E PO's tertiary amine groups. Minor rank switching is confined to ranks 2, 3, and 4 between PVP-VA 64, PVP K30, and Soluplus.
5. **K Distribution**:
   $K=2$ and $K=3$ divide the valid replicates almost equally: $K=2$ accounts for **$50.78\%$** and $K=3$ accounts for **$49.17\%$**. $K=4$ accounts for **$0.06\%$**, and $K=1$ is $0.0\%$.
6. **Eigengap & Stability Behavior**:
   Baseline eigengap is $\delta_2 = 0.8169$ (`STABLE`). In Monte Carlo propagation, $83.43\%$ of replicates are `STABLE`, $2.36\%$ trigger `WARNING`, and $0.28\%$ ($28$ replicates) are `BLOCKED` by near-degenerate eigengaps ($\delta_K < 0.03$).
7. **Blocked Replicate Fraction**:
   $14.21\%$ of generated replicates are blocked ($N_{\text{blocked}} = 1421$), with $1393$ blocks from `AHP_CR_BLOCKED` and $28$ blocks from `EIGENGAP_BLOCKED`.
8. **Most Influential Morris Factors**:
   - `score_POL-002-2026_s_HSP` (max $\mu^* = 0.2478$)
   - `score_POL-001-2026_s_HSP` (max $\mu^* = 0.2429$)
   - `score_POL-005-2026_s_HSP` (max $\mu^* = 0.1791$)
   - `score_POL-006-2026_s_HSP` (max $\mu^* = 0.1771$)
9. **Experimental Validation Shortlist**:
   - Primary: **Eudragit E PO** (`POL-007-2026`) — dominant candidate for ionic complexation with ibuprofen.
   - Secondary: **PVP-VA 64** (`POL-002-2026`) — neutral non-ionic benchmark carrier.

---

## 3. Blocked Cohort Audit

A strict input validation audit screened all $20$ candidate drug profiles in the repository:
- **Active Evaluated Cohorts**: $2$ (`IND-001-2026`, `DRG-0001`)
- **Blocked Due to Incomplete Descriptors**: $16$ profiles (`DRG-0003` through `DRG-0018` missing experimental/measured `density_amorphous_g_cm3`).
- **Blocked Due to Draft Status & Valence Error**: $1$ profile (`ITR-001-2026` marked draft, missing physiochemical parameters, and possessing explicit chemical valence violation on atom #17 N).
- **Superseded User Profile**: $1$ profile (`DRG-0002` superseded by authoritative `IND-001-2026`).

---

## 4. Scientific Disclaimer

> [!WARNING]
> All rankings and evaluations reported herein are **COMPUTATIONAL CANDIDATE PREDICTIONS** derived from thermodynamic, structural, and empirical decision models. They do not constitute experimental validation. Prospective laboratory verification (spray drying, powder X-ray diffraction, modulated differential scanning calorimetry, and dissolution testing) is strictly required prior to commercial formulation adoption.
 
---

**PHASE 6 STATUS: FORMALLY CLOSED**

