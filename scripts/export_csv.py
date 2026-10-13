from __future__ import annotations

from pathlib import Path

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.db.session import SessionLocal
from app.models import Employee
from scripts.data_generation import attendance_rows, salary_rows
from scripts.source_profile import load_source_profile

EXPORT_DIR = Path("data/exports")


def export_csv() -> None:
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    with SessionLocal() as db:
        employees = list(
            db.scalars(
                select(Employee)
                .options(joinedload(Employee.department), joinedload(Employee.role), joinedload(Employee.manager))
                .where(Employee.is_active.is_(True))
                .order_by(Employee.employee_code)
            ).all()
        )
    if not employees:
        print("No active employees found. CSV files were created with headers only.")

    employee_rows = [
        {
            "employee_id": employee.id,
            "employee_code": employee.employee_code,
            "first_name": employee.first_name,
            "last_name": employee.last_name,
            "work_email": employee.work_email,
            "phone": employee.phone,
            "joining_date": employee.joining_date.isoformat(),
            "department": employee.department.name,
            "role": employee.role.name,
            "manager_code": employee.manager.employee_code if employee.manager else "",
            "is_active": employee.is_active,
        }
        for employee in employees
    ]
    employee_keys = [
        {"employee_id": employee.id, "employee_code": employee.employee_code}
        for employee in employees
    ]
    profile = load_source_profile()

    pd.DataFrame(employee_rows).to_csv(EXPORT_DIR / "employees.csv", index=False, encoding="utf-8")
    pd.DataFrame(
        salary_rows(employee_keys, salary_low=profile["salary_low"], salary_high=profile["salary_high"])
    ).to_csv(EXPORT_DIR / "salaries.csv", index=False, encoding="utf-8")
    pd.DataFrame(attendance_rows(employee_keys)).to_csv(
        EXPORT_DIR / "attendance.csv", index=False, encoding="utf-8"
    )
    print(
        f"Exported employees={len(employee_rows)} salaries={len(employee_keys)} "
        f"attendance={len(employee_keys) * 3}"
    )


def main() -> None:
    export_csv()


if __name__ == "__main__":
    main()
