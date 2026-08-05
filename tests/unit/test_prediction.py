"""Unit tests for Layer 7 Prediction module (FBM & Predictor)."""

import numpy as np
import pytest

from asd_mcda.prediction.fbm import FailureBoundaryMap


def test_failure_boundary_map_fitting():
    fbm = FailureBoundaryMap()
    X, y, names = fbm.generate_synthetic_doe_dataset()
    res = fbm.fit(X, y)

    assert res.auc_roc >= 0.50
    assert len(res.beta_coefficients) == 4
    assert len(res.region_classification) > 0
