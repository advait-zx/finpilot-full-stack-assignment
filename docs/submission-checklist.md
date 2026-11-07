# FinPilot submission checklist

## Working application
- [ ] `docker compose up -d` starts db, api and frontend.
- [ ] `http://localhost:8000/health` reports API/database healthy.
- [ ] Viewer login works.
- [ ] Customer search/profile works.
- [ ] Portfolio totals/allocation/positions render.
- [ ] Transaction filters and pagination work.
- [ ] Goal create/edit works.
- [ ] Admin import works with `data/transactions_import_demo.csv`.

## Database / API
- [ ] Migrations work from a clean volume (`docker compose down -v`, then start).
- [ ] Swagger is reachable at `/docs`.
- [ ] `docs/sql-demo.sql` is reviewed and executable.
- [ ] Capture one real `EXPLAIN (ANALYZE, BUFFERS)` result for the interview/report appendix if desired.

## Repository
- [ ] Push to a private/public GitHub repository as requested by PINSEC.
- [ ] Do not commit `.env`, PostgreSQL data, `node_modules`, build output or secrets.
- [ ] Create several meaningful commits, not one giant final dump.
- [ ] Confirm GitHub Actions passes on the pushed repository.

## Deliverables
- [ ] README.md
- [ ] DECISIONS.md
- [ ] architecture report PDF/Word
- [ ] migrations
- [ ] tests
- [ ] CI workflow
- [ ] reviewer credentials and URLs
- [ ] repository URL shared with reviewer
