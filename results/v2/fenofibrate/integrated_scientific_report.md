# PharmaPolySCOPE v2 — Integrated Scientific Screening Report
## Compound: Fenofibrate (`DRG-0007`)

**Methodological Baseline**: v1.5 Frozen Core (`31eee4d`) + Phase 2–5 Validated Variable-$K$ Pipeline  
**Production Sign-Off**: Formally Remediated Density Semantics (SAS V1.0 §6.1 / DAS V1.0 §6.1)  
**Computational Status**: `PRODUCTION SCREENING COMPLETE — Prospective Laboratory Validation Pending`  

---

## 1. Executive Verdict & Ranking Synthesis

| Metric / Result | Value | Scientific Interpretation |
|---|---|---|
| **Top-Ranked Deterministic Candidate** | **Eudragit E PO** (`POL-007-2026`) | $C_L = 0.7413$, $D^+ = 1.4462, D^- = 4.1443$ |
| **Top-Ranked Uncertainty Candidate** | **Eudragit E PO** (`POL-007-2026`) | $P(R_i = 1 \mid \text{Valid}) = 99.77\%$, $\mathbb{E}[R] = 1.00$, $\text{Median}[R] = 1.0$ |
| **Primary Competitor / Runner-Up** | **PVP-VA 64** (`POL-002-2026`) | $C_L = 0.6271$, $P(R_i \le 2 \mid \text{Valid}) = 95.73\%$, $\mathbb{E}[R] = 2.04$ |
| **Spectral Decision Geometry** | **$K = 3$** (99.93% variance explained) | $\delta_3 = 0.2715$, Subspace Stability: **`STABLE`** |
| **AHP Governance Status** | **`ACCEPTED`** | Consistency Ratio $CR = 0.0494 < 0.08$ |
| **Input Density Semantics** | Crystalline Baseline + Fallback | $\rho_{\text{cryst}} = 1.296\text{ g/cm}^3$; $\rho_{\text{amorph}} = \text{null}$ (`crystalline_systematic_bias_flag`) |

---

## 2. Chemical Identity & Input Data Integrity

* **Drug Identifier**: `DRG-0007`
* **Generic Name**: Fenofibrate
* **Canonical SMILES**: `CC(C)OC(=O)C(C)(C)Oc1ccc(C(=O)c2ccc(Cl)cc2)cc1`
* **Molecular Weight**: $360.84\text{ g/mol}$
* **Thermal Properties**: $T_m = 353.65\text{ K}$ ($80.5^\circ\text{C}$), $T_g = 247.35\text{ K}$ ($-25.8^\circ\text{C}$)
* **Solubility Parameters**: $\delta_D = 16.25, \delta_P = 4.11, \delta_H = 6.68, R_0 = 7.50\text{ MPa}^{0.5}$
* **Density Provenance**:
  * `density_crystalline_g_cm3`: **1.296 g/cm³** (Experimental single-crystal XRD).
  * `density_amorphous_g_cm3`: **null** (Optional; unmeasured for this cohort).
  * `density source used for V_m`: **crystalline** ($V_m = 360.84 / 1.296 = 278.43\text{ cm}^3/\text{mol}$).
  * `Gordon-Taylor density source`: **crystalline with systematic_bias_flag** via `Drug.get_preferred_density()`.

---

## 3. Physical & Mechanistic Interpretation of Candidates

### A. Eudragit E PO (Rank 1 Deterministic & Uncertainty)
* **Thermodynamic Strengths**:
  * Outstanding Hansen match: $R_a = 1.558\text{ MPa}^{0.5}$, $\text{RED} = 0.2078$, $s_{\text{HSP}} = 0.8961$.
  * Extremely low Flory–Huggins interaction parameter: $\chi = 0.0409$, $s_{\chi} = 0.9591$.
  * Strongest overall thermodynamic affinity in the active library.
