from __future__ import annotations

import argparse
import random
from datetime import date

from faker import Faker
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models import Department, Employee, Role
from scripts.data_generation import DEPARTMENTS, ROLES, SEED, faker
from scripts.source_profile import assignment_for, load_source_profile


def seed_departments(db: Session) -> tuple[dict[str, Department], int, int]:
    inserted = skipped = 0
    departments = {department.name: department for department in db.scalars(select(Department)).all()}
    for name in DEPARTMENTS:
        if name in departments:
            skipped += 1
            continue
        department = Department(name=name, description=f"{name} team")
        db.add(department)
        db.flush()
        departments[name] = department
        inserted += 1
    return departments, inserted, skipped


def seed_roles(db: Session) -> tuple[dict[str, Role], int, int]:
    inserted = skipped = 0
    roles = {role.name: role for role in db.scalars(select(Role)).all()}
    for name in ROLES:
        if name in roles:
            skipped += 1
            continue
        role = Role(name=name, description=f"{name} role")
        db.add(role)
        db.flush()
        roles[name] = role
        inserted += 1
    return roles, inserted, skipped


def seed_employees(
    db: Session,
    departments: dict[str, Department],
    roles: dict[str, Role],
    count: int,
    profile: dict | None = None,
) -> tuple[int, int]:
    fake = faker()
    profile = profile or load_source_profile()
    profile_rng = random.Random(SEED)
    inserted = skipped = 0
    existing_codes = {code for (code,) in db.execute(select(Employee.employee_code)).all()}
    managers: list[Employee] = []
    department_list = list(departments.values())
    role_list = list(roles.values())

    for index in range(1, count + 1):
        code = f"GM-{index:04d}"
        if code in existing_codes:
            skipped += 1
            existing = db.scalar(select(Employee).where(Employee.employee_code == code))
            if existing and index <= 30:
                managers.append(existing)
            continue

        first = fake.unique.first_name()
        last = fake.unique.last_name()
        assignment = assignment_for(profile, index, profile_rng)
        if assignment:
            department = departments[assignment[0]]
            role = roles[assignment[1]]
        else:
            department = department_list[index % len(department_list)]
            role = role_list[index % len(role_list)]
        manager = managers[index % len(managers)] if managers and index > 30 else None
        employee = Employee(
            employee_code=code,
            first_name=first,
            last_name=last,
            work_email=f"{first.lower()}.{last.lower()}.{index:04d}@example.com",
            phone=fake.phone_number()[:30],
            joining_date=fake.date_between(start_date=date(2018, 1, 1), end_date=date(2026, 10, 1)),
            department=department,
            role=role,
            manager=manager,
        )
        db.add(employee)
        db.flush()
        existing_codes.add(code)
        inserted += 1
        if index <= 30:
            managers.append(employee)
    return inserted, skipped


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed deterministic synthetic GrowMar data.")
    parser.add_argument("--employees", type=int, default=300, help="Number of deterministic employees to ensure.")
    args = parser.parse_args()
    if args.employees < 1:
        parser.error("--employees must be at least 1")

    Faker.seed(SEED)
    with SessionLocal() as db:
        try:
            departments, dep_inserted, dep_skipped = seed_departments(db)
            roles, role_inserted, role_skipped = seed_roles(db)
            emp_inserted, emp_skipped = seed_employees(db, departments, roles, args.employees)
            db.commit()
        except Exception:
            db.rollback()
            raise

    print(f"Departments inserted={dep_inserted} skipped={dep_skipped}")
    print(f"Roles inserted={role_inserted} skipped={role_skipped}")
    print(f"Employees inserted={emp_inserted} skipped={emp_skipped}")
    from scripts.export_csv import export_csv

    export_csv()


if __name__ == "__main__":
    main()
