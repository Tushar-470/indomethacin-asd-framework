"""
Polymer management API routes.
Provides CRUD operations for the polymer library.
Reference polymers (from validated CSV) are read-only; user-created polymers can be modified/deleted.
"""

from fastapi import APIRouter, HTTPException
from typing import List

from backend.models.schemas import PolymerCreate, PolymerResponse, ValidationResult
from backend.services import engine_adapter
from backend.services.validation import validate_polymer_input

router = APIRouter(prefix="/api/polymers", tags=["Polymers"])


@router.get("", response_model=List[PolymerResponse])
async def list_polymers():
    """List all polymers (reference + user-created)."""
    polymers = engine_adapter.list_polymers()
    return polymers


@router.get("/{polymer_id}", response_model=PolymerResponse)
async def get_polymer(polymer_id: str):
    """Get a single polymer by ID."""
    polymer = engine_adapter.get_polymer(polymer_id)
    if polymer is None:
        raise HTTPException(status_code=404, detail=f"Polymer '{polymer_id}' not found.")
    return polymer


@router.post("", response_model=PolymerResponse, status_code=201)
async def create_polymer(polymer: PolymerCreate):
    """Create a new user polymer."""
    existing = engine_adapter.get_polymer(polymer.polymer_id)
    if existing is not None:
        raise HTTPException(status_code=409, detail=f"Polymer ID '{polymer.polymer_id}' already exists.")

    data = polymer.model_dump()
    saved = engine_adapter.save_polymer(data)
    return saved


@router.post("/validate", response_model=ValidationResult)
async def validate_polymer(polymer: PolymerCreate):
    """Validate polymer data without saving."""
    data = polymer.model_dump()
    existing_ids = [p["polymer_id"] for p in engine_adapter.list_polymers()]
    status, errors, warnings = validate_polymer_input(data, existing_ids)
    return ValidationResult(status=status, errors=errors, warnings=warnings)


@router.delete("/{polymer_id}")
async def delete_polymer(polymer_id: str):
    """Delete a user-created polymer. Reference polymers cannot be deleted."""
    polymer = engine_adapter.get_polymer(polymer_id)
    if polymer is None:
        raise HTTPException(status_code=404, detail=f"Polymer '{polymer_id}' not found.")
    if polymer.get("is_reference", True):
        raise HTTPException(status_code=403, detail="Cannot delete reference polymers.")

    deleted = engine_adapter.delete_polymer(polymer_id)
    if not deleted:
        raise HTTPException(status_code=500, detail="Failed to delete polymer.")
    return {"message": f"Polymer '{polymer_id}' deleted successfully."}
