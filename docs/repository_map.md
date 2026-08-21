# Repository Directory and Architectural Map

**Release**: v1.3.1-FREEZE  

---

```
asd_framework/
├── README.md                                  # Executive summary & quick-start guide
├── CHANGELOG.md                               # Framework version history & changelog
├── CITATION.cff                               # Academic citation metadata
├── LICENSE                                    # MIT Open Source License
├── FINAL_COMPUTATIONAL_BASELINE_MANIFEST.yaml  # Machine-readable baseline manifest
├── pyproject.toml                             # Python packaging & build metadata
├── requirements.txt                           # Core scientific dependencies
├── requirements-dev.txt                       # Developer & testing dependencies
├── requirements-web.txt                       # Web application backend dependencies
├── start_app.py                               # Web application launcher (FastAPI + React)
├── run_app.bat                                # Windows launcher shortcut
│
├── src/asd_mcda/                              # Core Computational Engine (FROZEN)
│   ├── cli.py                                 # Command-line entry point
│   ├── orchestrator.py                        # 11-step pipeline orchestrator
│   ├── compatibility/                         # HSP, Flory–Huggins, Gordon–Taylor models
│   ├── configuration/                         # YAML/JSON loaders & schema validators
│   ├── descriptors/                           # 2D RDKit structural descriptors
│   ├── drug/                                  # Drug profile dataclass
│   ├── integration/                           # PCA pre-processor & CCI integration
│   ├── mcda/                                  # Saaty AHP & TOPSIS rankers
│   ├── polymer/                               # Polymer library dataclass
│   ├── prediction/                            # Logistic Failure Boundary Mapping (FBM)
│   ├── reporting/                             # Markdown, JSON, Excel report generators
│   ├── sensitivity/                           # Morris Elementary Effects & OAT
│   ├── uncertainty/                           # Joint-distribution Monte Carlo UQ ($N=10k$)
│   ├── utils/                                 # Constants, helpers, logging config
│   ├── validation/                            # Input validation rules
│   └── visualization/                         # Publication plotters (300 DPI)
│
├── config/                                    # Active Configuration Inputs
│   ├── ahp/                                   # Pairwise comparison matrices (default + experts)
│   ├── drugs/indomethacin.json                # Authoritative Indomethacin profile
│   ├── polymers/                              # Active 5-polymer library CSV (v3)
│   └── workflow/workflow_config.yaml          # Master workflow configuration
│
├── results/                                   # Computational Artifacts & Outputs
│   ├── final/                                 # AUTHORITATIVE FROZEN BASELINE ARTIFACTS
│   │   ├── final_polymer_library.csv          # Authoritative candidate library
│   │   ├── final_score_matrix.csv             # Authoritative compatibility scores
│   │   ├── final_polymer_ranking.csv          # Authoritative TOPSIS ranking & probabilities
│   │   ├── final_monte_carlo_summary.json     # Authoritative UQ summary ($N=10,000$)
│   │   └── final_computational_report.md      # Final synthesized decision report
│   ├── reports/                               # Generated pipeline reports & baseline record
│   └── figures/                               # Generated 300 DPI publication plots
│
├── scripts/                                   # Quality Assurance & Verification Scripts
│   └── validate_final_dataset.py              # Automated dataset validator & SHA-256 checker
│
├── tests/                                     # Automated Verification Suite
│   ├── unit/                                  # Physics, MCDA, & component unit tests
│   ├── integration/                           # Full 11-step pipeline test
│   └── web/                                   # FastAPI REST endpoints & regression tests
│
├── backend/                                   # FastAPI REST Application Backend
├── frontend/                                  # React 18 + TypeScript + Vite Dashboard
│
├── docs/                                      # Framework Documentation Suite
│   ├── source_of_truth.md                     # Single authoritative file map
│   ├── computational_method.md                # Mathematical equations & definitions
│   ├── data_provenance.md                     # Drug & polymer physical data lineage
│   ├── data_dictionary.md                     # Dataset column descriptions & units
│   ├── study_overview.md                      # Research objective & lifecycle context
│   ├── reproducibility.md                     # Reproduction instructions & benchmarks
│   ├── limitations.md                         # Methodological & theoretical limitations
│   ├── repository_map.md                      # This directory architectural guide
│   ├── pre_cleanup_dependency_audit.md        # Pre-cleanup safety & dependency audit
│   ├── specifications/                        # Architecture specifications & master framework
│   └── verification/                          # Verification and validation audit reports
│
└── archive/                                   # Preserved Research & Development History
    ├── historical/                            # Prior baseline records & 6-polymer library
    ├── superseded/                            # Superseded pre-freeze decision reports
    └── development/                           # Forensic calibration & audit scripts
```
