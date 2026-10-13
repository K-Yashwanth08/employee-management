# Employee Management API Contract

Draft contract for Phase 1. Base URL locally: `http://localhost:8000`.

## Common Rules

Paginated responses:

```json
{"items": [], "total": 0, "page": 1, "size": 20, "total_pages": 0}
```

Error responses:

```json
{"error": {"code": "404", "message": "Employee not found"}}
```

Validation failures use HTTP 422. Duplicate employee codes, emails, department names, and role names use HTTP 409. Soft-deleted inactive records are excluded by default.

## Health

`GET /health`

Purpose: readiness smoke test.

Success `200`:

```json
{"status": "ok"}
```

## Departments

`POST /departments`

Body: `name` required, `description` optional.

Success `201` returns a department.

`GET /departments?page=1&size=20`

Lists active departments with pagination.

`GET /departments/{department_id}`

Returns one active department or 404.

`GET /departments/{department_id}/employees?page=1&size=20`

Lists active employees in the department.

## Roles

`POST /roles`

Body: `name` required, `description` optional.

`GET /roles?page=1&size=20`

Lists active roles.

`GET /roles/{role_id}`

Returns one active role or 404.

## Employees

`POST /employees`

Body:

```json
{
  "employee_code": "GM-0001",
  "first_name": "Avery",
  "last_name": "Morgan",
  "work_email": "avery.morgan@example.com",
  "phone": "+1-555-0101",
  "joining_date": "2024-01-15",
  "department_id": 1,
  "role_id": 1,
  "manager_id": null
}
```

Success `201` returns the employee with nested `department`, `role`, and optional `manager` summaries.

`GET /employees?page=1&size=20&department=Engineering&q=John`

Lists active employees. `department` accepts either a department ID or exact department name. `q` searches first and last names case-insensitively. Maximum page size is 100.

`GET /employees/{employee_id}`

Returns one active employee or 404.

`PATCH /employees/{employee_id}`

Partial update. Omitted fields are left unchanged. Explicit JSON `null` clears nullable fields such as `phone` and `manager_id`.

`DELETE /employees/{employee_id}`

Soft deletes by setting `is_active=false`. Success response is `204 No Content`.

`GET /employees/{employee_id}/team`

Returns active direct reports for the employee.

## Sample Dataset

The 10-record early handoff dataset is stored at `data/sample_employees.json`. All names, identifiers, phone numbers, and emails are synthetic and use `example.com`.
