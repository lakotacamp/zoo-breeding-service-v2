# app/services/offspring_service.py

from typing import List, Optional
from datetime import datetime, timezone
from test_data import animals
from app.schemas.offspring import MilestoneSchema  # Import correct schema
from app.services.utils_service import validate_uuid, is_eligible_for_breeding

def get_offspring_and_parents(offspring_id: str) -> Optional[dict]:
    validate_uuid(offspring_id)
    off = next((a for a in animals if a["id"] == offspring_id), None)
    if not off:
        return None
    parents = [p for p in animals if p["id"] in off.get("parent_ids", [])]
    return {"offspring": off, "parents": parents}

def get_offspring_milestones(offspring_id: str) -> Optional[dict]:
    validate_uuid(offspring_id)
    off = next((a for a in animals if a["id"] == offspring_id), None)
    if not off:
        return None
    return {"offspring_id": offspring_id, "milestones": off.get("milestones", [])}

def update_offspring_milestones(offspring_id: str, updated_milestones: List[MilestoneSchema]) -> bool:
    validate_uuid(offspring_id)
    off = next((a for a in animals if a["id"] == offspring_id), None)
    if not off:
        return False
    off["milestones"] = [
        {
            "name": m.name,
            "due_date": m.due_date.isoformat(),
            "completed_date": m.completed_date.isoformat() if m.completed_date else None,
            "notes": m.notes
        }
        for m in updated_milestones
    ]
    return True

alerts_list: List[str] = []

def check_milestones() -> List[str]:
    alerts_list.clear()
    now_utc = datetime.now(timezone.utc)
    for animal in animals:
        ms_list = animal.get("milestones", [])
        if isinstance(ms_list, list):
            for m in ms_list:
                raw_due = m.get("due_date")
                if not raw_due:
                    continue
                dt = datetime.fromisoformat(raw_due) if isinstance(raw_due, str) else raw_due
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                if dt <= now_utc and not m.get("completed_date"):
                    alerts_list.append(f"Milestone '{m['name']}' overdue for '{animal['name']}' ({animal['id']}).")
    return alerts_list
