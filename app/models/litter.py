# app/models/litter.py

from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional

class Litter(BaseModel):
    """
    A record representing a litter of offspring produced by a breeding event.
    """
    id: UUID = Field(
        default_factory=uuid4,
        title="Litter ID",
        description="Unique identifier for this litter."
    )
    breeding_id: Optional[UUID] = Field(
        None,
        title="Associated Breeding ID",
        description="Breeding event from which this litter resulted."
    )
    size: int = Field(
        ...,
        title="Number of Offspring",
        description="How many offspring were in this litter."
    )
    birth_date: datetime = Field(
        ...,
        title="Birth Date",
        description="When the litter was born."
    )
    description: Optional[str] = Field(
        None,
        title="Litter Description",
        description="Additional notes about this litter's characteristics or status."
    )
    parent_1_id: UUID
    parent_2_id: UUID
    parent_1_name: str
    parent_2_name: str
    species: str
    created_at: datetime = Field(
        default_factory=datetime.now,
        title="Created At",
        description="When this litter record was created."
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        title="Updated At",
        description="When this litter record was last updated."
    )
