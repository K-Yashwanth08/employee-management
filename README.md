# GrowMar Employee Management System

Phase 1 is a FastAPI backend for departments, roles, and employees. It uses SQLAlchemy 2.x models, Alembic migrations, PostgreSQL for app runtime, pytest for tests, Faker for deterministic synthetic data, and pandas for CSV exports.

## Features

- `GET /health` returns `{"status":"ok"}`.
- Employee create, list, retrieve, update, soft delete, and direct reports.
- Department and role create/list/retrieve endpoints.
- Pagination, department filtering, and name search.
- Environment-based settings with `pydantic-settings`.
- Alembic migration for departments, roles, employees, constraints, indexes, and relationships.
- Deterministic seed data and linked CSV exports for employees, salaries, and attendance.

## Structure

`app/api/routes` handles HTTP. `app/services` contains business rules. `app/repositories` contains database queries. `app/models` contains ORM tables. `app/schemas` contains Pydantic request/response models. `scripts` contains seed/export commands. `docs` contains the draft API contract and ER diagram.

## Windows PowerShell Setup

```powershell
cd D:\employee-management
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and replace placeholder passwords/secrets. Do not commit `.env`. Keep `POSTGRES_PASSWORD` synchronized with the password in `DATABASE_URL`; URL-encode reserved characters in the URL password.

For local non-Docker PostgreSQL, set `DATABASE_URL` to your local host, for example:

```powershell
$env:DATABASE_URL="postgresql+psycopg://postgres:your-password@localhost:5432/employees"
```

## Docker

Install Docker Desktop, then run:

```powershell
docker compose up --build -d
```

The API is exposed at `http://localhost:8000`, and Swagger UI is at `http://localhost:8000/docs`. Inside Docker the API connects to PostgreSQL through hostname `db`; do not use `localhost` in the container database URL. The API container applies Alembic migrations before starting Uvicorn. Wait for both services to report healthy with `docker compose ps`.

## Local interface

After installing the requirements, start the API and dashboard from PowerShell:

```powershell
.\scripts\run_local.ps1
```

When `DATABASE_URL` is not already set in the shell, the script uses the local `local_exec.db` SQLite file and applies migrations before starting the server. Open `http://127.0.0.1:8000` for the employee dashboard or `http://127.0.0.1:8000/docs` for the API documentation. Set `DATABASE_URL` in the shell first if you want to use another database.

## Migrations

```powershell
# Local PostgreSQL only; for Docker Compose, migrations run during API startup.
alembic upgrade head
alembic downgrade -1
```

Alembic loads `DATABASE_URL` through application settings. Production startup should use migrations, not `Base.metadata.create_all()`.

## Tests

```powershell
pytest
```

Tests use isolated SQLite databases so they do not modify development data. PostgreSQL migration checks still require a running PostgreSQL database.

## Seed and Export

```powershell
python -m scripts.seed
python -m scripts.export_csv
```

`python -m scripts.seed` creates departments, roles, and 300 deterministic Faker employees, then writes all three CSV exports. It skips existing employee codes, so repeat runs do not create duplicate employees. Salaries and three months of attendance are generated deterministically and carry both `employee_id` and `employee_code` references. Exports are written to `data/exports/` and are ignored by Git. Docker startup applies migrations; seed inside the container with `docker compose exec api python -m scripts.seed`. To keep generated exports on Windows, run seeding locally only after setting a host-reachable `DATABASE_URL`, or add a bind mount for the export directory.

### Kaggle source data

The optional local profile source is [Human Resources Data Set by Rich Huebner and Carla Patalano](https://www.kaggle.com/datasets/rhuebner/human-resources-data-set), specifically `HRDataset_v14.csv`. Download it from Kaggle and place it at `data/HRDataset_v14.csv` to use its department, position, and salary distributions. The pipeline loads only those three columns, trims category values, drops rows with missing profile fields, and maps the source categories onto GrowMar departments and roles. Faker creates all employee names, emails, phone numbers, and join dates; source names, IDs, and other personal attributes are never loaded.

The v14 author’s license note is **CC BY-NC-ND 4.0** and permits learning or teaching use. Do not commit or redistribute the source file or any adapted copy; the source CSV path is Git-ignored. Keep use of source-informed synthetic output within the permitted noncommercial educational scope. Without the optional CSV, the seed command works using fixed synthetic defaults.

## Database Design

See `docs/er-diagram.md`. Phase 1 gives each employee one department and one primary role. This keeps the first release simple and matches the current employee profile requirement. If GrowMar later needs multiple simultaneous roles, add an employee-role join table with a new Alembic migration.

Soft deletion uses `is_active=false`; list and get endpoints exclude inactive records by default.

## Dataset Notes

The master dataset is generated with Faker and a fixed seed. No source employee names, emails, phone numbers, or identifiers are copied. See [Kaggle source data](#kaggle-source-data) for attribution and license limits.

## Security

Secrets belong in `.env` or deployment secret storage, not source code. Error responses use a consistent wrapper and do not expose stack traces, SQL, or credentials.

## Troubleshooting

- Docker DB not ready: `docker compose ps` and check the `db` health status.
- Connection refused locally: confirm `DATABASE_URL` uses `localhost` outside Docker and `db` inside Docker.
- Migration import errors: activate `.venv` and run commands from `D:\employee-management`.
- PowerShell execution policy: if activation is blocked, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

## Clone and Run Checklist

```powershell
git clone <repo-url>
cd employee-management
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
docker compose up --build -d
docker compose ps
docker compose exec api python -m scripts.seed
pytest
```
