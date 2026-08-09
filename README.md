# PCs Preventive Maintenance Dashboard

Lab Infrastructure Preventive Monitoring & Asset Management System.
See `docs/planning_document.txt` and `docs/documentation.txt` for the full
requirements, architecture, and database design behind this project.

## Backend setup

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt

# Copy the example env file and fill in your real database URL
copy .env.example .env      # Windows
cp .env.example .env        # macOS/Linux
```

Edit `.env` and set `DATABASE_URL` to your Neon (or other PostgreSQL)
connection string. It defaults to a local SQLite file
(`sqlite:///./maintenance.db`) if left unset, which is fine for quick local
testing but not for the shared multi-PC deployment described in the planning
document.

## Apply database migrations

```bash
cd backend
alembic upgrade head
```

This creates/updates all tables (`computers`, `ram_slots`, `storage_devices`,
`peripherals`, `peripheral_events`, `software_licenses`, `installed_software`,
`metrics_history`, `hardware_change_log`, `alerts`, `maintenance_assets`,
`maintenance_tasks`, `maintenance_log`, `users`, `audit_log`) to match the
SQLAlchemy models in `backend/app/models/`.

To create a new migration after changing a model:

```bash
alembic revision --autogenerate -m "describe your change"
alembic upgrade head
```

## Run the backend

```bash
cd backend
uvicorn app.main:app --reload
```

Then check `http://127.0.0.1:8000/health` — it should return
`{"status": "healthy", "database": "connected"}` once the database is
reachable.

## Project layout

```
backend/
  app/
    core/       # settings (.env driven)
    db/         # SQLAlchemy engine/session/Base
    models/     # ORM models, one file per table
    schemas/    # Pydantic request/response models
    main.py     # FastAPI app entrypoint
  migrations/   # Alembic migrations
docs/           # planning + requirements documentation
```
