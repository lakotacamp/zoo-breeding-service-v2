import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_list_all_litters():
    """
    Test the /litters/ endpoint for retrieving all litters.
    """
    response = client.get("/litters/")
    assert response.status_code == 200
    data = response.json()
    assert "litters" in data
    assert isinstance(data["litters"], list)

def test_get_litter_by_id():
    """
    Dynamically fetch the first litter's ID, then call /litter/{litter_id}.
    """
    # 1) First, get the list of litters
    resp = client.get("/litters/")
    assert resp.status_code == 200
    data = resp.json()
    all_litters = data.get("litters", [])

    # 2) If no litters, skip
    if not all_litters:
        pytest.skip("No litters available to test.")

    # 3) Grab a real existing ID
    litter_id = str(all_litters[0]["id"])  # convert to string if needed

    # 4) Now test your read endpoint with a valid ID
    response = client.get(f"/litter/{litter_id}")
    assert response.status_code == 200

    # 5) Optionally check the content
    litter = response.json()
    assert "id" in litter
    assert litter["id"] == litter_id
