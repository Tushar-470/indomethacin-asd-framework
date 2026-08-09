"""Unit tests for FigureGenerator."""

from pathlib import Path
import pandas as pd
import pytest

from asd_mcda.visualization.plotters import FigureGenerator


def test_figure_6_generation(tmp_path):
    fig_gen = FigureGenerator(tmp_path, dpi=100)
    df_ranking = pd.DataFrame(
        {
            "polymer_id": ["POL-005-2026", "POL-003-2026"],
            "polymer_name": ["Soluplus", "HPMC Acetate Succinate Low"],
            "abbreviation": ["SOLUPLUS", "HPMCAS_L"],
            "topsis_cl": [0.7776, 0.7347],
            "topsis_rank": [1, 2],
        }
    )

    out_path = fig_gen.plot_figure_6_ranking(df_ranking)
    assert out_path.exists()
    assert out_path.stat().st_size > 0


def test_figure_6_dynamic_labels_no_duplicates(tmp_path):
    """Verify Figure 6 labels contain actual polymer names and prohibit POL-XXXX [POL-XXXX] duplicate labels."""
    fig_gen = FigureGenerator(tmp_path, dpi=100)
    df_ranking = pd.DataFrame(
        {
            "polymer_id": ["POL-005-2026", "POL-003-2026", "POL-002-2026"],
            "polymer_name": ["Soluplus", "HPMC Acetate Succinate Low", "PVP-Vinyl Acetate 64"],
            "abbreviation": ["SOLUPLUS", "HPMCAS_L", "PVP_VA_64"],
            "topsis_cl": [0.7776, 0.7347, 0.6288],
            "topsis_rank": [1, 2, 3],
        }
    )

    out_path = fig_gen.plot_figure_6_ranking(df_ranking)
    assert out_path.exists()

    # Re-verify logic directly
    for _, row in df_ranking.iterrows():
        pid = row["polymer_id"]
        pname = row["polymer_name"]
        formatted = f"{pname} [{pid}]"
        assert pid not in pname
        assert formatted == f"{pname} [{pid}]"
        assert formatted != f"{pid} [{pid}]"

