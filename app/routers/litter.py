# app/routers/litter.py

from fastapi import APIRouter, HTTPException
from uuid import UUID
from typing import Optional
from app.models.litter import Litter
from app.services import litter_service

router = APIRouter()

@router.post("/litter/", response_model=Litter, tags=["litter"], operation_id="createLitter")
def create_litter(litter: Litter):
    """Create a new litter."""
    success = litter_service.create_litter_record(litter)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid breeding_id or data.")
    return litter

@router.get("/litters/", tags=["litter"], operation_id="listAllLitters")
def list_all_litters(page: int = 1, per_page: int = 10):
    return litter_service.list_all_litters(page, per_page)

@router.get("/litter/{litter_id}", response_model=Litter, tags=["litter"], operation_id="readLitter")
def read_litter(litter_id: UUID):
    result = litter_service.read_litter_record(litter_id)
    if not result:
        raise HTTPException(status_code=404, detail="Litter record not found.")
    return result

@router.put("/litter/{litter_id}", response_model=Litter, tags=["litter"], operation_id="updateLitter")
def update_litter(litter_id: UUID, updated: Litter):
    result = litter_service.update_litter_record(litter_id, updated)
    if not result:
        raise HTTPException(status_code=404, detail="Litter record not found.")
    return result

@router.delete("/litter/{litter_id}", tags=["litter"], operation_id="deleteLitter")
def delete_litter(litter_id: UUID):
    ok = litter_service.delete_litter_record(litter_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Litter record not found.")
    return {"detail": "Litter record deleted"}

@router.get("/litters/animal/{animal_id}", tags=["litter"], operation_id="getLittersByAnimal") 
def get_litters_by_animal(animal_id: str):
    results = litter_service.get_litters_by_animal(animal_id)
    if not results:
        raise HTTPException(status_code=404, detail="No litters found for this animal.")
    return {"litters": results}
