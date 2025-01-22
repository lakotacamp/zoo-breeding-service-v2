# import pytest
# from fastapi.testclient import TestClient
# from uuid import uuid4
# from datetime import datetime, timedelta, timezone
# import logging

# from main import app, COOLDOWN_PERIOD_DAYS, is_eligible_for_breeding, alerts
# from test_data import animals

# logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

# client = TestClient(app)

# def validate_response(response, key):
#     assert response.status_code == 200, f"Expected 200, got {response.status_code}"
#     js = response.json()
#     assert key in js, f"Missing key '{key}' in response"
#     return js[key]

# def validate_animal(an):
#     assert "id" in an
#     assert "species" in an
#     assert "sex" in an
#     assert an["health_status"] in ["Healthy", "Slightly Ill", "Critical"]
#     if an["sex"] == "male":
#         assert an.get("pregnant", "no") == "no"
#     else:
#         if an.get("pregnant") == "yes":
#             assert "expected_birth_date" in an

# def validate_pair(pair):
#     a1, a2 = pair
#     assert a1["species"] == a2["species"]
#     assert a1["sex"] != a2["sex"]
#     assert a1["health_status"] == "Healthy"
#     assert a2["health_status"] == "Healthy"
#     assert a1.get("pregnant", "no") == "no"
#     assert a2.get("pregnant", "no") == "no"

# ####################
# # EXISTING TESTS
# ####################
# def test_get_all_animals():
#     resp_data = validate_response(client.get("/animals/"), "animals")
#     assert isinstance(resp_data, list)
#     assert len(resp_data) > 0
#     for an in resp_data:
#         validate_animal(an)

# @pytest.mark.parametrize("endpoint,key", [
#     ("/breeding/compatible_pairs/", "compatible_pairs"),
#     ("/litters/", "litters"),
# ])
# def test_get_list_endpoints(endpoint, key):
#     data_list = validate_response(client.get(endpoint), key)
#     assert isinstance(data_list, list)

# def test_get_compatible_pairs():
#     data_list = validate_response(client.get("/breeding/compatible_pairs/"), "compatible_pairs")
#     for pair in data_list:
#         parent_1, parent_2 = pair
#         validate_animal(parent_1)
#         validate_animal(parent_2)
#         assert parent_1["species"] == parent_2["species"]
#         assert parent_1["sex"] != parent_2["sex"]
#         assert is_eligible_for_breeding(parent_1, COOLDOWN_PERIOD_DAYS)
#         assert is_eligible_for_breeding(parent_2, COOLDOWN_PERIOD_DAYS)

# def test_get_offspring():
#     newborn = next((a for a in animals if a["age"] == 0), None)
#     if not newborn:
#         pytest.skip("No newborn in the data.")
#     data = validate_response(client.get(f"/offspring/{newborn['id']}"), "offspring")
#     assert data["id"] == newborn["id"]

# def test_get_lineage():
#     parent = next((a for a in animals if a.get("parent_ids")), None)
#     if not parent:
#         pytest.skip("No animal with parent_ids to test lineage.")
#     resp = client.get(f"/lineage/{parent['id']}")
#     js = resp.json()
#     assert resp.status_code == 200
#     assert "offspring" in js
#     assert isinstance(js["offspring"], list)

# def test_schedule_breeding():
#     pairs = validate_response(client.get("/breeding/compatible_pairs/"), "compatible_pairs")
#     if not pairs:
#         pytest.skip("No compatible pairs found.")
#     scheduled = validate_response(client.post("/breeding/schedule/"), "scheduled_events")
#     assert isinstance(scheduled, list)

# def test_check_births():
#     female = next((a for a in animals if a["sex"] == "female"
#                    and a["health_status"] == "Healthy"
#                    and a["pregnant"] == "no"), None)
#     if not female:
#         pytest.skip("No suitable female found for test births.")
#     male = next((a for a in animals if a["species"] == female["species"]
#                  and a["sex"] == "male"
#                  and a["health_status"] == "Healthy"), None)
#     if not male:
#         pytest.skip("No suitable male found for test births.")

#     female["pregnant"] = "yes"
#     female["expected_birth_date"] = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
#     female["parent_ids"] = [male["id"], female["id"]]

#     new_litters = validate_response(client.post("/breeding/check_births/"), "new_litters")
#     assert new_litters

# def test_get_breeding_history():
#     f = next((a for a in animals if a["sex"] == "female"), None)
#     if not f:
#         pytest.skip("No female found for breeding history test.")
#     resp = client.get(f"/breeding/history/{f['id']}")
#     js = resp.json()
#     assert resp.status_code == 200
#     assert "litters" in js

