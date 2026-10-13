from __future__ import annotations

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.models import Department, Employee


EMPLOYEE_LOADS = (
    joinedload(Employee.department),
    joinedload(Employee.role),
    joinedload(Employee.manager),
)


class EmployeeRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, employee_id: int, *, active_only: bool = True) -> Employee | None:
        statement = select(Employee).options(*EMPLOYEE_LOADS).where(Employee.id == employee_id)
        if active_only:
            statement = statement.where(Employee.is_active.is_(True))
        return self.db.scalar(statement)

    def get_by_code(self, employee_code: str) -> Employee | None:
        return self.db.scalar(select(Employee).where(Employee.employee_code == employee_code))

    def get_by_email(self, work_email: str) -> Employee | None:
        return self.db.scalar(select(Employee).where(func.lower(Employee.work_email) == work_email.lower()))

    def list(
        self,
        *,
        page: int,
        size: int,
        department: str | None = None,
        q: str | None = None,
        active_only: bool = True,
    ) -> tuple[list[Employee], int]:
        statement = select(Employee).options(*EMPLOYEE_LOADS)
        count_statement = select(func.count()).select_from(Employee)

        if department:
            statement = statement.join(Employee.department)
            count_statement = count_statement.join(Employee.department)
            if department.isdigit():
                condition = Employee.department_id == int(department)
            else:
                condition = func.lower(Department.name) == department.lower()
            statement = statement.where(condition)
            count_statement = count_statement.where(condition)

        if q:
            search = f"%{q.lower()}%"
            condition = or_(
                func.lower(Employee.first_name).like(search),
                func.lower(Employee.last_name).like(search),
            )
            statement = statement.where(condition)
            count_statement = count_statement.where(condition)

        if active_only:
            statement = statement.where(Employee.is_active.is_(True))
            count_statement = count_statement.where(Employee.is_active.is_(True))

        total = self.db.scalar(count_statement) or 0
        items = list(
            self.db.scalars(
                statement.order_by(Employee.id).offset((page - 1) * size).limit(size)
            ).all()
        )
        return items, total

    def create(self, employee: Employee) -> Employee:
        self.db.add(employee)
        self.db.flush()
        self.db.refresh(employee)
        return self.get(employee.id, active_only=False) or employee

    def direct_reports(self, employee_id: int) -> list[Employee]:
        return list(
            self.db.scalars(
                select(Employee)
                .options(*EMPLOYEE_LOADS)
                .where(Employee.manager_id == employee_id, Employee.is_active.is_(True))
                .order_by(Employee.last_name, Employee.first_name)
            ).all()
        )
