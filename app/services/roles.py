from __future__ import annotations

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Role
from app.repositories import RoleRepository
from app.schemas import RoleCreate
from app.services.errors import conflict, not_found


class RoleService:
    def __init__(self, db: Session):
        self.db = db
        self.roles = RoleRepository(db)

    def create(self, payload: RoleCreate) -> Role:
        if self.roles.get_by_name(payload.name):
            raise conflict("Role name already exists")
        role = Role(**payload.model_dump())
        try:
            role = self.roles.create(role)
            self.db.commit()
            self.db.refresh(role)
            return role
        except IntegrityError as exc:
            self.db.rollback()
            raise conflict("Role name already exists") from exc

    def list(self, *, page: int, size: int):
        return self.roles.list(page=page, size=size)

    def get(self, role_id: int) -> Role:
        role = self.roles.get(role_id)
        if role is None:
            raise not_found("Role not found")
        return role
