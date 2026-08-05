"""
Excel workbook exporter generating formatted 3-sheet decision reports.
Aligned with SAS V1.0 Section 5.1.11.
"""

from pathlib import Path
from typing import Dict, Any, Union
import pandas as pd


class ExcelExporter:
    """Exports structured pandas DataFrames to multi-sheet Excel file."""

    def export(
        self,
        summary_data: Dict[str, Any],
        ranking_df: pd.DataFrame,
        sensitivity_df: pd.DataFrame,
        output_path: Union[str, Path],
    ) -> Path:
        """Export Summary, Ranking, and Sensitivity sheets into single Excel workbook."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        df_summary = pd.DataFrame(
            [{"Parameter": k, "Value": str(v)} for k, v in summary_data.items()]
        )

        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            df_summary.to_excel(writer, sheet_name="Summary", index=False)
            ranking_df.to_excel(writer, sheet_name="Ranking", index=True)
            sensitivity_df.to_excel(writer, sheet_name="Sensitivity", index=False)

        return output_path
