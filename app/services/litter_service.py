# app/services/litter_service.py

from uuid import UUID
from typing import Optional, List
from app.database import litter_data, breeding_data
from app.models.litter import Litter
from test_data import animals
from app.services.utils_service import validate_uuid

def create_litter_record(litter: Litter) -> bool:
    validate_uuid(str(litter.breeding_id))
    if litter.breeding_id is not None:
        if not any(b.id == litter.breeding_id for b in breeding_data):
            return False
    litter_data.append(litter)
    return True

def list_all_litters(page: int, per_page: int) -> dict:
    total = len(litter_data)
    start = (page - 1) * per_page
    end = start + per_page
    return {
        "litters": litter_data[start:end],
        "page": page,
        "per_page": per_page,
        "total": total
    }

def read_litter_record(litter_id: UUID) -> Optional[Litter]:
    obj = next((lt for lt in litter_data if lt.id == litter_id), None)
    return obj

def update_litter_record(litter_id: UUID, updated: Litter) -> Optional[Litter]:
    for i, lt in enumerate(litter_data):
        if lt.id == litter_id:
            litter_data[i] = updated
            return updated
    return None

def delete_litter_record(litter_id: UUID) -> bool:
    for i, lt in enumerate(litter_data):
        if lt.id == litter_id:
            del litter_data[i]
            return True
    return False

def get_litters_by_animal(animal_id: str) -> List[Litter]:
    validate_uuid(animal_id)
    results = [
        lt for lt in litter_data
        if str(lt.parent_1_id) == animal_id or str(lt.parent_2_id) == animal_id
    ]
    return results
