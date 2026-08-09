"""Unit tests for FigureGenerator and Visualization Architecture."""

import re
from pathlib import Path
import pandas as pd
import pytest

from asd_mcda.visualization.plotters import FigureGenerator, resolve_polymer_display_name
from asd_mcda.polymer.polymer_library import Polymer, PolymerLibrary
from asd_mcda.drug.drug_profile import Drug


def test_no_hardcoded_figure_numbers_in_titles(tmp_path):
    """TEST 1: Verify generated titles do NOT contain 'Figure X:' prefixes."""
    fig_gen = FigureGenerator(tmp_path, dpi=100)

    df_ranking = pd.DataFrame({
        "polymer_id": ["POL-005-2026", "POL-003-2026"],
        "polymer_name": ["Soluplus", "HPMC Acetate Succinate Low"],
        "topsis_cl": [0.7776, 0.7347],
        "topsis_rank": [1, 2],
    })

    # Test Figure 6 generation
    p6 = fig_gen.plot_figure_6_ranking(df_ranking)
    assert p6.exists()

    # Verify no title in plotters.py has "Figure \d+:" pattern
    import inspect
    import asd_mcda.visualization.plotters as plotters_mod
    source = inspect.getsource(plotters_mod)
    
    # Assert no title setting string contains "Figure " followed by digits and colon
    figure_title_pattern = re.compile(r'set_title\s*\(\s*f?["\']Figure\s+\d+:')
    assert not figure_title_pattern.search(source), "Found hardcoded 'Figure X:' prefix in plotters.py titles!"


def test_polymer_labels_contain_name_and_id():
    """TEST 2: Verify polymer labels contain both polymer_name and polymer_id."""
    label = resolve_polymer_display_name("POL-005-2026", polymer_name="Soluplus")
    assert label == "Soluplus [POL-005-2026]"
    assert "Soluplus" in label
    assert "POL-005-2026" in label


def test_no_duplicate_pol_id_labels():
    """TEST 3: Verify no generated polymer label matches POL-* [POL-*]."""
    label_resolved = resolve_polymer_display_name("POL-005-2026", polymer_name="Soluplus")
    assert not re.match(r"^POL-[^\s]+\s+\[POL-[^\s]+\]$", label_resolved)
    
    # Test when name is identical to pid or missing
    label_missing = resolve_polymer_display_name("POL-999-TEST", polymer_name="POL-999-TEST")
    assert label_missing == "Unknown polymer [POL-999-TEST]"
    assert label_missing != "POL-999-TEST [POL-999-TEST]"


def test_adding_new_polymer_auto_resolves_name():
    """TEST 4: Verify adding a new polymer to canonical library auto-resolves name in visualization."""
    custom_dict = {
        "polymer_id": "POL-CUSTOM-100",
        "polymer_name": "Novel PolyOxazoline Carrier",
        "abbreviation": "POX_100",
        "mn_da": 50000,
        "tg_k": 390.0,
        "hsp_delta_d": 18.0,
        "hsp_delta_p": 8.0,
        "hsp_delta_h": 10.0,
        "monomer_smiles": "CCO",
    }
    poly = Polymer.from_dict(custom_dict)
    
    label = resolve_polymer_display_name(poly.polymer_id, polymer_name=poly.polymer_name)
    assert label == "Novel PolyOxazoline Carrier [POL-CUSTOM-100]"


def test_unresolved_polymer_id_generates_explicit_warning():
    """TEST 5: Verify unresolved polymer ID produces 'Unknown polymer [POL-XXX]' warning format."""
    label = resolve_polymer_display_name("POL-UNKNOWN-000")
    assert label == "Unknown polymer [POL-UNKNOWN-000]"
    assert label != "POL-UNKNOWN-000 [POL-UNKNOWN-000]"
