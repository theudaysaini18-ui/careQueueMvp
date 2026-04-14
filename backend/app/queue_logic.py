# backend/app/queue_logic.py
from collections import defaultdict
from typing import List, Dict
from .models import PatientVisit, Doctor, Status, Priority
from .ai_estimator import estimate_consult_minutes


def recalc_estimates(
    patients: List[PatientVisit],
    doctors_by_id: Dict[int, Doctor],
) -> None:
    """Recompute estimated consult + predicted wait for all waiting patients."""
    queues: Dict[int, List[PatientVisit]] = defaultdict(list)
    for p in patients:
        if p.status == Status.waiting:
            queues[p.assigned_doctor_id].append(p)

    for doctor_id, queue in queues.items():
        doctor = doctors_by_id[doctor_id]

        queue.sort(
            key=lambda p: (
                p.arrival_time,
                0 if p.priority == Priority.urgent else
                1 if p.priority == Priority.high else
                2
            )
        )

        elapsed = 0
        for p in queue:
            est = estimate_consult_minutes(p, doctor)
            p.estimated_consult_minutes = est
            p.predicted_wait_minutes = elapsed
            elapsed += est


def suggest_rebalance(
    patients: List[PatientVisit],
    doctors_by_id: Dict[int, Doctor],
):
    """
    Suggest moving a low-priority patient between doctors
    in the SAME department only, if one doctor's load is > 2x another's.
    Also returns the predicted wait reduction for that patient.
    """
    # Compute load per doctor (sum of estimated consult minutes)
    loads: Dict[int, int] = defaultdict(int)
    for p in patients:
        if p.status == Status.waiting:
            loads[p.assigned_doctor_id] += p.estimated_consult_minutes or 0

    if not loads:
        return None

    # Group doctors by department
    doctors_by_dept: Dict[str, List[int]] = defaultdict(list)
    for doc_id, doc in doctors_by_id.items():
        doctors_by_dept[doc.department].append(doc_id)

    for dept, doc_ids in doctors_by_dept.items():
        # Need at least 2 doctors in a department to rebalance
        if len(doc_ids) < 2:
            continue

        dept_loads = {doc_id: loads.get(doc_id, 0) for doc_id in doc_ids}
        busiest = max(dept_loads, key=dept_loads.get)
        least = min(dept_loads, key=dept_loads.get)

        # Only rebalance if busiest is at least 2x the least loaded
        if dept_loads[busiest] < 2 * dept_loads[least]:
            continue

        # Waiting patients for each doctor in this department
        busiest_queue = [
            p for p in patients
            if p.status == Status.waiting and p.assigned_doctor_id == busiest
        ]
        least_queue = [
            p for p in patients
            if p.status == Status.waiting and p.assigned_doctor_id == least
        ]

        if not busiest_queue:
            continue

        # Sort by arrival time (latest last)
        busiest_queue.sort(key=lambda p: p.arrival_time)

        # Prefer the last-arrived normal-priority patient
        movable = None
        for p in reversed(busiest_queue):
            if p.priority == Priority.normal:
                movable = p
                break

        if not movable:
            continue

        # Predicted wait at current doctor (already computed)
        wait_before = movable.predicted_wait_minutes or 0

        # Predicted wait if moved to the other doctor:
        # sum of existing queue at least doctor + this patient's own consult time
        target_doctor = doctors_by_id[least]
        est_at_target = estimate_consult_minutes(movable, target_doctor)
        load_at_target = sum(
            q.estimated_consult_minutes or 0 for q in least_queue
        )
        wait_after = load_at_target  # time until they are seen

        return {
            "patient_id": movable.id,
            "patient_name": movable.patient_name,
            "from_doctor_id": busiest,
            "to_doctor_id": least,
            "department": dept,
            "wait_before": int(wait_before),
            "wait_after": int(wait_after),
        }

    return None