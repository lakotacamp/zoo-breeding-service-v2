# from fastapi import FastAPI, HTTPException
# from uuid import UUID, uuid4
# from datetime import datetime, timedelta, timezone
# from random import randint, uniform, choice
# import logging
# from typing import List, Optional, Dict, Any
# from pydantic import BaseModel

# # Updated imports:
# from app.database import breeding_data, litter_data
# from app.models.breeding import Breeding
# from app.models.litter import Litter
# from app.models.behavior import BehavioralLogEntry
# from app.models.rehoming import RehomingRecord

# from app.utils.family_tree import build_family_tree

# # The rest (test_data, etc.) remains as before
# from test_data import (
#     animals,
#     breeding_events,
#     breeding_age_ranges,
#     litters,
#     valid_breeding_pairs,
#     gestation_periods,
# )

# logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

# app = FastAPI(
#     title="Zoo Breeding Service API",
#     description=(
#         "An API for managing zoo animal breeding, litters, offspring behavior logs, "
#         "milestones, rehoming, and more."
#     ),
#     version="1.0.0",
# )

# COOLDOWN_PERIOD_DAYS = 180

# alerts: List[str] = []
# rehoming_data: List[Dict[str, Any]] = []  # We'll store RehomingRecord-like dicts here

# ###############################
# # Additional placeholders / helpers
# ###############################
# def get_diversity_score(a1: Dict[str, Any], a2: Dict[str, Any]) -> float:
#     return uniform(0.0, 1.0)

# species_milestone_defaults = {
#     "Lion": [("Weaning", 180), ("Independence", 365)],
#     "Tiger": [("Weaning", 120), ("Independence", 400)],
#     "Elephant": [("Weaning", 365), ("Independence", 1000)],
#     "Giraffe": [("Weaning", 240)],
#     "Zebra": [("Weaning", 180)],
#     "Bear": [("Weaning", 210)],
# }

# def initialize_offspring_milestones(offspring: dict, birth_date: datetime):
#     sp = offspring["species"]
#     if sp not in species_milestone_defaults:
#         return
#     for milestone_name, offset_days in species_milestone_defaults[sp]:
#         due_dt = birth_date + timedelta(days=offset_days)
#         offspring["milestones"].append({
#             "name": milestone_name,
#             "due_date": due_dt.isoformat(),
#             "completed_date": None,
#             "notes": f"Auto milestone: {milestone_name}",
#         })

# def is_eligible_for_breeding(animal: dict, cooldown_period_days: int) -> bool:
#     logging.debug(f"Checking breeding eligibility for animal: {animal}")
#     if animal["health_status"] != "Healthy":
#         logging.debug("Animal not eligible: Not healthy.")
#         return False
#     age_min, age_max = breeding_age_ranges.get(animal["species"], (0, 999))
#     if not (age_min <= animal["age"] <= age_max):
#         logging.debug(f"Animal not eligible: age {animal['age']} not in {age_min}-{age_max}.")
#         return False
#     if animal["sex"] == "female" and animal["pregnant"] == "yes":
#         logging.debug("Animal not eligible: Pregnant.")
#         return False
#     if animal.get("last_breeding_date"):
#         try:
#             last_dt = datetime.fromisoformat(animal["last_breeding_date"])
#         except ValueError:
#             logging.debug(f"Invalid date format: {animal['last_breeding_date']}.")
#             return False
#         if last_dt.tzinfo is None:
#             last_dt = last_dt.replace(tzinfo=timezone.utc)
#         now_utc = datetime.now(timezone.utc)
#         cooldown_expired = (now_utc - last_dt) > timedelta(days=cooldown_period_days)
#         logging.debug(f"Cooldown expired: {cooldown_expired}")
#         if not cooldown_expired:
#             logging.debug("Animal not eligible: Cooldown period not expired.")
#             return False
#     return True

# def validate_uuid(id_value: str):
#     try:
#         UUID(id_value)
#     except ValueError:
#         raise HTTPException(status_code=400, detail=f"Invalid UUID: {id_value}")

