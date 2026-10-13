from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Employee
from app.schemas import EmployeeCreate, EmployeeResponse, EmployeeUpdate
from app.schemas.common import PaginatedResponse
from app.services import EmployeeService

router = APIRouter(prefix="/employees", tags=["employees"])


@router.get("/summary")
def employee_summary(db: Session = Depends(get_db)):
    total = db.scalar(select(func.count()).select_from(Employee)) or 0
    active = db.scalar(
        select(func.count()).select_from(Employee).where(Employee.is_active.is_(True))
    ) or 0
    return {"total": total, "active": active, "inactive": total - active}


@router.post("", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee(payload: EmployeeCreate, db: Session = Depends(get_db)):
    return EmployeeService(db).create(payload)


@router.get("", response_model=PaginatedResponse[EmployeeResponse])
def list_employees(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    department: str | None = Query(default=None, description="Department ID or exact department name"),
    q: str | None = Query(default=None, description="Case-insensitive search by first or last name"),
    db: Session = Depends(get_db),
):
    items, total = EmployeeService(db).list(page=page, size=size, department=department, q=q)
    return PaginatedResponse[EmployeeResponse].build(items=items, total=total, page=page, size=size)


@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    return EmployeeService(db).get(employee_id)


@router.patch("/{employee_id}", response_model=EmployeeResponse)
def update_employee(employee_id: int, payload: EmployeeUpdate, db: Session = Depends(get_db)):
    return EmployeeService(db).update(employee_id, payload)


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    EmployeeService(db).soft_delete(employee_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{employee_id}/team", response_model=list[EmployeeResponse])
def get_direct_reports(employee_id: int, db: Session = Depends(get_db)):
    return EmployeeService(db).direct_reports(employee_id)
