# app/services/breeding_service.py

from uuid import UUID, uuid4
from datetime import datetime, timezone, timedelta
from typing import Optional, List

from app.database import breeding_data, litter_data
from app.models.breeding import Breeding
from test_data import animals, breeding_events, breeding_age_ranges, gestation_periods
from app.services.utils_service import (
    validate_uuid, 
    get_animal_by_identifier, 
    is_eligible_for_breeding, 
    initialize_offspring_milestones
)
from random import randint, uniform, choice
import logging

logger = logging.getLogger(__name__)

def initialize_data():
    """
    Initialize mock data for breeding pairs, events, and litters.
    """
    for animal in animals:
        # Add basic structure if not already present
        animal.setdefault("parent_ids", [])
        animal.setdefault("milestones", [])
        animal.setdefault("health_status", "Healthy")
        animal.setdefault("last_breeding_date", None)

    print(f"Initialized {len(animals)} animals.")

def create_breeding_record(breeding: Breeding) -> Breeding:
    """
    Create a breeding record and add it to in-memory lists.
    """
    validate_uuid(str(breeding.parent_1_id))
    validate_uuid(str(breeding.parent_2_id))
    parent_1 = next((a for a in animals if a["id"] == str(breeding.parent_1_id)), None)
    parent_2 = next((a for a in animals if a["id"] == str(breeding.parent_2_id)), None)
    if not parent_1 or not parent_2:
        return None  # We'll handle the HTTPException in router

    breeding_data.append(breeding)
    breeding_events.append({
        "id": str(breeding.id),
        "parent_1_id": str(breeding.parent_1_id),
        "parent_2_id": str(breeding.parent_2_id),
        "parent_1_name": parent_1["name"],
        "parent_2_name": parent_2["name"],
        "occurred_at": breeding.occurred_at,
        "outcome": "Pending",
    })
    logger.info(f"Created breeding record: {breeding}")
    return breeding

def read_breeding_record(breeding_id: UUID) -> Optional[Breeding]:
    rec = next((b for b in breeding_data if b.id == breeding_id), None)
    return rec

def update_breeding_record(breeding_id: UUID, updated: Breeding) -> Optional[Breeding]:
    for i, b in enumerate(breeding_data):
        if b.id == breeding_id:
            breeding_data[i] = updated
            # Also update the static breeding_events list
            for evt in breeding_events:
                if evt["id"] == str(breeding_id):
                    evt["occurred_at"] = updated.occurred_at
                    evt["outcome"] = updated.outcome
            return updated
    return None

def delete_breeding_record(breeding_id: UUID) -> Optional[str]:
    for i, b in enumerate(breeding_data):
        if b.id == breeding_id:
            # remove linked litters
            litter_data[:] = [lt for lt in litter_data if lt.breeding_id != breeding_id]
            del breeding_data[i]
            return f"Breeding record {breeding_id} deleted along with linked litters."
    return None

def list_all_breeding_events(
    species: Optional[str],
    outcome: Optional[str],
    page: int,
    per_page: int
) -> dict:
    filtered = breeding_events[:]
    if species:
        sp_lower = species.lower()
        filtered = [
            e for e in filtered
            if any(
                a["species"].lower() == sp_lower
                for a in animals
                if str(a["id"]) in [e["parent_1_id"], e["parent_2_id"]]
            )
        ]
    if outcome:
        out_lower = outcome.lower()
        filtered = [e for e in filtered if e["outcome"].lower() == out_lower]

    total = len(filtered)
    start = (page - 1) * per_page
    end = start + per_page
    return {
        "breeding_events": filtered[start:end],
        "page": page,
        "per_page": per_page,
        "total": total
    }

