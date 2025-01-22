# app/schemas/animals.py
from pydantic import BaseModel
from typing import List, Dict, Any

class AnimalOutSchema(BaseModel):
    """
    Simple schema for listing or retrieving animals.
    Adjust fields as needed.
    """
    id: str
    species: str
    sex: str
    age: int
    health_status: str
    pregnant: str

    class Config:
        orm_mode = True

class AnimalListOutSchema(BaseModel):
    animals: List[AnimalOutSchema]
