# ASD Framework REST API Documentation

The FastAPI backend exposes REST endpoints wrapping the `asd_mcda` v1.0.0 engine.

Base URL: `http://127.0.0.1:8000/api`

---

## Endpoints Summary

### System & Health
| Method | Endpoint | Description |
|:---|:---|:---|
| `GET` | `/health` | Health check endpoint |
| `GET` | `/version` | Engine and web app version info |

### Drug Management
| Method | Endpoint | Description |
|:---|:---|:---|
| `GET` | `/drugs` | List all drug profiles (reference + user) |
| `GET` | `/drugs/{id}` | Get single drug profile details |
| `POST` | `/drugs` | Create new user drug profile |
| `POST` | `/drugs/validate` | Validate drug profile without saving |
| `DELETE` | `/drugs/{id}` | Delete user-created drug profile |

### Polymer Management
| Method | Endpoint | Description |
|:---|:---|:---|
| `GET` | `/polymers` | List all polymers (reference + user) |
| `GET` | `/polymers/{id}` | Get single polymer details |
| `POST` | `/polymers` | Create new user polymer |
| `POST` | `/polymers/validate` | Validate polymer data without saving |
| `DELETE` | `/polymers/{id}` | Delete user-created polymer |

### Computational Screening
| Method | Endpoint | Description |
|:---|:---|:---|
| `POST` | `/screening/run` | Execute 11-step screening pipeline |
| `GET` | `/screening/{id}` | Get screening result details |
| `GET` | `/screening/{id}/figures/{name}` | Serve generated figure PNG |
| `GET` | `/screening/{id}/reports/{file}` | Download report file (JSON/XLSX/CSV/MD) |

### Analysis History
| Method | Endpoint | Description |
|:---|:---|:---|
| `GET` | `/history` | List past analysis history |
| `GET` | `/history/{id}` | Get analysis record with input snapshot |
| `DELETE` | `/history/{id}` | Delete analysis record |

---

## Screening API Example

### Request: `POST /api/screening/run`

```json
{
  "drug_id": "IND-001-2026",
  "polymer_ids": [
    "POL-001-2026",
    "POL-002-2026",
    "POL-007-2026",
    "POL-005-2026",
    "POL-006-2026"
  ],
  "mode": "research",
  "drug_loading_ww": 0.30,
  "random_seed": 42
}
```

### Response Example

```json
{
  "analysis_id": "ANA-20260821-140000-a1b2c3",
  "selected_polymer": "Soluplus",
  "selected_polymer_id": "POL-005-2026",
  "topsis_cl": 0.736338,
  "confidence_tier": "Moderate Confidence (0.40 <= P(top-1) < 0.70)",
  "predicted_tg_k": 334.75,
  "predicted_chi": 0.2265,
  "miscibility_class": "Miscible (Below Critical chi_c = 0.50)",
  "ranking": [
    { "rank": 1, "polymer_id": "POL-005-2026", "abbreviation": "SOLUPLUS", "topsis_cl": 0.736338 },
    { "rank": 2, "polymer_id": "POL-006-2026", "abbreviation": "HPMC_E5", "topsis_cl": 0.684063 },
    { "rank": 3, "polymer_id": "POL-002-2026", "abbreviation": "PVP_VA_64", "topsis_cl": 0.504982 },
    { "rank": 4, "polymer_id": "POL-001-2026", "abbreviation": "PVP_K30", "topsis_cl": 0.442917 },
    { "rank": 5, "polymer_id": "POL-007-2026", "abbreviation": "EDR_EPO", "topsis_cl": 0.000000 }
  ],
  "software_version": "1.0.0"
}
```

