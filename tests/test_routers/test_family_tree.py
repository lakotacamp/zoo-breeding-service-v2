import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_lineage():
    """
    Retrieve immediate parents, offspring, and siblings for an existing animal ID.
    """
    # 1) Get the list of animals
    resp = client.get("/animals/")
    assert resp.status_code == 200
    data = resp.json()
    all_animals = data.get("animals", [])

    if not all_animals:
        pytest.skip("No animals found, skipping test.")

    # 2) Choose the first animal from the result
    animal_id = all_animals[0]["id"]

    # 3) Now call the lineage endpoint
    response = client.get(f"/lineage/{animal_id}")
    assert response.status_code == 200

    # Check your response structure
    lineage_data = response.json()
    assert "offspring" in lineage_data
    assert "parents" in lineage_data
    assert "siblings" in lineage_data

def test_get_lineage_tree():
    """
    Test the /lineage/tree/{animal_id} endpoint for retrieving a full lineage tree.
    """
    # 1) Get animals
    resp = client.get("/animals/")
    assert resp.status_code == 200
    data = resp.json()
    all_animals = data.get("animals", [])

    if not all_animals:
        pytest.skip("No animals found, skipping test.")

    # 2) Choose first real ID
    animal_id = all_animals[0]["id"]

    # 3) Call the tree endpoint
    depth = 3
    response = client.get(f"/lineage/tree/{animal_id}?depth={depth}")
    assert response.status_code == 200

    # Check your response
    tree_data = response.json()
    assert "lineage_tree" in tree_data