# def test_get_success_rate():
#     resp = client.get("/breeding/success_rate/")
#     js = resp.json()
#     assert isinstance(js, dict)
#     assert "total_events" in js
#     assert "successful_events" in js
#     assert "success_rate" in js
#     assert isinstance(js["success_rate"], float)

# def test_breeding_cooldown():
#     male_lion = next((a for a in animals if a["species"] == "Lion"
#                       and a["sex"] == "male"
#                       and a["health_status"] == "Healthy"), None)
#     female_lion = next((a for a in animals if a["species"] == "Lion"
#                         and a["sex"] == "female"
#                         and a["health_status"] == "Healthy"), None)
#     if not male_lion or not female_lion:
#         pytest.skip("No valid male/female lion for cooldown test.")

#     # within cooldown
#     male_lion["last_breeding_date"] = (datetime.now(timezone.utc) - timedelta(days=COOLDOWN_PERIOD_DAYS - 10)).isoformat()
#     female_lion["last_breeding_date"] = (datetime.now(timezone.utc) - timedelta(days=COOLDOWN_PERIOD_DAYS - 10)).isoformat()

#     resp = client.post("/breeding/schedule/")
#     events = resp.json()["scheduled_events"]
#     # ensure not scheduled
#     pair_found = any(
#         (evt["parent_1_id"] == male_lion["id"] and evt["parent_2_id"] == female_lion["id"]) or
#         (evt["parent_1_id"] == female_lion["id"] and evt["parent_2_id"] == male_lion["id"])
#         for evt in events
#     )
#     if pair_found:
#         pytest.fail("Cooldown not enforced: pair was scheduled within cooldown")

#     # beyond cooldown
#     older_date = (datetime.now(timezone.utc) - timedelta(days=COOLDOWN_PERIOD_DAYS + 10)).isoformat()
#     male_lion["last_breeding_date"] = older_date
#     female_lion["last_breeding_date"] = older_date

#     resp = client.post("/breeding/schedule/")
#     events = resp.json()["scheduled_events"]
#     pair_found = any(
#         (evt["parent_1_id"] == male_lion["id"] and evt["parent_2_id"] == female_lion["id"]) or
#         (evt["parent_1_id"] == female_lion["id"] and evt["parent_2_id"] == male_lion["id"])
#         for evt in events
#     )
#     assert pair_found, "Cooldown period not respected after expiration"

# def test_is_eligible_for_breeding():
#     temp_animal = {
#         "id": str(uuid4()),
#         "species": "Lion",
#         "sex": "male",
#         "age": 5,
#         "health_status": "Healthy",
#         "pregnant": "no",
#         "last_breeding_date": None,
#     }
#     assert is_eligible_for_breeding(temp_animal, COOLDOWN_PERIOD_DAYS)

#     temp_animal["health_status"] = "Critical"
#     assert not is_eligible_for_breeding(temp_animal, COOLDOWN_PERIOD_DAYS)

#     temp_animal["health_status"] = "Healthy"
#     temp_animal["last_breeding_date"] = (datetime.now(timezone.utc) - timedelta(days=COOLDOWN_PERIOD_DAYS - 1)).isoformat()
#     assert not is_eligible_for_breeding(temp_animal, COOLDOWN_PERIOD_DAYS)

#     temp_animal["last_breeding_date"] = (datetime.now(timezone.utc) - timedelta(days=COOLDOWN_PERIOD_DAYS + 1)).isoformat()
#     assert is_eligible_for_breeding(temp_animal, COOLDOWN_PERIOD_DAYS)

# ####################
# # NEW TESTS
# ####################

# def test_breeding_suggestions():
#     resp = client.get("/breeding/suggestions/")
#     js = resp.json()
#     assert "suggestions" in js
#     assert isinstance(js["suggestions"], list)

# def test_offspring_milestones():
#     # find an animal with milestones or create one
#     test_off = next((a for a in animals if a.get("milestones")), None)
#     if not test_off:
#         test_off = {
#             "id": str(uuid4()),
#             "name": "MilestoneTest",
#             "species": "Zebra",
#             "sex": "female",
#             "age": 0,
#             "health_status": "Healthy",
#             "pregnant": "no",
#             "milestones": []
#         }
#         animals.append(test_off)

#     ms_payload = [
#         {
#             "name": "Weaning",
#             "due_date": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
#             "completed_date": None,
#             "notes": "Should finish in 1 day"
#         }
#     ]
#     r = client.put(f"/offspring/milestones/{test_off['id']}", json=ms_payload)
#     assert r.status_code == 200

#     r = client.get(f"/offspring/milestones/{test_off['id']}")
#     assert r.status_code == 200
#     data = r.json()
#     assert len(data["milestones"]) == 1

