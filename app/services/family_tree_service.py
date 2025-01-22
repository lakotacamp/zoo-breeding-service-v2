# app/services/family_tree_service.py
from app.utils.family_tree import build_family_tree
from test_data import animals  # Assuming test_data contains the animals list

def get_lineage(animal_id: str) -> dict:
    """
    Retrieve immediate parents, offspring, and siblings for the given animal.
    """
    animal = next((a for a in animals if a["id"] == animal_id), None)
    if not animal:
        return None

    parents = [a for a in animals if a["id"] in animal.get("parent_ids", [])]
    siblings = [a for a in animals if set(a.get("parent_ids", [])) == set(animal.get("parent_ids", [])) and a["id"] != animal_id]
    offspring = [a for a in animals if animal_id in a.get("parent_ids", [])]

    return {
        "animal": animal,
        "parents": parents,
        "siblings": siblings,
        "offspring": offspring,
    }

def get_lineage_tree(animal_id: str, depth: int) -> dict:
    """
    Build a nested family tree for the given animal up to the specified depth.
    """
    return build_family_tree(animal_id, animals, depth)
