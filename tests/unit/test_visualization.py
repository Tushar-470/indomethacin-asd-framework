"""Unit tests for FigureGenerator."""

from pathlib import Path
import pandas as pd
import pytest

from asd_mcda.visualization.plotters import FigureGenerator


def test_figure_6_generation(tmp_path):
    fig_gen = FigureGenerator(tmp_path, dpi=100)
    df_ranking = pd.DataFrame(
        {
            "polymer_id": ["P1", "P2"],
            "abbreviation": ["SOL", "PVP"],
            "topsis_cl": [0.81, 0.72],
            "topsis_rank": [1, 2],
        }
    )

    out_path = fig_gen.plot_figure_6_ranking(df_ranking)
    assert out_path.exists()
    assert out_path.stat().st_size > 0
