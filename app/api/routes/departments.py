from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import DepartmentCreate, DepartmentResponse, EmployeeResponse
from app.schemas.common import PaginatedResponse
from app.services import DepartmentService

router = APIRouter(prefix="/departments", tags=["departments"])


@router.post("", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
def create_department(payload: DepartmentCreate, db: Session = Depends(get_db)):
    return DepartmentService(db).create(payload)


@router.get("", response_model=PaginatedResponse[DepartmentResponse])
def list_departments(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    items, total = DepartmentService(db).list(page=page, size=size)
    return PaginatedResponse[DepartmentResponse].build(items=items, total=total, page=page, size=size)


@router.get("/{department_id}", response_model=DepartmentResponse)
def get_department(department_id: int, db: Session = Depends(get_db)):
    return DepartmentService(db).get(department_id)


@router.get("/{department_id}/employees", response_model=PaginatedResponse[EmployeeResponse])
def list_department_employees(
    department_id: int,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    items, total = DepartmentService(db).employees_for_department(
        department_id=department_id, page=page, size=size
    )
    return PaginatedResponse[EmployeeResponse].build(items=items, total=total, page=page, size=size)
