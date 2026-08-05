"""Unit tests for Layer 8 Validation module."""

import pandas as pd
import pytest

from asd_mcda.validation.validator import FrameworkValidator


def test_framework_validator():
    full_ranking = pd.DataFrame(
        {
            "polymer_id": ["POL-005-2026", "POL-002-2026", "POL-001-2026", "POL-003-2026", "POL-006-2026", "POL-004-2026"],
            "abbreviation": ["SOLUPLUS", "PVP_VA_64", "PVP_K30", "HPMCAS_L", "HPMC_E5", "EDR_L100"],
            "topsis_cl": [0.81, 0.76, 0.72, 0.70, 0.65, 0.55],
            "topsis_rank": [1, 2, 3, 4, 5, 6],
        }
    )

    raw_scores = pd.DataFrame(
        {
            "polymer_id": ["POL-005-2026", "POL-002-2026", "POL-001-2026", "POL-003-2026", "POL-006-2026", "POL-004-2026"],
            "s_HSP": [0.80, 0.76, 0.71, 0.79, 0.72, 0.66],
            "s_chi": [0.72, 0.66, 0.58, 0.70, 0.60, 0.49],
            "s_desc": [0.65, 0.70, 0.68, 0.60, 0.55, 0.50],
            "s_GT": [0.42, 0.66, 0.94, 0.71, 0.91, 0.92],
            "s_lit": [1.0, 1.0, 1.0, 1.0, 0.5, 0.5],
        }
    )

    validator = FrameworkValidator()
    report = validator.validate(full_ranking, raw_scores)

    assert report.spearman_rho >= 0.70
    assert report.top1_agreement
    assert report.held_out_test_passed
    assert report.negative_controls_passed
