# app/schemas/litter.py
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional

class LitterCreateSchema(BaseModel):
    """
    Schema for creating a litter record.
    """
    breeding_id: Optional[UUID] = Field(None, title="Associated Breeding ID")
    size: int = Field(..., title="Number of Offspring")
    birth_date: datetime = Field(..., title="Birth Date")
    description: Optional[str] = None
    parent_1_id: UUID
    parent_2_id: UUID
    parent_1_name: str
    parent_2_name: str
    species: str

class LitterUpdateSchema(BaseModel):
    """
    Schema for updating a litter record.
    """
    breeding_id: Optional[UUID] = None
    size: Optional[int] = None
    birth_date: Optional[datetime] = None
    description: Optional[str] = None

class LitterOutSchema(BaseModel):
    """
    Schema returned to clients for a litter record.
    """
    id: UUID = Field(default_factory=uuid4, title="Litter ID")
    breeding_id: Optional[UUID] = None
    size: int
    birth_date: datetime
    description: Optional[str] = None
    parent_1_id: UUID
    parent_2_id: UUID
    parent_1_name: str
    parent_2_name: str
    species: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        orm_mode = True
