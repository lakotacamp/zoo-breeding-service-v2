# app/schemas/breeding.py
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional

class BreedingCreateSchema(BaseModel):
    """
    Schema for creating a breeding record.
    """
    parent_1_id: UUID = Field(..., title="Parent 1 ID")
    parent_2_id: UUID = Field(..., title="Parent 2 ID")
    parent_1_name: str = Field(..., max_length=100, title="Parent 1 Name")
    parent_2_name: str = Field(..., max_length=100, title="Parent 2 Name")
    occurred_at: datetime = Field(..., title="Breeding Occurred At")
    description: Optional[str] = Field(None, title="Breeding Description")

class BreedingUpdateSchema(BaseModel):
    """
    Schema for updating a breeding record.
    """
    parent_1_id: Optional[UUID] = None
    parent_2_id: Optional[UUID] = None
    parent_1_name: Optional[str] = None
    parent_2_name: Optional[str] = None
    occurred_at: Optional[datetime] = None
    description: Optional[str] = None

class BreedingOutSchema(BaseModel):
    """
    Schema returned to clients for a breeding record.
    """
    id: UUID = Field(default_factory=uuid4, title="Breeding Record ID")
    parent_1_id: UUID
    parent_2_id: UUID
    parent_1_name: str
    parent_2_name: str
    occurred_at: datetime
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        orm_mode = True