# def get_animal_by_identifier(identifier: str) -> dict:
#     if len(identifier) == 36:
#         match_ = next((a for a in animals if a["id"] == identifier), None)
#         if not match_:
#             raise HTTPException(status_code=404, detail=f"No animal found with ID '{identifier}'.")
#         return match_
#     matched = [a for a in animals if a["name"].lower() == identifier.lower()]
#     if not matched:
#         raise HTTPException(status_code=404, detail=f"No animal found with name '{identifier}'.")
#     if len(matched) > 1:
#         raise HTTPException(status_code=400, detail=f"Multiple animals found with name '{identifier}'. Use a unique ID.")
#     return matched[0]

# def initialize_data():
#     used_event_ids = set()
#     for evt in breeding_events:
#         if all(any(str(an["id"]) == str(evt[k]) for an in animals) for k in ["parent_1_id", "parent_2_id"]):
#             breeding_data.append(Breeding(**evt))
#             used_event_ids.add(evt["id"])
#     for lt in litters:
#         litter_data.append(Litter(**lt))

# initialize_data()

# ###############################
# # FastAPI endpoints
# ###############################



# ########################
# # BREEDING
# ########################
# @app.get("/animals/", tags=["animals"], operation_id="listAllAnimals")
# def list_all_animals():
#     """Return a list of all animals in the system."""
#     return {"animals": animals}

# @app.post("/breeding/", response_model=Breeding, tags=["breeding"], operation_id="createBreeding")
# def create_breeding(breeding: Breeding):
#     """Create a new breeding record."""
#     validate_uuid(str(breeding.parent_1_id))
#     validate_uuid(str(breeding.parent_2_id))
#     parent_1 = next((a for a in animals if a["id"] == str(breeding.parent_1_id)), None)
#     parent_2 = next((a for a in animals if a["id"] == str(breeding.parent_2_id)), None)
#     if not parent_1 or not parent_2:
#         raise HTTPException(status_code=400, detail="Invalid parent IDs.")

#     breeding_data.append(breeding)
#     breeding_events.append({
#         "id": str(breeding.id),
#         "parent_1_id": str(breeding.parent_1_id),
#         "parent_2_id": str(breeding.parent_2_id),
#         "parent_1_name": parent_1["name"],
#         "parent_2_name": parent_2["name"],
#         "occurred_at": breeding.occurred_at,
#         "outcome": "Pending",
#     })
#     logging.info(f"Created breeding record: {breeding}")
#     return breeding

# @app.get("/breeding/{breeding_id}", response_model=Breeding, tags=["breeding"], operation_id="readBreeding")
# def read_breeding(breeding_id: UUID):
#     """Retrieve a breeding record by its ID."""
#     validate_uuid(str(breeding_id))
#     obj = next((b for b in breeding_data if b.id == breeding_id), None)
#     if not obj:
#         raise HTTPException(status_code=404, detail="Breeding record not found.")
#     return obj

# @app.put("/breeding/{breeding_id}", response_model=Breeding, tags=["breeding"], operation_id="updateBreeding")
# def update_breeding(breeding_id: UUID, updated: Breeding):
#     validate_uuid(str(breeding_id))
#     for i, b in enumerate(breeding_data):
#         if b.id == breeding_id:
#             breeding_data[i] = updated
#             # Also update the static breeding_events list
#             for evt in breeding_events:
#                 if evt["id"] == str(breeding_id):
#                     evt["occurred_at"] = updated.occurred_at
#                     evt["outcome"] = updated.outcome
#             return updated
#     raise HTTPException(status_code=404, detail="Breeding record not found.")

# @app.delete("/breeding/{breeding_id}", tags=["breeding"], operation_id="deleteBreeding")
# def delete_breeding(breeding_id: UUID):
#     validate_uuid(str(breeding_id))
#     for i, b in enumerate(breeding_data):
#         if b.id == breeding_id:
#             # remove linked litters
#             litter_data[:] = [lt for lt in litter_data if lt.breeding_id != breeding_id]
#             del breeding_data[i]
#             return {"detail": f"Breeding record {breeding_id} deleted along with linked litters."}
#     raise HTTPException(status_code=404, detail="Breeding record not found.")

