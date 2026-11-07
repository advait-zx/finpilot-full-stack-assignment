# FinPilot reviewer walkthrough

## 1. Start the stack

```powershell
cd D:\finplot
docker compose up -d
docker compose ps
```

Expected services: `db`, `api`, `frontend` all `Up`.

URLs:
- Frontend: http://localhost:5173
- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## 2. Viewer flow

Use `viewer / viewer123`.

1. Search customers by name, ID, email or city.
2. Open a customer and explain KYC, segment, risk profile and account list.
3. Show total market value, account totals, asset allocation and positions.
4. Point out `price_as_of` and `snapshot_date` freshness fields.
5. Open transactions, apply account/instrument/type/date filters and page through results.
6. Open goals, create a goal, edit it and explain funded percentage and overdue/inconsistent flags.

## 3. Admin import flow

Use `admin / admin123`.

Upload `data/transactions_import_demo.csv`.

Expected outcome on the first run:
- 2 valid rows imported.
- 4 rows rejected: invalid instrument reference, future date, negative amount and duplicate ID within the file.

A second upload should demonstrate idempotency because the previously imported IDs are rejected as duplicates.

## 4. SQL / database discussion

Open `docs/sql-demo.sql` and be ready to explain:
- top customers by AUM
- asset allocation
- monthly net BUY/SELL flow
- instruments by distinct holders
- high-priority goals below 25% funded
- import/data-quality exceptions
- the `EXPLAIN (ANALYZE, BUFFERS)` example

## 5. Architecture discussion

Use `docs/architecture-report.pdf`.

Explain why this is a modular monolith, why PostgreSQL performs aggregation, why the importer rejects bad rows rather than editing raw CSVs, and what would change for production.

## 6. CI / Git

After pushing to GitHub, show `.github/workflows/ci.yml` and one successful Actions run. Do not claim CI evidence until a real run succeeds.
