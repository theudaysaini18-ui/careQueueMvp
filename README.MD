# CareQueue – AI‑Assisted OPD Control Panel

CareQueue is a hackathon‑ready MVP that helps outpatient departments manage doctor queues with AI‑assisted consult time estimation and intra‑department load balancing, built on FastAPI and Jinja2 templates.[web:144]

---

## Features

- **Live OPD dashboard**
  - Summary tiles for *Patients Waiting*, *Avg Predicted Wait*, *Doctors Available*, and *AI Suggestion*.
  - Per‑doctor queue cards showing patient name, age, reason, priority, estimated consult time, and predicted wait.

- **AI‑assisted consult estimates**
  - Simple rule‑based “AI” estimates consult duration based on age and reason text (e.g., chest pain, shortness of breath, high‑complexity symptoms).
  - Predicted wait for each patient is computed from the queue ahead of them.

- **Smart intra‑department rebalancing**
  - Suggests moving a patient **between doctors in the same department** (e.g., General OPD → General OPD) when queues are imbalanced.
  - Shows impact: current wait vs expected wait after the move.
  - One‑click “Apply Suggestion” to rebalance the queue.

- **Doctor‑centric workflow**
  - Each doctor has their own card with a “Next Patient” button.
  - Clicking “Next Patient” pops the top patient from that doctor’s queue.

- **Hackathon‑friendly implementation**
  - In‑memory data (no external DB) for reliability and zero setup.
  - Clean, Bootstrap‑based UI with cards, badges, and clear legends.
  - Small, readable FastAPI codebase that’s easy to demo and extend.[web:146][web:148]

---

## Tech Stack

- **Backend:** FastAPI, Starlette, Python 3.12[web:144]
- **Templating:** Jinja2
- **Frontend:** HTML, Bootstrap 5, custom CSS
- **Runtime:** Uvicorn ASGI server

Folder layout (simplified):

```text
careQueueMvp/
├── backend/
│   └── app/
│       ├── main.py            # FastAPI app, routes, dashboard logic
│       ├── models.py          # In‑memory domain models (Doctor, PatientVisit, etc.)
│       ├── queue_logic.py     # Estimation + rebalancing logic
│       ├── ai_estimator.py    # Simple rule‑based consult time estimator
│       ├── schemas.py         # Pydantic schemas for form handling
│       ├── templates/
│       │   ├── base.html
│       │   ├── dashboard.html
│       │   └── add_patient.html
│       └── static/
│           └── css/
│               └── style.css  # Custom styles
└── README.md
```

---

## Getting Started

### Prerequisites

- Python **3.12** installed (`python3.12 --version`).
- `git` and a terminal (Mac/Linux/WSL recommended).

### 1. Clone the repository

```bash
git clone <your-repo-url> careQueueMvp
cd careQueueMvp
```

### 2. Create and activate a virtual environment

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

On Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

If you have a `requirements.txt`:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If not, install the core packages directly:

```bash
python -m pip install --upgrade pip
python -m pip install fastapi "uvicorn[standard]" jinja2 python-multipart
```

### 4. Run the app

From the project root:

```bash
python -m uvicorn backend.app.main:app --reload
```

Then open:

- http://127.0.0.1:8000 – main OPD dashboard
- http://127.0.0.1:8000/docs – auto‑generated FastAPI docs (for API endpoints, if exposed)[web:144]

---

## Configuration

For this MVP:

- All data is stored **in memory**; restarting the server resets the queue.
- Seed doctors and sample patients are defined in `backend/app/main.py`.
- The complexity and consult‑time estimation rules are in `ai_estimator.py` and referenced from `queue_logic.py`.

You can tweak:

- Departments and doctor list.
- Priority levels and their visual styling.
- The keyword rules used to mark cases as “High complexity”.

---

## Limitations & Next Steps

Current limitations (acceptable for hackathon demo):

- No user authentication or role‑based access.
- No persistence layer (no database or integration with a real EMR).
- AI is rule‑based, not a trained model.

Potential extensions:

- Plug in a real database for visits and historical stats.
- Use a small ML model (or external API) for consult time / complexity prediction.
- Add analytics (e.g., average wait per doctor, per department, per day).
- Add authentication and audit logging for hospital environments.

---
