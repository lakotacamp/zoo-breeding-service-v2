# app/schemas/family_tree.py

from pydantic import BaseModel
from typing import List, Dict, Any
from app.schemas.animals import AnimalSchema


class LineageResponse(BaseModel):
    """
    Response for immediate family (parents, offspring, siblings).
    """
    parents: List[AnimalSchema]
    offspring: List[AnimalSchema]
    siblings: List[AnimalSchema]


class LineageTreeResponse(BaseModel):
    """
    Response for a deeper nested tree structure.
    """
    lineage_tree: Dict[str, Any]
