# FinPilot Architecture Report

## 1. Executive overview

FinPilot is an internal read-heavy wealth-operations dashboard. The application consolidates customer identity, accounts, investment holdings, transactions, risk profiles and financial goals. The implementation prioritises database integrity, traceable imports and a small set of understandable service boundaries over unnecessary distributed-system complexity.

Chosen stack: React/TypeScript/Vite for the browser, FastAPI/SQLAlchemy for the API, PostgreSQL for persistence, Alembic for migrations and Docker Compose for reproducible local startup.

## 2. System context

```mermaid
flowchart LR
    U[Viewer / Admin] --> F[React frontend\nlocalhost:5173]
    F -->|JWT + REST| A[FastAPI API\nlocalhost:8000]
    A --> P[(PostgreSQL\nlocalhost:5432)]
    AD[Admin CSV] --> F
    F --> A
    A --> R[Import validation\nand rejection log]
    R --> P
```

No external market-data or identity provider is required for the synthetic assessment.

## 3. Component architecture

```mermaid
flowchart TB
    UI[React pages/components] --> C[API client]
    C --> ROUTES[FastAPI route layer]
    ROUTES --> SERVICES[Business/import services]
    ROUTES --> ORM[SQLAlchemy query layer]
    SERVICES --> ORM
    ORM --> DB[(PostgreSQL)]
    DB --> VIEW[portfolio_positions_v]
```

Frontend pages are separated by user task: login, customer search, customer overview, transactions and admin import. Backend routes own HTTP contracts while import rules live in a separate service so they can be unit tested without HTTP.

## 4. ERD / data model

```mermaid
erDiagram
    CUSTOMER ||--o{ ACCOUNT : owns
    CUSTOMER ||--o{ GOAL : has
    CUSTOMER ||--o{ RISK_PROFILE : assessed_by
    ACCOUNT ||--o{ HOLDING_SNAPSHOT : contains
    ACCOUNT ||--o{ TRANSACTION : records
    INSTRUMENT ||--o{ HOLDING_SNAPSHOT : valued_by
    INSTRUMENT ||--o{ TRANSACTION : references
    IMPORT_BATCH ||--o{ IMPORT_REJECT : contains
```

Key integrity controls include primary keys on source identifiers, foreign keys, transaction/goal enumeration checks, non-negative numeric checks and a unique holding key on `(account_id, instrument_id, snapshot_date)`.

## 5. API design

The API is versioned under `/api/v1`. Protected routes require a bearer token. ADMIN-only routes use role-based dependency checks.

Read endpoints use backend filtering and pagination. Error responses use HTTP status codes and concise `detail` messages. FastAPI publishes OpenAPI automatically at `/docs`.

## 6. Key workflows

### Login

```mermaid
sequenceDiagram
    participant B as Browser
    participant A as API
    participant D as PostgreSQL
    B->>A: POST /auth/login
    A->>D: find user
    D-->>A: password hash + role
    A-->>B: short-lived JWT
```

### Customer portfolio read

```mermaid
sequenceDiagram
    participant B as Browser
    participant A as API
    participant D as PostgreSQL
    B->>A: GET /customers/{id}/portfolio
    A->>D: query portfolio_positions_v
    D-->>A: valued positions
    A->>A: group totals/allocation
    A-->>B: totals + allocation + positions
```

### Goal update

```mermaid
sequenceDiagram
    participant B as Browser
    participant A as API
    participant D as PostgreSQL
    B->>A: PATCH /goals/{id}
    A->>A: Pydantic validation
    A->>D: UPDATE within transaction
    D-->>A: updated row
    A-->>B: goal + funded percentage
```

### CSV import

```mermaid
flowchart TD
    F[Upload CSV] --> H{Required headers?}
    H -->|No| X[Reject file]
    H -->|Yes| V[Validate each row]
    V --> K{FK/enums/date/numeric/duplicate valid?}
    K -->|No| Q[Store ImportReject reason]
    K -->|Yes| I[Insert transaction]
    Q --> S[Commit batch summary]
    I --> S
```

### CI

```mermaid
flowchart LR
    G[Push / PR] --> B[Backend job]
    G --> F[Frontend job]
    B --> L[Ruff]
    L --> T[Pytest]
    F --> N[npm install]
    N --> V[Vite/TypeScript build]
```

## 7. Deployment topology

Docker Compose runs three services: PostgreSQL, FastAPI and the React/Vite frontend. The API waits for PostgreSQL health, applies migrations, seeds the synthetic dataset and then starts Uvicorn.

Production mapping would replace local PostgreSQL with a managed HA database, run API/frontend behind a TLS reverse proxy or ingress and move secrets to a secret manager.

## 8. Security

The local assessment uses seeded users and short-lived JWTs. Passwords are hashed. ADMIN operations are authorised server-side. ORM/parameterised SQL protects normal query paths from SQL injection. CSV writes are validated before insertion. CORS is explicitly configured.

The local browser stores JWTs in sessionStorage for simplicity. A production version should prefer corporate OIDC plus secure HTTP-only SameSite cookies or another server-managed session design. PII must be minimised in logs and source datasets should be encrypted at rest and in transit.

## 9. Reliability and operations

`/health` supports local readiness checks. API requests receive correlation IDs and searchable request logs. Import batches preserve accepted/rejected counts and row-level rejection reasons.

Production PostgreSQL would use connection pooling, automated backups and point-in-time recovery. Migrations would be tested in CI/staging and applied as a controlled deployment step with rollback/forward-fix procedures.

## 10. Trade-offs and roadmap

The design stays deliberately monolithic because the supplied dataset is small and the domain does not justify microservices. Synchronous SQLAlchemy keeps the code easy to explain in a live review. At larger scale the import flow should move to object storage plus a background worker and portfolio reads could add caching/materialised views where measurements justify them.

Deferred items include enterprise SSO, refresh-token/session rotation, frontend component tests, full audit events, central metrics/tracing, rate limiting and automated security scanning.
