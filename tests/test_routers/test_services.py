# tests/test_services/test_services.py
import pytest
from datetime import datetime, timedelta, timezone
from app.services.utils_service import is_eligible_for_breeding, COOLDOWN_PERIOD_DAYS

def test_is_eligible_for_breeding():
    """
    Test the utility function for determining breeding eligibility.
    """
    test_animal = {
        "id": "animal-id",
        "species": "Lion",
        "sex": "male",
        "age": 5,
        "health_status": "Healthy",
        "pregnant": "no",
        "last_breeding_date": None,
    }
    assert is_eligible_for_breeding(test_animal, COOLDOWN_PERIOD_DAYS)

    # Test with an unhealthy animal
    test_animal["health_status"] = "Critical"
    assert not is_eligible_for_breeding(test_animal, COOLDOWN_PERIOD_DAYS)

    # Test with a recent breeding date
    test_animal["health_status"] = "Healthy"
    test_animal["last_breeding_date"] = (datetime.now(timezone.utc) - timedelta(days=COOLDOWN_PERIOD_DAYS - 1)).isoformat()
    assert not is_eligible_for_breeding(test_animal, COOLDOWN_PERIOD_DAYS)

    # Test with an expired cooldown period
    test_animal["last_breeding_date"] = (datetime.now(timezone.utc) - timedelta(days=COOLDOWN_PERIOD_DAYS + 1)).isoformat()
    assert is_eligible_for_breeding(test_animal, COOLDOWN_PERIOD_DAYS)
