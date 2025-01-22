# tests/test_routers/test_mortality.py
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone
from main import app

client = TestClient(app)

def test_update_offspring_mortality():
    """
    Test the /offspring/mortality/{offspring_id} endpoint for updating mortality status.
    """
    # Possibly we can re-use a young animal from /animals/ or specifically search for any.
    resp = client.get("/animals/")
    assert resp.status_code == 200
    all_animals = resp.json().get("animals", [])
    if not all_animals:
        pytest.skip("No animals to test mortality update.")

    # pick the first one (or any logic to pick a suitable one)
    offspring_id = all_animals[0]["id"]

    payload = {
        "mortality_status": "Deceased",
        "mortality_reason": "Test reason",
        "date_of_death": datetime.now(timezone.utc).isoformat(),
    }
    response = client.put(f"/offspring/mortality/{offspring_id}", json=payload)
    assert response.status_code == 200
    # check result...
    data = response.json()
    assert "detail" in data
    assert "updated" in data["detail"]

def test_mortality_analytics():
    """
    Test the /analytics/mortality/ endpoint for retrieving mortality analytics.
    """
    response = client.get("/analytics/mortality/")
    assert response.status_code == 200
    data = response.json()
    assert "mortality_summary" in data
    assert isinstance(data["mortality_summary"], list)
