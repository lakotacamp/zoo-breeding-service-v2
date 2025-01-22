# app/routers/animals.py

from fastapi import APIRouter
from typing import Dict, Any

# You might want to import or refer to a service that handles animals
from app.services.animals_service import list_all_animals_service

router = APIRouter()

@router.get("/animals/", tags=["animals"], operation_id="listAllAnimals")
def list_all_animals():
    """Return a list of all animals in the system."""
    return {"animals": list_all_animals_service()}
