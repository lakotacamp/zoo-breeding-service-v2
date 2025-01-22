# app/models/behavior.py

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class BehavioralLogEntry(BaseModel):
    """
    A log entry capturing a specific behavior event for an offspring.
    """
    timestamp: datetime = Field(
        default_factory=datetime.now,
        title="Time of Observation",
        description="When this behavior was observed.",
        examples=["2023-01-05T13:45:00Z"]
    )
    behavior_type: str = Field(
        ...,
        title="Type of Behavior",
        description="Type or category of behavior observed (e.g., feeding, playing).",
        examples=["play", "feeding", "aggression"]
    )
    notes: Optional[str] = Field(
        None,
        title="Additional Notes",
        description="Any extra details the observer wishes to record.",
        examples=["Playing gently with siblings."]
    )
