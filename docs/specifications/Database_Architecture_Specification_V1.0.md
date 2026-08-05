# DATABASE ARCHITECTURE SPECIFICATION

## Version 1.0

### For the Master Research Framework Version 2.0 (Frozen)

**Quality by Design–Driven Development of Indomethacin Immediate-Release Tablets from Spray-Dried Amorphous Solid Dispersions Using an Integrated Computational Polymer Screening and Failure Mapping Framework**

**Document Classification:** OFFICIAL DATA BLUEPRINT  
**Status:** FROZEN — No implementation code permitted before this specification is approved  
**Date:** August 2026  
**Prepared by:** Interdisciplinary Scientific Data Architecture Team  
**Target Implementer:** M.Pharm Research Student (6-month timeline)  
**Aligned with:** Software Architecture Specification V1.0 | Master Research Framework V2.0

---

## DOCUMENT CONTROL

Table

|Version|Date|Author|Description|Status|
|:--|:--|:--|:--|:--|
|0.1|July 2026|Data Architecture Team|Initial schema draft based on Framework V1.0|Superseded|
|0.2|August 2026|Data Architecture Team|Revised per CSR-2026-IND-ASD-001 and SAS V1.0|Superseded|
|1.0|August 2026|Scientific Revision Committee|Frozen data blueprint aligned with Framework V2.0|**FROZEN**|

This document is the authoritative database architecture specification for the computational-experimental framework described in the Master Research Framework Version 2.0 (Frozen) and the Software Architecture Specification Version 1.0. No CSV files, YAML configurations, or database schemas shall be implemented before this specification is approved by the Scientific Revision Committee.

---

## TABLE OF CONTENTS

1. Executive Summary
    
2. Task 1 — Master Database Architecture
    
3. Task 2 — Drug Database
    
4. Task 3 — Polymer Database
    
5. Task 4 — Descriptor Database
    
6. Task 5 — Computational Results Database
    
7. Task 6 — Experimental Database
    
8. Task 7 — Validation Database
    
9. Task 8 — Configuration Files
    
10. Task 9 — Metadata Standards
    
11. Task 10 — Data Validation
    
12. Task 11 — Data Provenance
    
13. Task 12 — Publication Tables
    
14. Task 13 — Industrial Readiness
    
15. Task 14 — Documentation
    
16. Task 15 — Final Deliverable & Implementation Readiness
    
17. Appendices
    

---

## 1. EXECUTIVE SUMMARY

This Database Architecture Specification (DAS) Version 1.0 defines the complete data blueprint for a publication-quality, reproducible, and auditable data ecosystem that supports the Master Research Framework Version 2.0 (Frozen). The architecture is designed around eight core design principles:

1. **Schema-Before-Data:** Every column, unit, and constraint is defined before any data are entered.
    
2. **Scientific Justification:** Every field has an explicit pharmacological, physicochemical, or statistical rationale.
    
3. **Reproducibility by Design:** SHA-256 checksums, version pinning, and immutable audit trails are first-class citizens.
    
4. **FAIR Compliance:** Findable, Accessible, Interoperable, and Reusable data standards are enforced at the schema level.
    
5. **QbD Alignment:** Data structures directly map to ICH Q8(R2) Critical Quality Attributes (CQAs), Critical Material Attributes (CMAs), and Critical Process Parameters (CPPs).
    
6. **Extensibility:** The schema supports the six-polymer indomethacin worked example while reserving fields for future multi-drug expansion.
    
7. **Publication Readiness:** Every dataset is structured to generate manuscript tables, supplementary files, or supporting information without reformatting.
    
8. **Honest Positioning:** The schema acknowledges its TRL 4 status and distinguishes exploratory from confirmatory data fields explicitly.
    

### Target Environment

- Flat-file CSV architecture with JSON/YAML configuration (no relational database engine required).
    
- UTF-8 encoding, Unix line endings (LF), comma-delimited.
    
- Compatible with Python (pandas), R (readr), Excel, and Git version control.
    
- GitHub-hosted with Zenodo DOI archival for long-term data preservation.
    

---

## 2. TASK 1 — MASTER DATABASE ARCHITECTURE

### 2.1 Design Philosophy

The database architecture implements a **four-layer hierarchical data model** that mirrors the eight-layer computational architecture of Framework V2.0:

Table

|Layer|Name|Primary Files|Computational Mapping|Metadata Focus|
|:--|:--|:--|:--|:--|
|L1|Raw Data Layer|drug_database.csv, polymer_database.csv, descriptor_database.csv|Layers 1–3 (Drug Knowledge → Descriptor Generation)|Source provenance, literature references, physicochemical identity|
|L2|Processed Data Layer|results_database.csv, experimental_database.csv|Layers 4–7 (Compatibility → Prediction) + Experimental framework|Calculation parameters, instrument settings, process conditions|
|L3|Validation & Quality Layer|validation_database.csv, provenance_log.csv|Layer 8 (Validation) + Cross-cutting QC|Statistical metrics, QC flags, reviewer annotations, audit trails|
|L4|Configuration & Governance Layer|config.yaml, metadata_registry.json|Cross-cutting (all layers)|Naming conventions, units, controlled vocabulary, version control|

### 2.2 Entity Relationship Diagram (ERD)

The ERD (Figure 1, saved as `01_ERD_Database_Architecture_V1.0.png`) defines six primary entities and two cross-cutting governance entities:

**Primary Entities:**

1. **Drug Database** — Canonical physicochemical identity of the active pharmaceutical ingredient.
    
2. **Polymer Database** — Library of candidate polymeric carriers with regulatory and literature metadata.
    
3. **Descriptor Database** — Computed molecular descriptors and HSP group-contribution parameters.
    
4. **Computational Results Database** — All calculated compatibility scores, PCA outputs, AHP-TOPSIS rankings, and FBM predictions.
    
5. **Experimental Database** — Wet-lab characterization data from spray drying, DSC, FTIR, PXRD, dissolution, and stability.
    
6. **Validation Database** — Comparative metrics between computational predictions and experimental observations.
    

**Cross-Cutting Entities:** 7. **Configuration Registry** — All workflow parameters, thresholds, and weights as structured YAML/JSON. 8. **Provenance & Audit Log** — Immutable record of data origin, modification history, and verification status.

### 2.3 Relationship Definitions

Table

|Relationship|Cardinality|Directionality|Scientific Rationale|
|:--|:--|:--|:--|
|Drug → Descriptor|1:N|Unidirectional|One drug generates multiple descriptor sets (neutral + ionised states, multiple software versions)|
|Polymer → Descriptor|1:N|Unidirectional|One polymer generates descriptors per monomer + copolymer-weighted average|
|Drug → Computational Results|1:N|Unidirectional|One drug is screened against N polymers; each drug-polymer pair produces one result record|
|Polymer → Computational Results|1:N|Unidirectional|One polymer appears in N drug-polymer pairs across the library|
|Drug + Polymer → Experimental|M:N resolved via Formulation Code|Bidirectional (via FK)|Each formulation is a unique drug-polymer-batch combination; experimental data are inseparable from both parents|
|Computational Results → Validation|1:1 per formulation|Unidirectional|Each computational prediction is validated against exactly one experimental observation set|
|Experimental → Validation|1:1 per analysis|Unidirectional|Each experimental dataset produces one validation record per metric type|
|Configuration → All Entities|1:N|Omnidirectional (governance)|Configuration parameters govern calculation, acceptance criteria, and reporting for all entities|
|Provenance → All Entities|1:N|Omnidirectional (tracking)|Every entity record is tracked by at least one provenance entry|

### 2.4 Data Flow Architecture

The data flow (Figure 2, saved as `02_Data_Flow_Diagram_V1.0.png`) follows the 11-step computational workflow defined in Software Architecture V1.0, Section 3.4:

**Stage 1 (Input):** `drug_database.csv` + `polymer_database.csv` + `config/*.yaml` → Configuration Manager validates schemas.

**Stage 2 (Parsing):** Drug SMILES canonicalized; polymer library validated for uniqueness and PDI ≥ 1.0.

**Stage 3 (Descriptors):** RDKit computes 2D descriptors + Hoftyzer–Van Krevelen HSP → `descriptor_database.csv`.

**Stages 4–6 (Scoring):** HSP distance, Flory-Huggins χ, Gordon–Taylor Tg → `results_database.csv` (partial, scores only).

**Stage 7 (Integration):** PCA on 5-score matrix → retained PCs → CCI computation → `results_database.csv` (updated).

**Stage 8 (Ranking):** Multi-expert AHP → geometric-mean weights → TOPSIS ranking → `results_database.csv` (updated).

**Stage 8b (UQ):** Monte Carlo joint-distribution propagation → `results_database.csv` (uncertainty fields updated).

**Stage 8c (Sensitivity):** OAT + Morris screening → `results_database.csv` (sensitivity fields updated).

**Stage 9 (Prediction):** Logistic regression FBM → `results_database.csv` (FBM fields updated).

**Stage 10 (Validation):** Experimental data (`experimental_database.csv`) ingested → comparison metrics → `validation_database.csv`.

**Stage 11 (Reporting):** All databases consumed → `decision_report.json/pdf/xlsx`.

### 2.5 Metadata Hierarchy

The metadata hierarchy (Figure 3, saved as `03_Metadata_Hierarchy_V1.0.png`) enforces four levels of metadata governance:

**L4 (Governance):** `config.yaml` and `metadata_registry.json` define naming conventions, units, precision rules, controlled vocabularies, and version-control policies. These files are read-only at runtime and version-controlled via Git.

**L3 (Quality):** `validation_database.csv` and `provenance_log.csv` capture QC flags, statistical decisions, reviewer annotations, and audit trails. These files are append-only with SHA-256 chaining.

**L2 (Process):** `results_database.csv` and `experimental_database.csv` capture calculation versions, instrument IDs, SOP versions, and analyst identifiers. These files are write-once per execution.

**L1 (Source):** `drug_database.csv`, `polymer_database.csv`, and `descriptor_database.csv` capture literature DOIs, supplier batch IDs, CAS numbers, and raw analytical data. These files are immutable after initial curation.

---

## 3. TASK 2 — DRUG DATABASE

### 3.1 File Specification

**Filename:** `drug_database.csv`  
**Encoding:** UTF-8  
**Delimiter:** Comma (`,`)  
**Line Endings:** LF (Unix)  
**Header Row:** 1 (column names in row 1)  
**Schema Version:** 1.0.0  
**Primary Key:** `drug_id` (UUID v4)  
**Checksum:** SHA-256 computed on canonical sorted JSON representation  
**Scientific Justification:** This table stores the complete physicochemical identity of the active pharmaceutical ingredient. Every field is required for at least one computational layer (HSP, Flory-Huggins, Gordon–Taylor, or descriptors). The schema supports both experimental and estimated values with explicit provenance flags.

### 3.2 Column Specification

Table

