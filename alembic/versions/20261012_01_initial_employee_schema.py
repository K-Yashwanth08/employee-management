"""Create departments, roles, and employees.

Revision ID: 20261012_01
Revises:
Create Date: 2026-10-12
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20261012_01"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "departments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_departments")),
        sa.UniqueConstraint("name", name=op.f("uq_departments_name")),
    )
    op.create_index(op.f("ix_departments_is_active"), "departments", ["is_active"], unique=False)
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_roles")),
        sa.UniqueConstraint("name", name=op.f("uq_roles_name")),
    )
    op.create_index(op.f("ix_roles_is_active"), "roles", ["is_active"], unique=False)
    op.create_table(
        "employees",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("employee_code", sa.String(length=30), nullable=False),
        sa.Column("first_name", sa.String(length=100), nullable=False),
        sa.Column("last_name", sa.String(length=100), nullable=False),
        sa.Column("work_email", sa.String(length=320), nullable=False),
        sa.Column("phone", sa.String(length=30), nullable=True),
        sa.Column("joining_date", sa.Date(), server_default=sa.func.current_date(), nullable=False),
        sa.Column("department_id", sa.Integer(), nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.Column("manager_id", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("manager_id IS NULL OR manager_id != id", name=op.f("ck_employees_not_own_manager")),
        sa.ForeignKeyConstraint(["department_id"], ["departments.id"], name=op.f("fk_employees_department_id_departments"), ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["manager_id"], ["employees.id"], name=op.f("fk_employees_manager_id_employees"), ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], name=op.f("fk_employees_role_id_roles"), ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_employees")),
        sa.UniqueConstraint("employee_code", name="uq_employees_employee_code"),
        sa.UniqueConstraint("work_email", name="uq_employees_work_email"),
    )
    op.create_index("ix_employees_name", "employees", ["last_name", "first_name"], unique=False)
    op.create_index("ix_employees_department_id", "employees", ["department_id"], unique=False)
    op.create_index("ix_employees_manager_id", "employees", ["manager_id"], unique=False)
    op.create_index("ix_employees_is_active", "employees", ["is_active"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_employees_is_active", table_name="employees")
    op.drop_index("ix_employees_manager_id", table_name="employees")
    op.drop_index("ix_employees_department_id", table_name="employees")
    op.drop_index("ix_employees_name", table_name="employees")
    op.drop_table("employees")
    op.drop_index(op.f("ix_roles_is_active"), table_name="roles")
    op.drop_table("roles")
    op.drop_index(op.f("ix_departments_is_active"), table_name="departments")
    op.drop_table("departments")
