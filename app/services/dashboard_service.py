from datetime import date
from decimal import Decimal

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.models.financial_record import FinancialRecord, RecordType
from app.schemas.dashboard import CategoryTotal, DashboardSummaryResponse, MonthlyTrend
from app.services.record_service import RecordService


class DashboardService:
    @staticmethod
    def get_summary(db: Session, recent_limit: int = 5) -> DashboardSummaryResponse:
        income_stmt = select(func.coalesce(func.sum(FinancialRecord.amount), 0)).where(
            FinancialRecord.type == RecordType.income
        )
        expense_stmt = select(func.coalesce(func.sum(FinancialRecord.amount), 0)).where(
            FinancialRecord.type == RecordType.expense
        )

        total_income = RecordService.safe_decimal(db.execute(income_stmt).scalar_one())
        total_expenses = RecordService.safe_decimal(db.execute(expense_stmt).scalar_one())
        net_balance = total_income - total_expenses

        category_stmt = (
            select(FinancialRecord.type, FinancialRecord.category, func.sum(FinancialRecord.amount))
            .group_by(FinancialRecord.type, FinancialRecord.category)
            .order_by(FinancialRecord.type.asc(), FinancialRecord.category.asc())
        )
        category_rows = db.execute(category_stmt).all()
        category_totals = [
            CategoryTotal(type=row[0], category=row[1], total=RecordService.safe_decimal(row[2])) for row in category_rows
        ]

        recent_stmt = (
            select(FinancialRecord)
            .order_by(FinancialRecord.date.desc(), FinancialRecord.id.desc())
            .limit(recent_limit)
        )
        recent_activity = db.execute(recent_stmt).scalars().all()

        monthly_trends = DashboardService._get_monthly_trends(db, months=6)

        return DashboardSummaryResponse(
            total_income=total_income,
            total_expenses=total_expenses,
            net_balance=net_balance,
            category_wise_totals=category_totals,
            recent_activity=recent_activity,
            monthly_trends=monthly_trends,
        )

    @staticmethod
    def _get_monthly_trends(db: Session, months: int) -> list[MonthlyTrend]:
        month_starts = DashboardService._last_month_starts(months)
        first_month = month_starts[0]

        month_key = func.strftime('%Y-%m-01', FinancialRecord.date)
        stmt = (
            select(
                month_key.label('month'),
                func.sum(case((FinancialRecord.type == RecordType.income, FinancialRecord.amount), else_=0)).label('income'),
                func.sum(case((FinancialRecord.type == RecordType.expense, FinancialRecord.amount), else_=0)).label('expense'),
            )
            .where(FinancialRecord.date >= first_month)
            .group_by(month_key)
            .order_by(month_key.asc())
        )
        rows = db.execute(stmt).all()

        monthly_map: dict[date, tuple[Decimal, Decimal]] = {}
        for row in rows:
            month_date = date.fromisoformat(row[0])
            income = RecordService.safe_decimal(row[1])
            expense = RecordService.safe_decimal(row[2])
            monthly_map[month_date] = (income, expense)

        trends: list[MonthlyTrend] = []
        for month in month_starts:
            income, expense = monthly_map.get(month, (Decimal('0.00'), Decimal('0.00')))
            trends.append(MonthlyTrend(month=month, income=income, expense=expense, net=income - expense))

        return trends

    @staticmethod
    def _last_month_starts(months: int) -> list[date]:
        today = date.today()
        starts: list[date] = []
        year = today.year
        month = today.month

        for _ in range(months):
            starts.append(date(year, month, 1))
            month -= 1
            if month == 0:
                month = 12
                year -= 1

        starts.reverse()
        return starts