# @app.get("/breeding/", tags=["breeding"], operation_id="listAllBreeding")
# def list_all_breeding(
#     species: Optional[str] = None,
#     outcome: Optional[str] = None,
#     page: int = 1,
#     per_page: int = 10
# ):
#     filtered = breeding_events[:]
#     if species:
#         sp_lower = species.lower()
#         filtered = [
#             e for e in filtered
#             if any(
#                 a["species"].lower() == sp_lower
#                 for a in animals
#                 if str(a["id"]) in [e["parent_1_id"], e["parent_2_id"]]
#             )
#         ]
#     if outcome:
#         out_lower = outcome.lower()
#         filtered = [e for e in filtered if e["outcome"].lower() == out_lower]

#     total = len(filtered)
#     start = (page - 1) * per_page
#     end = start + per_page
#     return {
#         "breeding_events": filtered[start:end],
#         "page": page,
#         "per_page": per_page,
#         "total": total
#     }

# @app.get("/breeding/compatible_pairs/", tags=["breeding"], operation_id="listCompatiblePairs")
# def get_compatible_pairs():
#     visited = set()
#     results = []
#     for a1 in animals:
#         for a2 in animals:
#             if a1["id"] == a2["id"]:
#                 continue
#             pair_key = tuple(sorted([a1["id"], a2["id"]]))
#             if pair_key in visited:
#                 continue
#             visited.add(pair_key)

#             if (a1["species"] == a2["species"] and
#                 a1["sex"] != a2["sex"] and
#                 is_eligible_for_breeding(a1, COOLDOWN_PERIOD_DAYS) and
#                 is_eligible_for_breeding(a2, COOLDOWN_PERIOD_DAYS)):
#                 results.append((a1, a2))
#     return {"compatible_pairs": results}

# @app.post("/breeding/schedule/", tags=["breeding"], operation_id="scheduleBreeding")
# def schedule_breeding():
#     current_time = datetime.now(timezone.utc)
#     scheduled_events = []
#     logging.info("Regenerating valid breeding pairs...")

#     for a1 in animals:
#         for a2 in animals:
#             if a1["id"] == a2["id"]:
#                 continue
#             # skip if any female in the pair is pregnant
#             if (a1["sex"] == "female" and a1["pregnant"] == "yes") or \
#                (a2["sex"] == "female" and a2["pregnant"] == "yes"):
#                 continue

#             if (a1["species"] == a2["species"] and
#                 a1["sex"] != a2["sex"] and
#                 is_eligible_for_breeding(a1, COOLDOWN_PERIOD_DAYS) and
#                 is_eligible_for_breeding(a2, COOLDOWN_PERIOD_DAYS)):

#                 evt_id = str(uuid4())
#                 scheduled_events.append({
#                     "id": evt_id,
#                     "parent_1_id": a1["id"],
#                     "parent_2_id": a2["id"],
#                     "parent_1_name": a1["name"],
#                     "parent_2_name": a2["name"],
#                     "occurred_at": current_time.isoformat(),
#                     "outcome": "Scheduled",
#                 })
#                 a1["last_breeding_date"] = current_time.isoformat()
#                 a2["last_breeding_date"] = current_time.isoformat()
#                 logging.info(f"Breeding scheduled: {a1['name']} + {a2['name']}")

#     if not scheduled_events:
#         logging.warning("No breeding events scheduled.")
#     return {"scheduled_events": scheduled_events}

# @app.post("/breeding/check_births/", tags=["breeding"], operation_id="checkBirths")
# def check_births():
#     current_date = datetime.now(timezone.utc)
#     new_litters = []

#     for mother in animals:
#         if mother.get("pregnant") == "yes" and mother.get("expected_birth_date"):
#             exp_str = mother["expected_birth_date"]
#             try:
#                 dt = datetime.fromisoformat(exp_str)
#             except ValueError:
#                 continue
#             if dt.tzinfo is None:
#                 dt = dt.replace(tzinfo=timezone.utc)
#             if dt <= current_date:
#                 if len(mother.get("parent_ids", [])) < 2:
#                     logging.error(f"Animal {mother['id']} is missing valid parent IDs.")
#                     continue
#                 p1_id, p2_id = mother["parent_ids"]
#                 p1 = next((a for a in animals if a["id"] == p1_id), None)
#                 p2 = next((a for a in animals if a["id"] == p2_id), None)
#                 if not (p1 and p2):
#                     logging.error("Invalid parent data.")
#                     continue

