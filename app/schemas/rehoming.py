# app/schemas/rehoming.py
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional

class RehomingCreateSchema(BaseModel):
    """
    Schema for rehoming an offspring to a new location.
    """
    new_location: str = Field(..., title="New Location")
    transfer_date: datetime = Field(default_factory=datetime.now, title="Transfer Date")
    notes: Optional[str] = None
    offspring_id: Optional[UUID] = None

class RehomingOutSchema(BaseModel):
    """
    Schema returned to clients for a rehoming record.
    """
    id: UUID = Field(default_factory=uuid4, title="Rehoming Record ID")
    new_location: str
    transfer_date: datetime
    notes: Optional[str] = None
    offspring_id: Optional[UUID] = None

    class Config:
        orm_mode = True
