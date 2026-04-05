from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.financial_record import FinancialRecord
from app.schemas.record import RecordCreate, RecordQueryParams, RecordUpdate


class RecordService:
    @staticmethod
    def create_record(db: Session, payload: RecordCreate, created_by: int) -> FinancialRecord:
        record = FinancialRecord(
            amount=payload.amount,
            type=payload.type,
            category=payload.category,
            date=payload.date,
            notes=payload.notes,
            created_by=created_by,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def get_record(db: Session, record_id: int) -> FinancialRecord:
        record = db.get(FinancialRecord, record_id)
        if not record:
            raise NotFoundError(message='Record not found')
        return record

    @staticmethod
    def list_records(db: Session, params: RecordQueryParams) -> tuple[list[FinancialRecord], int]:
        stmt = select(FinancialRecord)
        count_stmt = select(func.count(FinancialRecord.id))

        if params.type:
            stmt = stmt.where(FinancialRecord.type == params.type)
            count_stmt = count_stmt.where(FinancialRecord.type == params.type)
        if params.category:
            stmt = stmt.where(FinancialRecord.category == params.category)
            count_stmt = count_stmt.where(FinancialRecord.category == params.category)
        if params.start_date:
            stmt = stmt.where(FinancialRecord.date >= params.start_date)
            count_stmt = count_stmt.where(FinancialRecord.date >= params.start_date)
        if params.end_date:
            stmt = stmt.where(FinancialRecord.date <= params.end_date)
            count_stmt = count_stmt.where(FinancialRecord.date <= params.end_date)
        if params.created_by:
            stmt = stmt.where(FinancialRecord.created_by == params.created_by)
            count_stmt = count_stmt.where(FinancialRecord.created_by == params.created_by)

        stmt = stmt.order_by(FinancialRecord.date.desc(), FinancialRecord.id.desc())
        stmt = stmt.offset(params.offset).limit(params.limit)

        items = db.execute(stmt).scalars().all()
        total = db.execute(count_stmt).scalar_one()
        return items, total

    @staticmethod
    def update_record(db: Session, record_id: int, payload: RecordUpdate) -> FinancialRecord:
        record = RecordService.get_record(db, record_id)

        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(record, key, value)

        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def delete_record(db: Session, record_id: int) -> None:
        record = RecordService.get_record(db, record_id)
        db.delete(record)
        db.commit()

    @staticmethod
    def safe_decimal(value: Decimal | int | None) -> Decimal:
        if value is None:
            return Decimal('0.00')
        if isinstance(value, Decimal):
            return value
        return Decimal(str(value))
