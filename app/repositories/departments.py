from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models import Department


class DepartmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, department_id: int, *, active_only: bool = True) -> Department | None:
        statement = select(Department).where(Department.id == department_id)
        if active_only:
            statement = statement.where(Department.is_active.is_(True))
        return self.db.scalar(statement)

    def get_by_name(self, name: str) -> Department | None:
        return self.db.scalar(select(Department).where(func.lower(Department.name) == name.lower()))

    def list(self, *, page: int, size: int, active_only: bool = True) -> tuple[list[Department], int]:
        statement = select(Department).order_by(Department.name)
        count_statement = select(func.count()).select_from(Department)
        if active_only:
            statement = statement.where(Department.is_active.is_(True))
            count_statement = count_statement.where(Department.is_active.is_(True))
        total = self.db.scalar(count_statement) or 0
        items = list(self.db.scalars(statement.offset((page - 1) * size).limit(size)).all())
        return items, total

    def create(self, department: Department) -> Department:
        self.db.add(department)
        self.db.flush()
        return department

    def get_with_employees(self, department_id: int) -> Department | None:
        return self.db.scalar(
            select(Department)
            .options(selectinload(Department.employees))
            .where(Department.id == department_id, Department.is_active.is_(True))
        )
