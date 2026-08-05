"""Unit tests for ReportGenerator and ExcelExporter."""

import os
from pathlib import Path
import pandas as pd
import pytest

from asd_mcda.reporting.excel_exporter import ExcelExporter


def test_excel_exporter(tmp_path):
    exporter = ExcelExporter()
    summary = {"Drug": "Indomethacin", "Selected": "Soluplus"}
    ranking = pd.DataFrame({"polymer_id": ["P1", "P2"], "topsis_rank": [1, 2]})
    sensitivity = pd.DataFrame({"factor": ["PC1", "PC2"], "mu": [0.18, 0.08]})

    out_file = tmp_path / "test_report.xlsx"
    res_path = exporter.export(summary, ranking, sensitivity, out_file)

    assert res_path.exists()
    assert res_path.stat().st_size > 0
