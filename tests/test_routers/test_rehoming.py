# tests/test_routers/test_rehoming.py
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone
from main import app

client = TestClient(app)

def test_rehome_offspring():
    resp = client.get("/animals/")
    assert resp.status_code == 200
    all_animals = resp.json().get("animals", [])
    if not all_animals:
        pytest.skip("No animals found to test rehoming.")

    # pick first
    offspring_id = all_animals[0]["id"]
    payload = {
        "new_location": "Sanctuary A",
        "transfer_date": datetime.now(timezone.utc).isoformat(),
        "notes": "Transferred due to overcrowding.",
    }
    response = client.post(f"/offspring/rehoming/{offspring_id}", json=payload)
    # if your code returns 404 when the 'offspring' has no parent or is a certain species,
    # you may want to pick an actual young animal or handle that logic. 
    assert response.status_code == 200
    # ...

def test_get_rehoming_history():
    from test_data import animals

    # 1) find any existing animal that we can test
    # for rehoming, there's no strict requirement except that it exists
    candidate = animals[0] if animals else None
    if not candidate:
        pytest.skip("No animals in test_data, cannot test rehoming history.")
    real_id = candidate["id"]

    response = client.get(f"/offspring/rehoming/{real_id}")
    # If your route requires it to exist in rehoming_data, you might need to 
    # do a prior step that calls the rehome endpoint. But let's see if 
    # your code simply returns an empty record list if none found.

    # 2) confirm the status code
    # maybe your code returns 200 with { "records": [] } if no rehoming was done
    # or 404 if the route expects "only recognized offspring" etc.
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    data = response.json()
    assert "records" in data
    assert isinstance(data["records"], list)
