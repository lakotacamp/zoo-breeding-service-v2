# tests/test_routers/test_offspring.py
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta, timezone
from main import app

client = TestClient(app)

def test_get_offspring_milestones():
    # 1) Grab some existing offspring from /animals/ or the first female with "parent_ids" etc.
    r = client.get("/animals/")
    assert r.status_code == 200
    animals_data = r.json().get("animals", [])

    if not animals_data:
        pytest.skip("No animals to test milestones with.")

    # 2) Find one with some 'milestones' if you want
    target_off = None
    for a in animals_data:
        if a.get("milestones"):
            target_off = a
            break
    if not target_off:
        pytest.skip("No animal with 'milestones' found. Skipping test.")

    offspring_id = target_off["id"]

    # 3) Now actually test the endpoint
    response = client.get(f"/offspring/milestones/{offspring_id}")
    assert response.status_code == 200
    data = response.json()
    assert "milestones" in data

def test_check_milestones():
    """
    Test the /offspring/check_milestones endpoint for overdue milestone alerts.
    """
    response = client.post("/offspring/check_milestones")
    assert response.status_code == 200
    data = response.json()
    assert "alerts" in data
    assert isinstance(data["alerts"], list)
