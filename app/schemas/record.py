from __future__ import annotations

from datetime import date as DateType
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator, model_validator

from app.models.financial_record import RecordType


class RecordCreate(BaseModel):
    amount: Decimal = Field(gt=Decimal('0'))
    type: RecordType
    category: str = Field(min_length=1, max_length=120)
    date: DateType
    notes: str | None = Field(default=None, max_length=2000)

    @field_validator('category')
    @classmethod
    def normalize_category(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError('category cannot be empty')
        return value

    @field_validator('notes')
    @classmethod
    def normalize_notes(cls, value: str | None) -> str | None:
        return value.strip() if value else value


class RecordUpdate(BaseModel):
    amount: Decimal | None = Field(default=None, gt=Decimal('0'))
    type: RecordType | None = None
    category: str | None = Field(default=None, min_length=1, max_length=120)
    date: DateType | None = None
    notes: str | None = Field(default=None, max_length=2000)

    @field_validator('category')
    @classmethod
    def normalize_optional_category(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            raise ValueError('category cannot be empty')
        return value


class RecordResponse(BaseModel):
    id: int
    amount: Decimal
    type: RecordType
    category: str
    date: DateType
    notes: str | None
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = {'from_attributes': True}


class RecordListResponse(BaseModel):
    items: list[RecordResponse]
    limit: int
    offset: int
    total: int


class RecordQueryParams(BaseModel):
    type: RecordType | None = None
    category: str | None = None
    start_date: DateType | None = None
    end_date: DateType | None = None
    created_by: int | None = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)

    @field_validator('category')
    @classmethod
    def normalize_category_filter(cls, value: str | None) -> str | None:
        return value.strip() if value else value

    @model_validator(mode='after')
    def validate_date_range(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValueError('end_date must be greater than or equal to start_date')
        return self