|#|Column Name|Data Type|Constraints|Units|Scientific Justification|Missing Value Rule|
|:--|:--|:--|:--|:--|:--|:--|
|1|`drug_id`|String (UUID v4)|PK, unique, non-null|—|Immutable identifier for referential integrity across all databases|FAIL — cannot be null|
|2|`generic_name`|String|Non-null, max 255 chars|—|IUPAC-preferred name for manuscript and regulatory communication|FAIL|
|3|`canonical_smiles`|String|Non-null, RDKit-parseable|—|Structural input for descriptor calculation (Layer 3) and InChIKey derivation|FAIL|
|4|`inchi_key`|String (27 chars)|Non-null, derived from SMILES|—|Global identifier for duplicate detection and cross-referencing (PubChem, ChEMBL)|FAIL|
|5|`molecular_formula`|String|Non-null, Hill notation|—|Stoichiometric identity check; required for MW validation|FAIL|
|6|`molecular_weight_g_mol`|Float|> 0, ≤ 2000|g/mol|Required for Flory-Huggins χ calculation (molar volume derivation)|FAIL|
|7|`bcs_class`|String (enum)|Non-null, ∈ {I, II, III, IV, unknown}|—|Framework scope boundary; BCS II is the target class (low solubility, high permeability)|FAIL|
|8|`tm_k`|Float|300 < value < 800|K|Melting point for Boyer–Beaman Tg estimation and polymorph characterization|FAIL|
|9|`tg_k`|Float|200 < value < 500|K|Experimental glass transition temperature (preferred); used in Gordon–Taylor K calculation|NULL → use `tg_k_estimated` with flag|
|10|`tg_k_estimated`|Float|200 < value < 500|K|Boyer–Beaman fallback (0.7 × Tm); used when experimental Tg unavailable|NULL → if `tg_k` present|
|11|`tg_source`|String (enum)|∈ {experimental, boyer_beaman, literature, unknown}|—|Provenance flag for Tg value; triggers ±10 K uncertainty if estimated|FAIL|
|12|`density_crystalline_g_cm3`|Float|0.8 < value < 2.0|g/cm³|Crystalline density for Simha–Boyer K calculation; systematic bias flag if amorphous unavailable|FAIL|
|13|`density_amorphous_g_cm3`|Float|0.8 < value < 2.0|g/cm³|Amorphous density (preferred for GT); indomethacin: 1.22 g/cm³ (V2.0 revision)|NULL → use crystalline with `systematic_bias_flag`|
|14|`density_source`|String (enum)|∈ {experimental, literature, estimated, unknown}|—|Provenance for density; determines systematic bias flag in GT prediction|FAIL|
|15|`pka`|Float|0 < value < 14|—|Ionisation constant; determines ionisation state at physiological pH and HSP validity|NULL → tag as `neutral_assumption`|
|16|`logp`|Float|-5 < value < 10|—|Crippen logP from RDKit; lipophilicity descriptor for BCS classification verification|FAIL|
|17|`logd_ph74`|Float|-5 < value < 10|—|Distribution coefficient at pH 7.4; biopharmaceutical relevance for dissolution prediction|NULL → estimate from logp and pKa (Henderson-Hasselbalch)|
|18|`hbd`|Integer|≥ 0, ≤ 20|count|Hydrogen bond donor count; descriptor-based compatibility score (s_desc, weight 0.30)|FAIL|
|19|`hba`|Integer|≥ 0, ≤ 30|count|Hydrogen bond acceptor count; s_desc component (weight 0.30)|FAIL|
|20|`tpsa_angstrom2`|Float|≥ 0, ≤ 500|Å²|Topological polar surface area; s_desc component (weight 0.20)|FAIL|
|21|`rotatable_bonds`|Integer|≥ 0, ≤ 50|count|Molecular flexibility descriptor; s_desc component (weight 0.20)|FAIL|
|22|`aromatic_rings`|Integer|≥ 0, ≤ 20|count|π–π stacking potential; descriptor-based compatibility signal|FAIL|
|23|`hsp_delta_d`|Float|0 ≤ value ≤ 30|MPa^0.5|Hansen dispersion parameter; HSP distance calculation (Equation 1)|FAIL|
|24|`hsp_delta_p`|Float|0 ≤ value ≤ 30|MPa^0.5|Hansen polar parameter; HSP distance calculation|FAIL|
|25|`hsp_delta_h`|Float|0 ≤ value ≤ 30|MPa^0.5|Hansen hydrogen-bonding parameter; HSP distance calculation|FAIL|
|26|`hsp_ro`|Float|0 < value ≤ 15|MPa^0.5|Solubility sphere radius; RED denominator (Equation 2)|FAIL|
|27|`hsp_source`|String (enum)|∈ {experimental, hoftyzer_van_krevelen, stefanis_panayiotou, literature, unknown}|—|Provenance for HSP values; determines uncertainty magnitude (±1.5 MPa^0.5 if estimated)|FAIL|
|28|`molar_volume_cm3_mol`|Float|> 0|cm³/mol|Molar volume for Flory-Huggins χ calculation (Lindvig conversion, Equation 5)|FAIL|
|29|`delta_h_fus_kj_mol`|Float|> 0|kJ/mol|Enthalpy of fusion; optional for melting-point-depression (MPD) calibration of χ|NULL → MPD calibration infeasible|
|30|`aqueous_solubility_ph12_mg_ml`|Float|≥ 0|mg/mL|Solubility at gastric pH; biopharmaceutical relevance|NULL → label as `not_measured`|
|31|`aqueous_solubility_ph68_mg_ml`|Float|≥ 0|mg/mL|Solubility at intestinal pH; dissolution prediction input|NULL → label as `not_measured`|
|32|`polymorphs`|String (pipe-delimited)|Non-null|—|Known polymorph forms (e.g., "gamma|alpha"); polymorph-specific Tm and density|FAIL|
|33|`ionisation_state`|String (enum)|∈ {neutral, ionised, zwitterionic, unknown}|—|HSP group-contribution validity flag; ionised drugs break neutral-state HSP approximation|FAIL|
|34|`reference_doi`|String (semicolon-delimited)|Non-null|—|Primary literature source(s) for experimental values; CrossRef-validated format|FAIL|
|35|`reference_source`|String (enum)|∈ {peer_reviewed, handbook, supplier_coA, calculated, unknown}|—|Hierarchical evidence quality ranking for data quality scoring|FAIL|
|36|`data_quality_score`|Float|0.0–1.0|—|Composite score: 1.0 = peer-reviewed experimental; 0.5 = calculated/estimated; 0.0 = unknown|FAIL|
|37|`validation_status`|String (enum)|∈ {validated, estimated, provisional, deprecated}|—|Curation status; `deprecated` triggers exclusion from ranking|FAIL|
|38|`checksum_sha256`|String (64 chars)|Non-null, hex|—|Cryptographic integrity check on canonical JSON representation of this record|FAIL|
|39|`created_timestamp`|ISO 8601|Non-null|UTC|Record creation time for audit trail|FAIL|
|40|`modified_timestamp`|ISO 8601|Non-null|UTC|Last modification time; must update on any field change|FAIL|
|41|`modified_by`|String|Non-null|—|Analyst or script identifier responsible for last modification|FAIL|

### 3.3 Indomethacin Example Record (Reference)

csv

```csv
drug_id,generic_name,canonical_smiles,inchi_key,molecular_formula,molecular_weight_g_mol,bcs_class,tm_k,tg_k,tg_k_estimated,tg_source,density_crystalline_g_cm3,density_amorphous_g_cm3,density_source,pka,logp,logd_ph74,hbd,hba,tpsa_angstrom2,rotatable_bonds,aromatic_rings,hsp_delta_d,hsp_delta_p,hsp_delta_h,hsp_ro,hsp_source,molar_volume_cm3_mol,delta_h_fus_kj_mol,aqueous_solubility_ph12_mg_ml,aqueous_solubility_ph68_mg_ml,polymorphs,ionisation_state,reference_doi,reference_source,data_quality_score,validation_status,checksum_sha256,created_timestamp,modified_timestamp,modified_by
IND-001-2026,Indomethacin,CC1=C(C=C(C=C1)OC)C2=C(C3=CC=CC=C3N2CC(=O)O)C(=O)C4=CC=C(C=C4)Cl,CGIGDMFJXJATDK-UHFFFAOYSA-N,C19H16ClNO4,357.79,II,424.15,315.15,296.91,experimental,1.31,1.22,literature,4.5,4.27,1.32,2,4,68.5,4,2,19.2,7.9,8.4,8.0,literature,273.0,34.5,0.005,0.100,gamma|alpha,neutral,10.1016/j.xphs.2007.01.001,peer_reviewed,1.0,validated,sha256_placeholder,2026-08-01T00:00:00Z,2026-08-01T00:00:00Z,data_architect
```

---

## 4. TASK 3 — POLYMER DATABASE

### 4.1 File Specification

**Filename:** `polymer_database.csv`  
**Encoding:** UTF-8 | **Delimiter:** Comma | **Line Endings:** LF  
**Schema Version:** 1.0.0  
**Primary Key:** `polymer_id` (UUID v4)  
**Scientific Justification:** This table stores the complete physicochemical and regulatory identity of all candidate polymeric carriers. The schema supports homopolymers and copolymers, distinguishes regulatory grades, and captures literature evidence for miscibility with the target drug.

### 4.2 Column Specification

Table

|#|Column Name|Data Type|Constraints|Units|Scientific Justification|Missing Value Rule|
|:--|:--|:--|:--|:--|:--|:--|
|1|`polymer_id`|String (UUID v4)|PK, unique, non-null|—|Immutable identifier; referenced by descriptor, results, experimental, and validation databases|FAIL|
|2|`polymer_name`|String|Non-null, max 255 chars|—|Full chemical name (e.g., "Polyvinylpyrrolidone K30")|FAIL|
|3|`abbreviation`|String|Non-null, max 50 chars|—|Standard abbreviation (e.g., "PVP_K30") for manuscript and internal reference|FAIL|
|4|`polymer_family`|String (enum)|∈ {cellulosic, vinylic, acrylic, polyether, polyester, polyamide, natural_gum, other}|—|Structural class for rapid filtering and family-level analysis|FAIL|
|5|`polymer_class`|String (enum)|∈ {neutral, anionic, cationic, amphiphilic, zwitterionic}|—|Charge class determines ionic interaction potential with drug (critical for indomethacin pKa 4.5)|FAIL|
|6|`regulatory_status`|String (enum)|∈ {FDA_IID, Ph.Eur., USP_NF, JP, ChP, none, under_review}|—|Regulatory acceptability for oral solid dosage forms; FDA IID listed preferred for QbD submissions|FAIL|
|7|`supplier`|String|Non-null|—|Commercial source and catalog number for batch traceability|FAIL|
|8|`catalog_number`|String|Non-null|—|Supplier-specific identifier for reordering and batch consistency|NULL → use `unknown`|
|9|`batch_number`|String|Non-null|—|Manufacturing batch for GMP traceability (even at lab scale)|NULL → use `lab_scale_unbatched`|
|10|`mn_da`|Float|> 0|Da|Number-average molecular weight; required for χ critical calculation (degree of polymerization)|FAIL|
|11|`mw_da`|Float|≥ mn_da|Da|Weight-average molecular weight; PDI numerator|NULL → PDI cannot be computed|
|12|`pdi`|Float|≥ 1.0|—|Polydispersity index (Mw/Mn); PDI < 1.0 is physically impossible and triggers validation error|FAIL|
|13|`tg_k`|Float|200 < value < 600|K|Polymer glass transition temperature; Gordon–Taylor input and anti-plasticization assessment|FAIL|
|14|`tg_source`|String (enum)|∈ {experimental_dsc, experimental_dma, literature, estimated, unknown}|—|Provenance for Tg; determines uncertainty (±3 K if literature, ±10 K if estimated)|FAIL|
|15|`density_g_cm3`|Float|0.8 < value < 2.0|g/cm³|Bulk density for Simha–Boyer K calculation in Gordon–Taylor equation|FAIL|
|16|`density_source`|String (enum)|∈ {experimental_pycnometry, literature, estimated, unknown}|—|Provenance for density|FAIL|
|17|`hsp_delta_d`|Float|0 ≤ value ≤ 30|MPa^0.5|Hansen dispersion parameter for drug-polymer HSP distance|FAIL|
|18|`hsp_delta_p`|Float|0 ≤ value ≤ 30|MPa^0.5|Hansen polar parameter|FAIL|
|19|`hsp_delta_h`|Float|0 ≤ value ≤ 30|MPa^0.5|Hansen hydrogen-bonding parameter|FAIL|
|20|`hsp_total`|Float|Computed: sqrt(δD² + δP² + δH²)|MPa^0.5|Total Hansen solubility parameter; sanity check for component consistency|FAIL|
|21|`hsp_source`|String (enum)|∈ {experimental, hoftyzer_van_krevelen, group_contribution, literature, unknown}|—|Provenance for HSP; determines uncertainty magnitude|FAIL|
|22|`functional_groups`|String (pipe-delimited)|Non-null|—|Inventory of H-bond donors/acceptors, esters, ethers, amides (e.g., "lactam|amide|ether")|FAIL|
|23|`monomer_smiles`|String (pipe-delimited)|Non-null, RDKit-parseable|—|Repeat-unit SMILES; single string for homopolymers, pipe-delimited for copolymers|FAIL|
|24|`copolymer_mole_fractions`|String (pipe-delimited)|Sum = 1.0 if copolymer; NULL if homopolymer|—|Monomer mole fractions for weighted-average descriptor calculation|NULL → homopolymer assumed|
|25|`known_asd_applications`|String (semicolon-delimited)|Non-null|—|Literature-reported ASD drugs formulated with this polymer (e.g., "indomethacin;itraconazole")|NULL → `none_reported`|
|26|`spray_drying_suitability`|String (enum)|∈ {excellent, good, moderate, poor, unknown}|—|Empirical processability score based on Tg, solvent solubility, and hygroscopicity|FAIL|
|27|`hygroscopicity`|String (enum)|∈ {non_hygroscopic, slightly, moderately, very, unknown}|—|Critical for stability risk assessment and storage condition specification|FAIL|
|28|`literature_evidence_score`|Float|∈ {0.0, 0.5, 1.0}|—|1.0 = published miscibility with drug; 0.5 = no data; 0.0 = published immiscibility (s_lit input)|FAIL|
|29|`literature_dois`|String (semicolon-delimited)|Non-null if literature_evidence_score ≠ 0.5|—|Supporting references for miscibility/immiscibility claims|NULL if score = 0.5|
|30|`data_source`|String (enum)|∈ {supplier_coA, peer_reviewed, handbook, in_house, unknown}|—|Primary origin of physicochemical data|FAIL|
|31|`confidence_level`|String (enum)|∈ {high, moderate, low, very_low}|—|Aggregated confidence based on data source, replication, and method validation|FAIL|
|32|`validation_status`|String (enum)|∈ {validated, provisional, estimated, deprecated}|—|Curation status; `deprecated` excludes polymer from ranking|FAIL|
|33|`checksum_sha256`|String (64 chars)|Non-null|—|Record integrity|FAIL|
|34|`created_timestamp`|ISO 8601|Non-null|UTC|Audit trail|FAIL|
|35|`modified_timestamp`|ISO 8601|Non-null|UTC|Audit trail|FAIL|
|36|`modified_by`|String|Non-null|—|Accountability|FAIL|

