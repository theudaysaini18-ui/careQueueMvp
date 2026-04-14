# backend/app/models.py
from enum import Enum
from datetime import datetime
from typing import Optional


class Priority(str, Enum):
    normal = "Normal"
    high = "High"
    urgent = "Urgent"


class Status(str, Enum):
    waiting = "waiting"
    in_consultation = "in_consultation"
    completed = "completed"


class Doctor:
    def __init__(self, id: int, name: str, department: str, avg_consult_minutes: int):
        self.id = id
        self.name = name
        self.department = department
        self.avg_consult_minutes = avg_consult_minutes


class PatientVisit:
    def __init__(
        self,
        id: int,
        patient_name: str,
        age: int,
        priority: Priority,
        reason: str,
        arrival_time: datetime,
        assigned_doctor_id: int,
        status: Status = Status.waiting,
        estimated_consult_minutes: Optional[int] = None,
        predicted_wait_minutes: Optional[int] = None,
    ):
        self.id = id
        self.patient_name = patient_name
        self.age = age
        self.priority = priority
        self.reason = reason
        self.arrival_time = arrival_time
        self.assigned_doctor_id = assigned_doctor_id
        self.status = status
        self.estimated_consult_minutes = estimated_consult_minutes
        self.predicted_wait_minutes = predicted_wait_minutes