def get_compatible_pairs() -> List[tuple]:
    visited = set()
    results = []
    from app.services.utils_service import COOLDOWN_PERIOD_DAYS
    for a1 in animals:
        for a2 in animals:
            if a1["id"] == a2["id"]:
                continue
            pair_key = tuple(sorted([a1["id"], a2["id"]]))
            if pair_key in visited:
                continue
            visited.add(pair_key)

            if (a1["species"] == a2["species"] and
                a1["sex"] != a2["sex"] and
                is_eligible_for_breeding(a1, COOLDOWN_PERIOD_DAYS) and
                is_eligible_for_breeding(a2, COOLDOWN_PERIOD_DAYS)):
                results.append((a1, a2))
    return results

def schedule_breeding() -> List[dict]:
    from app.services.utils_service import COOLDOWN_PERIOD_DAYS
    current_time = datetime.now(timezone.utc)
    scheduled_events = []
    logger.info("Regenerating valid breeding pairs...")

    for a1 in animals:
        for a2 in animals:
            if a1["id"] == a2["id"]:
                continue
            # skip if any female in the pair is pregnant
            if (a1["sex"] == "female" and a1["pregnant"] == "yes") or \
               (a2["sex"] == "female" and a2["pregnant"] == "yes"):
                continue

            if (a1["species"] == a2["species"] and
                a1["sex"] != a2["sex"] and
                is_eligible_for_breeding(a1, COOLDOWN_PERIOD_DAYS) and
                is_eligible_for_breeding(a2, COOLDOWN_PERIOD_DAYS)):

                evt_id = str(uuid4())
                scheduled_events.append({
                    "id": evt_id,
                    "parent_1_id": a1["id"],
                    "parent_2_id": a2["id"],
                    "parent_1_name": a1["name"],
                    "parent_2_name": a2["name"],
                    "occurred_at": current_time.isoformat(),
                    "outcome": "Scheduled",
                })
                a1["last_breeding_date"] = current_time.isoformat()
                a2["last_breeding_date"] = current_time.isoformat()
                logger.info(f"Breeding scheduled: {a1['name']} + {a2['name']}")

    if not scheduled_events:
        logger.warning("No breeding events scheduled.")
    return scheduled_events

def check_births() -> List[dict]:
    from app.services.utils_service import COOLDOWN_PERIOD_DAYS
    current_date = datetime.now(timezone.utc)
    new_litters = []

    for mother in animals:
        if mother.get("pregnant") == "yes" and mother.get("expected_birth_date"):
            exp_str = mother["expected_birth_date"]
            try:
                dt = datetime.fromisoformat(exp_str)
            except ValueError:
                continue
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            if dt <= current_date:
                if len(mother.get("parent_ids", [])) < 2:
                    logger.error(f"Animal {mother['id']} is missing valid parent IDs.")
                    continue
                p1_id, p2_id = mother["parent_ids"]
                p1 = next((a for a in animals if a["id"] == p1_id), None)
                p2 = next((a for a in animals if a["id"] == p2_id), None)
                if not (p1 and p2):
                    logger.error("Invalid parent data.")
                    continue

                litter_size = randint(1, 5)
                from app.models.litter import Litter
                new_lit_data = {
                    "id": uuid4(),
                    "breeding_id": uuid4(),  # fallback or real
                    "size": litter_size,
                    "birth_date": current_date,
                    "description": f"Litter of {litter_size}",
                    "parent_1_id": p1_id,
                    "parent_2_id": p2_id,
                    "parent_1_name": p1["name"],
                    "parent_2_name": p2["name"],
                    "species": mother["species"],
                }
                new_lit = Litter(**new_lit_data)
                litter_data.append(new_lit)
                new_litters.append(new_lit_data)

                # create baby animals
                for _ in range(litter_size):
                    baby_id = str(uuid4())
                    baby_name = f"{mother['species']}_Baby_{baby_id[:5]}"
                    baby_dict = {
                        "id": baby_id,
                        "name": baby_name,
                        "species": mother["species"],
                        "sex": choice(["male", "female"]),
                        "age": 0,
                        "health_status": "Healthy",
                        "pregnant": "no",
                        "expected_birth_date": None,
                        "last_breeding_date": None,
                        "birth_weight": round(uniform(1.0, 5.0), 2),
                        "growth_rate": round(uniform(0.5, 1.5), 2),
                        "physical_markings": None,
                        "parent_ids": [p1_id, p2_id],
                        "mortality_status": "Alive",
                        "mortality_reason": None,
                        "date_of_death": None,
                        "milestones": [],
                    }
                    initialize_offspring_milestones(baby_dict, current_date)
                    animals.append(baby_dict)

                mother["pregnant"] = "no"
                mother["expected_birth_date"] = None

    return new_litters