#                 litter_size = randint(1, 5)
#                 new_lit = {
#                     "id": uuid4(),
#                     "breeding_id": uuid4(),  # fallback or real
#                     "size": litter_size,
#                     "birth_date": current_date,
#                     "description": f"Litter of {litter_size}",
#                     "parent_1_id": p1_id,
#                     "parent_2_id": p2_id,
#                     "parent_1_name": p1["name"],
#                     "parent_2_name": p2["name"],
#                     "species": mother["species"],
#                 }
#                 litter_data.append(Litter(**new_lit))
#                 new_litters.append(new_lit)

#                 for _ in range(litter_size):
#                     baby_id = str(uuid4())
#                     baby_name = f"{mother['species']}_Baby_{baby_id[:5]}"
#                     baby_dict = {
#                         "id": baby_id,
#                         "name": baby_name,
#                         "species": mother["species"],
#                         "sex": choice(["male", "female"]),
#                         "age": 0,
#                         "health_status": "Healthy",
#                         "pregnant": "no",
#                         "expected_birth_date": None,
#                         "last_breeding_date": None,
#                         "birth_weight": round(uniform(1.0, 5.0), 2),
#                         "growth_rate": round(uniform(0.5, 1.5), 2),
#                         "physical_markings": None,
#                         "parent_ids": [p1_id, p2_id],
#                         "mortality_status": "Alive",
#                         "mortality_reason": None,
#                         "date_of_death": None,
#                         "milestones": [],
#                     }
#                     initialize_offspring_milestones(baby_dict, current_date)
#                     animals.append(baby_dict)

#                 mother["pregnant"] = "no"
#                 mother["expected_birth_date"] = None

#     return {"new_litters": new_litters}

# @app.get("/breeding/success_rate/", tags=["breeding"], operation_id="getSuccessRate")
# def get_success_rate():
#     total = len(breeding_events)
#     success = sum(1 for e in breeding_events if e.get("outcome") == "Successful")
#     rate = round((success / total) * 100, 2) if total else 0.0
#     return {
#         "total_events": total,
#         "successful_events": success,
#         "success_rate": rate,
#     }

# @app.get("/breeding/success_rate/{type_}/{value}", tags=["breeding"], operation_id="getSuccessRateByType")
# def get_success_rate_by_type(type_: str, value: str):
#     if type_ == "animal":
#         an = get_animal_by_identifier(value)
#         val_id = an["id"]
#         relevant = [e for e in breeding_events if val_id in [e["parent_1_id"], e["parent_2_id"]]]
#     elif type_ == "species":
#         sp_lower = value.lower()
#         a_ids = [a["id"] for a in animals if a["species"].lower() == sp_lower]
#         relevant = [e for e in breeding_events if e["parent_1_id"] in a_ids or e["parent_2_id"] in a_ids]
#     else:
#         raise HTTPException(status_code=400, detail="Invalid type. Use 'animal' or 'species'.")

#     total = len(relevant)
#     success = sum(1 for e in relevant if e.get("outcome") == "Successful")
#     rate = (success / total * 100) if total else 0
#     return {
#         "type": type_,
#         "value": value,
#         "total_events": total,
#         "successful_events": success,
#         "success_rate": rate,
#     }

# @app.get("/breeding/suggestions/", tags=["breeding"], operation_id="getBreedingSuggestions")
# def get_breeding_suggestions():
#     suggestions = []
#     for p1 in animals:
#         for p2 in animals:
#             if (p1["id"] != p2["id"] and
#                 p1["species"] == p2["species"] and
#                 p1["sex"] != p2["sex"] and
#                 is_eligible_for_breeding(p1, COOLDOWN_PERIOD_DAYS) and
#                 is_eligible_for_breeding(p2, COOLDOWN_PERIOD_DAYS)
#                ):
#                 # success rate
#                 total_ev, succ_ev = 0, 0
#                 for evt in breeding_events:
#                     if {evt["parent_1_id"], evt["parent_2_id"]} == {p1["id"], p2["id"]}:
#                         total_ev += 1
#                         if evt["outcome"] == "Successful":
#                             succ_ev += 1
#                 sr = succ_ev / total_ev if total_ev else 0.0

#                 age_min, age_max = breeding_age_ranges.get(p1["species"], (1, 20))
#                 midpoint = (age_min + age_max) / 2
#                 avg_age = (p1["age"] + p2["age"]) / 2
#                 age_diff = abs(avg_age - midpoint)
#                 age_score = max(0, (age_max - age_min)/2 - age_diff)

