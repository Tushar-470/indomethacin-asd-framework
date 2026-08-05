# Developer Guide

## Architecture Rationale

The software package is structured cleanly into 15 domain subpackages under `src/asd_mcda/`, adhering strictly to single-responsibility and acyclic dependency principles.

### Dependency Graph

```
cli -> orchestrator -> [drug, polymer, descriptors, compatibility, integration, mcda, prediction, validation, uncertainty, sensitivity, reporting, visualization] -> utils
```

## Adding New Compatibility Signals

To add a new compatibility signal (e.g., COSMO-RS or Molecular Dynamics $\chi$):

1. Extend `CompatibilityMatrix` in `src/asd_mcda/compatibility/matrix.py`.
2. Update the columns of the raw score matrix $S$.
3. PCA pre-processing in `src/asd_mcda/integration/pca.py` will automatically accommodate the expanded feature set and evaluate effective dimensionality $k$.

## Code Standards

- **Formatting**: PEP 8 compliance with 4-space indentation and type hints on all public methods.
- **Testing**: Every new feature must include corresponding pytest unit tests in `tests/unit/`.
