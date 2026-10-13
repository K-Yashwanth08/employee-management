from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas import RoleCreate, RoleResponse
from app.schemas.common import PaginatedResponse
from app.services import RoleService

router = APIRouter(prefix="/roles", tags=["roles"])


@router.post("", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def create_role(payload: RoleCreate, db: Session = Depends(get_db)):
    return RoleService(db).create(payload)


@router.get("", response_model=PaginatedResponse[RoleResponse])
def list_roles(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    items, total = RoleService(db).list(page=page, size=size)
    return PaginatedResponse[RoleResponse].build(items=items, total=total, page=page, size=size)


@router.get("/{role_id}", response_model=RoleResponse)
def get_role(role_id: int, db: Session = Depends(get_db)):
    return RoleService(db).get(role_id)
