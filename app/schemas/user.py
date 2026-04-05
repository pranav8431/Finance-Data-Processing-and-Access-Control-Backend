from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.user import UserRole, UserStatus


class UserBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr

    @field_validator('name')
    @classmethod
    def normalize_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError('name cannot be empty')
        return value


class UserCreate(UserBase):
    role: UserRole
    status: UserStatus = UserStatus.active
    password: str = Field(min_length=3, max_length=128)


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    email: EmailStr | None = None
    role: UserRole | None = None
    status: UserStatus | None = None

    @field_validator('name')
    @classmethod
    def normalize_optional_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            raise ValueError('name cannot be empty')
        return value


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: UserRole
    status: UserStatus
    created_at: datetime
    updated_at: datetime

    model_config = {'from_attributes': True}
