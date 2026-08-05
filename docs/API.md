# API Reference Documentation

## `asd_mcda.drug`
- **`Drug`**: Immutable value object for API physicochemical profile.
  - `from_dict(data: dict) -> Drug`
  - `from_json(path: Path) -> Drug`
  - `estimate_tg() -> float`
  - `get_preferred_density() -> Tuple[float, str]`

## `asd_mcda.polymer`
- **`Polymer`**: Dataclass representing polymer carrier attributes.
- **`PolymerLibrary`**: Container collection for polymers.
  - `from_csv(path: Path, drug: Drug) -> PolymerLibrary`

## `asd_mcda.compatibility`
- **`HSPModel`**: Computes $R_a$, RED, $s_{\text{HSP}}$, and checks Gate 1.
- **`FloryHugginsModel`**: Computes Lindvig $\chi$, critical $\chi_c$, $s_{\chi}$.
- **`GordonTaylorModel`**: Computes $T_{g,\text{mix}}$ via Simha-Boyer $K$, Kwei $q$, $s_{\text{GT}}$.
- **`CompatibilityMatrix`**: Assembles $N \times 5$ raw score matrix $S$.

## `asd_mcda.integration`
- **`PCAPreprocessor`**: Fits StandardScaler and PCA to $S$, retaining PCs for $\ge 95\%$ variance.
- **`CompositeCompatibilityIndex`**: Computes weighted linear combination on retained PCs.

## `asd_mcda.mcda`
- **`AHPWeightElicitor`**: Principal eigenvector method, $CR < 0.08$ Gate 2, geometric-mean aggregation, Kendall's $W$.
- **`TOPSISRanker`**: Euclidean distances $D^+, D^-$, closeness coefficient $CL$, ranking table.

## `asd_mcda.prediction`
- **`FailureBoundaryMap`**: Logistic-regression FBM with bootstrap CIs.
- **`FormulationPredictor`**: Performance predictions for top-ranked polymers.

## `asd_mcda.uncertainty`
- **`MonteCarloUQ`**: Joint-distribution Monte Carlo ($N=10,000$) for decision confidence $P(\text{top-1})$.

## `asd_mcda.sensitivity`
- **`OATSensitivity`**: One-At-a-Time weight perturbations ($\times 0.5, \times 1.5$).
- **`MorrisSensitivity`**: Morris elementary effects ($\mu, \sigma$) screening.
