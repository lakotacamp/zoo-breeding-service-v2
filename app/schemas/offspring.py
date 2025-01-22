# app/schemas/offspring.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MilestoneSchema(BaseModel):
    name: str
    due_date: datetime
    completed_date: Optional[datetime] = None
    notes: Optional[str] = None

class OffspringMilestonesOut(BaseModel):
    """
    Schema for returning the offspring_id and the relevant milestone data.
    """
    offspring_id: str
    milestones: list[MilestoneSchema]

class OffspringOut(BaseModel):
    """
    Schema for returning an offspring, with optional parent info, etc.
    """
    id: str
    name: str
    species: str
    sex: str
    age: int
    health_status: str
    pregnant: str
    # etc. (mirroring your data)
    # you can add or remove fields as needed

    class Config:
        orm_mode = True
