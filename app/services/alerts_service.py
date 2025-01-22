# app/services/alerts_service.py

from typing import List
from app.services.offspring_service import alerts_list

def list_current_alerts() -> List[str]:
    """
    Return the current list of alerts (e.g., overdue milestone messages).
    """
    return alerts_list
