# tests/test_routers/test_breeding.py
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta, timezone
from app.services.utils_service import COOLDOWN_PERIOD_DAYS, is_eligible_for_breeding
from main import app

client = TestClient(app)

def test_get_compatible_pairs():
    """
    Test the /breeding/compatible_pairs/ endpoint for retrieving compatible breeding pairs.
    """
    response = client.get("/breeding/compatible_pairs/")
    assert response.status_code == 200
    data = response.json()
    assert "compatible_pairs" in data
    for pair in data["compatible_pairs"]:
        parent_1, parent_2 = pair
        assert parent_1["species"] == parent_2["species"]
        assert parent_1["sex"] != parent_2["sex"]
        assert is_eligible_for_breeding(parent_1, COOLDOWN_PERIOD_DAYS)
        assert is_eligible_for_breeding(parent_2, COOLDOWN_PERIOD_DAYS)

def test_schedule_breeding():
    """
    Test the /breeding/schedule/ endpoint for scheduling breeding events.
    """
    response = client.post("/breeding/schedule/")
    assert response.status_code == 200
    scheduled_events = response.json().get("scheduled_events", [])
    assert isinstance(scheduled_events, list)

def test_get_success_rate():
    """
    Test the /breeding/success_rate/ endpoint for retrieving breeding success rate.
    """
    response = client.get("/breeding/success_rate/")
    assert response.status_code == 200
    data = response.json()
    assert "success_rate" in data
    assert isinstance(data["success_rate"], float)

def test_breeding_cooldown():
    """
    Test the breeding cooldown mechanism in /breeding/schedule/.
    """
    male_lion = {
        "id": "male-lion-id",
        "species": "Lion",
        "sex": "male",
        "health_status": "Healthy",
        "last_breeding_date": (datetime.now(timezone.utc) - timedelta(days=COOLDOWN_PERIOD_DAYS - 1)).isoformat(),
    }
    female_lion = {
        "id": "female-lion-id",
        "species": "Lion",
        "sex": "female",
        "health_status": "Healthy",
        "last_breeding_date": (datetime.now(timezone.utc) - timedelta(days=COOLDOWN_PERIOD_DAYS - 1)).isoformat(),
    }

    response = client.post("/breeding/schedule/")
    events = response.json().get("scheduled_events", [])
    pair_found = any(
        (evt["parent_1_id"] == male_lion["id"] and evt["parent_2_id"] == female_lion["id"]) or
        (evt["parent_1_id"] == female_lion["id"] and evt["parent_2_id"] == male_lion["id"])
        for evt in events
    )
    assert not pair_found, "Cooldown not enforced: pair scheduled within cooldown"
