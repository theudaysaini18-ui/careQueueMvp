# backend/app/main.py
from datetime import datetime

from pathlib import Path
from datetime import datetime
from typing import List, Dict

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader, select_autoescape

from .models import Doctor, PatientVisit, Priority, Status
from .schemas import PatientCreate
from .queue_logic import recalc_estimates, suggest_rebalance

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI()

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

templates_env = Environment(
    loader=FileSystemLoader(str(BASE_DIR / "templates")),
    autoescape=select_autoescape(["html", "xml"]),
    cache_size=0,   # disable Jinja cache
)

# In-memory "database"
doctors: Dict[int, Doctor] = {
    1: Doctor(id=1, name="Dr. Mehta",  department="General OPD", avg_consult_minutes=12),
    2: Doctor(id=2, name="Dr. Singh",  department="General OPD", avg_consult_minutes=14),
    3: Doctor(id=3, name="Dr. Rao",    department="Cardiology",  avg_consult_minutes=18),
    4: Doctor(id=4, name="Dr. Iyer",   department="Orthopaedics", avg_consult_minutes=20),
}
patients: List[PatientVisit] = []
_next_patient_id = 1


def _get_next_patient_id() -> int:
    global _next_patient_id
    pid = _next_patient_id
    _next_patient_id += 1
    return pid


# Seed with a few demo patients so dashboard isn't empty
def seed_demo():
    global patients
    if patients:
        return
    now = datetime.now()
    patients = [
        PatientVisit(
            id=_get_next_patient_id(),
            patient_name="Rahul Sharma",
            age=34,
            priority=Priority.normal,
            reason="Fever and headache",
            arrival_time=now,
            assigned_doctor_id=1,
        ),
        PatientVisit(
            id=_get_next_patient_id(),
            patient_name="Suman Devi",
            age=62,
            priority=Priority.high,
            reason="Chest discomfort and shortness of breath",
            arrival_time=now,
            assigned_doctor_id=2,
        ),
    ]
    recalc_estimates(patients, doctors)


seed_demo()

def compute_summary():
    waiting = [p for p in patients if p.status == Status.waiting]
    high_priority = [
        p for p in waiting if p.priority in (Priority.high, Priority.urgent)
    ]
    avg_wait = (
        sum(p.predicted_wait_minutes or 0 for p in waiting) / len(waiting)
        if waiting else 0
    )
    return {
        "total_waiting": len(waiting),
        "high_priority_count": len(high_priority),
        "avg_wait": int(avg_wait),
        "doctor_count": len(doctors),
    }



@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    recalc_estimates(patients, doctors)

    waiting_patients = [p for p in patients if p.status == Status.waiting]
    in_consult = [p for p in patients if p.status == Status.in_consultation]
    completed = [p for p in patients if p.status == Status.completed]

    summary = compute_summary()
    suggestion = suggest_rebalance(patients, doctors)


    # IMPORTANT: this must be unconditional, not inside any if
    template = templates_env.get_template("dashboard.html")

    html = template.render(
        request=request,
        doctors=doctors,
        patients=patients,
        waiting_patients=waiting_patients,
        in_consult=in_consult,
        completed=completed,
        summary=summary,
        suggestion=suggestion,
    )
    return HTMLResponse(content=html)




@app.get("/add", response_class=HTMLResponse)
async def add_patient_form(request: Request):
    template = templates_env.get_template("add_patient.html")
    html = template.render(
        request=request,
        doctors=doctors.values(),
        priorities=list(Priority),
    )
    return HTMLResponse(content=html)


@app.post("/add")
async def add_patient(
    request: Request,
    patient_name: str = Form(...),
    age: int = Form(...),
    priority: Priority = Form(...),
    reason: str = Form(...),
    assigned_doctor_id: int = Form(...),
):
    pv = PatientVisit(
        id=_get_next_patient_id(),
        patient_name=patient_name,
        age=age,
        priority=priority,
        reason=reason,
        arrival_time=datetime.now(),
        assigned_doctor_id=int(assigned_doctor_id),
    )
    patients.append(pv)
    recalc_estimates(patients, doctors)
    return RedirectResponse(url="/", status_code=303)


@app.post("/next/{doctor_id}")
async def next_patient(doctor_id: int):
    for p in patients:
        if p.assigned_doctor_id == doctor_id and p.status == Status.waiting:
            p.status = Status.completed
            break
    recalc_estimates(patients, doctors)
    return RedirectResponse(url="/", status_code=303)


@app.post("/apply_rebalance")
async def apply_rebalance():
    suggestion = suggest_rebalance(patients, doctors)
    if suggestion:
        pid = suggestion["patient_id"]
        to_doc = suggestion["to_doctor_id"]
        for p in patients:
            if p.id == pid:
                p.assigned_doctor_id = to_doc
                break
        recalc_estimates(patients, doctors)

    return RedirectResponse(url="/", status_code=303)