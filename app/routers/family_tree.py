# app/routers/family_tree.py

from fastapi import APIRouter, HTTPException
from app.services.family_tree_service import get_lineage, get_lineage_tree

router = APIRouter()

@router.get("/lineage/{animal_id}", tags=["family_tree"], operation_id="getLineage")
def get_lineage_endpoint(animal_id: str):
    """
    Retrieve immediate parents, offspring, and siblings for the given animal.
    """
    lineage = get_lineage(animal_id)
    if lineage is None:
        raise HTTPException(status_code=404, detail="Animal not found")
    return lineage

@router.get("/lineage/tree/{animal_id}", tags=["family_tree"], operation_id="getLineageTree")
def get_lineage_tree_endpoint(animal_id: str, depth: int = 5):
    """
    Recursively build a nested family tree up to a specified max depth.
    """
    tree = get_lineage_tree(animal_id, depth)
    if not tree:
        raise HTTPException(status_code=404, detail="Animal not found")
    return {"lineage_tree": tree}
