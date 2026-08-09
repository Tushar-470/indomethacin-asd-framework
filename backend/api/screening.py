"""
Screening API routes.
Executes the computational screening pipeline via the engine adapter.
Serves generated figures and reports.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from typing import Optional

from backend.models.schemas import ScreeningRequest, ScreeningResponse
from backend.services import engine_adapter

router = APIRouter(prefix="/api/screening", tags=["Screening"])


@router.post("/run", response_model=ScreeningResponse)
async def run_screening(request: ScreeningRequest):
    """
    Execute the full computational polymer screening pipeline.

    This endpoint:
    1. Loads the selected drug profile and polymers
    2. Runs the frozen asd_mcda 11-step pipeline (HSP, FH, GT, PCA, AHP, TOPSIS, UQ, SA, FBM, Validation)
    3. Generates publication-quality figures (300 DPI)
    4. Generates reports (JSON, XLSX, CSV, MD)
    5. Records the analysis in history for provenance tracking

    Mode:
    - 'research': Only validated drugs/polymers; produces research-grade outputs
    - 'exploratory': Any data allowed; clearly labeled as unvalidated predictions
    """
    try:
        result = engine_adapter.run_screening(
            drug_id=request.drug_id,
            polymer_ids=request.polymer_ids,
            mode=request.mode,
            drug_loading_ww=request.drug_loading_ww,
            random_seed=request.random_seed,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.get("/{analysis_id}")
async def get_screening_result(analysis_id: str):
    """Get the full results of a completed screening analysis."""
    result = engine_adapter.get_screening_result(analysis_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Analysis '{analysis_id}' not found.")
    return result


@router.get("/{analysis_id}/figures/{figure_name}")
async def get_figure(analysis_id: str, figure_name: str):
    """Serve a generated figure PNG file."""
    path = engine_adapter.get_figure_path(analysis_id, figure_name)
    if path is None:
        raise HTTPException(status_code=404, detail=f"Figure '{figure_name}' not found.")
    return FileResponse(path, media_type="image/png", filename=figure_name)


@router.get("/{analysis_id}/reports/{filename}")
async def get_report(analysis_id: str, filename: str):
    """Download a generated report file."""
    path = engine_adapter.get_report_path(analysis_id, filename)
    if path is None:
        raise HTTPException(status_code=404, detail=f"Report '{filename}' not found.")

    media_types = {
        ".json": "application/json",
        ".csv": "text/csv",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".md": "text/markdown",
    }
    ext = "." + filename.rsplit(".", 1)[-1] if "." in filename else ""
    media_type = media_types.get(ext, "application/octet-stream")
    return FileResponse(path, media_type=media_type, filename=filename)
