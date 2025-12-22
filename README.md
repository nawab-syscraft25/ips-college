# IPS Academy API

Lightweight FastAPI + SQLAlchemy app for IPS Academy (multi-college CMS).

**Project layout**
- `app/` — FastAPI app, core, api, models, schemas, services, utils.
- `app/models/` — canonical editable models (e.g. `app/models/college.py`).
- `app/schemas/` — schema re-exports and central import used by Alembic.
- `alembic/` — migration environment and versions.
- `.env` — environment variables (not committed).

**Prerequisites**
- Python 3.11+ (venv recommended)
- Virtualenv: `python -m venv .venv`
- DB: MySQL or PostgreSQL (connection configured via `DATABASE_URL` in `.env`)
- Install dependencies: `pip install -r requirements.txt`

Quick start

1. Activate virtualenv (Windows PowerShell):

```powershell
.venv\Scripts\Activate.ps1
```

2. Export `PYTHONPATH` when running scripts locally (or run from project root):

```powershell
$env:PYTHONPATH = "."
python app/tests/test_db.py
```

3. Run the app (development):

```powershell
uvicorn app.main:app --reload
```

Database migrations (Alembic)

- Alembic is configured to load models via `app/schemas/schema.py` which imports models from `app/models/`.
- To create an autogenerate migration after editing models (edit `app/models/*.py`):

```powershell
$env:PYTHONPATH = "."
alembic -c alembic.ini revision --autogenerate -m "describe changes"
```

- To apply migrations:

```powershell
$env:PYTHONPATH = "."
alembic -c alembic.ini upgrade head
```

Model workflow and where to edit

- Edit canonical models in `app/models/` (for example, `app/models/college.py`).
- `app/schemas/schema.py` imports `app.models.college.College` (and other models) so Alembic autogenerate sees changes.
- Avoid duplicating model classes across files — keep a single class per table.

Notes about the repository changes

- A compatibility shim `app/models/schema.py` re-exports `app/schemas/schema.py` to preserve older imports.
- `.gitignore` present at repo root; do not commit `.env`.
- Alembic config was adjusted so migrations can be generated; migration files live under `alembic/versions/` and should be tracked.

Testing

- A simple DB connectivity test is at `app/tests/test_db.py`.
- Run unit tests (if added) with `pytest`.

If you want me to also:
- Commit these changes (`git add . && git commit -m "chore: add README and migration setup"`).
- Create a sample migration for a model edit and apply it to a different DB (dry-run). 

Tell me which next step you'd like.