* **Critical Physical Boundary / Risk**:
  * Fenofibrate is a **neutral lipophilic ester** (no free carboxylic acid or phenolic group). It **cannot** form ionic salt bridges with the basic dimethylaminoethyl methacrylate groups of Eudragit E PO.
  * Fenofibrate has an extraordinarily low $T_g$ ($247.35\text{ K} = -25.8^\circ\text{C}$). Pure amorphous fenofibrate is a supercooled liquid at room temperature with intense recrystallization driving force.
  * Eudragit E PO has a low polymer $T_g$ ($323.15\text{ K} = 50.0^\circ\text{C}$). At 30% drug loading, the Gordon–Taylor predicted $T_{g,\text{mix}}$ is only $295.16\text{ K}$ ($22.0^\circ\text{C}$), yielding $s_{\text{GT}} = 0.4202$.
  * **Risk**: High vulnerability to moisture-induced plasticization and room-temperature devitrification.

### B. PVP-VA 64 (Rank 2 Deterministic & Uncertainty)
* **Thermodynamic & Kinetic Balance**:
  * Favorable thermodynamic miscibility: $s_{\text{HSP}} = 0.6447$, $s_{\chi} = 0.5215$.
  * Superior Anti-Plasticization: PVP-VA 64 has a high $T_g$ ($378.15\text{ K} = 105.0^\circ\text{C}$). At 30% drug loading, $T_{g,\text{mix}} = 328.71\text{ K}$ ($55.6^\circ\text{C}$), well above ambient temperature ($s_{\text{GT}} = 1.0000$).
  * Forms stable hydrogen bonds with the ester carbonyl oxygens of Fenofibrate.
* **Formulation Insight**: PVP-VA 64 provides the requisite kinetic glass stabilization barrier that prevents room-temperature recrystallization, making it the most balanced commercial comparator for prospective formulation.

---

## 4. Comparison with Old Diagnostic Run

| Metric | Old Diagnostic Run (`DRG-0007`) | New Production Run (`DRG-0007`) | Difference / Source of Change |
|---|---|---|---|
| **Gate Status** | `BLOCKED — INPUT INTEGRITY FAILURE` | **`PRODUCTION VALID`** | Remediated Phase-6 ingestion filter; restored SAS V1.0 fallback authority. |
| **Raw Score Matrix** | Identical ($s_{\text{HSP}}=0.8961, s_{\chi}=0.9591$) | Identical ($s_{\text{HSP}}=0.8961, s_{\chi}=0.9591$) | Exact numerical equivalence (0.0000 difference). |
| **Retained $K$** | $K = 3$ | **$K = 3$** | Identical spectral decomposition ($CV = 99.93\%$). |
| **Deterministic Ranking** | 1: EDR_EPO, 2: PVP_VA_64, 3: PVP_K30 | **1: EDR_EPO, 2: PVP_VA_64, 3: PVP_K30** | Identical closeness coefficients ($C_L = 0.7413, 0.6271$). |
| **Monte Carlo $P(\text{top-1})$** | EDR_EPO: 99.77%, PVP_VA_64: 0.23% | **EDR_EPO: 99.77%, PVP_VA_64: 0.23%** | Exact numerical convergence across 8,594 valid replicates. |
| **Morris Top Factor** | `ahp_0_1` | **`ahp_0_1`** | Exact trajectory equivalence across 10 valid paths. |

---

## 5. Methodological Boundary & Disclaimer

> [!IMPORTANT]
> **Eudragit E PO was the top-ranked computational candidate ($C_L = 0.7413$, $P(\text{top-1}) = 99.77\%$) and PVP-VA 64 was the top-ranked anti-plasticizing candidate ($C_L = 0.6271$).**  
> These computational rankings reflect thermodynamic and kinetic model predictions. Under no circumstances should these candidates be claimed as "proven effective", "guaranteed stable", or "proven to enhance bioavailability" prior to prospective empirical laboratory spray-drying, solid-state characterization (PXRD/DSC), and dissolution testing.
