"""Unit tests for Layer 6 Decision subpackage (AHP & TOPSIS)."""

import numpy as np
import pandas as pd
import pytest

from asd_mcda.mcda.ahp import AHPWeightElicitor
from asd_mcda.mcda.topsis import TOPSISRanker


def test_ahp_single_matrix():
    # 2x2 consistent pairwise matrix
    matrix = np.array([[1.0, 2.0], [0.5, 1.0]])
    ahp = AHPWeightElicitor()
    weights, lambda_max, ci, cr = ahp.calculate_single_matrix_weights(matrix)

    assert len(weights) == 2
    assert np.isclose(np.sum(weights), 1.0)
    assert cr <= 0.08


def test_ahp_multi_expert_aggregation():
    m1 = np.array([[1.0, 2.0], [0.5, 1.0]])
    m2 = np.array([[1.0, 3.0], [0.333, 1.0]])
    m3 = np.array([[1.0, 1.5], [0.667, 1.0]])

    ahp = AHPWeightElicitor()
    res = ahp.aggregate_multi_expert_matrices([m1, m2, m3])

    assert res.is_multi_expert
    assert res.kendall_w > 0.0
    assert len(res.weights) == 2


def test_topsis_ranking():
    scores = pd.DataFrame(
        {
            "polymer_id": ["P1", "P2", "P3"],
            "abbreviation": ["P1", "P2", "P3"],
            "PC1": [2.5, 1.0, -1.5],
            "PC2": [0.5, -0.5, 1.0],
        }
    )
    weights = np.array([0.7, 0.3])
    topsis = TOPSISRanker()
    res = topsis.fit_predict(scores, weights)

    df_rank = res.ranking_table
    assert len(df_rank) == 3
    assert df_rank.iloc[0]["polymer_id"] == "P1"
    assert df_rank.iloc[0]["topsis_rank"] == 1