### 4.3 Six-Polymer Library Example (Reference)

csv

```csv
polymer_id,polymer_name,abbreviation,polymer_family,polymer_class,regulatory_status,supplier,catalog_number,batch_number,mn_da,mw_da,pdi,tg_k,tg_source,density_g_cm3,density_source,hsp_delta_d,hsp_delta_p,hsp_delta_h,hsp_total,hsp_source,functional_groups,monomer_smiles,copolymer_mole_fractions,known_asd_applications,spray_drying_suitability,hygroscopicity,literature_evidence_score,literature_dois,data_source,confidence_level,validation_status,checksum_sha256,created_timestamp,modified_timestamp,modified_by
POL-001-2026,Polyvinylpyrrolidone K30,PVP_K30,vinylic,neutral,FDA_IID,BASF,9003-39-8,LOT-2026-A,40000,50000,1.25,443.0,experimental_dsc,1.20,literature,17.4,8.2,11.7,21.9,hoftyzer_van_krevelen,lactam|amide,C=CN1CCCC1=O,,indomethacin;itraconazole;carbamazepine,excellent,very,1.0,10.1016/j.xphs.2007.01.001,supplier_coA,high,validated,sha256_placeholder,2026-08-01T00:00:00Z,2026-08-01T00:00:00Z,data_architect
POL-002-2026,PVP-Vinyl Acetate 64,PVP_VA_64,vinylic,neutral,FDA_IID,BASF,25086-89-9,LOT-2026-B,45000,54000,1.20,380.0,experimental_dsc,1.20,literature,17.0,8.0,10.0,20.6,hoftyzer_van_krevelen,lactam|amide|ester,C=CN1CCCC1=O|CC(=O)OC,0.6|0.4,indomethacin;felodipine,good,moderately,1.0,10.1016/j.ijpharm.2010.01.001,supplier_coA,high,validated,sha256_placeholder,2026-08-01T00:00:00Z,2026-08-01T00:00:00Z,data_architect
POL-003-2026,HPMC Acetate Succinate Low,HPMCAS_L,cellulosic,anionic,FDA_IID,Shin-Etsu,71138-97-1,LOT-2026-C,100000,120000,1.20,394.0,experimental_dsc,1.28,literature,18.0,8.2,10.5,21.8,hoftyzer_van_krevelen,ether|ester|carboxyl,COCC1O[C@H](O)[C@@H](O)[C@H](O)[C@H]1O,,indomethacin;naproxen,good,slightly,1.0,10.1016/j.ijpharm.2014.05.001,supplier_coA,high,validated,sha256_placeholder,2026-08-01T00:00:00Z,2026-08-01T00:00:00Z,data_architect
POL-004-2026,Eudragit L100,EDR_L100,acrylic,anionic,Ph.Eur.,Evonik,25806-15-1,LOT-2026-D,125000,150000,1.20,438.0,experimental_dsc,1.25,literature,16.5,7.5,9.0,19.9,hoftyzer_van_krevelen,ester|carboxyl,CC(C)C(=O)OC(C)C|C/C(=C\\C(=O)O)C,0.5|0.5,indomethacin;carbamazepine,moderate,slightly,0.5,,supplier_coA,moderate,validated,sha256_placeholder,2026-08-01T00:00:00Z,2026-08-01T00:00:00Z,data_architect
POL-005-2026,Soluplus,SOLUPLUS,acrylic,amphiphilic,FDA_IID,BASF,402932-23-4,LOT-2026-E,90000,118800,1.32,343.0,experimental_dsc,1.15,literature,18.0,8.5,10.5,21.9,hoftyzer_van_krevelen,ester|ether|lactam,CC(=O)OCC(C)C|CC(C)C(=O)OCC(C)C|C=CN1CCCC1=O,0.3|0.3|0.4,indomethacin;itraconazole,excellent,slightly,1.0,10.1016/j.ijpharm.2010.05.001,supplier_coA,high,validated,sha256_placeholder,2026-08-01T00:00:00Z,2026-08-01T00:00:00Z,data_architect
POL-006-2026,Hydroxypropyl Methylcellulose E5,HPMC_E5,cellulosic,neutral,USP_NF,Dow Chemical,9004-65-3,LOT-2026-F,20000,26000,1.30,438.0,experimental_dsc,1.33,literature,18.5,8.8,12.0,22.9,hoftyzer_van_krevelen,ether|hydroxyl,COCC1O[C@H](O)[C@@H](O)[C@H](O)[C@H]1O,,indomethacin;felodipine,good,moderately,0.5,,supplier_coA,moderate,validated,sha256_placeholder,2026-08-01T00:00:00Z,2026-08-01T00:00:00Z,data_architect
```

---

## 5. TASK 4 — DESCRIPTOR DATABASE

### 5.1 File Specification

**Filename:** `descriptor_database.csv`  
**Encoding:** UTF-8 | **Delimiter:** Comma | **Line Endings:** LF  
**Schema Version:** 1.0.0  
**Composite Primary Key:** (`descriptor_id`)  
**Foreign Keys:** `drug_id` → Drug Database; `polymer_id` → Polymer Database  
**Scientific Justification:** This table separates computed descriptors from raw physicochemical properties to enable version tracking, reproducibility verification, and recalculation on demand. It stores both RDKit 2D descriptors and Hoftyzer–Van Krevelen group-contribution outputs.

### 5.2 Column Specification

Table

|#|Column Name|Data Type|Constraints|Units|Scientific Justification|Missing Value Rule|
|:--|:--|:--|:--|:--|:--|:--|
|1|`descriptor_id`|String (UUID v4)|PK, unique|—|Unique identifier for each descriptor calculation event|FAIL|
|2|`drug_id`|String (UUID)|FK → drug_database.drug_id|—|Links to parent drug; NULL for polymer-only descriptors|NULL allowed|
|3|`polymer_id`|String (UUID)|FK → polymer_database.polymer_id|—|Links to parent polymer; NULL for drug-only descriptors|NULL allowed|
|4|`entity_type`|String (enum)|∈ {drug, polymer, copolymer_weighted}|—|Distinguishes drug descriptors, polymer descriptors, and copolymer averages|FAIL|
|5|`descriptor_name`|String|Non-null|—|Standardized descriptor name (e.g., "MolLogP", "TPSA", "NumHDonors")|FAIL|
|6|`descriptor_value`|Float|—|varies|Numerical value; unit specified in `units` column|FAIL|
|7|`descriptor_definition`|String|Non-null|—|Human-readable definition (e.g., "Crippen octanol-water partition coefficient")|FAIL|
|8|`calculation_method`|String (enum)|∈ {rdkit_2d, rdkit_3d, hoftyzer_van_krevelen, stefanis_panayiotou, custom_script}|—|Algorithm provenance; determines reproducibility and uncertainty|FAIL|
|9|`rdkit_version`|String|SemVer format|—|Exact RDKit version for bit-for-bit reproducibility|FAIL|
|10|`software_version`|String|SemVer format|—|Framework version that generated this descriptor|FAIL|
|11|`units`|String|Non-null|—|Physical units (e.g., "log_units", "angstrom2", "count", "MPa^0.5")|FAIL|
|12|`normalization_status`|String (enum)|∈ {raw, min_max_scaled, z_score, robust_scaled, none}|—|Whether value has been normalized; raw preferred for auditability|FAIL|
|13|`normalization_method`|String|Required if normalized|—|Description of normalization parameters (e.g., "min=0, max=500")|NULL if raw|
|14|`normalization_reference`|String|Required if normalized|—|Dataset used for normalization bounds|NULL if raw|
|15|`calculation_date`|ISO 8601|Non-null|UTC|Timestamp of descriptor computation|FAIL|
|16|`input_smiles`|String|Non-null|—|SMILES string used as input (preserved even if canonicalization occurred)|FAIL|
|17|`input_smiles_canonical`|Boolean|Non-null|—|TRUE if input was canonicalized before calculation|FAIL|
|18|`calculation_environment`|String|Non-null|—|OS, Python version, conda environment hash|FAIL|
|19|`checksum_sha256`|String (64 chars)|Non-null|—|Integrity check on input SMILES + parameters|FAIL|

### 5.3 Descriptor Inventory (Mandatory Set)

The following descriptors MUST be calculated for every drug and polymer:

Table

|Descriptor|RDKit Name|Type|Unit|Used In|
|:--|:--|:--|:--|:--|
|Molecular Weight|`MolWt`|float|g/mol|s_desc normalization reference|
|Crippen LogP|`MolLogP`|float|log units|BCS verification, s_desc (weight 0.20)|
|Topological Polar Surface Area|`TPSA`|float|Å²|s_desc (weight 0.20)|
|Hydrogen Bond Donors|`NumHDonors`|int|count|s_desc (weight 0.30)|
|Hydrogen Bond Acceptors|`NumHAcceptors`|int|count|s_desc (weight 0.30)|
|Rotatable Bonds|`NumRotatableBonds`|int|count|Flexibility descriptor|
|Aromatic Rings|`NumAromaticRings`|int|count|π-stacking descriptor|
|Fractional Polar Surface Area|`TPSA / MolWt`|float|—|Normalized polarity|
|HSP δD (group contribution)|`HSP_delta_D`|float|MPa^0.5|HSP distance (Eq. 1)|
|HSP δP (group contribution)|`HSP_delta_P`|float|MPa^0.5|HSP distance|
|HSP δH (group contribution)|`HSP_delta_H`|float|MPa^0.5|HSP distance|

---

## 6. TASK 5 — COMPUTATIONAL RESULTS DATABASE

### 6.1 File Specification

**Filename:** `results_database.csv`  
**Encoding:** UTF-8 | **Delimiter:** Comma | **Line Endings:** LF  
**Schema Version:** 1.0.0  
**Composite Primary Key:** (`result_id`)  
**Foreign Keys:** `drug_id`, `polymer_id`  
**Scientific Justification:** This is the central analytical database. It stores every calculated score, index, and prediction produced by the eight computational layers. The schema is designed to support the Decision Report (Framework V2.0, Table 12.1) directly.

### 6.2 Column Specification

Table

