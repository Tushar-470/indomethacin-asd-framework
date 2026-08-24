# PharmaPolySCOPE Brand Guidelines

**Pharmaceutical Polymer Screening and Computational Optimization Platform**  
*Release: v1.5.0-FOUR-CRITERION-FREEZE*

---

## 1. Official Nomenclature & System Hierarchy

| Identity Layer | Designation | Description |
|:---|:---|:---|
| **Official Brand Name** | **PharmaPolySCOPE** | Exact casing: `PharmaPoly` (SemiBold) + `SCOPE` (Bold) |
| **Formal Name Expansion** | **Pharmaceutical Polymer Screening and Computational Optimization Platform** | Official technical title for documentation & publications |
| **Descriptive Subtitle** | *A Four-Criterion Computational Framework for Rational Polymer Selection in Amorphous Solid Dispersions* | Scientific scope & domain context |
| **Public Product Release** | **PharmaPolySCOPE v1.5.0** | Current user-facing software release |
| **Scientific Baseline** | **`v1.5.0-FOUR-CRITERION-FREEZE`** | Frozen four-criterion computational engine baseline |
| **Internal Engine Package** | `asd_mcda` | Core Python numerical & computational library |

---

## 2. Approved Brand Concept: The Lattice Lens

The official PharmaPolySCOPE brand identity is **The Lattice Lens**.

### Core Symbolism:
- **Hexagonal Lattice**: Represents the interconnected macromolecular network and topological structure of pharmaceutical polymer carriers.
- **Central Lens / Scope**: Represents rigorous analytical screening, thermodynamic parameter estimation, and multi-criteria optimization.
- **Node Precision & Symmetry**: Communicates deterministic reproducibility, mathematical transitivity (AHP), and multi-criteria decision convergence (TOPSIS).

### Visual Hierarchy:
1. **Primary**: Hexagonal polymeric lattice with 6 perimeter nodes.
2. **Secondary**: Central analytical scope / optical aperture.
3. **Subtle Focus**: Central nodal convergence point.

> [!NOTE]
> The Lattice Lens is an abstract mathematical symbol. It does **not** depict a specific drug or polymer molecule, nor does it resemble a weapon crosshair, targeting reticle, or cybersecurity shield.

---

## 3. Color System

The PharmaPolySCOPE palette reflects pharmaceutical rigor, computational precision, and clinical clarity.

### Primary Color Palette

| Palette Role | Hex Code | RGB | HSL | Intended Application |
|:---|:---|:---|:---|:---|
| **Deep Teal (Light Primary)** | `#147A8C` | `rgb(20, 122, 140)` | `hsl(189, 75%, 31%)` | Primary symbol on light backgrounds, formal documents |
| **Navy Ink (Light Wordmark)** | `#0B3D4C` | `rgb(11, 61, 76)` | `hsl(194, 75%, 17%)` | Primary wordmark typography on light backgrounds |
| **Cyan Glow (Dark Primary)** | `#2DB5C7` | `rgb(45, 181, 199)` | `hsl(187, 63%, 48%)` | Symbol and highlighted elements on dark UI backgrounds |
| **Pure White (Dark Wordmark)** | `#FFFFFF` | `rgb(255, 255, 255)` | `hsl(0, 0%, 100%)` | Wordmark typography on dark UI surfaces |
| **Monochrome Black** | `#000000` | `rgb(0, 0, 0)` | `hsl(0, 0%, 0%)` | High-contrast printing, black-and-white reports |
| **Slate Ink (Secondary)** | `#1A2332` | `rgb(26, 35, 50)` | `hsl(218, 32%, 15%)` | Technical metadata, secondary headings |

### UI Accent vs. Brand Distinction

> [!IMPORTANT]
> The bright accent cyan (`#5CE1E6`) is strictly a **UI highlight / status accent**. It must **never** be used as the primary logo color or wordmark color.

---

## 4. Typography

### Wordmark Construction

The wordmark **PharmaPolySCOPE** is constructed with the **Inter** typeface (with fallback to standard sans-serif system typefaces):

$$\text{\textbf{PharmaPoly}} \quad (\text{Inter SemiBold, weight 600}) + \text{\textbf{SCOPE}} \quad (\text{Inter Bold, weight 700})$$

