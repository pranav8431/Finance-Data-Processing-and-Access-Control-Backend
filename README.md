# Finance Dashboard Backend

Complete backend assignment for a finance dashboard with role-based access control, transactional business logic, analytics queries, migration-based schema management, and automated tests.

This project includes:
- REST API built with FastAPI
- SQLite persistence through SQLAlchemy 2.x
- Alembic migration for initial schema
- JWT authentication + centralized RBAC enforcement
- Dashboard analytics endpoint with Decimal-safe calculations
- Pytest suite validating auth, RBAC, filters, pagination, and analytics
- Browser-based frontend test harness at `/ui/`

## API Documentation Link
- Repository API docs file: `docs/API_DOCUMENTATION.md`
- Local interactive docs (when server is running):
  - Swagger UI: `http://127.0.0.1:8000/docs`
  - ReDoc: `http://127.0.0.1:8000/redoc`

## 1) Tech Stack and Why
- Python 3.11+ (tested on Python 3.13 in this environment)
- FastAPI for fast API development with strong request validation
- SQLAlchemy 2.x for clean ORM modeling and composable query logic
- SQLite for portable local development and assignment execution
- Alembic for schema versioning without runtime `create_all` in production path
- Pydantic v2 for explicit API contracts and validation
- Pytest + TestClient for reliable behavior verification

## 2) Project Structure and Responsibilities
```text
app/
  main.py                  # FastAPI app bootstrap, exception handlers, route/static mounting
  core/
    config.py              # Settings from env
    security.py            # JWT + password hashing helpers
    exceptions.py          # Domain/application exceptions
    logging.py             # Logging configuration
  db/
    session.py             # SQLAlchemy engine/session/base
    base.py                # Model imports for metadata
  models/
    user.py                # User ORM model + enums
    financial_record.py    # FinancialRecord ORM model + enum
  schemas/
    auth.py                # Login request/response schemas
    user.py                # User CRUD schemas
    record.py              # Record CRUD/filter/pagination schemas
    dashboard.py           # Dashboard response schemas
  services/
    auth_service.py        # Login business logic
    user_service.py        # User management logic
    record_service.py      # Record CRUD/filter logic
    dashboard_service.py   # Aggregations, trends, recent activity
  api/
    deps.py                # Centralized auth, active-user, role checks
    router.py              # Route composition
    routes/
      auth.py
      users.py
      records.py
      dashboard.py
  static/
    index.html             # Overview page
    auth.html              # Authentication page
    users.html             # User-management page
    records.html           # Records page
    dashboard.html         # Dashboard page
    styles.css             # Shared UI styles
    core.js                # Shared API/session client utilities
    overview.js            # Overview page logic
    auth.js                # Auth page logic
    users.js               # Users page logic
    records.js             # Records page logic
    dashboard.js           # Dashboard page logic
alembic/
  env.py
  versions/0001_initial_schema.py
scripts/
  seed.py
tests/
  conftest.py
  test_auth.py
  test_rbac.py
  test_inactive.py
  test_records.py
  test_dashboard.py
```

Design principle: route handlers are intentionally thin; business behavior lives in services; auth and RBAC checks are centralized in dependencies.

## 3) Data Model

### User
- `id` integer primary key
- `name` non-empty string
- `email` unique, indexed, normalized to lowercase
- `role` enum: `viewer | analyst | admin`
- `status` enum: `active | inactive`
- `password_hash` string
- `created_at`, `updated_at`

### FinancialRecord
- `id` integer primary key
- `amount` `Numeric(14,2)` (Decimal-safe, no float)
- `type` enum: `income | expense`
- `category` indexed string
- `date` indexed date
- `notes` nullable text
- `created_by` indexed FK -> `users.id`
- `created_at`, `updated_at`

Indexes and constraints are created in `alembic/versions/0001_initial_schema.py`.

## 4) Authentication and Authorization

### Login
- Endpoint: `POST /api/v1/auth/login`
- Input: `email`, `password`
- Output: bearer token + expiry metadata

### JWT details
- Algorithm: `HS256`
- Claims include `sub` (user id), `role`, `status`, and expiry
- Security tradeoff: token includes role/status, but authorization still loads user from DB on each request to enforce latest status/role updates and prevent stale permissions.

### Centralized enforcement (`app/api/deps.py`)
- `get_current_user`: validates token and resolves user
- `require_active_user`: blocks inactive users
- `require_roles(...)`: enforces route role policy

### RBAC matrix
| Capability | Viewer | Analyst | Admin |
|---|---|---|---|
| Login | Yes | Yes | Yes |
| Read records list/detail | Yes | Yes | Yes |
| Read dashboard summary | Yes | Yes | Yes |
| Create/update/delete records | No | No | Yes |
| User management endpoints | No | No | Yes |

## 5) API Endpoints
| Method | Path | Auth | Roles | Purpose |
|---|---|---|---|---|
| GET | `/health` | No | Public | Service health check |
| POST | `/api/v1/auth/login` | No | Public | Authenticate and get JWT |
| POST | `/api/v1/users` | Yes | Admin | Create user |
| GET | `/api/v1/users` | Yes | Admin | List users |
| GET | `/api/v1/users/{user_id}` | Yes | Admin | Get user by id |
| PATCH | `/api/v1/users/{user_id}` | Yes | Admin | Update name/email/role/status |
| POST | `/api/v1/records` | Yes | Admin | Create financial record |
| GET | `/api/v1/records` | Yes | Viewer/Analyst/Admin | List records with filters + pagination |
| GET | `/api/v1/records/{record_id}` | Yes | Viewer/Analyst/Admin | Get record detail |
| PATCH | `/api/v1/records/{record_id}` | Yes | Admin | Update record |
| DELETE | `/api/v1/records/{record_id}` | Yes | Admin | Hard delete record |
| GET | `/api/v1/dashboard/summary` | Yes | Viewer/Analyst/Admin | Summary analytics |
| GET | `/ui/` | No | Public | Frontend tester for all API functions |