|#|Column Name|Data Type|Constraints|Units|Scientific Justification|Missing Value Rule|
|:--|:--|:--|:--|:--|:--|:--|
|1|`result_id`|String (UUID v4)|PK, unique|—|Unique identifier for each drug-polymer-calculation combination|FAIL|
|2|`drug_id`|String (UUID)|FK → Drug|—|Parent drug|FAIL|
|3|`polymer_id`|String (UUID)|FK → Polymer|—|Parent polymer|FAIL|
|4|`calculation_run_id`|String (UUID)|Non-null|—|Groups all results from a single pipeline execution (enables rerun comparison)|FAIL|
|5|`drug_loading_ww`|Float|0.0–1.0|mass fraction|Drug mass fraction for which scores are computed (default 0.30)|FAIL|
|6|`hsp_distance_ra`|Float|≥ 0|MPa^0.5|Hansen distance (Equation 1); primary HSP compatibility metric|FAIL|
|7|`hsp_red`|Float|≥ 0|—|Relative Energy Difference (Equation 2); Gate 1 threshold = 1.0|FAIL|
|8|`s_hsp_score`|Float|0.0–1.0|—|Normalized HSP compatibility: max(0, 1 − RED/2)|FAIL|
|9|`flory_huggins_chi`|Float|—|dimensionless|Lindvig conversion (Equation 5); enthalpic mixing parameter|FAIL|
|10|`chi_critical`|Float|—|dimensionless|χc = 0.5(1 + 1/√r₁ + 1/√r₂)²; phase separation threshold|FAIL|
|11|`s_chi_score`|Float|0.0–1.0|—|Normalized χ compatibility: max(0, 1 − χ)|FAIL|
|12|`gordon_taylor_k`|Float|> 0|—|Simha–Boyer K = (ρ_drug × Tg_drug) / (ρ_polymer × Tg_polymer)|FAIL|
|13|`predicted_tg_k`|Float|200–600|K|Gordon–Taylor Tg_mix prediction (Equation 6)|FAIL|
|14|`predicted_tg_kwei_k`|Float|200–600|K|Optional Kwei-corrected Tg (if q parameter available)|NULL → Kwei not applied|
|15|`s_gt_score`|Float|0.0–1.0|—|Normalized GT score: (Tg_mix − (Tg_drug+30)) / 50, clipped [0,1]|FAIL|
|16|`s_desc_score`|Float|0.0–1.0|—|Weighted descriptor compatibility (HBD 0.3, HBA 0.3, TPSA 0.2, aromatic 0.2)|FAIL|
|17|`s_lit_score`|Float|∈ {0.0, 0.5, 1.0}|—|Literature evidence score from polymer database|FAIL|
|18|`pca_pc1_score`|Float|—|—|Principal Component 1 score from 5-score matrix PCA|FAIL|
|19|`pca_pc2_score`|Float|—|—|Principal Component 2 score (if retained)|NULL if k=1|
|20|`pca_pc3_score`|Float|—|—|Principal Component 3 score (if retained)|NULL if k<3|
|21|`pca_variance_explained_pc1`|Float|0.0–1.0|—|Proportion variance explained by PC1|FAIL|
|22|`pca_effective_dimensionality_k`|Integer|1–5|—|Number of retained PCs (≥95% cumulative variance)|FAIL|
|23|`cci_value`|Float|0.0–1.0|—|Composite Compatibility Index (Equation 10, revised): weighted sum of retained PCs|FAIL|
|24|`cci_contribution_pc1`|Float|—|—|Justification trace: w₁ × T_i,1|FAIL|
|25|`cci_contribution_pc2`|Float|—|—|Justification trace: w₂ × T_i,2|NULL if k=1|
|26|`ahp_weight_pc1`|Float|0.0–1.0|—|AHP-derived weight for PC1|FAIL|
|27|`ahp_weight_pc2`|Float|0.0–1.0|—|AHP-derived weight for PC2|NULL if k=1|
|28|`ahp_cr_aggregated`|Float|0.0–1.0|—|Consistency ratio of geometric-mean aggregated matrix; Gate 2 threshold < 0.08|FAIL|
|29|`ahp_kendall_w`|Float|0.0–1.0|—|Inter-expert concordance; < 0.50 triggers re-elicitation|FAIL|
|30|`ahp_expert_count`|Integer|1–5|—|Number of experts in elicitation panel|FAIL|
|31|`topsis_cl`|Float|0.0–1.0|—|Closeness coefficient (Equation 9); ranking metric|FAIL|
|32|`topsis_rank`|Integer|≥ 1|—|Final polymer rank (1 = best)|FAIL|
|33|`topsis_ideal_distance`|Float|≥ 0|—|Euclidean distance to ideal solution (D+)|FAIL|
|34|`topsis_anti_ideal_distance`|Float|≥ 0|—|Euclidean distance to anti-ideal solution (D−)|FAIL|
|35|`fbm_p_failure`|Float|0.0–1.0|—|Logistic regression P(failure) (Equation 11)|NULL if FBM not fitted|
|36|`fbm_region`|String (enum)|∈ {Safe, Warning, Failure, not_calculated}|—|Probabilistic region: Safe <0.30, Warning 0.30–0.70, Failure >0.70|NULL if FBM not fitted|
|37|`fbm_auc_roc`|Float|0.5–1.0|—|Model fit metric; < 0.75 triggers "low confidence" flag|NULL if FBM not fitted|
|38|`monte_carlo_p_top1`|Float|0.0–1.0|—|Decision confidence: fraction of MC iterations where this polymer is rank-1|FAIL|
|39|`monte_carlo_ci_lower`|Float|0.0–1.0|—|2.5th percentile of CCI distribution|FAIL|
|40|`monte_carlo_ci_upper`|Float|0.0–1.0|—|97.5th percentile of CCI distribution|FAIL|
|41|`confidence_tier`|String (enum)|∈ {High, Moderate, Low, Very_Low}|—|High: P(top-1) ≥ 0.70; Moderate: 0.40–0.70; Low: < 0.40|FAIL|
|42|`sensitivity_top1_stability_fraction`|Float|0.0–1.0|—|Fraction of OAT/MC runs where top-1 is unchanged|FAIL|
|43|`sensitivity_median_spearman_rho`|Float|-1.0–1.0|—|Median rank correlation across MC weight variations|FAIL|
|44|`sensitivity_morris_mu_pc1`|Float|≥ 0|—|Morris elementary effect mean for PC1 weight|FAIL|
|45|`sensitivity_morris_sigma_pc1`|Float|≥ 0|—|Morris elementary effect SD for PC1 weight|FAIL|
|46|`sensitivity_flags`|String (semicolon-delimited)|—|—|Dominant/interactive weight flags (e.g., "PC1_dominant;PC2_interactive")|NULL if no flags|
|47|`calculation_version`|String|SemVer|—|Software version (e.g., "1.0.0")|FAIL|
|48|`calculation_timestamp`|ISO 8601|Non-null|UTC|Execution timestamp|FAIL|
|49|`random_seed`|Integer|Non-null|—|Fixed seed for reproducibility (default 42)|FAIL|
|50|`checksum_sha256`|String (64 chars)|Non-null|—|Integrity check on all input fields + config|FAIL|

---

## 7. TASK 6 — EXPERIMENTAL DATABASE

### 7.1 File Specification

**Filename:** `experimental_database.csv`  
**Encoding:** UTF-8 | **Delimiter:** Comma | **Line Endings:** LF  
**Schema Version:** 1.0.0  
**Primary Key:** `experiment_id` (UUID v4)  
**Foreign Keys:** `drug_id`, `polymer_id`  
**Scientific Justification:** This table captures all wet-lab characterization data required for validation against computational predictions. The schema supports the 40-week implementation roadmap (Framework V2.0, Section 23) and ICH Q1A(R2) stability study requirements.

### 7.2 Column Specification

Table

|#|Column Name|Data Type|Constraints|Units|Scientific Justification|Missing Value Rule|
|:--|:--|:--|:--|:--|:--|:--|
|1|`experiment_id`|String (UUID v4)|PK, unique|—|Unique identifier for each experimental record|FAIL|
|2|`drug_id`|String (UUID)|FK → Drug|—|Parent drug|FAIL|
|3|`polymer_id`|String (UUID)|FK → Polymer|—|Parent polymer|FAIL|
|4|`formulation_code`|String|Non-null, unique per batch|—|Human-readable code (e.g., "IND-PVP30-B1-D30")|FAIL|
|5|`batch_number`|String|Non-null|—|Manufacturing batch identifier (3 batches required for rank-1 polymer, V2.0)|FAIL|
|6|`batch_replicate`|Integer|≥ 1|—|Replicate within batch (for intra-batch precision)|FAIL|
|7|`drug_load_percent_ww`|Float|10.0–50.0|% w/w|Actual drug loading measured by HPLC-UV|FAIL|
|8|`spray_dryer_model`|String|Non-null|—|Instrument identifier (e.g., "Buchi_B-290_Serial_12345")|FAIL|
|9|`inlet_temperature_c`|Float|60–150|°C|Critical Process Parameter (CPP); DoE factor|FAIL|
|10|`outlet_temperature_c`|Float|40–90|°C|CPP; indicates drying efficiency and thermal stress|FAIL|
|11|`feed_rate_ml_min`|Float|2–20|mL/min|CPP; affects droplet size and drying time|FAIL|
|12|`atomization_flow_l_h`|Float|400–800|L/h|CPP; nitrogen flow rate for atomization|FAIL|
|13|`aspirator_rate_percent`|Float|80–100|%|CPP; vacuum level for powder collection|FAIL|
|14|`solvent`|String (enum)|∈ {acetone, ethanol, methanol, dichloromethane, acetone_water_mix}|—|Solvent for feed solution; acetone preferred for indomethacin|FAIL|
|15|`feed_concentration_percent_wv`|Float|2–20|% w/v|Total solids concentration in feed|FAIL|
|16|`yield_percent`|Float|0–100|%|Process efficiency; mass of collected powder / mass of solids fed|FAIL|
|17|`yield_method`|String (enum)|∈ {gravimetric, calculated_from_hplc}|—|Method for yield determination|FAIL|
|18|`dsc_tg_k`|Float|200–500|K|Glass transition temperature by DSC; primary CMA for stability|FAIL|
|19|`dsc_tonset_k`|Float|200–500|K|Onset of Tg transition; indicates transition breadth|NULL if not reported|
|20|`dsc_delta_cp_j_g_k`|Float|> 0|J/(g·K)|Heat capacity change at Tg; indicates amorphicity|NULL if not reported|
|21|`dsc_mdsc_reversing_tg_k`|Float|200–500|K|MDSC reversing heat flow Tg (V2.0 recommendation)|NULL if conventional DSC only|
|22|`ftir_carbonyl_shift_cm`|Float|1600–1800|cm⁻¹|Carbonyl stretch position; H-bonding indicator|NULL if not measured|
|23|`ftir_hydrogen_bond_shift_cm`|Float|3000–3600|cm⁻¹|O-H/N-H stretch shift; specific interaction evidence|NULL if not measured|
|24|`ftir_method`|String (enum)|∈ {atr, kbr_pellet, nujol_mull}|—|ATR preferred per V2.0 (criticism Q-MOD-012)|FAIL|
|25|`pxrd_crystalline_bool`|Boolean|Non-null|—|TRUE if crystalline peaks detected; FALSE = amorphous|FAIL|
|26|`pxrd_2theta_main_peak`|Float|5–40|° 2θ|Position of strongest peak (if crystalline)|NULL if amorphous|
|27|`pxrd_method`|String|Non-null|—|Instrument parameters (Cu-Kα, 40 kV, 40 mA, etc.)|FAIL|
|28|`drug_content_percent`|Float|80–120|%|Actual drug content by HPLC-UV vs theoretical loading|FAIL|
|29|`dissolution_q15_percent`|Float|0–150|%|Cumulative dissolution at 15 min; primary CQA|FAIL|
|30|`dissolution_q30_percent`|Float|0–150|%|Cumulative dissolution at 30 min; FBM primary endpoint|FAIL|
|31|`dissolution_q60_percent`|Float|0–150|%|Cumulative dissolution at 60 min|FAIL|
|32|`dissolution_medium_ph`|Float|∈ {1.2, 4.5, 6.8}|—|Multi-pH mandatory per V2.0 (criticism 5.4)|FAIL|
|33|`dissolution_apparatus`|String (enum)|∈ {USP_I, USP_II, USP_IV}|—|USP Apparatus II (paddles) standard per V2.0|FAIL|
|34|`dissolution_rpm`|Integer|50–100|rpm|Agitation speed|FAIL|
|35|`dissolution_temperature_c`|Float|37.0 ± 0.5|°C|Bath temperature|FAIL|
|36|`dissolution_vessel_n`|Integer|6–24|—|Number of vessels; 12 per polymer per pH per V2.0|FAIL|
|37|`tablet_hardness_kp`|Float|4–8|kp|Tablet breaking force; USP <1216>|NULL if not tableted|
|38|`tablet_friability_percent`|Float|0–2|%|Weight loss after tumbling; USP <1216>|NULL if not tableted|
|39|`tablet_disintegration_min`|Float|0–30|min|Disintegration time; USP <701>|NULL if not tableted|
|40|`tablet_weight_mg`|Float|100–500|mg|Mean tablet weight|NULL if not tableted|
|41|`tablet_weight_rsd_percent`|Float|0–5|%|Relative standard deviation of weight|NULL if not tableted|
|42|`stability_timepoint_months`|Float|∈ {0, 1, 3, 6, 12, 24}|months|ICH Q1A timepoint; 0 = initial|FAIL|
|43|`stability_condition`|String (enum)|∈ {T0, 25C_60RH, 30C_65RH, 40C_75RH}|—|Storage condition per ICH Q1A(R2)|FAIL|
|44|`stability_assay_percent`|Float|90–110|%|Drug assay at timepoint by HPLC-UV|NULL if not tested|
|45|`stability_water_content_percent`|Float|0–10|%|Karl Fischer water content (V2.0 addition, criticism Q-MOD-020)|NULL if not tested|
|46|`residual_solvent_ppm`|Float|≥ 0|ppm|GC-HS residual solvent (ICH Q3C); acetone limit 5000 ppm|NULL if not tested|
|47|`residual_solvent_identity`|String|—|—|Identified residual solvent|NULL if not tested|
|48|`analyst_id`|String|Non-null|—|Analyst identifier for GLP traceability|FAIL|
|49|`experiment_date`|ISO 8601|Non-null|UTC|Date of experiment execution|FAIL|
|50|`instrument_qc_pass_bool`|Boolean|Non-null|—|TRUE if instrument calibration verified within date|FAIL|
|51|`sop_version`|String|Non-null|—|Standard Operating Procedure version used|FAIL|
|52|`validation_status`|String (enum)|∈ {raw, qc_passed, outlier_flagged, rejected}|—|QC status; `rejected` excludes record from validation|FAIL|
|53|`checksum_sha256`|String (64 chars)|Non-null|—|Record integrity|FAIL|

---

## 8. TASK 7 — VALIDATION DATABASE

### 8.1 File Specification

**Filename:** `validation_database.csv`  
**Encoding:** UTF-8 | **Delimiter:** Comma | **Line Endings:** LF  
**Schema Version:** 1.0.0  
**Primary Key:** `validation_id` (UUID v4)  
**Foreign Keys:** `result_id` → Results; `experiment_id` → Experimental  
**Scientific Justification:** This table stores the comparative statistical metrics between computational predictions and experimental observations. It implements the validation strategy revisions from Framework V2.0 (Section 11): negative controls, held-out test sets, baseline comparisons, and LOO cross-validation.

### 8.2 Column Specification

Table

