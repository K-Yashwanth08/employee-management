# Employee Management Phase 1 ER Diagram

```mermaid
erDiagram
    DEPARTMENT ||--o{ EMPLOYEE : has
    ROLE ||--o{ EMPLOYEE : assigned_as_primary_role
    EMPLOYEE ||--o{ EMPLOYEE : manages

    DEPARTMENT {
        int id PK
        string name UK
        string description
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    ROLE {
        int id PK
        string name UK
        string description
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    EMPLOYEE {
        int id PK
        string employee_code UK
        string first_name
        string last_name
        string work_email UK
        string phone
        date joining_date
        int department_id FK
        int role_id FK
        int manager_id FK
        boolean is_active
        datetime created_at
        datetime updated_at
    }
```

Phase 1 gives every employee one department and one primary role. If the organization later needs multiple simultaneous roles, add an employee-role join table in a new migration.
