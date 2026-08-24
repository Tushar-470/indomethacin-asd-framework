"""Unit tests for Layer 5 Evidence Integration (PCA & CCI)."""

import numpy as np
import pandas as pd
import pytest

from asd_mcda.integration.pca import PCAPreprocessor
from asd_mcda.integration.cci import CompositeCompatibilityIndex


@pytest.fixture
def sample_score_matrix():
    data = [
        {"polymer_id": "P1", "s_HSP": 0.80, "s_chi": 0.72, "s_desc": 0.65, "s_GT": 0.42},
        {"polymer_id": "P2", "s_HSP": 0.76, "s_chi": 0.66, "s_desc": 0.70, "s_GT": 0.66},
        {"polymer_id": "P3", "s_HSP": 0.79, "s_chi": 0.70, "s_desc": 0.55, "s_GT": 0.71},
        {"polymer_id": "P4", "s_HSP": 0.66, "s_chi": 0.49, "s_desc": 0.60, "s_GT": 0.92},
        {"polymer_id": "P5", "s_HSP": 0.72, "s_chi": 0.60, "s_desc": 0.50, "s_GT": 0.91},
    ]
    df = pd.DataFrame(data)
    df.set_index("polymer_id", inplace=False)
    return df


def test_pca_preprocessor(sample_score_matrix):
    pca = PCAPreprocessor(variance_threshold=0.95)
    res = pca.fit_transform(sample_score_matrix)

    assert res.n_components_retained >= 1
    assert res.scores_matrix_t.shape[0] == 5
    assert res.scores_matrix_t.shape[1] == res.n_components_retained
    assert np.sum(res.explained_variance_ratio) <= 1.0001


def test_composite_compatibility_index(sample_score_matrix):
    pca = PCAPreprocessor(variance_threshold=0.95)
    pca_res = pca.fit_transform(sample_score_matrix)

    weights = np.ones(pca_res.n_components_retained) / pca_res.n_components_retained
    cci_engine = CompositeCompatibilityIndex(pca_res, weights)
    df_cci = cci_engine.compute_cci()

    assert "cci_value" in df_cci.columns
    assert len(df_cci) == 5
    assert (df_cci["cci_value"] >= 0.0).all() and (df_cci["cci_value"] <= 1.0).all()
