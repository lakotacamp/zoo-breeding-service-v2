# app/routers/mortality.py
from fastapi import APIRouter, HTTPException
from app.schemas.mortality import MortalityUpdateSchema  # Import the correct schema
from app.services import mortality_service

router = APIRouter()

@router.put("/offspring/mortality/{offspring_id}", tags=["mortality"], operation_id="updateOffspringMortality")
def update_offspring_mortality(offspring_id: str, payload: MortalityUpdateSchema):
    """
    Update the mortality status (Alive/Deceased) and optionally set reason
    or date_of_death for an offspring.
    """
    updated = mortality_service.update_offspring_mortality(offspring_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="Offspring not found")
    return {"detail": f"Offspring mortality updated: {offspring_id}"}

@router.get("/analytics/mortality/", tags=["mortality"], operation_id="mortalityAnalytics")
def mortality_analytics():
    """
    Return summary of mortality by species.
    """
    return {"mortality_summary": mortality_service.mortality_analytics()}
