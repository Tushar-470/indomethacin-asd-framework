# Study Overview and Framework Context

**Project Title**: Quality by Design–Driven Development of Indomethacin Immediate-Release Tablets from Spray-Dried Amorphous Solid Dispersions: A Computational–Experimental Framework for Polymer Selection, Predictive Formulation Design, and Failure Boundary Mapping  
**Release**: v1.3.1-FREEZE  
**Status**: Computational Baseline Frozen; Prospective Experimental Validation Pending  

---

## 1. Scientific Objective

The objective of this research is to establish and validate an integrated, reproducible computational decision framework for rational polymer carrier selection in spray-dried amorphous solid dispersions (SD-ASDs) of indomethacin (BCS Class II). The framework replaces trial-and-error laboratory screening cascades with a multi-physics, multi-criteria decision analysis (MCDA) workflow coupled to stochastic uncertainty quantification and failure boundary mapping.

---

## 2. Research Lifecycle Status

```
[Phase 1: Computational Model Development] ──> [Phase 2: Baseline Freeze (v1.3.1)] ──> [Phase 3: Prospective Experiments]
                    COMPLETED                                CURRENT STATUS                             PENDING
```

- **Current State**: The computational screening engine, parameter lineage, and five-polymer ranking are **frozen and internally validated**.
- **Prospective Stage**: Laboratory preparation for spray drying, solid-state characterization (mDSC, PXRD, FTIR), non-sink dissolution, and physical stability mapping is underway.

---

## 3. Five-Polymer Candidate Library

The active candidate set comprises five compendial polymers spanning vinylic, cellulosic, and acrylic carrier classes:

1. **`POL-001-2026` — Polyvinylpyrrolidone K30 (`PVP_K30`)**
2. **`POL-002-2026` — PVP-Vinyl Acetate 64 (`PVP_VA_64`)**
3. **`POL-005-2026` — Soluplus (`SOLUPLUS`)**
4. **`POL-006-2026` — Hydroxypropyl Methylcellulose E5 (`HPMC_E5`)**
5. **`POL-007-2026` — Eudragit E PO (`EDR_EPO`)**

---

## 4. Frozen Computational Baseline Findings

### Deterministic TOPSIS Ranking (v1.4.0-CORRECTED-FREEZE)

| Rank | Candidate Polymer | TOPSIS $C_L$ | Model Designation |
| :---: | :--- | :---: | :--- |
| **1** | **Hydroxypropyl Methylcellulose E5** | **0.835911** | **Top-Ranked Computational Candidate** |
| 2 | Soluplus | 0.694342 | High-Affinity Miscibility Candidate |
| 3 | Polyvinylpyrrolidone K30 | 0.549368 | High-Tg Alternative Candidate |
| 4 | PVP-Vinyl Acetate 64 | 0.470256 | Intermediate Affinity Candidate |
| 5 | Eudragit E PO | 0.090501 | Boundary Anti-Ideal Candidate |

### Monte Carlo Uncertainty Quantification ($N=10{,}000$, Seed = 42)

- **HPMC E5 $P(\text{top-1})$**: **42.4%**
- **Soluplus $P(\text{top-1})$**: **35.0%**
- **PVP K30 $P(\text{top-1})$**: **13.3%**
- **Eudragit E PO $P(\text{top-1})$**: **6.1%**
- **PVP-VA 64 $P(\text{top-1})$**: **3.2%**
- **UQ Confidence Tier**: **Moderate Confidence** ($0.40 \le P(\text{top-1}) < 0.70$)


---

## 5. Terminology and Scientific Integrity Rules

- **"Top-Ranked Computational Candidate"** is used strictly in place of "best polymer" or "optimal carrier".
- **"Monte Carlo top-1 Selection Probability"** represents numerical ranking stability under assumed parameter variance, **NOT** a probability of experimental in vivo or in vitro success.
- All results represent **pre-laboratory computational predictions** requiring prospective physical validation.
