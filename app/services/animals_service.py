# app/services/animals_service.py

from typing import List
from test_data import animals

def list_all_animals_service() -> List[dict]:
    """
    Return a list of all animals in the system (from in-memory 'animals').
    """
    return animals
