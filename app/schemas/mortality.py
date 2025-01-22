# app/schemas/mortality.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class MortalityUpdateSchema(BaseModel):
    """
    A schema for updating an offspring's mortality status.
    """
    mortality_status: str = Field(..., title="Mortality Status")
    mortality_reason: Optional[str] = Field(None, title="Mortality Reason")
    date_of_death: Optional[datetime] = Field(None, title="Date of Death")
