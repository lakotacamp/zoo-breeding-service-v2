# app/utils/family_tree.py

def build_family_tree(animal_id: str, animals: list, depth: int) -> dict:
    """
    Recursively build a family tree for the given animal ID.

    Args:
        animal_id (str): The ID of the animal.
        animals (list): List of all animals in the system.
        depth (int): Maximum depth to recurse.

    Returns:
        dict: A nested family tree dictionary.
    """
    if depth == 0:
        return {}

    # Find the animal in the list
    animal = next((a for a in animals if a["id"] == animal_id), None)
    if not animal:
        return {}

    # Build the immediate family (parents and offspring)
    parents = [a for a in animals if a["id"] in animal.get("parent_ids", [])]
    offspring = [a for a in animals if animal_id in a.get("parent_ids", [])]

    # Recurse for each parent and offspring
    return {
        "animal": animal,
        "parents": [build_family_tree(p["id"], animals, depth - 1) for p in parents],
        "offspring": [build_family_tree(o["id"], animals, depth - 1) for o in offspring],
    }