- **Tracking / Letter Spacing**: `-0.02em` (tight, precise technical tracking).
- **Proportions**: The wordmark forms a single cohesive technical unit. "SCOPE" is distinct in weight but not exaggerated in size.

---

## 5. Logo Variants & File Assets

All vector assets are 100% self-contained SVG files with no external dependencies or embedded raster images.

| File Path | Description | Dimensions / Context |
|:---|:---|:---|
| `docs/brand/logo-symbol.svg` | Standalone Lattice Lens vector symbol | `128×128` (Scalable) |
| `docs/brand/logo-horizontal-light.svg` | Full lockup for light backgrounds (`#147A8C` / `#0B3D4C`) | `380×64` |
| `docs/brand/logo-horizontal-dark.svg` | Full lockup for dark backgrounds (`#2DB5C7` / `#FFFFFF`) | `380×64` |
| `docs/brand/logo-monochrome-black.svg` | Pure monochrome black mark | `380×64` |
| `docs/brand/logo-monochrome-white.svg` | Pure monochrome white mark | `380×64` |
| `docs/brand/favicon.ico` | Multi-resolution icon for web browsers | `16×16, 32×32, 48×48, 64×64` |
| `docs/brand/favicon-32x32.png` | High-DPI PNG browser favicon | `32×32` |

---

## 6. Small-Size Adaptations (Responsive Geometry)

To ensure maximum legibility across different optical scales, the symbol adapts its geometric density according to the rendering dimension:

| Scale | Resolution | Geometric Structure |
|:---|:---|:---|
| **Micro (Favicon small)** | `16×16 px` | Solid simplified regular hexagon |
| **Small (Tab favicon)** | `32×32 px` | Hexagon outline + 6 node vertices + central focus dot |
| **Medium (Sidebar icon)** | `48×48 px` | Hexagon outline + nodes + 6 spokes + simplified lens ring + focus dot |
| **Standard (UI header)** | `64×64 px` | Hexagon lattice + nodes + spokes + outer & inner lens rings + focus dot |
| **Display (Full mark)** | `128×128+ px` | Full geometric Lattice Lens with dual lens aperture rings and optical node anchors |

---

## 7. Clear Space & Minimum Sizing

### Clear Space
- Minimum clear space around the logo equals $\frac{1}{2}$ the height of the symbol ($0.5H$).
- No text, borders, or foreign visual elements may encroach upon the clear space zone.

### Minimum Sizes
- **Horizontal Logo Lockup**: Minimum width = `140 px` (digital) or `30 mm` (print).
- **Symbol Only**: Minimum width/height = `16 px` (micro) or `5 mm` (print).

---

## 8. Prohibited Brand Usage

To maintain scientific credibility and software brand integrity, the following practices are strictly prohibited:

- ❌ **Do not** add 3D bevels, drop shadows, glow effects, or decorative gradients to the symbol.
- ❌ **Do not** rotate the symbol off its vertical optical axis (vertex at top and bottom).
- ❌ **Do not** distort, stretch, or alter the aspect ratio of the hexagon or wordmark.
- ❌ **Do not** change the capitalization pattern (e.g., *Pharmapolyscope*, *PHARMAPOLYSCOPE*, or *pharma-poly-scope* are non-compliant; use **PharmaPolySCOPE**).
- ❌ **Do not** place developer attribution inside the logo mark or lockup.
- ❌ **Do not** add crosshairs, gun sights, or circular reticles that make the mark look like targeting software.

---

## 9. Developer Attribution Rules

- **Approved Attribution Text**: `"Developed by Tushar Mathapati"`
- **Permitted Locations**:
  - `README.md` (Table 1 architecture metadata and Citation section)
  - Software documentation (`docs/WEB_APP_GUIDE.md`, `docs/API_GUIDE.md`)
  - Repository metadata (`pyproject.toml`, `CITATION.cff`)
  - Application launcher banner (`start_app.py`)
  - Application sidebar footer metadata
- **Strict Exclusions**:
  - The developer name must **never** appear inside the logo, favicon, or logo lockup.
  - The developer name must **never** appear in the scientific Full Screening PDF report, PDF cover, or PDF headers/footers.
