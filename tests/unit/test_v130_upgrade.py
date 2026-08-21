"""
Unit tests for v1.3.0 Scientific Reliability Enhancements.
"""

import json
import pathlib
import numpy as np
import pandas as pd
import pytest

from asd_mcda.configuration.loader import ConfigManager
from asd_mcda.drug.drug_profile import Drug
from asd_mcda.polymer.polymer_library import PolymerLibrary
from asd_mcda.compatibility.matrix import CompatibilityMatrix
from asd_mcda.uncertainty.monte_carlo import MonteCarloUQ
from asd_mcda.utils.helpers import wilson_score_ci

def test_active_matrix_filtering():
    cm = ConfigManager(pathlib.Path("config/workflow/workflow_config.yaml"))
    drug = Drug.from_dict(cm.load_drug_json())
    lib = PolymerLibrary.from_csv(cm.get_polymer_library_path(), drug)
    comp = CompatibilityMatrix(drug, lib)
    df_active = comp.build_active_matrix()
    
    assert list(df_active.columns) == ["s_HSP", "s_chi", "s_GT"]
    assert len(df_active) == 5

def test_wilson_score_ci_bounds():
    ci_str = wilson_score_ci(0.546, 10000)
    assert "[" in ci_str and "]" in ci_str
    assert "53.6%" in ci_str or "53.7%" in ci_str or "54" in ci_str

def test_prospective_lock_file_exists():
    lock_path = pathlib.Path("results/reports/v130_prospective_validation_lock.json")
    if not lock_path.exists():
        lock_path = pathlib.Path("archive/superseded/v130_prospective_validation_lock.json")
    assert lock_path.exists()
    with open(lock_path, "r") as f:
        data = json.load(f)
    assert data["version"] == "1.3.0"
    assert data["prediction_frozen"] is True
    assert data["selected_polymer_id"] == "POL-005-2026"


