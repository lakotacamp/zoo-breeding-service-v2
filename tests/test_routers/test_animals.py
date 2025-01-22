# tests/test_routers/test_animals.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_all_animals():
    """
    Test the /animals/ endpoint for retrieving all animals.
    """
    response = client.get("/animals/")
    assert response.status_code == 200
    data = response.json()
    assert "animals" in data
    assert isinstance(data["animals"], list)
    for animal in data["animals"]:
        assert "id" in animal
        assert "species" in animal
        assert "sex" in animal