#                 diversity_score = get_diversity_score(p1, p2)
#                 final_score = (sr * 2.0) + age_score + (diversity_score * 1.5)

#                 suggestions.append({
#                     "parent_1": p1,
#                     "parent_2": p2,
#                     "score": round(final_score, 3),
#                     "historical_success_rate": round(sr, 3),
#                     "age_midpoint_distance": age_diff,
#                     "diversity_score": round(diversity_score, 3),
#                 })

#     suggestions.sort(key=lambda x: x["score"], reverse=True)
#     return {"suggestions": suggestions[:10]}

# ########################
# # LITTER
# ########################
# @app.post("/litter/", response_model=Litter, tags=["litter"], operation_id="createLitter")
# def create_litter(litter: Litter):
#     validate_uuid(str(litter.breeding_id))
#     if not any(b.id == litter.breeding_id for b in breeding_data):
#         raise HTTPException(status_code=400, detail="Invalid breeding_id.")
#     litter_data.append(litter)
#     return litter

# @app.get("/litters/", tags=["litter"], operation_id="listAllLitters")
# def list_all_litters(page: int = 1, per_page: int = 10):
#     total = len(litter_data)
#     start = (page - 1) * per_page
#     end = start + per_page
#     return {
#         "litters": litter_data[start:end],
#         "page": page,
#         "per_page": per_page,
#         "total": total
#     }

# @app.get("/litter/{litter_id}", response_model=Litter, tags=["litter"], operation_id="readLitter")
# def read_litter(litter_id: UUID):
#     validate_uuid(str(litter_id))
#     obj = next((lt for lt in litter_data if lt.id == litter_id), None)
#     if not obj:
#         raise HTTPException(status_code=404, detail="Litter record not found.")
#     return obj

# @app.put("/litter/{litter_id}", response_model=Litter, tags=["litter"], operation_id="updateLitter")
# def update_litter(litter_id: UUID, updated: Litter):
#     validate_uuid(str(litter_id))
#     for i, lt in enumerate(litter_data):
#         if lt.id == litter_id:
#             litter_data[i] = updated
#             return updated
#     raise HTTPException(status_code=404, detail="Litter record not found.")

# @app.delete("/litter/{litter_id}", tags=["litter"], operation_id="deleteLitter")
# def delete_litter(litter_id: UUID):
#     validate_uuid(str(litter_id))
#     for i, lt in enumerate(litter_data):
#         if lt.id == litter_id:
#             del litter_data[i]
#             return {"detail": "Litter record deleted"}
#     raise HTTPException(status_code=404, detail="Litter record not found.")

# @app.get("/litters/animal/{animal_id}", tags=["litter"], operation_id="getLittersByAnimal")     
# def get_litters_by_animal(animal_id: str):
#     validate_uuid(animal_id)
#     results = [
#         lt for lt in litter_data
#         if str(lt.parent_1_id) == animal_id or str(lt.parent_2_id) == animal_id
#     ]
#     if not results:
#         raise HTTPException(status_code=404, detail="No litters found for this animal.")
#     return {"litters": results}

# @app.get("/breeding/history/{identifier}", tags=["breeding"], operation_id="getBreedingHistory")
# def get_breeding_history(identifier: str):
#     an = get_animal_by_identifier(identifier)
#     relevant_evts = [e for e in breeding_events if an["id"] in [e["parent_1_id"], e["parent_2_id"]]]
#     evt_ids = [str(e["id"]) for e in relevant_evts]
#     related_litters = [lt for lt in litter_data if str(lt.breeding_id) in evt_ids]
#     return {
#         "breeding_history": relevant_evts,
#         "litters": related_litters,
#         "eligible_for_breeding": is_eligible_for_breeding(an, COOLDOWN_PERIOD_DAYS),
#     }

# ########################
# # MILESTONES
# ########################
# class Milestone(BaseModel):
#     name: str
#     due_date: datetime
#     completed_date: Optional[datetime] = None
#     notes: Optional[str] = None

# @app.get("/offspring/milestones/{offspring_id}", tags=["milestones"], operation_id="getOffspringMilestones")
# def get_offspring_milestones(offspring_id: str):
#     validate_uuid(offspring_id)
#     off = next((a for a in animals if a["id"] == offspring_id), None)
#     if not off:
#         raise HTTPException(status_code=404, detail="Offspring not found")
#     return {"offspring_id": offspring_id, "milestones": off.get("milestones", [])}

