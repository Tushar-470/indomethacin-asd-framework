# ASD Framework Web Application User Guide

The ASD Computational Polymer Screening Framework includes a local-first web application built on top of the frozen `asd_mcda` v1.0.0 scientific engine.

---

## Quick Start

### Starting the Application

From the project root directory:

```bash
python start_app.py
```

This launches:
- **FastAPI Backend**: `http://127.0.0.1:8000`
- **React Frontend**: `http://127.0.0.1:5173`
- **API Documentation**: `http://127.0.0.1:8000/api/docs`

---

## Key Features

### 1. Dashboard (`/`)
- View engine version and data status.
- Quick navigation to Drug Library, Polymer Library, and Screening Workspace.
- Recent analysis history overview.

### 2. Drug Library (`/drugs`)
- Inspect active pharmaceutical ingredient (API) profiles.
- View melting point ($T_m$), glass transition ($T_g$), BCS class, Hansen Solubility Parameters (δD, δP, δH), and SMILES identity.
- Add new draft drug profiles with automatic descriptor calculation and validation feedback.

### 3. Polymer Library (`/polymers`)
- Browse candidate polymeric carriers.
- View molecular weight ($M_n$), glass transition ($T_g$), density, functional groups, and literature evidence scores.
- Add new candidate polymers with copolymer support.

### 4. Screening Workspace (`/screening`)
- **Step 1**: Select API (e.g. Indomethacin).
- **Step 2**: Select polymers to screen (checkbox list with search filter).
- **Step 3**: Select execution mode:
  - **Research Mode**: Strictly enforced data validation; produces publication-grade outputs.
  - **Exploratory Mode**: Permits draft/unvalidated data; clearly labeled with uncertainty warnings.
- **Step 4**: Set drug loading fraction (default 30% w/w) and click **Run Screening**.

### 5. Results Dashboard (`/results/:analysis_id`)
- **Top Selection Card**: Highlighted top-ranked polymer (e.g., Soluplus), TOPSIS closeness coefficient ($C_L$), decision confidence tier, predicted $T_g$, Flory-Huggins $\chi$, and miscibility classification.
- **Ranking Table**: Full candidate ranking table sorted by $C_L$.
- **Interactive Tabs**:
  - **Overview**: Gate status (Gate 1, Gate 2) and PCA dimensionality summary.
  - **Figures**: All 5 publication PNG figures (300 DPI) rendered inline.
  - **Uncertainty**: Decision confidence $P(\text{top-1})$ chart and Gelman-Rubin convergence metrics.
  - **Sensitivity**: OAT stability and Morris elementary effects scatter plot ($\mu$ vs $\sigma$).
  - **Reports**: One-click download for Excel workbook (`.xlsx`), JSON (`.json`), CSV (`.csv`), and Markdown (`.md`) reports.

### 6. Analysis History (`/history`)
- Complete audit trail of all past screening runs.
- Click any analysis to reload full results view.
- Provenance details including software version, config checksum, and random seed.

---

## Architectural Guarantee

The web application is a **pure presentation layer**. All thermodynamic calculations, multi-criteria decision analysis (AHP-TOPSIS), Monte Carlo joint-distribution uncertainty quantification, Morris sensitivity screening, and logistic failure boundary mapping are executed directly by `src/asd_mcda/`. No scientific equations are duplicated in frontend code.
