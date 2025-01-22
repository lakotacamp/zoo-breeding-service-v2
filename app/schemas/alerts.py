# app/schemas/alerts.py
from pydantic import BaseModel
from typing import List

class AlertsOutSchema(BaseModel):
    """
    Schema for listing alerts (e.g., overdue milestones).
    """
    alerts: List[str]
