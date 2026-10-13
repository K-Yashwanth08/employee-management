from sqlalchemy import select

from app.models import Employee
from scripts.data_generation import attendance_rows, salary_rows
from scripts.seed import seed_departments, seed_employees, seed_roles
from scripts.source_profile import load_source_profile


def test_seed_repeat_runs_are_idempotent(db_session):
    departments, _, _ = seed_departments(db_session)
    roles, _, _ = seed_roles(db_session)
    inserted, skipped = seed_employees(db_session, departments, roles, 10)
    db_session.commit()

    departments, _, _ = seed_departments(db_session)
    roles, _, _ = seed_roles(db_session)
    inserted_again, skipped_again = seed_employees(db_session, departments, roles, 10)
    db_session.commit()

    assert inserted == 10
    assert skipped == 0
    assert inserted_again == 0
    assert skipped_again == 10
    assert len(db_session.scalars(select(Employee)).all()) == 10


def test_export_rows_have_expected_columns_and_valid_employee_refs(db_session):
    departments, _, _ = seed_departments(db_session)
    roles, _, _ = seed_roles(db_session)
    seed_employees(db_session, departments, roles, 3)
    db_session.commit()

    employees = [
        {"employee_id": employee.id, "employee_code": employee.employee_code}
        for employee in db_session.scalars(select(Employee)).all()
    ]
    salary = salary_rows(employees)
    attendance = attendance_rows(employees)

    assert set(salary[0]) == {
        "employee_id", "employee_code", "annual_salary", "currency", "effective_date"
    }
    assert set(attendance[0]) == {
        "employee_id", "employee_code", "month", "working_days", "present_days", "absent_days"
    }
    employee_refs = {(employee["employee_id"], employee["employee_code"]) for employee in employees}
    assert {(row["employee_id"], row["employee_code"]) for row in salary} == employee_refs
    assert {(row["employee_id"], row["employee_code"]) for row in attendance} == employee_refs
    assert len(attendance) == len(employees) * 3
    assert salary == salary_rows(employees)
    assert attendance == attendance_rows(employees)


def test_kaggle_profile_reads_only_clean_aggregate_columns(tmp_path):
    source = tmp_path / "hr.csv"
    source.write_text(
        "Employee_Name,EmpID,Department,Position,Salary\n"
        "Must Not Load,999,Production,Production Technician I,60000\n"
        "Also Private,998,IT/IS,Software Engineer,90000\n",
        encoding="utf-8",
    )

    profile = load_source_profile(source)

    assert len(profile["assignments"]) == 2
    assert profile["assignments"] == [
        ("Operations", "Operations Coordinator"),
        ("Engineering", "Software Engineer"),
    ]
    assert profile["salary_low"] <= profile["salary_high"]