# def test_milestone_alerts():
#     test_off = next((a for a in animals if a.get("milestones")), None)
#     if not test_off:
#         pytest.skip("No offspring with milestones.")
#     # set first milestone to overdue
#     test_off["milestones"][0]["due_date"] = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
#     test_off["milestones"][0]["completed_date"] = None

#     # trigger check
#     r = client.post("/offspring/check_milestones")
#     assert r.status_code == 200
#     data = r.json()
#     assert "alerts" in data
#     assert len(data["alerts"]) >= 1

#     # confirm /alerts/ shows them
#     r = client.get("/alerts/")
#     assert r.status_code == 200
#     data = r.json()
#     assert "alerts" in data
#     assert len(data["alerts"]) >= 1

# def test_mortality_updates_and_analytics():
#     newborn = next((a for a in animals if a["age"] == 0), None)
#     if not newborn:
#         pytest.skip("No newborn to test mortality.")
#     payload = {
#         "mortality_status": "Deceased",
#         "mortality_reason": "Test cause",
#         "date_of_death": datetime.now(timezone.utc).isoformat()
#     }
#     r = client.put(f"/offspring/mortality/{newborn['id']}", json=payload)
#     assert r.status_code == 200

#     r = client.get("/analytics/mortality/")
#     assert r.status_code == 200
#     js = r.json()
#     assert "mortality_summary" in js
#     assert isinstance(js["mortality_summary"], list)

#     # Re-check for final confirmation
#     r = client.get("/analytics/mortality/")
#     data = r.json()
#     assert "mortality_summary" in data
#     assert isinstance(data["mortality_summary"], list)

# ####################
# # ADDITIONAL NEW TESTS
# ####################

# def test_breeding_pregnant_female_excluded():
#     """Ensure pregnant female is excluded from /breeding/schedule/."""
#     female = next((a for a in animals 
#                    if a["sex"] == "female"
#                    and a["health_status"] == "Healthy"), None)
#     if not female:
#         pytest.skip("No healthy female found for test.")
#     male = next((a for a in animals 
#                  if a["species"] == female["species"]
#                  and a["sex"] == "male"
#                  and a["health_status"] == "Healthy"), None)
#     if not male:
#         pytest.skip("No matching male found.")

#     # Mark female as pregnant
#     female["pregnant"] = "yes"
#     resp = client.post("/breeding/schedule/")
#     scheduled = resp.json().get("scheduled_events", [])
#     pair_scheduled = any(
#         (evt["parent_1_id"] == female["id"] and evt["parent_2_id"] == male["id"]) or
#         (evt["parent_1_id"] == male["id"] and evt["parent_2_id"] == female["id"])
#         for evt in scheduled
#     )
#     assert not pair_scheduled, "Pregnant female incorrectly scheduled."

#     # revert
#     female["pregnant"] = "no"

# def test_breeding_schedule_cooldown_immediate_retry():
#     """
#     Tests scheduling a pair, then tries to schedule them again within cooldown.
#     """
#     pair = None
#     for a1 in animals:
#         if a1["sex"] == "male" and a1["health_status"] == "Healthy":
#             for a2 in animals:
#                 if (a2["sex"] == "female"
#                     and a2["health_status"] == "Healthy"
#                     and a1["species"] == a2["species"]):
#                     pair = (a1, a2)
#                     break
#             if pair:
#                 break

#     if not pair:
#         pytest.skip("No male-female healthy pair found.")
#     male, female = pair

#     # Force them outside the cooldown
#     older_date = (datetime.now(timezone.utc) - timedelta(days=COOLDOWN_PERIOD_DAYS + 10)).isoformat()
#     male["last_breeding_date"] = older_date
#     female["last_breeding_date"] = older_date

#     # 1) Schedule breeding once
#     r = client.post("/breeding/schedule/")
#     scheduled = r.json().get("scheduled_events", [])
#     pair_in_scheduled = any(
#         (evt["parent_1_id"] == male["id"] and evt["parent_2_id"] == female["id"])
#         or (evt["parent_1_id"] == female["id"] and evt["parent_2_id"] == male["id"])
#         for evt in scheduled
#     )
#     assert pair_in_scheduled, "Expected pair not scheduled the first time."

#     # 2) Attempt scheduling again => Should fail
#     r2 = client.post("/breeding/schedule/")
#     scheduled2 = r2.json().get("scheduled_events", [])
#     pair_in_scheduled2 = any(
#         (evt["parent_1_id"] == male["id"] and evt["parent_2_id"] == female["id"])
#         or (evt["parent_1_id"] == female["id"] and evt["parent_2_id"] == male["id"])
#         for evt in scheduled2
#     )
#     assert not pair_in_scheduled2, "Pair incorrectly scheduled within cooldown."