|#|Column Name|Data Type|Constraints|Units|Scientific Justification|Missing Value Rule|
|:--|:--|:--|:--|:--|:--|:--|
|1|`validation_id`|String (UUID v4)|PK, unique|—|Unique identifier|FAIL|
|2|`result_id`|String (UUID)|FK → Results|—|Computational prediction being validated|FAIL|
|3|`experiment_id`|String (UUID)|FK → Experimental|—|Experimental observation used for validation|FAIL|
|4|`validation_type`|String (enum)|∈ {prospective, retrospective, loo_cv, held_out_test, negative_control, baseline_comparison}|—|Distinguishes validation protocols (V2.0 Section 11)|FAIL|
|5|`prediction_variable`|String (enum)|∈ {tg_k, dissolution_q30, rank_order, miscibility_class, stability_tier, fbm_boundary}|—|Which prediction is being validated|FAIL|
|6|`predicted_value`|Float/String|—|varies|Computational prediction (numeric or categorical)|FAIL|
|7|`observed_value`|Float/String|—|varies|Experimental observation (numeric or categorical)|FAIL|
|8|`prediction_error`|Float|—|varies|Predicted − Observed (signed)|FAIL|
|9|`prediction_error_abs`|Float|≥ 0|varies|Absolute error|FAIL|
|10|`rmse_k`|Float|≥ 0|K|Root mean square error (for Tg predictions)|NULL if not continuous|
|11|`rmse_bootstrap_ci_lower`|Float|≥ 0|K|2.5th percentile of bootstrap RMSE distribution|NULL if not bootstrapped|
|12|`rmse_bootstrap_ci_upper`|Float|≥ 0|K|97.5th percentile of bootstrap RMSE distribution|NULL if not bootstrapped|
|13|`mae_k`|Float|≥ 0|K|Mean absolute error|NULL if not continuous|
|14|`mae_bootstrap_ci_lower`|Float|≥ 0|K|Bootstrap CI for MAE|NULL if not bootstrapped|
|15|`mae_bootstrap_ci_upper`|Float|≥ 0|K|Bootstrap CI for MAE|NULL if not bootstrapped|
|16|`spearman_rho`|Float|-1.0–1.0|—|Rank correlation; H1 primary endpoint (≥ 0.70)|NULL if not rank-based|
|17|`spearman_ci_lower`|Float|-1.0–1.0|—|95% CI via Fisher z-transformation|NULL if n < 6|
|18|`spearman_ci_upper`|Float|-1.0–1.0|—|95% CI via Fisher z-transformation|NULL if n < 6|
|19|`kendall_tau`|Float|-1.0–1.0|—|Kendall rank correlation|NULL if not rank-based|
|20|`top_k_agreement`|Integer|0–N|—|Number of polymers correctly ranked in top-k|NULL if not rank-based|
|21|`baseline_comparison_type`|String (enum)|∈ {hsp_only, equal_weight, full_cci, none}|—|Which baseline this record compares against|NULL if not baseline comparison|
|22|`delta_spearman_vs_baseline`|Float|-1.0–1.0|—|Δρ = ρ(full CCI) − ρ(baseline); must be ≥ 0.10|NULL if not baseline comparison|
|23|`validation_decision`|String (enum)|∈ {supported, not_supported, marginally_supported, exploratory, inconclusive}|—|Pre-registered decision rule outcome (V2.0 Section 15.0)|FAIL|
|24|`exploratory_confirmatory_flag`|String (enum)|∈ {exploratory, confirmatory, preliminary}|—|n=6–8 = exploratory; n≥20 = confirmatory (V2.0 Section 11.3)|FAIL|
|25|`null_hypothesis`|String|Non-null|—|Formal H₀ notation (e.g., "ρ < 0.70")|FAIL|
|26|`alternative_hypothesis`|String|Non-null|—|Formal H₁ notation (e.g., "ρ ≥ 0.70")|FAIL|
|27|`alpha_level`|Float|0.0–1.0|—|Significance level (default 0.05)|FAIL|
|28|`p_value`|Float|0.0–1.0|—|Test statistic p-value|NULL if not applicable|
|29|`effect_size`|Float|—|—|Cohen's d, eta², or other appropriate effect size|NULL if not applicable|
|30|`power_analysis_n_required`|Integer|≥ 1|—|Sample size required for 80% power at observed effect size|NULL if not computed|
|31|`reviewer_notes`|String (max 2000 chars)|—|—|Free-text interpretation by validation reviewer|NULL if no notes|
|32|`validation_date`|ISO 8601|Non-null|UTC|Timestamp of validation analysis|FAIL|
|33|`validator_id`|String|Non-null|—|Analyst or script performing validation|FAIL|
|34|`checksum_sha256`|String (64 chars)|Non-null|—|Integrity check|FAIL|

---

## 8. TASK 8 — CONFIGURATION FILES

### 8.1 Design Philosophy

Configuration files are the **governance layer** of the database architecture. They externalize all tunable parameters, thresholds, and weights so that (a) no hard-coded constants exist in the computational pipeline, and (b) every execution is fully reproducible from version-controlled configuration alone. All configuration files are **read-only at runtime** and modified only through Git-tracked commits.

### 8.2 File Inventory

Table

|Filename|Format|Purpose|Runtime Access|
|:--|:--|:--|:--|
|`config.yaml`|YAML|Master workflow configuration|Read-only|
|`weights.yaml`|YAML|AHP-derived and fixed weights|Read-only|
|`thresholds.yaml`|YAML|Gate thresholds and acceptance criteria|Read-only|
|`validation_rules.yaml`|YAML|Data validation schema and rules|Read-only|
|`logging.yaml`|YAML|Logging levels, paths, and retention|Read-only|
|`metadata_registry.json`|JSON|Controlled vocabularies and naming conventions|Read-only|

### 8.3 config.yaml — Master Workflow Configuration

yaml

```yaml
schema_version: "1.0.0"
database_version: "1.0.0"
framework_version: "2.0"

# Execution control
execution:
  mode: "full"  # Options: full, compute_only, validate_only
  random_seed: 42
  parallel_workers: 1  # Deterministic; no parallelization for reproducibility
  
# File paths (relative to project root)
paths:
  drug_database: "data/drug_database.csv"
  polymer_database: "data/polymer_database.csv"
  descriptor_database: "data/descriptor_database.csv"
  results_database: "data/results_database.csv"
  experimental_database: "data/experimental_database.csv"
  validation_database: "data/validation_database.csv"
  provenance_log: "logs/provenance_log.csv"
  output_dir: "results/"
  
# Drug-specific parameters
drug:
  default_drug_id: "IND-001-2026"
  drug_loading_default_ww: 0.30
  drug_loading_range:
    min: 0.10
    max: 0.50
    step: 0.05
  ionisation_state_ph: 7.4  # For logD estimation
  
# Polymer library parameters
polymer:
  min_candidates: 3  # Gate 1: halt if fewer than 3 polymers pass RED filter
  max_candidates: 50  # Future expansion limit
  default_library: "config/polymers/polymer_library_v2.csv"
  
# Computational parameters
computation:
  temperature_k: 298.15  # Standard temperature for HSP and chi calculations
  hsp_lindvig_weights: [0.6, 0.25, 0.25]  # δD, δP, δH weights for chi conversion
  chi_uncertainty_relative: 0.25  # V2.0 revised from 0.15 (criticism 4.3)
  gt_kwei_q: null  # Optional; fitted from experimental data if available
  
# PCA parameters
pca:
  variance_threshold: 0.95  # Cumulative variance to retain PCs
  center: true
  scale: true
  
# Monte Carlo Uncertainty Quantification
monte_carlo:
  n_iterations: 10000
  n_chains: 5
  convergence_method: "gelman_rubin"  # Alternative: "coefficient_of_variation"
  r_hat_threshold: 1.01
  covariance_structure: "diagonal"  # V2.0 revised from "full" (criticism 8.2)
  confidence_level: 0.95
  
# Failure Boundary Map (FBM)
fbm:
  enabled: true
  model_type: "logistic_regression"
  solver: "lbfgs"
  max_iter: 1000
  class_weight: "balanced"
  cross_validation_folds: 5
  min_samples_per_class: 3  # V2.0: minimum 3 per class for FBM fitting
  random_state: 42
  
# Reporting
reporting:
  output_formats: ["json", "pdf", "xlsx"]
  include_justification_traces: true
  include_sensitivity_analysis: true
  include_raw_data: false  # Raw data linked, not embedded
  template_dir: "templates/"
```

### 8.4 weights.yaml — AHP and Fixed Weights

yaml

```yaml
schema_version: "1.0.0"
description: "All weights externalized. No hard-coded constants in source code."

# Fixed descriptor compatibility weights (s_desc)
descriptor_weights:
  hbd: 0.30
  hba: 0.30
  tpsa: 0.20
  aromatic_rings: 0.20
  note: "Sum must equal 1.0; validated at runtime"

# AHP pairwise comparison matrix template (5 experts)
# Values: 1=equal, 3=moderate, 5=strong, 7=very strong, 9=extreme
ahp_template:
  criteria: ["PC1", "PC2", "PC3"]
  scale: "saaty_1_to_9"
  min_experts: 3
  max_experts: 5
  aggregation_method: "geometric_mean"
  cr_threshold: 0.08  # Gate 2 threshold
  kendall_w_threshold: 0.50  # Re-elicitation trigger

# Example expert matrices (to be replaced by actual elicitation)
expert_matrices:
  expert_1:
    PC1_vs_PC2: 5  # PC1 strongly preferred over PC2
    PC1_vs_PC3: 7
    PC2_vs_PC3: 3
  expert_2:
    PC1_vs_PC2: 3
    PC1_vs_PC3: 5
    PC2_vs_PC3: 1
  # ... additional experts

# TOPSIS parameters
topsis:
  distance_metric: "euclidean"
  weight_normalization: "vector"  # sum of squared weights = 1
```

### 8.5 thresholds.yaml — Gate Thresholds and Acceptance Criteria

### 8.5 thresholds.yaml — Gate Thresholds and Acceptance Criteria

yaml

```yaml
schema_version: "1.0.0"
description: "All decision gates and acceptance criteria. Modification requires Scientific Revision Committee approval."

# Gate 1: HSP Pre-filter
gate_1_hsp_filter:
  red_max: 1.0
  min_polymers_passing: 3
  action_if_failing: "halt_and_report"
  action_message: "Insufficient polymers pass HSP filter. Expand library or relax RED threshold (requires committee approval)."

# Gate 2: AHP Consistency
gate_2_ahp_consistency:
  cr_max: 0.08
  action_if_failing: "re_elicit"
  max_re_elicitation_rounds: 3
  action_if_persistent_failure: "use_equal_weights_with_exploratory_flag"

# Gate 3: Validation Metrics
gate_3_validation:
  rmse_max_k: 10.0  # Tg prediction RMSE must be ≤ 10 K
  spearman_rho_min: 0.70  # H1 primary endpoint
  mae_max_k: 8.0
  top_1_agreement_min: 1  # At least top-1 polymer must match
  action_if_failing: "refinement_loop"
  max_refinement_iterations: 3

# Gate 4: FBM Pre-registration
gate_4_fbm_preregistration:
  required: true
  preregistration_file: "docs/fbm_preregistration_v1.md"
  action_if_missing: "disable_fbm_and_flag_exploratory"

# Confidence tier thresholds
confidence_tiers:
  high:
    mc_p_top1_min: 0.70
    label: "High"
  moderate:
    mc_p_top1_min: 0.40
    mc_p_top1_max: 0.70
    label: "Moderate"
  low:
    mc_p_top1_max: 0.40
    label: "Low"

# Data quality thresholds
data_quality:
  min_data_quality_score: 0.5  # Records below this flagged as "low confidence"
  systematic_bias_flag_threshold: 0.2  # Density difference > 20% triggers flag
```

### 8.6 validation_rules.yaml — Data Validation Schema

yaml

```yaml
schema_version: "1.0.0"

# CSV file validation rules
file_validation:
  encoding: "utf-8"
  line_endings: "lf"
  delimiter: ","
  quote_char: '"'
  escape_char: "\\"
  required_files:
    - "drug_database.csv"
    - "polymer_database.csv"
    - "descriptor_database.csv"
    - "results_database.csv"

# Column-level validation
column_rules:
  uuid_v4:
    pattern: "^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
    description: "Standard UUID v4 format"
  
  doi:
    pattern: "^10\\.[0-9]{4,}/.+$"
    description: "CrossRef DOI format"
  
  sem_ver:
    pattern: "^(0|[1-9]\\d*)\\.(0|[1-9]\\d*)\\.(0|[1-9]\\d*)(?:-((?:0|[1-9]\\d*|\\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\\.(?:0|[1-9]\\d*|\\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\\+([0-9a-zA-Z-]+(?:\\.[0-9a-zA-Z-]+)*))?$"
    description: "Semantic Versioning 2.0.0"
  
  iso_8601:
    pattern: "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(?:\\.\\d+)?(?:Z|[+-]\\d{2}:\\d{2})$"
    description: "ISO 8601 timestamp with timezone"

# Referential integrity rules
referential_integrity:
  drug_id_exists: "drug_database.drug_id"
  polymer_id_exists: "polymer_database.polymer_id"
  result_id_exists: "results_database.result_id"
  experiment_id_exists: "experimental_database.experiment_id"

# Custom validation functions (Python module paths)
custom_validators:
  smiles_parseable: "validators.chemistry.validate_smiles"
  inchi_key_derivable: "validators.chemistry.validate_inchi_key"
  hsp_consistency: "validators.physics.validate_hsp_triangle"
  pdi_physical: "validators.physics.validate_pdi"
```

