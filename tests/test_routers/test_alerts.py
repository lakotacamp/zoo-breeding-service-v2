# tests/test_routers/test_alerts.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_list_alerts():
    """
    Test the /alerts/ endpoint for retrieving alerts.
    """
    response = client.get("/alerts/")
    assert response.status_code == 200
    data = response.json()
    assert "alerts" in data
    assert isinstance(data["alerts"], list)
