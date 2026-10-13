from __future__ import annotations

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Employee
from app.repositories import DepartmentRepository, EmployeeRepository, RoleRepository
from app.schemas import EmployeeCreate, EmployeeUpdate
from app.services.errors import conflict, not_found, unprocessable


class EmployeeService:
    def __init__(self, db: Session):
        self.db = db
        self.employees = EmployeeRepository(db)
        self.departments = DepartmentRepository(db)
        self.roles = RoleRepository(db)

    def _validate_refs(self, *, department_id: int, role_id: int, manager_id: int | None, employee_id: int | None = None):
        if self.departments.get(department_id) is None:
            raise unprocessable("Department does not exist")
        if self.roles.get(role_id) is None:
            raise unprocessable("Role does not exist")
        if manager_id is not None:
            if employee_id is not None and manager_id == employee_id:
                raise unprocessable("Employee cannot manage themselves")
            manager = self.employees.get(manager_id)
            if manager is None:
                raise unprocessable("Manager does not exist")
            seen = {employee_id} if employee_id is not None else set()
            current = manager
            while current is not None:
                if current.id in seen:
                    raise unprocessable("Manager assignment would create a cycle")
                seen.add(current.id)
                current = self.employees.get(current.manager_id) if current.manager_id else None

    def _check_unique(self, *, employee_code: str | None, work_email: str | None, employee_id: int | None = None):
        if employee_code:
            existing = self.employees.get_by_code(employee_code)
            if existing and existing.id != employee_id:
                raise conflict("Employee code already exists")
        if work_email:
            existing = self.employees.get_by_email(work_email)
            if existing and existing.id != employee_id:
                raise conflict("Work email already exists")

    def create(self, payload: EmployeeCreate) -> Employee:
        self._check_unique(employee_code=payload.employee_code, work_email=str(payload.work_email))
        self._validate_refs(
            department_id=payload.department_id,
            role_id=payload.role_id,
            manager_id=payload.manager_id,
        )
        employee = Employee(**payload.model_dump())
        try:
            employee = self.employees.create(employee)
            self.db.commit()
            return employee
        except IntegrityError as exc:
            self.db.rollback()
            raise conflict("Employee code or work email already exists") from exc

    def list(self, *, page: int, size: int, department: str | None, q: str | None):
        return self.employees.list(page=page, size=size, department=department, q=q)

    def get(self, employee_id: int) -> Employee:
        employee = self.employees.get(employee_id)
        if employee is None:
            raise not_found("Employee not found")
        return employee

    def update(self, employee_id: int, payload: EmployeeUpdate) -> Employee:
        employee = self.get(employee_id)
        changes = payload.model_dump(exclude_unset=True)
        new_department_id = changes.get("department_id", employee.department_id)
        new_role_id = changes.get("role_id", employee.role_id)
        new_manager_id = changes.get("manager_id", employee.manager_id)
        self._check_unique(
            employee_code=changes.get("employee_code"),
            work_email=str(changes["work_email"]) if changes.get("work_email") else None,
            employee_id=employee_id,
        )
        self._validate_refs(
            department_id=new_department_id,
            role_id=new_role_id,
            manager_id=new_manager_id,
            employee_id=employee_id,
        )
        for key, value in changes.items():
            setattr(employee, key, value)
        try:
            self.db.commit()
            return self.get(employee_id)
        except IntegrityError as exc:
            self.db.rollback()
            raise conflict("Employee code or work email already exists") from exc

    def soft_delete(self, employee_id: int) -> None:
        employee = self.get(employee_id)
        employee.is_active = False
        self.db.commit()

    def direct_reports(self, employee_id: int) -> list[Employee]:
        self.get(employee_id)
        return self.employees.direct_reports(employee_id)