### 8.7 metadata_registry.json — Controlled Vocabularies

JSON

```json
{
  "schema_version": "1.0.0",
  "controlled_vocabularies": {
    "bcs_class": ["I", "II", "III", "IV", "unknown"],
    "polymer_family": ["cellulosic", "vinylic", "acrylic", "polyether", "polyester", "polyamide", "natural_gum", "other"],
    "polymer_class": ["neutral", "anionic", "cationic", "amphiphilic", "zwitterionic"],
    "regulatory_status": ["FDA_IID", "Ph.Eur.", "USP_NF", "JP", "ChP", "none", "under_review"],
    "tg_source": ["experimental_dsc", "experimental_dma", "literature", "estimated", "unknown"],
    "hsp_source": ["experimental", "hoftyzer_van_krevelen", "stefanis_panayiotou", "group_contribution", "literature", "unknown"],
    "validation_status": ["validated", "estimated", "provisional", "deprecated"],
    "confidence_tier": ["High", "Moderate", "Low", "Very_Low"],
    "exploratory_confirmatory_flag": ["exploratory", "confirmatory", "preliminary"],
    "validation_decision": ["supported", "not_supported", "marginally_supported", "exploratory", "inconclusive"],
    "fbm_region": ["Safe", "Warning", "Failure", "not_calculated"],
    "spray_drying_suitability": ["excellent", "good", "moderate", "poor", "unknown"],
    "hygroscopicity": ["non_hygroscopic", "slightly", "moderately", "very", "unknown"],
    "dissolution_apparatus": ["USP_I", "USP_II", "USP_IV"],
    "ftir_method": ["atr", "kbr_pellet", "nujol_mull"],
    "stability_condition": ["T0", "25C_60RH", "30C_65RH", "40C_75RH"],
    "validation_type": ["prospective", "retrospective", "loo_cv", "held_out_test", "negative_control", "baseline_comparison"]
  },
  "naming_conventions": {
    "column_names": "snake_case",
    "file_names": "snake_case",
    "uuid_format": "lowercase_hyphenated",
    "enum_values": "snake_case"
  },
  "units": {
    "temperature": "kelvin",
    "energy": "kilojoules_per_mole",
    "density": "grams_per_cubic_centimeter",
    "molecular_weight": "grams_per_mole",
    "pressure": "megapascals",
    "time": "seconds",
    "concentration": "milligrams_per_milliliter"
  },
  "precision_rules": {
    "default_significant_figures": 3,
    "temperature": "1_decimal_place",
    "percentages": "1_decimal_place",
    "p_values": "3_decimal_places_or_scientific",
    "correlation_coefficients": "2_decimal_places"
  }
}
```

---

## 9. TASK 9 — METADATA STANDARDS

 I'll continue writing the complete Database Architecture Specification directly in the chat. Here is the full specification from Task 8 onwards:

---

## 9. TASK 8 — CONFIGURATION FILES (Continued)

### 9.3 config.yaml — Master Workflow Configuration

```yaml
schema_version: "1.0.0"
database_version: "1.0.0"
framework_version: "2.0"

# Execution control
execution:
  mode: "full"  # Options: full, compute_only, validate_only
  random_seed: 42
  parallel_workers: 1  # Deterministic; no parallelization for reproducibility
  
# File paths (relative to project root)
paths:
  drug_database: "data/drug_database.csv"
  polymer_database: "data/polymer_database.csv"
  descriptor_database: "data/descriptor_database.csv"
  results_database: "data/results_database.csv"
  experimental_database: "data/experimental_database.csv"
  validation_database: "data/validation_database.csv"
  provenance_log: "logs/provenance_log.csv"
  output_dir: "results/"
  
# Drug-specific parameters
drug:
  default_drug_id: "IND-001-2026"
  drug_loading_default_ww: 0.30
  drug_loading_range:
    min: 0.10
    max: 0.50
    step: 0.05
  ionisation_state_ph: 7.4  # For logD estimation
  
# Polymer library parameters
polymer:
  min_candidates: 3  # Gate 1: halt if fewer than 3 polymers pass RED filter
  max_candidates: 50  # Future expansion limit
  default_library: "config/polymers/polymer_library_v2.csv"
  
# Computational parameters
computation:
  temperature_k: 298.15  # Standard temperature for HSP and chi calculations
  hsp_lindvig_weights: [0.6, 0.25, 0.25]  # δD, δP, δH weights for chi conversion
  chi_uncertainty_relative: 0.25  # V2.0 revised from 0.15 (criticism 4.3)
  gt_kwei_q: null  # Optional; fitted from experimental data if available
  
# PCA parameters
pca:
  variance_threshold: 0.95  # Cumulative variance to retain PCs
  center: true
  scale: true
  
# Monte Carlo Uncertainty Quantification
monte_carlo:
  n_iterations: 10000
  n_chains: 5
  convergence_method: "gelman_rubin"  # Alternative: "coefficient_of_variation"
  r_hat_threshold: 1.01
  covariance_structure: "diagonal"  # V2.0 revised from "full" (criticism 8.2)
  confidence_level: 0.95
  
# Failure Boundary Map (FBM)
fbm:
  enabled: true
  model_type: "logistic_regression"
  solver: "lbfgs"
  max_iter: 1000
  class_weight: "balanced"
  cross_validation_folds: 5
  min_samples_per_class: 3  # V2.0: minimum 3 per class for FBM fitting
  random_state: 42
  
# Reporting
reporting:
  output_formats: ["json", "pdf", "xlsx"]
  include_justification_traces: true
  include_sensitivity_analysis: true
  include_raw_data: false  # Raw data linked, not embedded
  template_dir: "templates/"
```

### 9.4 weights.yaml — AHP and Fixed Weights

```yaml
schema_version: "1.0.0"
description: "All weights externalized. No hard-coded constants in source code."

# Fixed descriptor compatibility weights (s_desc)
descriptor_weights:
  hbd: 0.30
  hba: 0.30
  tpsa: 0.20
  aromatic_rings: 0.20
  note: "Sum must equal 1.0; validated at runtime"

# AHP pairwise comparison matrix template (5 experts)
# Values: 1=equal, 3=moderate, 5=strong, 7=very strong, 9=extreme
ahp_template:
  criteria: ["PC1", "PC2", "PC3"]
  scale: "saaty_1_to_9"
  min_experts: 3
  max_experts: 5
  aggregation_method: "geometric_mean"
  cr_threshold: 0.08  # Gate 2 threshold
  kendall_w_threshold: 0.50  # Re-elicitation trigger

# Example expert matrices (to be replaced by actual elicitation)
expert_matrices:
  expert_1:
    PC1_vs_PC2: 5  # PC1 strongly preferred over PC2
    PC1_vs_PC3: 7
    PC2_vs_PC3: 3
  expert_2:
    PC1_vs_PC2: 3
    PC1_vs_PC3: 5
    PC2_vs_PC3: 1
  # ... additional experts

# TOPSIS parameters
topsis:
  distance_metric: "euclidean"
  weight_normalization: "vector"  # sum of squared weights = 1
```

### 9.5 thresholds.yaml — Gate Thresholds and Acceptance Criteria

```yaml
schema_version: "1.0.0"
description: "All decision gates and acceptance criteria. Modification requires Scientific Revision Committee approval."

# Gate 1: HSP Pre-filter
gate_1_hsp_filter:
  red_max: 1.0
  min_polymers_passing: 3
  action_if_failing: "halt_and_report"
  action_message: "Insufficient polymers pass HSP filter. Expand library or relax RED threshold (requires committee approval)."

# Gate 2: AHP Consistency
gate_2_ahp_consistency:
  cr_max: 0.08
  action_if_failing: "re_elicit"
  max_re_elicitation_rounds: 3
  action_if_persistent_failure: "use_equal_weights_with_exploratory_flag"

# Gate 3: Validation Metrics
gate_3_validation:
  rmse_max_k: 10.0  # Tg prediction RMSE must be ≤ 10 K
  spearman_rho_min: 0.70  # H1 primary endpoint
  mae_max_k: 8.0
  top_1_agreement_min: 1  # At least top-1 polymer must match
  action_if_failing: "refinement_loop"
  max_refinement_iterations: 3

# Gate 4: FBM Pre-registration
gate_4_fbm_preregistration:
  required: true
  preregistration_file: "docs/fbm_preregistration_v1.md"
  action_if_missing: "disable_fbm_and_flag_exploratory"

# Confidence tier thresholds
confidence_tiers:
  high:
    mc_p_top1_min: 0.70
    label: "High"
  moderate:
    mc_p_top1_min: 0.40
    mc_p_top1_max: 0.70
    label: "Moderate"
  low:
    mc_p_top1_max: 0.40
    label: "Low"

# Data quality thresholds
data_quality:
  min_data_quality_score: 0.5  # Records below this flagged as "low confidence"
  systematic_bias_flag_threshold: 0.2  # Density difference > 20% triggers flag
```

### 9.6 validation_rules.yaml — Data Validation Schema

```yaml
schema_version: "1.0.0"

# CSV file validation rules
file_validation:
  encoding: "utf-8"
  line_endings: "lf"
  delimiter: ","
  quote_char: '"'
  escape_char: "\\"
  required_files:
    - "drug_database.csv"
    - "polymer_database.csv"
    - "descriptor_database.csv"
    - "results_database.csv"

# Column-level validation
column_rules:
  uuid_v4:
    pattern: "^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
    description: "Standard UUID v4 format"
  
  doi:
    pattern: "^10\\.[0-9]{4,}/.+$"
    description: "CrossRef DOI format"
  
  sem_ver:
    pattern: "^(0|[1-9]\\d*)\\.(0|[1-9]\\d*)\\.(0|[1-9]\\d*)(?:-((?:0|[1-9]\\d*|\\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\\.(?:0|[1-9]\\d*|\\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\\+([0-9a-zA-Z-]+(?:\\.[0-9a-zA-Z-]+)*))?$"
    description: "Semantic Versioning 2.0.0"
  
  iso_8601:
    pattern: "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(?:\\.\\d+)?(?:Z|[+-]\\d{2}:\\d{2})$"
    description: "ISO 8601 timestamp with timezone"

# Referential integrity rules
referential_integrity:
  drug_id_exists: "drug_database.drug_id"
  polymer_id_exists: "polymer_database.polymer_id"
  result_id_exists: "results_database.result_id"
  experiment_id_exists: "experimental_database.experiment_id"

# Custom validation functions (Python module paths)
custom_validators:
  smiles_parseable: "validators.chemistry.validate_smiles"
  inchi_key_derivable: "validators.chemistry.validate_inchi_key"
  hsp_consistency: "validators.physics.validate_hsp_triangle"
  pdi_physical: "validators.physics.validate_pdi"
```

### 9.7 metadata_registry.json — Controlled Vocabularies

```json
{
  "schema_version": "1.0.0",
  "controlled_vocabularies": {
    "bcs_class": ["I", "II", "III", "IV", "unknown"],
    "polymer_family": ["cellulosic", "vinylic", "acrylic", "polyether", "polyester", "polyamide", "natural_gum", "other"],
    "polymer_class": ["neutral", "anionic", "cationic", "amphiphilic", "zwitterionic"],
    "regulatory_status": ["FDA_IID", "Ph.Eur.", "USP_NF", "JP", "ChP", "none", "under_review"],
    "tg_source": ["experimental_dsc", "experimental_dma", "literature", "estimated", "unknown"],
    "hsp_source": ["experimental", "hoftyzer_van_krevelen", "stefanis_panayiotou", "group_contribution", "literature", "unknown"],
    "validation_status": ["validated", "estimated", "provisional", "deprecated"],
    "confidence_tier": ["High", "Moderate", "Low", "Very_Low"],
    "exploratory_confirmatory_flag": ["exploratory", "confirmatory", "preliminary"],
    "validation_decision": ["supported", "not_supported", "marginally_supported", "exploratory", "inconclusive"],
    "fbm_region": ["Safe", "Warning", "Failure", "not_calculated"],
    "spray_drying_suitability": ["excellent", "good", "moderate", "poor", "unknown"],
    "hygroscopicity": ["non_hygroscopic", "slightly", "moderately", "very", "unknown"],
    "dissolution_apparatus": ["USP_I", "USP_II", "USP_IV"],
    "ftir_method": ["atr", "kbr_pellet", "nujol_mull"],
    "stability_condition": ["T0", "25C_60RH", "30C_65RH", "40C_75RH"],
    "validation_type": ["prospective", "retrospective", "loo_cv", "held_out_test", "negative_control", "baseline_comparison"]
  },
  "naming_conventions": {
    "column_names": "snake_case",
    "file_names": "snake_case",
    "uuid_format": "lowercase_hyphenated",
    "enum_values": "snake_case"
  },
  "units": {
    "temperature": "kelvin",
    "energy": "kilojoules_per_mole",
    "density": "grams_per_cubic_centimeter",
    "molecular_weight": "grams_per_mole",
    "pressure": "megapascals",
    "time": "seconds",
    "concentration": "milligrams_per_milliliter"
  },
  "precision_rules": {
    "default_significant_figures": 3,
    "temperature": "1_decimal_place",
    "percentages": "1_decimal_place",
    "p_values": "3_decimal_places_or_scientific",
    "correlation_coefficients": "2_decimal_places"
  }
}
```

