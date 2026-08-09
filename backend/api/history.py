"""
Analysis history API routes.
Provides read access to past analyses and their provenance records.
"""

from fastapi import APIRouter, HTTPException
from typing import List

from backend.models.schemas import AnalysisHistoryEntry
from backend.services import history_db

router = APIRouter(prefix="/api/history", tags=["History"])


@router.get("", response_model=List[AnalysisHistoryEntry])
async def list_analyses():
    """List all past analyses in reverse chronological order."""
    analyses = history_db.list_analyses()
    return analyses


@router.get("/{analysis_id}")
async def get_analysis(analysis_id: str):
    """Get full details of a past analysis including input snapshot and provenance."""
    record = history_db.get_analysis(analysis_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Analysis '{analysis_id}' not found.")
    return record


@router.delete("/{analysis_id}")
async def delete_analysis(analysis_id: str):
    """Delete an analysis history record."""
    deleted = history_db.delete_analysis(analysis_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Analysis '{analysis_id}' not found.")
    return {"message": f"Analysis '{analysis_id}' deleted successfully."}
