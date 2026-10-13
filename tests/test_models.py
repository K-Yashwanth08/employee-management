import pytest
from datetime import date
from sqlalchemy import create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.models import Department, Employee, Role


@pytest.fixture
def session():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    with Session(engine) as database:
        yield database
    Base.metadata.drop_all(engine)
    engine.dispose()


def add_department_and_role(session: Session) -> tuple[Department, Role]:
    department = Department(name="Engineering")
    role = Role(name="Software Engineer")
    session.add_all([department, role])
    session.flush()
    return department, role


def test_duplicate_work_email_is_rejected(session: Session):
    department, role = add_department_and_role(session)
    session.add(
        Employee(
            employee_code="EMP-001",
            first_name="Avery",
            last_name="Morgan",
            work_email="avery.morgan@example.com",
            joining_date=date(2024, 1, 10),
            department=department,
            role=role,
        )
    )
    session.commit()

    session.add(
        Employee(
            employee_code="EMP-002",
            first_name="Jordan",
            last_name="Reed",
            work_email="avery.morgan@example.com",
            joining_date=date(2024, 1, 11),
            department=department,
            role=role,
        )
    )
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_manager_relationship_returns_direct_reports(session: Session):
    department, role = add_department_and_role(session)
    manager = Employee(
        employee_code="EMP-003",
        first_name="Morgan",
        last_name="Lee",
        work_email="morgan.lee@example.com",
        joining_date=date(2024, 1, 12),
        department=department,
        role=role,
    )
    report = Employee(
        employee_code="EMP-004",
        first_name="Taylor",
        last_name="Kim",
        work_email="taylor.kim@example.com",
        joining_date=date(2024, 1, 13),
        department=department,
        role=role,
        manager=manager,
    )
    session.add_all([manager, report])
    session.commit()

    loaded_manager = session.scalar(select(Employee).where(Employee.id == manager.id))
    assert loaded_manager is not None
    assert loaded_manager.direct_reports[0].full_name == "Taylor Kim"
    assert loaded_manager.direct_reports[0].manager_id == loaded_manager.id


def test_employee_cannot_manage_themselves(session: Session):
    department, role = add_department_and_role(session)
    employee = Employee(
        employee_code="EMP-005",
        first_name="Casey",
        last_name="Parker",
        work_email="casey.parker@example.com",
        joining_date=date(2024, 1, 14),
        department=department,
        role=role,
    )
    session.add(employee)
    session.flush()
    employee.manager_id = employee.id

    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()