# @app.put("/offspring/milestones/{offspring_id}", tags=["milestones"], operation_id="updateOffspringMilestones")
# def update_offspring_milestones(offspring_id: str, updated_milestones: List[Milestone]):
#     validate_uuid(offspring_id)
#     off = next((a for a in animals if a["id"] == offspring_id), None)
#     if not off:
#         raise HTTPException(status_code=404, detail="Offspring not found")
#     off["milestones"] = [m.dict() for m in updated_milestones]
#     return {"detail": f"Updated milestones for {offspring_id}"}

# @app.post("/offspring/check_milestones", tags=["milestones"], operation_id="checkMilestones")
# def check_milestones():
#     alerts.clear()
#     now_utc = datetime.now(timezone.utc)
#     for animal in animals:
#         ms_list = animal.get("milestones", [])
#         if isinstance(ms_list, list):
#             for m in ms_list:
#                 raw_due = m.get("due_date")
#                 if not raw_due:
#                     continue
#                 dt = datetime.fromisoformat(raw_due) if isinstance(raw_due, str) else raw_due
#                 if dt.tzinfo is None:
#                     dt = dt.replace(tzinfo=timezone.utc)
#                 if dt <= now_utc and not m.get("completed_date"):
#                     alerts.append(f"Milestone '{m['name']}' overdue for '{animal['name']}' ({animal['id']}).")
#     return {"alerts": alerts}

# @app.get("/alerts/", tags=["alerts"], operation_id="listAlerts")
# def list_alerts():
#     return {"alerts": alerts}

# ########################
# # MORTALITY
# ########################
# class MortalityUpdate(BaseModel):
#     mortality_status: str
#     mortality_reason: Optional[str] = None
#     date_of_death: Optional[datetime] = None

# @app.put("/offspring/mortality/{offspring_id}", tags=["mortality"], operation_id="updateOffspringMortality")
# def update_offspring_mortality(offspring_id: str, payload: MortalityUpdate):
#     validate_uuid(offspring_id)
#     off = next((a for a in animals if a["id"] == offspring_id), None)
#     if not off:
#         raise HTTPException(status_code=404, detail="Offspring not found")
#     off["mortality_status"] = payload.mortality_status
#     off["mortality_reason"] = payload.mortality_reason
#     off["date_of_death"] = payload.date_of_death.isoformat() if payload.date_of_death else None
#     return {"detail": f"Offspring mortality updated: {offspring_id}"}

# @app.get("/analytics/mortality/", tags=["mortality"], operation_id="mortalityAnalytics")
# def mortality_analytics():
#     summary = {}
#     for a in animals:
#         sp = a["species"]
#         if sp not in summary:
#             summary[sp] = {"Alive": 0, "Deceased": 0}
#         if a.get("mortality_status", "Alive") == "Deceased":
#             summary[sp]["Deceased"] += 1
#         else:
#             summary[sp]["Alive"] += 1
#     results = []
#     for sp, val in summary.items():
#         total = val["Alive"] + val["Deceased"]
#         if total == 0:
#             continue
#         mr = (val["Deceased"] / total) * 100
#         results.append({
#             "species": sp,
#             "alive": val["Alive"],
#             "deceased": val["Deceased"],
#             "mortality_rate": round(mr, 2),
#         })
#     return {"mortality_summary": results}

# ###############################
# # OFFSPRING endpoints
# ###############################
# @app.get("/offspring/{offspring_id}", tags=["offspring"], operation_id="getOffspring")
# def get_offspring(offspring_id: str):
#     validate_uuid(offspring_id)
#     off = next((a for a in animals if a["id"] == offspring_id), None)
#     if not off:
#         raise HTTPException(status_code=404, detail="Offspring not found")
#     parents = [p for p in animals if p["id"] in off.get("parent_ids", [])]
#     return {"offspring": off, "parents": parents}

# ###############################
# # Behavior endpoints
# ###############################
# @app.post("/offspring/behavior/{offspring_id}", tags=["behavior"], operation_id="logBehavior")
# def log_behavior(offspring_id: str, entry: BehavioralLogEntry):
#     tgt = next((a for a in animals if a["id"] == offspring_id), None)
#     if not tgt:
#         raise HTTPException(status_code=404, detail="Offspring not found")