---

## 10. TASK 9 — METADATA STANDARDS

### 10.1 Naming Conventions

All database objects follow **snake_case** conventions with explicit semantic meaning:

| Object Type | Convention | Example | Rationale |
|-------------|-----------|---------|-----------|
| Column names | `snake_case` | `molecular_weight_g_mol` | Readability; units embedded |
| File names | `snake_case` | `drug_database.csv` | OS compatibility; clarity |
| UUIDs | `lowercase-hyphenated` | `IND-001-2026` | Human-readable prefix + sequence |
| Enums | `snake_case` | `experimental_dsc` | Consistency with Python/R |
| Formulation codes | `DRUG-POLY-BATCH-LOAD` | `IND-PVP30-B1-D30` | Instant recognizability |

### 10.2 Unit Standards

**All temperatures in Kelvin.** Celsius values are converted at data entry with the conversion logged in provenance. This eliminates ambiguity in thermal calculations (Gordon–Taylor, HSP, DSC).

**Standard units by category:**

| Physical Quantity | Standard Unit | Conversion Notes |
|-------------------|-------------|------------------|
| Temperature | Kelvin (K) | K = °C + 273.15 |
| Energy | kJ/mol | 1 kcal/mol = 4.184 kJ/mol |
| Density | g/cm³ | 1 g/mL = 1 g/cm³ |
| Molecular weight | g/mol | — |
| Pressure | MPa | 1 MPa = 10 bar = 145 psi |
| Solubility parameter | MPa^0.5 | 1 (cal/cm³)^0.5 = 2.0455 MPa^0.5 |
| Distance | Å (angstrom) | 1 Å = 0.1 nm |
| Time | seconds (s) | Minutes/hours converted at entry |
| Concentration | mg/mL | % w/w converted to mass fraction |

### 10.3 Precision and Rounding

| Data Type | Significant Figures | Rounding Rule | Example |
|-----------|-------------------|---------------|---------|
| Temperatures | 1 decimal place | Half-up | 315.15 K |
| Densities | 2 decimal places | Half-up | 1.22 g/cm³ |
| Molecular weights | 2 decimal places | Half-up | 357.79 g/mol |
| HSP parameters | 1 decimal place | Half-up | 19.2 MPa^0.5 |
| Scores (0–1) | 3 decimal places | Half-up | 0.847 |
| Correlation coefficients | 2 decimal places | Half-up | 0.85 |
| p-values | 3 decimal places or scientific | Half-up | 0.042 or 2.3×10⁻⁵ |
| Percentages | 1 decimal place | Half-up | 87.3% |

### 10.4 Missing Value Encoding

| Encoding | Meaning | Usage Context |
|----------|---------|---------------|
| `NA` | Not applicable | Field does not apply to this record type |
| `NULL` | Not available / not measured | Value could exist but was not determined |
| `-999` | Explicitly missing with trace | Legacy compatibility; must be flagged |
| `unknown` | Categorical unknown | Enum fields where value is genuinely unknown |
| `not_calculated` | Computation skipped | FBM or sensitivity not run for this record |
| `not_tested` | Experiment not performed | Stability or tablet data not yet collected |

**Rule:** Missing values MUST be accompanied by a `*_missing_reason` column or provenance entry explaining why the value is absent.

### 10.5 Controlled Vocabularies

All enum fields draw from the `metadata_registry.json` controlled vocabulary. Adding a new value requires:
1. Scientific justification documented in the revision log
2. Committee approval for breaking changes
3. Backward compatibility mapping for existing records
4. Version bump in `metadata_registry.json`

### 10.6 Version Control

**Semantic Versioning (SemVer 2.0.0)** applies to all database schemas:

- **MAJOR (X.0.0):** Breaking schema change (column removal, type change, enum restriction)
- **MINOR (x.Y.0):** Additive change (new columns, new enums) — backward compatible
- **PATCH (x.y.Z):** Bug fix, documentation correction, constraint relaxation

**Current versions:**
- Drug Database Schema: `1.0.0`
- Polymer Database Schema: `1.0.0`
- Descriptor Database Schema: `1.0.0`
- Results Database Schema: `1.0.0`
- Experimental Database Schema: `1.0.0`
- Validation Database Schema: `1.0.0`
- Configuration Schema: `1.0.0`

---

## 11. TASK 10 — DATA VALIDATION

### 11.1 Validation Architecture

Data validation operates at **three gates** before any data enters the database:

**Gate A (Ingestion Validation):** File-level checks — encoding, delimiter, header presence, required columns.
**Gate B (Record Validation):** Row-level checks — data types, range constraints, enum membership, referential integrity.
**Gate C (Cross-Record Validation):** Inter-row checks — uniqueness, consistency, derived-field correctness, checksum verification.

### 11.2 Ingestion Validation (Gate A)

| Check | Method | Failure Action |
|-------|--------|---------------|
| UTF-8 encoding | `chardet` or Python `open(encoding='utf-8')` | Reject file; log error |
| LF line endings | `file` command or Python `splitlines()` | Convert with warning; log |
| Comma delimiter | Parse first 5 rows; verify consistent column count | Reject file; log error |
| Header row present | Row 1 must match schema definition | Reject file; log error |
| No BOM | Byte-order mark detection | Strip BOM; warn |
| Quoting consistency | CSV parser strict mode | Reject malformed rows |

### 11.3 Record Validation (Gate B)

| Check Category | Examples | Failure Action |
|----------------|----------|---------------|
| **Type validation** | `molecular_weight_g_mol` must be float; `hbd` must be int | Reject row; log |
| **Range validation** | `pdi` ≥ 1.0; `tg_k` between 200–800 K | Flag outlier; require manual review |
| **Enum validation** | `bcs_class` ∈ {I, II, III, IV, unknown} | Reject row; log |
| **Pattern validation** | `drug_id` matches UUID v4 regex; `doi` matches `10.xxxx/...` | Reject row; log |
| **Null handling** | Required fields (FAIL rules) cannot be null | Reject row; log |
| **Cross-field logic** | If `density_amorphous_g_cm3` is NULL, `systematic_bias_flag` must be TRUE | Auto-set flag; warn |

### 11.4 Cross-Record Validation (Gate C)

| Check | Method | Frequency |
|-------|--------|-----------|
| **Referential integrity** | All `drug_id` values in results must exist in drug_database | Every results update |
| **Uniqueness** | `formulation_code` must be unique across experimental_database | Every insert |
| **Derived field correctness** | `hsp_total` = √(δD² + δP² + δH²) within 0.1 tolerance | Every polymer insert |
| **Checksum verification** | SHA-256 of canonical JSON must match stored checksum | Every read operation |
| **Temporal consistency** | `modified_timestamp` ≥ `created_timestamp` | Every update |
| **Version consistency** | All files in a calculation run must share `calculation_run_id` | Every pipeline execution |

### 11.5 Validation Error Reporting

All validation failures are logged to `logs/validation_errors_YYYYMMDD_HHMMSS.json` with the following structure:

```json
{
  "validation_timestamp": "2026-08-05T10:30:00Z",
  "file_path": "data/polymer_database.csv",
  "schema_version": "1.0.0",
  "errors": [
    {
      "row_number": 5,
      "column": "pdi",
      "value": "0.95",
      "rule_violated": "pdi >= 1.0",
      "severity": "error",
      "action_taken": "rejected",
      "suggested_correction": "Verify Mn and Mw values; PDI = Mw/Mn must be ≥ 1.0"
    }
  ],
  "summary": {
    "total_rows": 6,
    "rows_passed": 5,
    "rows_rejected": 1,
    "rows_flagged": 0
  }
}
```

---

## 12. TASK 11 — DATA PROVENANCE

### 12.1 Provenance Philosophy

Every data point in the architecture is **traceable to origin**. The provenance system answers four questions for every record:
1. **Where did this come from?** (Source: literature, experiment, calculation)
2. **Who created it?** (Actor: analyst, script, external database)
3. **When was it created?** (Timestamp: ISO 8601 UTC)
4. **What has changed?** (History: immutable audit trail)

### 12.2 Provenance Log Schema

**Filename:** `provenance_log.csv`  
**Schema Version:** 1.0.0  
**Access:** Append-only; write-once per action

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `provenance_id` | UUID v4 | PK | Unique provenance entry |
| `entity_type` | Enum | {drug, polymer, descriptor, result, experiment, validation, config} | Which database entity |
| `entity_id` | UUID | FK to entity PK | Specific record affected |
| `action` | Enum | {created, modified, deleted, validated, deprecated, recalculated} | Type of action |
| `actor` | String | Non-null | Analyst ID or script name |
| `origin_source` | String | Non-null | Primary source: DOI, instrument serial, script path |
| `calculation_source` | String | Nullable | For computed data: algorithm, version, parameters |
| `experimental_source` | String | Nullable | For experimental data: SOP version, instrument ID, batch |
| `previous_value` | String | Nullable | JSON of previous state (for modifications) |
| `new_value` | String | Nullable | JSON of new state |
| `modification_reason` | String | Max 1000 chars | Why the change was made |
| `git_commit_hash` | String (40 chars) | Non-null | Git commit at time of action |
| `git_branch` | String | Non-null | Git branch |
| `git_dirty_flag` | Boolean | Non-null | TRUE if uncommitted changes existed |
| `timestamp` | ISO 8601 | Non-null | Action timestamp |
| `checksum_sha256` | String (64 chars) | Non-null | Integrity of this provenance record |

### 12.3 Provenance Workflow Examples

**Example 1: Drug Database Curation**
```
provenance_id: PROV-001-2026
entity_type: drug
entity_id: IND-001-2026
action: created
actor: data_architect
origin_source: 10.1016/j.xphs.2007.01.001
calculation_source: null
experimental_source: null
previous_value: null
new_value: {"canonical_smiles": "CC1=C(...)", "tm_k": 424.15, ...}
modification_reason: "Initial curation from peer-reviewed literature"
git_commit_hash: a1b2c3d4...
git_branch: main
git_dirty_flag: false
timestamp: 2026-08-01T00:00:00Z
```

**Example 2: Computational Results Update**
```
provenance_id: PROV-042-2026
entity_type: result
entity_id: RES-001-2026
action: recalculated
actor: pipeline_v1.0.0.py
origin_source: null
calculation_source: {"algorithm": "gordon_taylor", "kwei_q": null, "version": "1.0.0"}
experimental_source: null
previous_value: {"predicted_tg_k": 385.2, "s_gt_score": 0.72}
new_value: {"predicted_tg_k": 387.1, "s_gt_score": 0.74}
modification_reason: "Recomputed after amorphous density correction (1.22 g/cm3)"
git_commit_hash: e5f6g7h8...
git_branch: main
git_dirty_flag: false
timestamp: 2026-08-03T14:22:00Z
```

### 12.4 Immutable Audit Trail

The provenance log is **append-only**. No record may be deleted or modified after insertion. If an error is discovered:
1. A new provenance entry is appended with `action: corrected`
2. The `previous_value` field contains the erroneous state
3. The `new_value` field contains the corrected state
4. The `modification_reason` explains the correction

This creates a complete, tamper-evident history suitable for regulatory inspection and scientific reproducibility.

---

## 13. TASK 12 — PUBLICATION TABLES

### 13.1 Direct Mapping to Manuscript

Every database is designed to generate specific manuscript elements without reformatting:

| Manuscript Element | Source Database | Target Table/Figure | Generation Method |
|-------------------|-------------------|---------------------|-------------------|
| Table 1: Drug physicochemical properties | `drug_database.csv` | One-row summary | Direct export |
| Table 2: Polymer library | `polymer_database.csv` | Six-row summary | Filter by `validation_status=validated` |
| Table 3: Computed compatibility scores | `results_database.csv` | All rows, selected columns | Select: polymer, RED, χ, Tg, CCI, TOPSIS rank |
| Table 4: AHP weights and consistency | `results_database.csv` | Single row per run | Select: ahp_weight_pc1, ahp_cr_aggregated, kendall_w |
| Table 5: Uncertainty quantification | `results_database.csv` | Top-3 polymers | Select: mc_p_top1, ci_lower, ci_upper, confidence_tier |
| Table 6: Experimental characterization | `experimental_database.csv` | All formulations | Filter by `stability_timepoint_months=0` |
| Table 7: Validation metrics | `validation_database.csv` | All validation types | Group by `validation_type` |
| Figure 1: HSP 3D plot | `results_database.csv` | Scatter plot | Python matplotlib (RDKit 3D) |
| Figure 2: PCA biplot | `results_database.csv` | Biplot | Python sklearn + matplotlib |
| Figure 3: TOPSIS ranking | `results_database.csv` | Bar chart | Direct plotting |
| Figure 4: FBM boundary | `results_database.csv` | Contour plot | Python scipy + matplotlib |
| Figure 5: Dissolution profiles | `experimental_database.csv` | Line plot | Group by formulation, plot Q15/Q30/Q60 |
| Supplementary Table S1: Full results | `results_database.csv` | All columns | Direct export to Excel |
| Supplementary Table S2: Provenance | `provenance_log.csv` | All entries | Direct export |

