from datetime import date
from decimal import Decimal

from pydantic import BaseModel

from app.models.financial_record import RecordType
from app.schemas.record import RecordResponse


class CategoryTotal(BaseModel):
    type: RecordType
    category: str
    total: Decimal


class MonthlyTrend(BaseModel):
    month: date
    income: Decimal
    expense: Decimal
    net: Decimal


class DashboardSummaryResponse(BaseModel):
    total_income: Decimal
    total_expenses: Decimal
    net_balance: Decimal
    category_wise_totals: list[CategoryTotal]
    recent_activity: list[RecordResponse]
    monthly_trends: list[MonthlyTrend]