## 6) Validation and Error Contract

Validation implemented via Pydantic schemas:
- `amount > 0`
- strict enums for role/status/type
- non-empty trimmed string fields
- valid email format
- `end_date >= start_date` for record filters
- pagination bounds: `limit` in `1..100`, `offset >= 0`

Error response envelope (consistent):
```json
{
  "error": {
    "code": "...",
    "message": "...",
    "details": null
  }
}
```

Status codes used:
- `400` bad request
- `401` unauthorized
- `403` forbidden
- `404` not found
- `409` conflict
- `422` validation error

Global exception handlers are defined in `app/main.py`.

## 7) Dashboard Summary Behavior
`GET /api/v1/dashboard/summary` returns:
- `total_income`
- `total_expenses`
- `net_balance`
- `category_wise_totals` grouped by `type + category`
- `recent_activity` (latest 5 records by `date desc, id desc`)
- `monthly_trends` (last 6 months with income/expense/net per month)

All arithmetic is Decimal-safe.

## 8) Setup and Run

### Requirements
- Python 3.11+ and `pip`

If `python3.11` is unavailable locally, use any installed Python 3.11+ (example: `python3.13`).

### Local setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
python scripts/seed.py
uvicorn app.main:app --reload
```

API base URL: `http://127.0.0.1:8000`

Frontend tester: `http://127.0.0.1:8000/ui/`

## 9) Seeded Credentials
- `admin@example.com / admin123`
- `viewer@example.com / viewer123`
- `analyst@example.com / analyst123`
- `inactive@example.com / inactive123`

## 10) Frontend Test Harness (`/ui/`)
The built-in frontend now uses a multi-page operations-console layout:
- `/ui/` overview page (health and shared session settings)
- `/ui/auth.html` authentication/session page
- `/ui/users.html` user-management page
- `/ui/records.html` records CRUD + filter page
- `/ui/dashboard.html` dashboard insights page

Shared session behavior:
- Base URL and bearer token are persisted in browser local storage and reused across pages.
- Session panel shows decoded token context (`sub`, `role`, `status`) for quick validation.
- Every page includes a response console to inspect status codes and response payloads.

This is intended for fast evaluator demos and QA verification.

## 11) Testing
Run:
```bash
pytest -q
```

Covered scenarios:
- Auth: login success/failure, protected endpoint without token
- RBAC: viewer/analyst denied writes, admin allowed writes, non-admin denied user-management
- Inactive user blocked from protected routes
- Records: filters by type/category/date, pagination, deterministic ordering
- Dashboard: totals/net correctness and monthly trend values

## 12) Example cURL Commands

Login:
```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}'
```

List records with filters:
```bash
curl "http://127.0.0.1:8000/api/v1/records?type=expense&category=rent&start_date=2026-01-01&end_date=2026-12-31&limit=10&offset=0" \
  -H "Authorization: Bearer <TOKEN>"
```

Create record (admin only):
```bash
curl -X POST http://127.0.0.1:8000/api/v1/records \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"amount":"499.99","type":"expense","category":"tools","date":"2026-04-05","notes":"license"}'
```

Dashboard summary:
```bash
curl http://127.0.0.1:8000/api/v1/dashboard/summary \
  -H "Authorization: Bearer <TOKEN>"
```

Create user (admin only):
```bash
curl -X POST http://127.0.0.1:8000/api/v1/users \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Ops","email":"ops@example.com","role":"viewer","status":"active","password":"ops123"}'
```

Update user (admin only):
```bash
curl -X PATCH http://127.0.0.1:8000/api/v1/users/2 \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Viewer Renamed","status":"inactive"}'
```

## 13) Configuration
`.env.example` contains:
- `APP_NAME`
- `ENVIRONMENT`
- `DEBUG`
- `API_V1_PREFIX`
- `DATABASE_URL`
- `JWT_SECRET_KEY`
- `JWT_ALGORITHM`
- `ACCESS_TOKEN_EXPIRE_MINUTES`

Always set a strong `JWT_SECRET_KEY` outside local demo usage.

## 14) Assumptions and Tradeoffs
- Password auth is intentionally minimal for assignment scope; no password reset/MFA/lockout.
- Hard delete is used for records to keep behavior explicit and simple.
- SQLite is used for portability; production should move to PostgreSQL.
- Authorization resolves current user from DB each request for up-to-date status/role enforcement.

## 15) Known Limitations and Next Improvements
- Refresh tokens and token revocation/blacklist
- Login rate limiting and brute-force protections
- Audit trail for admin actions
- Better observability (structured logs, tracing)
- Additional edge-case tests for malformed/forged token variants

## 16) Troubleshooting
- Port already in use:
  - Run server on a different port: `uvicorn app.main:app --reload --port 8001`
- `python3.11` not found:
  - Use any available Python 3.11+ executable (for example `python3.13`)
- Migration errors after schema changes:
  - Ensure you run `alembic upgrade head` after pulling changes
- Import errors in tests:
  - Run tests from project root and keep `pytest.ini` unchanged
