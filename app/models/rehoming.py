# app/models/rehoming.py

from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional

class RehomingRecord(BaseModel):
    """
    A record of transferring an offspring to a new location.
    """
    id: UUID = Field(
        default_factory=uuid4,
        title="Rehoming Record ID",
        description="Unique identifier for this rehoming record."
    )
    new_location: str = Field(
        ...,
        title="New Location",
        description="Name or location identifier where the offspring is transferred."
    )
    transfer_date: datetime = Field(
        default_factory=datetime.now,
        title="Transfer Date",
        description="When the offspring was transferred."
    )
    notes: Optional[str] = Field(
        None,
        title="Rehoming Notes",
        description="Additional notes about the transfer."
    )
    offspring_id: Optional[UUID] = Field(
        None,
        title="Offspring ID",
        description="UUID of the offspring that is being rehomed."
    )