### 13.2 Table Generation Scripts

All publication tables are generated by version-controlled Python scripts in `scripts/publication/`:

- `generate_table_drug_properties.py` → Table 1
- `generate_table_polymer_library.py` → Table 2
- `generate_table_compatibility_scores.py` → Table 3
- `generate_table_ahp_weights.py` → Table 4
- `generate_table_uncertainty.py` → Table 5
- `generate_table_experimental.py` → Table 6
- `generate_table_validation.py` → Table 7
- `generate_figures.py` → Figures 1–5

Each script:
1. Reads the relevant database
2. Validates schema version compatibility
3. Applies filtering per manuscript requirements
4. Formats numbers per precision rules (Section 10.3)
5. Outputs LaTeX (for manuscript) and Excel (for supplementary)
6. Logs execution to provenance

---

## 14. TASK 13 — INDUSTRIAL READINESS

### 14.1 QbD Alignment

The database architecture directly supports ICH Q8(R2), Q9, and Q10 principles:

| ICH Guideline | Database Implementation | Evidence Field |
|---------------|--------------------------|----------------|
| **Q8(R2) — CQA Definition** | `experimental_database.dissolution_q30_percent`, `dsc_tg_k`, `stability_assay_percent` | Critical Quality Attributes |
| **Q8(R2) — CMA Definition** | `drug_database.hsp_delta_d`, `polymer_database.tg_k`, `polymer_database.hygroscopicity` | Critical Material Attributes |
| **Q8(R2) — CPP Definition** | `experimental_database.inlet_temperature_c`, `feed_rate_ml_min`, `atomization_flow_l_h` | Critical Process Parameters |
| **Q9 — Risk Assessment** | `results_database.fbm_p_failure`, `confidence_tier` | Failure probability and confidence |
| **Q10 — Change Management** | `provenance_log` complete audit trail | Every modification tracked |
| **Q1A(R2) — Stability** | `experimental_database.stability_*` | ICH stability conditions and timepoints |

### 14.2 Regulatory Submission Readiness

For future IND/ANDA submission, the database provides:

1. **Complete CMC Section:** All drug and polymer physicochemical data formatted per FDA eCTD Module 3.
2. **Method Validation:** Computational method descriptions, validation metrics, and acceptance criteria.
3. **Batch Records:** `experimental_database.formulation_code` and `batch_number` link to manufacturing records.
4. **Stability Data:** ICH Q1A(R2) compliant timepoint and condition tracking.
5. **Risk Assessment:** FBM probabilistic failure mapping supports Quality Risk Assessment (QRA).

### 14.3 Technology Readiness Level (TRL) Positioning

The architecture acknowledges **TRL 4** (laboratory validation) status:

| TRL Level | Database Evidence | Status |
|-----------|-------------------|--------|
| TRL 1–2 (Basic principles) | `drug_database`, `polymer_database` | Complete |
| TRL 3 (Proof of concept) | `descriptor_database`, `results_database` (computational only) | Complete |
| **TRL 4 (Lab validation)** | `experimental_database`, `validation_database` | **In progress** |
| TRL 5 (Relevant environment) | Scale-up data (not in scope) | Reserved fields |
| TRL 6–9 (Pilot to operational) | GMP batch records, commercial scale | Reserved fields |

Fields for TRL 5+ are reserved in `experimental_database` (e.g., `pilot_scale_batch`, `commercial_scale_batch`) but marked as `NA` for the current scope.

---

## 15. TASK 14 — DOCUMENTATION

### 15.1 User Documentation

**Target Audience:** M.Pharm research student (6-month implementation)

| Document | Location | Content |
|----------|----------|---------|
| Database Schema Guide | `docs/database_schema_guide.md` | Complete column definitions, examples, and diagrams |
| Data Entry Manual | `docs/data_entry_manual.md` | Step-by-step instructions for curating drug and polymer data |
| Configuration Guide | `docs/configuration_guide.md` | How to modify thresholds, weights, and validation rules |
| Troubleshooting Guide | `docs/troubleshooting.md` | Common validation errors and solutions |
| API Reference | `docs/api_reference.md` | Python functions for database I/O and validation |

### 15.2 Developer Documentation

| Document | Location | Content |
|----------|----------|---------|
| Architecture Decision Records | `docs/adr/` | Why CSV was chosen over SQL; why SHA-256; why YAML |
| Schema Migration Guide | `docs/migrations.md` | How to bump schema versions and migrate data |
| Testing Guide | `docs/testing.md` | Unit tests, integration tests, and validation test suites |
| Contribution Guidelines | `CONTRIBUTING.md` | How to propose schema changes |

### 15.3 Maintenance Documentation

| Document | Location | Content |
|----------|----------|---------|
| Change Log | `CHANGELOG.md` | All schema changes, bug fixes, and version bumps |
| Deprecation Log | `docs/deprecations.md` | Fields marked for future removal and migration paths |
| Backup and Recovery | `docs/backup_recovery.md` | Git-based backup strategy and disaster recovery |

---

## 16. TASK 15 — FINAL DELIVERABLE & IMPLEMENTATION READINESS

### 16.1 Deliverable Checklist

| # | Deliverable | Status | Location |
|---|-------------|--------|----------|
| 1 | Entity Relationship Diagram (ERD) | ✅ Complete | `01_ERD_Database_Architecture_V1.0.png` |
| 2 | Data Flow Diagram | ✅ Complete | `02_Data_Flow_Diagram_V1.0.png` |
| 3 | Metadata Hierarchy Diagram | ✅ Complete | `03_Metadata_Hierarchy_V1.0.png` |
| 4 | Drug Database Schema + Example | ✅ Complete | Section 3.2–3.3 |
| 5 | Polymer Database Schema + Example | ✅ Complete | Section 4.2–4.3 |
| 6 | Descriptor Database Schema | ✅ Complete | Section 5.2 |
| 7 | Results Database Schema | ✅ Complete | Section 6.2 |
| 8 | Experimental Database Schema | ✅ Complete | Section 7.2 |
| 9 | Validation Database Schema | ✅ Complete | Section 8.2 |
| 10 | Configuration Files (YAML/JSON) | ✅ Complete | Section 9.3–9.7 |
| 11 | Metadata Standards Document | ✅ Complete | Section 10 |
| 12 | Data Validation Rules | ✅ Complete | Section 11 |
| 13 | Provenance System Design | ✅ Complete | Section 12 |
| 14 | Publication Table Mapping | ✅ Complete | Section 13 |
| 15 | Industrial Readiness Assessment | ✅ Complete | Section 14 |
| 16 | Documentation Plan | ✅ Complete | Section 15 |

### 16.2 Implementation Readiness Statement

**This Database Architecture Specification Version 1.0 is FROZEN and ready for implementation.** 

The following conditions are met:
- ✅ All schemas are defined with complete column specifications
- ✅ All constraints, units, and validation rules are documented
- ✅ Example records are provided for drug and polymer databases
- ✅ Configuration files are fully specified with no hard-coded constants
- ✅ Provenance and audit systems are designed for immutability
- ✅ Publication-ready table mappings are established
- ✅ QbD and regulatory alignment is documented
- ✅ All diagrams are generated and cross-referenced

**Implementation may commence only after:**
1. Scientific Revision Committee approval of this specification
2. Assignment of `checksum_sha256` placeholder values to real computed hashes
3. Completion of AHP expert elicitation (for `weights.yaml` population)
4. Procurement of polymer samples with verified batch numbers (for `polymer_database.csv`)

### 16.3 Post-Implementation Verification

After implementation, the following verification steps are mandatory:

| Step | Verification | Acceptance Criteria |
|------|-----------|---------------------|
| 1 | Schema validation | All CSV files pass Gate A, B, and C validation |
| 2 | Referential integrity | All foreign keys resolve; no orphans |
| 3 | Checksum verification | All SHA-256 hashes match computed values |
| 4 | Round-trip test | Export → re-import → identical checksum |
| 5 | Publication generation | All 7 tables and 5 figures generate without error |
| 6 | Provenance audit | Every record has at least one provenance entry |
| 7 | Configuration isolation | Zero hard-coded constants in source code |

---

## 17. APPENDICES

### Appendix A: Glossary

| Term | Definition |
|------|-----------|
| **ASD** | Amorphous Solid Dispersion |
| **AHM** | Analytic Hierarchy Process |
| **BCS** | Biopharmaceutics Classification System |
| **CCI** | Composite Compatibility Index |
| **CMA** | Critical Material Attribute (ICH Q8) |
| **CPP** | Critical Process Parameter (ICH Q8) |
| **CQA** | Critical Quality Attribute (ICH Q8) |
| **CV** | Controlled Vocabulary |
| **DSC** | Differential Scanning Calorimetry |
| **FBM** | Failure Boundary Map |
| **GT** | Gordon–Taylor equation |
| **HSP** | Hansen Solubility Parameters |
| **ICH** | International Council for Harmonisation |
| **MC** | Monte Carlo |
| **OAT** | One-At-a-Time sensitivity analysis |
| **PCA** | Principal Component Analysis |
| **PDI** | Polydispersity Index |
| **QbD** | Quality by Design |
| **RED** | Relative Energy Difference |
| **SOP** | Standard Operating Procedure |
| **TOPSIS** | Technique for Order Preference by Similarity to Ideal Solution |
| **TRL** | Technology Readiness Level |
| **UQ** | Uncertainty Quantification |

### Appendix B: Schema Version History

| Version | Date | Changes | Migration Required |
|---------|------|---------|-------------------|
| 1.0.0 | 2026-08-05 | Initial frozen release | N/A (baseline) |

### Appendix C: Cross-Reference to Framework V2.0

| Framework Section | Database Implementation |
|-------------------|------------------------|
| Section 3.1 (Drug Database) | Task 2, Section 3 |
| Section 3.2 (Polymer Database) | Task 3, Section 4 |
| Section 4.0 (HSP Scoring) | `results_database.s_hsp_score` |
| Section 5.0 (Flory-Huggins) | `results_database.s_chi_score` |
| Section 6.0 (Gordon–Taylor) | `results_database.s_gt_score` |
| Section 7.0 (PCA + CCI) | `results_database.cci_value`, `pca_*` |
| Section 8.0 (AHP-TOPSIS) | `results_database.topsis_*`, `ahp_*` |
| Section 9.0 (UQ) | `results_database.monte_carlo_*` |
| Section 10.0 (Sensitivity) | `results_database.sensitivity_*` |
| Section 11.0 (FBM) | `results_database.fbm_*` |
| Section 12.0 (Validation) | Task 7, Section 8 |
| Section 13.0 (Experimental) | Task 6, Section 7 |
| Section 15.0 (Decision Report) | Task 12, Section 13 |

### Appendix D: Cross-Reference to Software Architecture V1.0

| SAS Section | Database Implementation |
|-------------|------------------------|
| Section 3.4 (11-Step Workflow) | Task 1, Section 2.4 |
| Section 4.0 (Configuration Manager) | Task 8, Section 9 |
| Section 5.0 (Data Manager) | Task 10, Section 11 |
| Section 6.0 (Reproducibility) | Task 11, Section 12 |
| Section 7.0 (Testing) | Task 10, Section 11.5 |

---

**END OF DATABASE ARCHITECTURE SPECIFICATION VERSION 1.0**

*This document is frozen. Any modification requires a formal amendment request to the Scientific Revision Committee, including impact assessment, migration plan, and version bump justification.*

---

## DIAGRAMS REFERENCE

The following visual diagrams were generated to support this specification:

1. **[Entity Relationship Diagram](sandbox:///mnt/agents/output/01_ERD_Database_Architecture_V1.0.png)** — Complete ERD showing all 8 entities, their fields, and relationships with cardinality.

2. **[Data Flow Diagram](sandbox:///mnt/agents/output/02_Data_Flow_Diagram_V1.0.png)** — 11-step computational workflow mapped to database read/write operations, including all 4 decision gates and refinement loops.

3. **[Metadata Hierarchy Diagram](sandbox:///mnt/agents/output/03_Metadata_Hierarchy_V1.0.png)** — Four-layer data governance model (L1 Raw → L4 Governance) with cross-cutting standards.![[02_Data_Flow_Diagram_V1.0.png]]

![[01_ERD_Database_Architecture_V1.0.png]]

![[03_Metadata_Hierarchy_V1.0.png]]