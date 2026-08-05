"""Unit tests for Sensitivity Analysis modules (OAT & Morris)."""

import numpy as np
import pandas as pd
import pytest

from asd_mcda.sensitivity.oat import OATSensitivity
from asd_mcda.sensitivity.morris import MorrisSensitivity


@pytest.fixture
def sample_scores_t():
    df = pd.DataFrame(
        {
            "polymer_id": ["P1", "P2", "P3"],
            "abbreviation": ["P1", "P2", "P3"],
            "PC1": [2.5, 1.0, -1.5],
            "PC2": [0.5, -0.5, 1.0],
        }
    )
    df.set_index("polymer_id", inplace=False)
    return df


def test_oat_sensitivity(sample_scores_t):
    oat = OATSensitivity()
    base_w = np.array([0.7, 0.3])
    res = oat.analyze(sample_scores_t, base_w)

    assert res.top1_stability_fraction >= 0.0
    assert len(res.perturbation_summary) > 0


def test_morris_sensitivity(sample_scores_t):
    morris = MorrisSensitivity(r_trajectories=5)
    res = morris.analyze(sample_scores_t, n_weights=2)

    assert len(res.mu) == 2
    assert len(res.feature_names) == 2
