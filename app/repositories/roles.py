from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Role


class RoleRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, role_id: int, *, active_only: bool = True) -> Role | None:
        statement = select(Role).where(Role.id == role_id)
        if active_only:
            statement = statement.where(Role.is_active.is_(True))
        return self.db.scalar(statement)

    def get_by_name(self, name: str) -> Role | None:
        return self.db.scalar(select(Role).where(func.lower(Role.name) == name.lower()))

    def list(self, *, page: int, size: int, active_only: bool = True) -> tuple[list[Role], int]:
        statement = select(Role).order_by(Role.name)
        count_statement = select(func.count()).select_from(Role)
        if active_only:
            statement = statement.where(Role.is_active.is_(True))
            count_statement = count_statement.where(Role.is_active.is_(True))
        total = self.db.scalar(count_statement) or 0
        items = list(self.db.scalars(statement.offset((page - 1) * size).limit(size)).all())
        return items, total

    def create(self, role: Role) -> Role:
        self.db.add(role)
        self.db.flush()
        return role
