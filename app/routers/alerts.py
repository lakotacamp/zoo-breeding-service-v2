# app/routers/alerts.py

from fastapi import APIRouter
from app.services import alerts_service

router = APIRouter()

@router.get("/alerts/", tags=["alerts"], operation_id="listAlerts")
def list_alerts():
    """
    Return the current in-memory alerts list (e.g., overdue milestones).
    """
    return {"alerts": alerts_service.list_current_alerts()}
