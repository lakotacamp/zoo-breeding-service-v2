# app/routers/rehoming.py

from fastapi import APIRouter, HTTPException
from app.models.rehoming import RehomingRecord
from app.services import rehoming_service

router = APIRouter()

@router.post("/offspring/rehoming/{offspring_id}", tags=["rehoming"], operation_id="rehomingOffspring")
def rehome_offspring(offspring_id: str, record: RehomingRecord):
    """
    Rehome an offspring to a new location.
    """
    result = rehoming_service.rehome_offspring(offspring_id, record)
    if not result:
        raise HTTPException(status_code=404, detail="Offspring not found")
    return result

@router.get("/offspring/rehoming/{offspring_id}", tags=["rehoming"], operation_id="getRehomingHistory")
def get_rehoming_history(offspring_id: str):
    """
    Get the rehoming history of an offspring.
    """
    records = rehoming_service.get_rehoming_history(offspring_id)
    # The service can return an empty list, or None if the offspring not found
    if records is None:
        # Means offspring not found at all
        raise HTTPException(status_code=404, detail="Offspring not found")
    elif not records:
        # Means no rehoming records
        return {"detail": "No rehoming records found.", "records": []}
    return {"records": records}
