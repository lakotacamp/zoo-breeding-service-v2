# app/routers/offspring.py

from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.offspring import MilestoneSchema  # Correct import
from app.services import offspring_service

router = APIRouter()

@router.get("/offspring/{offspring_id}", tags=["offspring"], operation_id="getOffspring")
def get_offspring(offspring_id: str):
    result = offspring_service.get_offspring_and_parents(offspring_id)
    if not result:
        raise HTTPException(status_code=404, detail="Offspring not found")
    return result

@router.get("/offspring/milestones/{offspring_id}", tags=["milestones"], operation_id="getOffspringMilestones")
def get_offspring_milestones(offspring_id: str):
    ms = offspring_service.get_offspring_milestones(offspring_id)
    if ms is None:
        raise HTTPException(status_code=404, detail="Offspring not found")
    return ms

@router.put("/offspring/milestones/{offspring_id}", tags=["milestones"], operation_id="updateOffspringMilestones")
def update_offspring_milestones(offspring_id: str, updated_milestones: List[MilestoneSchema]):
    success = offspring_service.update_offspring_milestones(offspring_id, updated_milestones)
    if not success:
        raise HTTPException(status_code=404, detail="Offspring not found")
    return {"detail": f"Updated milestones for {offspring_id}"}

@router.post("/offspring/check_milestones", tags=["milestones"], operation_id="checkMilestones")
def check_milestones():
    alerts = offspring_service.check_milestones()
    return {"alerts": alerts}
