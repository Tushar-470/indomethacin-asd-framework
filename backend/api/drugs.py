"""
Drug management API routes.
Provides CRUD operations for drug profiles.
Reference drugs are read-only; user-created drugs can be modified/deleted.
"""

from fastapi import APIRouter, HTTPException
from typing import List

from backend.models.schemas import DrugProfileCreate, DrugProfileResponse, ValidationResult
from backend.services import engine_adapter
from backend.services.validation import validate_drug_input

router = APIRouter(prefix="/api/drugs", tags=["Drugs"])


@router.get("", response_model=List[DrugProfileResponse])
async def list_drugs():
    """List all available drug profiles (reference + user-created)."""
    drugs = engine_adapter.list_drugs()
    return drugs


@router.get("/{drug_id}", response_model=DrugProfileResponse)
async def get_drug(drug_id: str):
    """Get a single drug profile by ID."""
    drug = engine_adapter.get_drug(drug_id)
    if drug is None:
        raise HTTPException(status_code=404, detail=f"Drug profile '{drug_id}' not found.")
    return drug


@router.post("", response_model=DrugProfileResponse, status_code=201)
async def create_drug(drug: DrugProfileCreate):
    """Create a new user drug profile."""
    existing = engine_adapter.get_drug(drug.drug_id)
    if existing is not None:
        raise HTTPException(status_code=409, detail=f"Drug ID '{drug.drug_id}' already exists.")

    data = drug.model_dump()
    saved = engine_adapter.save_drug(data)
    return saved


@router.post("/validate", response_model=ValidationResult)
async def validate_drug(drug: DrugProfileCreate):
    """Validate drug profile data without saving."""
    data = drug.model_dump()
    status, errors, warnings = validate_drug_input(data)
    return ValidationResult(status=status, errors=errors, warnings=warnings)


@router.delete("/{drug_id}")
async def delete_drug(drug_id: str):
    """Delete a user-created drug profile. Reference drugs cannot be deleted."""
    drug = engine_adapter.get_drug(drug_id)
    if drug is None:
        raise HTTPException(status_code=404, detail=f"Drug '{drug_id}' not found.")
    if drug.get("is_reference", True):
        raise HTTPException(status_code=403, detail="Cannot delete reference drug profiles.")

    deleted = engine_adapter.delete_drug(drug_id)
    if not deleted:
        raise HTTPException(status_code=500, detail="Failed to delete drug profile.")
    return {"message": f"Drug '{drug_id}' deleted successfully."}
