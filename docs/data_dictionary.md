# Data Dictionary

**Release**: v1.3.1-FREEZE  
**Framework**: Master Research Framework V2.0  

---

## 1. Polymer Library Dataset Fields

**Authoritative File**: `config/polymers/polymer_library_v3_five_polymers.csv`  

| Column Name | Data Type | Physical Unit | Description |
| :--- | :---: | :---: | :--- |
| `polymer_id` | String | — | Unique immutable identifier (e.g. `POL-001-2026`) |
| `polymer_name` | String | — | Full canonical IUPAC / chemical name |
| `abbreviation` | String | — | Standardized short label for plots and tabular summaries |
| `polymer_family` | String | — | Chemical classification family (`vinylic`, `cellulosic`, `acrylic`) |
| `polymer_class` | String | — | Functional charge/property class (`neutral`, `amphiphilic`, `cationic`) |
| `regulatory_status` | String | — | Regulatory compendial monograph status (`FDA_IID`, `USP_NF`, `Ph.Eur.`) |
| `supplier` | String | — | Primary chemical / excipient manufacturer |
| `catalog_number` | String | — | Manufacturer catalog or CAS registry number |
| `batch_number` | String | — | Reference batch or lot identifier |
| `mn_da` | Float | Da | Number-average molecular weight |
| `mw_da` | Float | Da | Weight-average molecular weight |
| `pdi` | Float | — | Polydispersity index ($M_w / M_n$) |
| `tg_k` | Float | K | Glass transition temperature from experimental DSC |
| `tg_source` | String | — | Provenance source of $T_g$ measurement |
| `density_g_cm3` | Float | $\text{g/cm}^3$ | Bulk / pycnometric polymer density |
| `density_source` | String | — | Provenance source of density value |
| `hsp_delta_d` | Float | $\text{MPa}^{0.5}$ | Dispersion Hansen Solubility Parameter |
| `hsp_delta_p` | Float | $\text{MPa}^{0.5}$ | Polar Hansen Solubility Parameter |
| `hsp_delta_h` | Float | $\text{MPa}^{0.5}$ | Hydrogen bonding Hansen Solubility Parameter |
| `hsp_total` | Float | $\text{MPa}^{0.5}$ | Total Hildebrand solubility parameter ($\sqrt{\delta_D^2+\delta_P^2+\delta_H^2}$) |
| `hsp_source` | String | — | Calculation engine (`hoftyzer_van_krevelen`) |
| `functional_groups` | String | — | Pipe-delimited list of active functional chemical groups |
| `monomer_smiles` | String | — | SMILES string(s) for monomer repeat units |
| `copolymer_mole_fractions` | String | — | Pipe-delimited mole fractions for copolymer monomer units |
| `known_asd_applications` | String | — | Semicolon-delimited list of precedent ASD drug compounds |
| `spray_drying_suitability` | String | — | Qualitative technical suitability for spray drying |
| `hygroscopicity` | String | — | Compendial hygroscopicity classification |
| `literature_evidence_score` | Float | — | Precedent evidence weight factor $[0.0, 1.0]$ |
| `literature_dois` | String | — | Reference DOIs for peer-reviewed studies |
| `data_source` | String | — | Primary source classification (`supplier_coA`, `literature`) |
| `confidence_level` | String | — | Quality assurance tier (`high`, `moderate`) |
| `validation_status` | String | — | Dataset validation status flag (`validated`) |

---

## 2. Active Compatibility Score Matrix Fields

**Authoritative File**: `results/final/final_score_matrix.csv`  

| Column Name | Data Type | Physical Unit | Description |
| :--- | :---: | :---: | :--- |
| `polymer_id` | String | — | Unique polymer identifier |
| `s_HSP` | Float | — | Normalized Hansen solubility score $[0.0, 1.0]$ |
| `s_chi` | Float | — | Normalized Flory–Huggins interaction score $[0.0, 1.0]$ |
| `s_GT` | Float | — | Normalized Gordon–Taylor anti-plasticization score $[0.0, 1.0]$ |

---

## 3. Final Polymer Ranking Fields

**Authoritative File**: `results/final/final_polymer_ranking.csv`  

| Column Name | Data Type | Physical Unit | Description |
| :--- | :---: | :---: | :--- |
| `topsis_rank` | Integer | — | Deterministic MCDA ranking position ($1 = \text{top-ranked}$) |
| `polymer_id` | String | — | Polymer identifier |
| `polymer_name` | String | — | Full canonical polymer name |
| `abbreviation` | String | — | Standardized abbreviation |
| `topsis_cl` | Float | — | TOPSIS relative closeness coefficient $C_L \in [0.0, 1.0]$ |
| `p_top1_percent` | Float | % | Joint-distribution Monte Carlo top-1 selection probability |
