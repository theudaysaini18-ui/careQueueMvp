# backend/app/schemas.py
from datetime import datetime
from pydantic import BaseModel, Field
from .models import Priority


class PatientCreate(BaseModel):
    patient_name: str = Field(..., min_length=1)
    age: int = Field(..., ge=0, le=120)
    priority: Priority
    reason: str = Field(..., min_length=3)
    assigned_doctor_id: int