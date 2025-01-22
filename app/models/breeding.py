# app/models/breeding.py

from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional

class Breeding(BaseModel):
    """
    A record of a breeding event between two animals.
    """
    id: UUID = Field(
        default_factory=uuid4,
        title="Breeding Record ID",
        description="Unique identifier for this breeding record."
    )
    parent_1_id: UUID = Field(..., title="Parent 1 ID")
    parent_2_id: UUID = Field(..., title="Parent 2 ID")
    parent_1_name: str = Field(
        ...,
        title="Parent 1 Name",
        max_length=100,
        examples=["LionKing"]
    )
    parent_2_name: str = Field(
        ...,
        title="Parent 2 Name",
        max_length=100,
        examples=["LionQueen"]
    )
    occurred_at: datetime = Field(
        ...,
        title="Breeding Occurred At",
        examples=["2023-03-01T09:00:00Z"]
    )
    description: Optional[str] = Field(
        None,
        title="Breeding Description",
        description="Any details about the breeding event outcome or context."
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        title="Created At",
        description="When this record was initially created."
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        title="Updated At",
        description="When this record was last updated."
    )
