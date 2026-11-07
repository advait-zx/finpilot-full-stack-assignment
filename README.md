# FinPilot

FinPilot is a synthetic investment portfolio and financial-goal monitoring application built for the PINSEC full-stack coding assignment.

## Stack

- Frontend: React + TypeScript + Vite + Recharts
- Backend: FastAPI + SQLAlchemy + Pydantic
- Database: PostgreSQL
- Migrations: Alembic
- Authentication: seeded local users + JWT bearer token
- Local orchestration: Docker Compose
- CI: GitHub Actions

## Reviewer flow

1. Sign in.
2. Search for a customer by ID, name, email or city.
3. Open the customer dashboard and review risk profile, accounts, AUM, asset allocation, positions and goals.
4. Open the transaction page and use server-side date, account, instrument and type filters with pagination.
5. Create or edit a financial goal and observe validation/funded percentage.
6. Sign in as ADMIN and import a transaction CSV. Invalid rows are returned with row-level rejection reasons.

## Demo credentials

Local synthetic credentials only:

- VIEWER: `viewer` / `viewer123`
- ADMIN: `admin` / `admin123`

Production would use an identity provider or secure server-side session and secrets would be managed outside the repository.

## Local setup

Requirements:

- Docker Desktop / Docker Engine with Compose

From the repository root:

```bash
cp .env.example .env
docker compose up --build
```

Services:

- Frontend: http://localhost:5173
- API: http://localhost:8000/api/v1
- Swagger: http://localhost:8000/docs
- Health: http://localhost:8000/health
- PostgreSQL: localhost:5432

The API container applies Alembic migrations and then runs the idempotent bootstrap seed. Raw supplied CSV files are mounted read-only from `./data`.

To stop the stack:

```bash
docker compose down
```

To reset the local database completely:

```bash
docker compose down -v
docker compose up --build
```

## Backend without Docker

```bash
cd backend
python -m venv .venv
# activate the virtual environment
pip install -r requirements.txt
alembic upgrade head
python -m app.db.seed
uvicorn app.main:app --reload
```

Set `DATABASE_URL` to a reachable PostgreSQL database before running migrations.

## Frontend without Docker

```bash
cd frontend
npm install
npm run dev
```

By default the frontend calls `http://localhost:8000/api/v1`. Override it with `VITE_API_URL`.

## Tests

Backend:

```bash
cd backend
pytest -q
```

Frontend production build:

```bash
cd frontend
npm install
npm run build
```

## CSV data quality strategy

The raw source files are never edited. The transaction importer validates:

- required columns
- unique/idempotent transaction IDs
- account foreign keys
- instrument foreign keys
- transaction type and status enumerations
- date format and future dates
- non-negative quantity, price and amount

Rejected rows are stored in `import_rejects` and returned by the API. Valid rows are inserted in the same database transaction as the import batch metadata.

The supplied data contains deliberate issues including a duplicate transaction ID, an invalid instrument reference, a future transaction date, a negative fee amount and duplicate holding positions. The bootstrap seed keeps the raw inputs unchanged and prevents duplicate holdings through a database unique constraint plus loader-side duplicate detection.

## PostgreSQL design

Important query paths are indexed rather than indexing every column. Examples include:

- `accounts.customer_id`
- `transactions(account_id, trade_date)`
- `holdings_snapshot(account_id, snapshot_date)`
- search columns such as customer name/email/city

`portfolio_positions_v` centralises position market-value and unrealised-P/L calculation in PostgreSQL.

Reviewer SQL examples are in `docs/sql-demo.sql`, including top AUM customers, asset allocation, monthly net flow, distinct holders, underfunded high-priority goals and import exceptions.

## API surface

- `POST /api/v1/auth/login`
- `GET /api/v1/customers`
- `GET /api/v1/customers/{customer_id}`
- `GET /api/v1/customers/{customer_id}/portfolio`
- `GET /api/v1/customers/{customer_id}/transactions`
- `GET /api/v1/customers/{customer_id}/goals`
- `POST /api/v1/customers/{customer_id}/goals`
- `PATCH /api/v1/goals/{goal_id}`
- `POST /api/v1/admin/imports/transactions`
- `GET /health`

## Repository structure

```text
finpilot/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   └── services/
│   ├── alembic/
│   └── tests/
├── frontend/
│   └── src/
├── data/
├── docs/
├── .github/workflows/ci.yml
├── docker-compose.yml
├── DECISIONS.md
└── README.md
```

## CI

GitHub Actions runs on push and pull request.

Backend job:

1. install dependencies
2. Ruff lint
3. Pytest

Frontend job:

1. install dependencies
2. TypeScript/Vite production build

## Production-hardening notes

For a real deployment I would add OIDC/SSO, HTTP-only secure cookies or a server-managed session, managed PostgreSQL with backups/PITR, a secret manager, structured central logging, metrics/tracing, rate limiting, CSP/security headers, import file object storage, background import workers and vulnerability/dependency scanning.

See `DECISIONS.md` and `docs/architecture-report.md` for trade-offs and architecture detail.

## Windows quick start

```powershell
cd D:\finplot
Copy-Item .env.example .env
docker compose up -d --build
docker compose ps
```

Run the optional smoke test after all three services are `Up`:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\smoke_test.ps1
```

## Reviewer import demo

For the ADMIN import demonstration, use `data/transactions_import_demo.csv` rather than re-uploading the full bootstrap `transactions.csv`.

On the first upload the demo file is designed to produce both successful and rejected rows so the validation behavior is visible. Re-uploading it demonstrates duplicate/idempotency handling.

## Submission documents

- `docs/architecture-report.pdf` - mandatory architecture/design report
- `docs/architecture-report.docx` - editable report source
- `docs/reviewer-walkthrough.md` - recommended live demo order
- `docs/submission-checklist.md` - final pre-submission checks
- `docs/sql-demo.sql` - reviewer SQL and EXPLAIN example
