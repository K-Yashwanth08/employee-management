from __future__ import annotations

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Department
from app.repositories import DepartmentRepository, EmployeeRepository
from app.schemas import DepartmentCreate
from app.services.errors import conflict, not_found


class DepartmentService:
    def __init__(self, db: Session):
        self.db = db
        self.departments = DepartmentRepository(db)
        self.employees = EmployeeRepository(db)

    def create(self, payload: DepartmentCreate) -> Department:
        if self.departments.get_by_name(payload.name):
            raise conflict("Department name already exists")
        department = Department(**payload.model_dump())
        try:
            department = self.departments.create(department)
            self.db.commit()
            self.db.refresh(department)
            return department
        except IntegrityError as exc:
            self.db.rollback()
            raise conflict("Department name already exists") from exc

    def list(self, *, page: int, size: int):
        return self.departments.list(page=page, size=size)

    def get(self, department_id: int) -> Department:
        department = self.departments.get(department_id)
        if department is None:
            raise not_found("Department not found")
        return department

    def employees_for_department(self, *, department_id: int, page: int, size: int):
        self.get(department_id)
        return self.employees.list(page=page, size=size, department=str(department_id))
