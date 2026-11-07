# FinPilot engineering decisions

## Stack

FastAPI + SQLAlchemy + PostgreSQL were selected for explicit validation, readable API contracts and SQL visibility. React + TypeScript + Vite provides a small client surface without a server-rendering layer that the current internal dashboard does not need.

## Authentication

The assignment uses seeded local reviewer users and short-lived JWT bearer tokens. The browser keeps the token in `sessionStorage` only. This keeps the local assessment simple, but production should prefer a secure, HTTP-only, SameSite cookie or a corporate identity provider with OIDC. The JWT secret must come from a secret manager in production.

## Data quality

Raw CSV files are never modified. Invalid rows are rejected with row-level reasons. Transaction IDs are idempotency keys. Invalid foreign keys, future dates, negative numeric values and duplicate IDs are rejected. Duplicate holdings are skipped during bootstrap because the final table has a unique `(account_id, instrument_id, snapshot_date)` constraint.

The deliberate negative FEE row is rejected under the chosen rule that imported `amount` is non-negative gross/cash magnitude and transaction direction is represented by transaction type. If a real source system defines fees as signed cash flows, this rule would be changed after agreeing the source contract.

## Database

Aggregation happens in PostgreSQL through joins and the `portfolio_positions_v` view instead of loading all rows into the browser. Composite indexes focus on transaction account/date filtering and holding account/snapshot access.

## Scope deliberately deferred

* Enterprise SSO / refresh-token rotation
* Background job queue for very large imports
* Object storage for uploaded source files
* Full audit-event model
* Frontend automated component tests
* Production monitoring stack
* TLS/reverse proxy for localhost

These are production-hardening steps rather than requirements for the supplied synthetic dataset.
