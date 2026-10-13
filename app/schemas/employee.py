from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

from app.schemas.common import IdName
from app.schemas.department import non_blank


def not_future(value: date) -> date:
    if value > date.today():
        raise ValueError("joining_date cannot be in the future")
    return value


class EmployeeCreate(BaseModel):
    employee_code: str = Field(min_length=1, max_length=30)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    work_email: EmailStr
    phone: str | None = Field(default=None, max_length=30)
    joining_date: date
    department_id: int
    role_id: int
    manager_id: int | None = None

    _employee_code_not_blank = field_validator("employee_code")(non_blank)
    _first_name_not_blank = field_validator("first_name")(non_blank)
    _last_name_not_blank = field_validator("last_name")(non_blank)
    _joining_date_not_future = field_validator("joining_date")(not_future)


class EmployeeUpdate(BaseModel):
    employee_code: str | None = Field(default=None, min_length=1, max_length=30)
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    work_email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=30)
    joining_date: date | None = None
    department_id: int | None = None
    role_id: int | None = None
    manager_id: int | None = None
    is_active: bool | None = None

    _employee_code_not_blank = field_validator("employee_code")(non_blank)
    _first_name_not_blank = field_validator("first_name")(non_blank)
    _last_name_not_blank = field_validator("last_name")(non_blank)
    _joining_date_not_future = field_validator("joining_date")(not_future)

    @model_validator(mode="after")
    def reject_null_for_required_fields(self):
        required_when_provided = {
            "employee_code",
            "first_name",
            "last_name",
            "work_email",
            "joining_date",
            "department_id",
            "role_id",
            "is_active",
        }
        null_fields = [
            field
            for field in required_when_provided & self.model_fields_set
            if getattr(self, field) is None
        ]
        if null_fields:
            raise ValueError(f"Fields cannot be null: {', '.join(sorted(null_fields))}")
        return self


class EmployeeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_code: str
    first_name: str
    last_name: str
    work_email: EmailStr
    phone: str | None
    joining_date: date
    is_active: bool
    department: IdName
    role: IdName
    manager: IdName | None
    created_at: datetime
    updated_at: datetime
