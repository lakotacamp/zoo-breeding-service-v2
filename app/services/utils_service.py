# app/services/utils_service.py

from uuid import UUID
from fastapi import HTTPException
from datetime import datetime, timezone, timedelta
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

COOLDOWN_PERIOD_DAYS = 10  # or from a config if needed

def validate_uuid(id_value: str):
    try:
        UUID(id_value)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid UUID: {id_value}")

def get_animal_by_identifier(identifier: str):
    from test_data import animals
    if len(identifier) == 36:
        match_ = next((a for a in animals if a["id"] == identifier), None)
        if not match_:
            raise HTTPException(status_code=404, detail=f"No animal found with ID '{identifier}'.")
        return match_
    matched = [a for a in animals if a["name"].lower() == identifier.lower()]
    if not matched:
        raise HTTPException(status_code=404, detail=f"No animal found with name '{identifier}'.")
    if len(matched) > 1:
        raise HTTPException(status_code=400, detail=f"Multiple animals found with name '{identifier}'. Use a unique ID.")
    return matched[0]

def is_eligible_for_breeding(animal: dict, cooldown_period_days: int) -> bool:
    from test_data import breeding_age_ranges
    logging.debug(f"Checking breeding eligibility for animal: {animal}")
    if animal["health_status"] != "Healthy":
        logging.debug("Animal not eligible: Not healthy.")
        return False
    age_min, age_max = breeding_age_ranges.get(animal["species"], (0, 999))
    if not (age_min <= animal["age"] <= age_max):
        logging.debug(f"Animal not eligible: age {animal['age']} not in {age_min}-{age_max}.")
        return False
    if animal["sex"] == "female" and animal["pregnant"] == "yes":
        logging.debug("Animal not eligible: Pregnant.")
        return False
    if animal.get("last_breeding_date"):
        try:
            last_dt = datetime.fromisoformat(animal["last_breeding_date"])
        except ValueError:
            logging.debug(f"Invalid date format: {animal['last_breeding_date']}.")
            return False
        if last_dt.tzinfo is None:
            last_dt = last_dt.replace(tzinfo=timezone.utc)
        now_utc = datetime.now(timezone.utc)
        cooldown_expired = (now_utc - last_dt) > timedelta(days=cooldown_period_days)
        logging.debug(f"Cooldown expired: {cooldown_expired}")
        if not cooldown_expired:
            logging.debug("Animal not eligible: Cooldown period not expired.")
            return False
    return True

def get_diversity_score(a1: Dict[str, Any], a2: Dict[str, Any]) -> float:
    """
    Example placeholder for a 'genetic diversity' measure.
    """
    from random import uniform
    return uniform(0.0, 1.0)

def initialize_offspring_milestones(offspring: dict, birth_date: datetime):
    species_milestone_defaults = {
        "Lion": [("Weaning", 180), ("Independence", 365)],
        "Tiger": [("Weaning", 120), ("Independence", 400)],
        "Elephant": [("Weaning", 365), ("Independence", 1000)],
        "Giraffe": [("Weaning", 240)],
        "Zebra": [("Weaning", 180)],
        "Bear": [("Weaning", 210)],
    }
    sp = offspring["species"]
    if sp not in species_milestone_defaults:
        return
    for milestone_name, offset_days in species_milestone_defaults[sp]:
        due_dt = birth_date + timedelta(days=offset_days)
        offspring["milestones"].append({
            "name": milestone_name,
            "due_date": due_dt.isoformat(),
            "completed_date": None,
            "notes": f"Auto milestone: {milestone_name}",
        })
