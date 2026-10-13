from __future__ import annotations

import random
from datetime import date, timedelta

from faker import Faker

DEPARTMENTS = [
    "Engineering",
    "People",
    "Sales",
    "Finance",
    "Marketing",
    "Operations",
]
ROLES = [
    "Software Engineer",
    "Engineering Manager",
    "HR Specialist",
    "Sales Executive",
    "Finance Analyst",
    "Marketing Associate",
    "Operations Coordinator",
]
SEED = 4217


def faker() -> Faker:
    fake = Faker("en_US")
    Faker.seed(SEED)
    random.seed(SEED)
    return fake


def salary_rows(
    employees: list[dict[str, int | str]], *, salary_low: int = 42_000, salary_high: int = 150_000
) -> list[dict[str, str | int]]:
    rng = random.Random(SEED)
    rows = []
    salary_low = max(30_000, salary_low)
    salary_high = max(salary_low + 500, salary_high)
    for employee in sorted(employees, key=lambda row: str(row["employee_code"])):
        base = rng.randrange(salary_low, salary_high, 500)
        rows.append(
            {
                "employee_id": employee["employee_id"],
                "employee_code": employee["employee_code"],
                "annual_salary": base,
                "currency": "USD",
                "effective_date": "2026-01-01",
            }
        )
    return rows


def attendance_rows(employees: list[dict[str, int | str]], *, months: int = 3) -> list[dict[str, str | int]]:
    rng = random.Random(SEED + 1)
    today = date(2026, 10, 1)
    first_month = date(today.year, today.month, 1)
    starts = []
    for offset in range(months):
        month = first_month - timedelta(days=offset * 31)
        starts.append(date(month.year, month.month, 1))

    rows = []
    for employee in sorted(employees, key=lambda row: str(row["employee_code"])):
        for month_start in sorted(starts):
            working_days = 21 + rng.randint(-1, 2)
            absent_days = rng.randint(0, 3)
            rows.append(
                {
                    "employee_id": employee["employee_id"],
                    "employee_code": employee["employee_code"],
                    "month": month_start.strftime("%Y-%m"),
                    "working_days": working_days,
                    "present_days": working_days - absent_days,
                    "absent_days": absent_days,
                }
            )
    return rows