def get_success_rate() -> dict:
    total = len(breeding_events)
    success = sum(1 for e in breeding_events if e.get("outcome") == "Successful")
    rate = round((success / total) * 100, 2) if total else 0.0
    return {
        "total_events": total,
        "successful_events": success,
        "success_rate": rate,
    }

def get_success_rate_by_type(type_: str, value: str) -> dict:
    if type_ == "animal":
        an = get_animal_by_identifier(value)
        val_id = an["id"]
        relevant = [e for e in breeding_events if val_id in [e["parent_1_id"], e["parent_2_id"]]]
    elif type_ == "species":
        sp_lower = value.lower()
        a_ids = [a["id"] for a in animals if a["species"].lower() == sp_lower]
        relevant = [e for e in breeding_events if e["parent_1_id"] in a_ids or e["parent_2_id"] in a_ids]
    else:
        return {"error": "Invalid type. Use 'animal' or 'species'."}

    total = len(relevant)
    success = sum(1 for e in relevant if e.get("outcome") == "Successful")
    rate = (success / total * 100) if total else 0
    return {
        "type": type_,
        "value": value,
        "total_events": total,
        "successful_events": success,
        "success_rate": rate,
    }

def get_breeding_suggestions() -> List[dict]:
    suggestions = []
    from app.services.utils_service import COOLDOWN_PERIOD_DAYS, get_diversity_score
    for p1 in animals:
        for p2 in animals:
            if (p1["id"] != p2["id"] and
                p1["species"] == p2["species"] and
                p1["sex"] != p2["sex"] and
                is_eligible_for_breeding(p1, COOLDOWN_PERIOD_DAYS) and
                is_eligible_for_breeding(p2, COOLDOWN_PERIOD_DAYS)
               ):
                total_ev, succ_ev = 0, 0
                for evt in breeding_events:
                    if {evt["parent_1_id"], evt["parent_2_id"]} == {p1["id"], p2["id"]}:
                        total_ev += 1
                        if evt["outcome"] == "Successful":
                            succ_ev += 1
                sr = succ_ev / total_ev if total_ev else 0.0

                age_min, age_max = breeding_age_ranges.get(p1["species"], (1, 20))
                midpoint = (age_min + age_max) / 2
                avg_age = (p1["age"] + p2["age"]) / 2
                age_diff = abs(avg_age - midpoint)
                age_score = max(0, (age_max - age_min)/2 - age_diff)

                d_score = get_diversity_score(p1, p2)
                final_score = (sr * 2.0) + age_score + (d_score * 1.5)

                suggestions.append({
                    "parent_1": p1,
                    "parent_2": p2,
                    "score": round(final_score, 3),
                    "historical_success_rate": round(sr, 3),
                    "age_midpoint_distance": age_diff,
                    "diversity_score": round(d_score, 3),
                })

    suggestions.sort(key=lambda x: x["score"], reverse=True)
    return suggestions

def get_breeding_history(identifier: str) -> dict:
    an = get_animal_by_identifier(identifier)
    relevant_evts = [e for e in breeding_events if an["id"] in [e["parent_1_id"], e["parent_2_id"]]]
    evt_ids = [str(e["id"]) for e in relevant_evts]
    related_litters = [lt for lt in litter_data if str(lt.breeding_id) in evt_ids]
    from app.services.utils_service import COOLDOWN_PERIOD_DAYS
    eligible = is_eligible_for_breeding(an, COOLDOWN_PERIOD_DAYS)
    return {
        "breeding_history": relevant_evts,
        "litters": related_litters,
        "eligible_for_breeding": eligible,
    }
