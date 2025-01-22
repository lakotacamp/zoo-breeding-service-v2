# app/routers/breeding.py

from fastapi import APIRouter, HTTPException
from uuid import UUID
from typing import Optional
from app.models.breeding import Breeding
from app.services import breeding_service

router = APIRouter()

@router.post("/breeding/", response_model=Breeding, tags=["breeding"], operation_id="createBreeding")
def create_breeding(breeding: Breeding):
    """Create a new breeding record."""
    return breeding_service.create_breeding_record(breeding)

@router.get("/breeding/{breeding_id}", response_model=Breeding, tags=["breeding"], operation_id="readBreeding")
def read_breeding(breeding_id: UUID):
    """Retrieve a breeding record by its ID."""
    rec = breeding_service.read_breeding_record(breeding_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Breeding record not found.")
    return rec

@router.put("/breeding/{breeding_id}", response_model=Breeding, tags=["breeding"], operation_id="updateBreeding")
def update_breeding(breeding_id: UUID, updated: Breeding):
    rec = breeding_service.update_breeding_record(breeding_id, updated)
    if not rec:
        raise HTTPException(status_code=404, detail="Breeding record not found.")
    return rec

@router.delete("/breeding/{breeding_id}", tags=["breeding"], operation_id="deleteBreeding")
def delete_breeding(breeding_id: UUID):
    deleted_detail = breeding_service.delete_breeding_record(breeding_id)
    if not deleted_detail:
        raise HTTPException(status_code=404, detail="Breeding record not found.")
    return {"detail": deleted_detail}

@router.get("/breeding/", tags=["breeding"], operation_id="listAllBreeding")
def list_all_breeding(species: Optional[str] = None, outcome: Optional[str] = None,
                      page: int = 1, per_page: int = 10):
    return breeding_service.list_all_breeding_events(species, outcome, page, per_page)

@router.get("/breeding/compatible_pairs/", tags=["breeding"], operation_id="listCompatiblePairs")
def get_compatible_pairs():
    return {"compatible_pairs": breeding_service.get_compatible_pairs()}

@router.post("/breeding/schedule/", tags=["breeding"], operation_id="scheduleBreeding")
def schedule_breeding():
    return {"scheduled_events": breeding_service.schedule_breeding()}

@router.post("/breeding/check_births/", tags=["breeding"], operation_id="checkBirths")
def check_births():
    return {"new_litters": breeding_service.check_births()}

@router.get("/breeding/success_rate/", tags=["breeding"], operation_id="getSuccessRate")
def get_success_rate():
    return breeding_service.get_success_rate()

@router.get("/breeding/success_rate/{type_}/{value}", tags=["breeding"], operation_id="getSuccessRateByType")
def get_success_rate_by_type(type_: str, value: str):
    return breeding_service.get_success_rate_by_type(type_, value)

@router.get("/breeding/suggestions/", tags=["breeding"], operation_id="getBreedingSuggestions")
def get_breeding_suggestions():
    return {"suggestions": breeding_service.get_breeding_suggestions()}

@router.get("/breeding/history/{identifier}", tags=["breeding"], operation_id="getBreedingHistory")
def get_breeding_history(identifier: str):
    return breeding_service.get_breeding_history(identifier)