#     if "behavioral_logs" not in tgt:
#         tgt["behavioral_logs"] = []
#     rec = entry.dict()
#     tgt["behavioral_logs"].append(rec)
#     return {"detail": f"Behavior logged for {offspring_id}", "entry": rec}

# @app.get("/offspring/behavior/{offspring_id}", tags=["behavior"], operation_id="getBehaviorLogs")
# def get_behavior_logs(offspring_id: str):
#     tgt = next((a for a in animals if a["id"] == offspring_id), None)
#     if not tgt:
#         raise HTTPException(status_code=404, detail="Offspring not found")
#     logs = tgt.get("behavioral_logs", [])
#     return {"offspring_id": offspring_id, "behavioral_logs": logs}

# ###############################
# # Rehoming endpoints
# ###############################
# @app.post("/offspring/rehoming/{offspring_id}", tags=["rehoming"], operation_id="rehomingOffspring")
# def rehome_offspring(offspring_id: str, record: RehomingRecord):
#     tgt = next((a for a in animals if a["id"] == offspring_id), None)
#     if not tgt:
#         raise HTTPException(status_code=404, detail="Offspring not found")

#     rec_dict = record.dict()
#     # If your RehomingRecord had offspring_id in the schema:
#     # record.offspring_id = UUID(offspring_id)

#     rehoming_data.append(rec_dict)

#     # Mark the offspring as transferred
#     tgt["rehoming_status"] = "Transferred"
#     tgt["new_location"] = record.new_location
#     tgt["transfer_date"] = record.transfer_date.isoformat()

#     return {"detail": f"Offspring {offspring_id} rehomed.", "record": rec_dict}

# @app.get("/offspring/rehoming/{offspring_id}", tags=["rehoming"], operation_id="getRehomingHistory")
# def get_rehoming_history(offspring_id: str):
#     # If record has an 'offspring_id' field, we can filter on it
#     # but right now we didn't store it, so we rely on the assumption
#     # it was stored in the record’s dictionary as "offspring_id".
#     # If we want to do so, we must do:
#     # results = [r for r in rehoming_data if r.get("offspring_id") == UUID(offspring_id)]
#     # or (if we never set it), then we can't filter properly:
#     # We'll just return them all. Or store it as well:

#     # This code tries to see if we stored "offspring_id" in rec_dict
#     # earlier. If we did not, you may need to store it. For demonstration:
#     found_records = []
#     for r in rehoming_data:
#         # if it has "offspring_id" inside, then check:
#         if "offspring_id" in r:
#             if str(r["offspring_id"]) == offspring_id:
#                 found_records.append(r)
#         # else we can't match
#     if not found_records:
#         return {"detail": "No rehoming records found.", "records": []}
#     return {"records": found_records}

# ###############################
# # Family Tree
# ###############################
# @app.get("/lineage/{animal_id}", tags=["family_tree"], operation_id="getLineage")
# def get_lineage(animal_id: str):
#     validate_uuid(animal_id)
#     target = next((a for a in animals if a["id"] == animal_id), None)
#     if not target:
#         raise HTTPException(status_code=404, detail="Animal not found")

#     parents = [p for p in animals if p["id"] in target.get("parent_ids", [])]
#     offspring_ = [o for o in animals if animal_id in o.get("parent_ids", [])]
#     sibling_ids = set(
#         s["id"] for s in animals
#         if set(s.get("parent_ids", [])) == set(target.get("parent_ids", []))
#         and s["id"] != animal_id
#     )
#     siblings = [s for s in animals if s["id"] in sibling_ids]

#     return {
#         "parents": parents,
#         "offspring": offspring_,
#         "siblings": siblings,
#     }

# @app.get("/lineage/tree/{animal_id}", tags=["family_tree"], operation_id="getLineageTree")
# def get_lineage_tree(animal_id: str, depth: int = 5):
#     # Validate
#     if not any(a["id"] == animal_id for a in animals):
#         raise HTTPException(status_code=404, detail="Animal not found")

#     tree = build_family_tree(animal_id, animals, max_depth=depth)
#     return {"lineage_tree": tree}
