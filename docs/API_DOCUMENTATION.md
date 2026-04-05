# Finance Dashboard API Documentation

This document describes the REST API for the Finance Dashboard backend.

Base URL (local): `http://127.0.0.1:8000`
API prefix: `/api/v1`

Interactive docs when running locally:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Authentication

### Login
`POST /api/v1/auth/login`

Request:
```json
{
  "email": "admin@example.com",
  "password": "admin123"
}
```

Success response `200`:
```json
{
  "access_token": "<JWT>",
  "token_type": "bearer",
  "expires_in_seconds": 3600
}
```

Use token in header:
`Authorization: Bearer <JWT>`

## Roles and Access Matrix

| Action | viewer | analyst | admin |
|---|---|---|---|
| Login | Yes | Yes | Yes |
| Read records list/detail | Yes | Yes | Yes |
| Read dashboard summary | Yes | Yes | Yes |
| Create/Update/Delete records | No | No | Yes |
| User management endpoints | No | No | Yes |

Inactive users are denied protected endpoints even with valid JWT.

## Error Format

All handled errors follow:
```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": null
  }
}
```

Common HTTP statuses:
- `400` bad request
- `401` unauthorized
- `403` forbidden
- `404` not found
- `409` conflict
- `422` validation error

## Endpoints

### Health

#### `GET /health`
Public health check.

Response `200`:
```json
{
  "status": "ok"
}
```

### Users (Admin only)

#### `POST /api/v1/users`
Create a user.

Request:
```json
{
  "name": "Ops User",
  "email": "ops@example.com",
  "password": "ops123",
  "role": "viewer",
  "status": "active"
}
```

Response `201`: created user object.

#### `GET /api/v1/users`
List users.

Response `200`: array of users.

#### `GET /api/v1/users/{user_id}`
Get one user.

Response `200`: user object.

#### `PATCH /api/v1/users/{user_id}`
Partial update (`name`, `email`, `role`, `status`).

Example request:
```json
{
  "name": "Viewer Updated",
  "status": "inactive"
}
```

Response `200`: updated user.

### Financial Records

#### `POST /api/v1/records` (Admin)
Create a financial record.

Request:
```json
{
  "amount": "499.99",
  "type": "expense",
  "category": "tools",
  "date": "2026-04-05",
  "notes": "license"
}
```

Response `201`: created record.

#### `GET /api/v1/records` (Viewer/Analyst/Admin)
List records with filters and pagination.

Query params:
- `type` = `income|expense`
- `category` = string
- `start_date` = `YYYY-MM-DD`
- `end_date` = `YYYY-MM-DD`
- `created_by` = user id
- `limit` = `1..100` (default 20)
- `offset` = `>=0` (default 0)

Ordering is deterministic: `date desc, id desc`.

Response `200`:
```json
{
  "items": [],
  "limit": 20,
  "offset": 0,
  "total": 0
}
```

#### `GET /api/v1/records/{record_id}` (Viewer/Analyst/Admin)
Get record detail.

#### `PATCH /api/v1/records/{record_id}` (Admin)
Update record fields.

Example request:
```json
{
  "notes": "updated",
  "amount": "510.00"
}
```

#### `DELETE /api/v1/records/{record_id}` (Admin)
Hard delete record.

Response `204`: no content.

### Dashboard

#### `GET /api/v1/dashboard/summary` (Viewer/Analyst/Admin)
Returns aggregated dashboard data.

Response `200` shape:
```json
{
  "total_income": "0.00",
  "total_expenses": "0.00",
  "net_balance": "0.00",
  "category_wise_totals": [
    {
      "type": "income",
      "category": "salary",
      "total": "1000.00"
    }
  ],
  "recent_activity": [],
  "monthly_trends": [
    {
      "month": "2026-04-01",
      "income": "1000.00",
      "expense": "500.00",
      "net": "500.00"
    }
  ]
}
```

## Validation Rules

- `amount` must be greater than 0.
- Enum fields must be valid values.
- Required strings must be non-empty after trimming.
- `end_date >= start_date`.
- `limit <= 100` and `offset >= 0`.
- Email must be valid format.

## Seeded Test Users

- `admin@example.com / admin123`
- `viewer@example.com / viewer123`
- `analyst@example.com / analyst123`
- `inactive@example.com / inactive123`

## Quick cURL Examples

Login:
```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}'
```

Read records:
```bash
curl "http://127.0.0.1:8000/api/v1/records?type=expense&limit=10" \
  -H "Authorization: Bearer <TOKEN>"
```

Dashboard summary:
```bash
curl http://127.0.0.1:8000/api/v1/dashboard/summary \
  -H "Authorization: Bearer <TOKEN>"
```
