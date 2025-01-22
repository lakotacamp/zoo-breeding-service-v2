# app/services/mortality_service.py
from app.schemas.mortality import MortalityUpdateSchema  # Import the correct schema
from typing import List
from test_data import animals

def update_offspring_mortality(offspring_id: str, payload: MortalityUpdateSchema) -> bool:
    """
    Update the mortality status of an offspring. Optionally set the reason or date of death.
    """
    offspring = next((a for a in animals if a["id"] == offspring_id), None)
    if not offspring:
        return False

    offspring["mortality_status"] = payload.mortality_status
    if payload.mortality_reason:
        offspring["mortality_reason"] = payload.mortality_reason
    if payload.date_of_death:
        offspring["date_of_death"] = payload.date_of_death.isoformat()

    return True

def mortality_analytics() -> List[dict]:
    """
    Return a summary of mortality by species.
    """
    summary = {}
    for animal in animals:
        species = animal["species"]
        if animal.get("mortality_status") == "Deceased":
            summary[species] = summary.get(species, 0) + 1
    return [{"species": k, "mortality_count": v} for k, v in summary.items()]
