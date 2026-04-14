# backend/app/ai_estimator.py
from .models import PatientVisit, Priority, Doctor


def estimate_consult_minutes(patient: PatientVisit, doctor: Doctor) -> int:
    """
    Lightweight AI-style estimator for consultation duration.
    In a real system, this would be a trained ML model.
    """
    base = doctor.avg_consult_minutes

    # Priority impact
    if patient.priority == Priority.high:
        base += 3
    elif patient.priority == Priority.urgent:
        base += 6

    # Age impact (older patients may need more time)
    if patient.age >= 60:
        base += 5
    elif patient.age <= 5:
        base += 4

    # Reason complexity (string length as a proxy)
    reason_len = len(patient.reason)
    if reason_len > 40:
        base += 4
    elif reason_len < 10:
        base -= 2

    return max(base, 5)