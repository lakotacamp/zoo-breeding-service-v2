# app/services/rehoming_service.py

from typing import Optional, List
from test_data import animals
from app.services.utils_service import validate_uuid
from app.models.rehoming import RehomingRecord

rehoming_data = []  # or from app.database if you prefer

def rehome_offspring(offspring_id: str, record: RehomingRecord) -> Optional[dict]:
    validate_uuid(offspring_id)
    tgt = next((a for a in animals if a["id"] == offspring_id), None)
    if not tgt:
        return None

    rec_dict = record.dict()
    rehoming_data.append(rec_dict)

    # Mark the offspring as transferred
    tgt["rehoming_status"] = "Transferred"
    tgt["new_location"] = record.new_location
    tgt["transfer_date"] = record.transfer_date.isoformat()

    return {"detail": f"Offspring {offspring_id} rehomed.", "record": rec_dict}

def get_rehoming_history(offspring_id: str) -> Optional[List[dict]]:
    """
    Return a list of rehoming records for the given offspring,
    or None if the offspring does not exist at all.
    """
    validate_uuid(offspring_id)
    # check if the offspring truly exists
    if not any(a["id"] == offspring_id for a in animals):
        return None

    # see if we have any records in rehoming_data
    found_records = []
    for r in rehoming_data:
        if "offspring_id" in r:
            if str(r["offspring_id"]) == offspring_id:
                found_records.append(r)
    return found_records
