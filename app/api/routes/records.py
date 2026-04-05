from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_roles
from app.models.financial_record import RecordType
from app.models.user import User, UserRole
from app.schemas.record import RecordCreate, RecordListResponse, RecordQueryParams, RecordResponse, RecordUpdate
from app.services.record_service import RecordService

router = APIRouter(prefix='/records', tags=['Records'])


@router.post('', response_model=RecordResponse, status_code=201)
def create_record(
    payload: RecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin)),
) -> RecordResponse:
    return RecordService.create_record(db, payload, created_by=current_user.id)


@router.get('', response_model=RecordListResponse)
def list_records(
    params: Annotated[RecordQueryParams, Depends()],
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.viewer, UserRole.analyst, UserRole.admin)),
) -> RecordListResponse:
    items, total = RecordService.list_records(db, params)
    return RecordListResponse(items=items, total=total, limit=params.limit, offset=params.offset)


@router.get('/{record_id}', response_model=RecordResponse)
def get_record(
    record_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.viewer, UserRole.analyst, UserRole.admin)),
) -> RecordResponse:
    return RecordService.get_record(db, record_id)


@router.patch('/{record_id}', response_model=RecordResponse)
def update_record(
    record_id: int,
    payload: RecordUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin)),
) -> RecordResponse:
    return RecordService.update_record(db, record_id, payload)


@router.delete('/{record_id}', status_code=204)
def delete_record(
    record_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.admin)),
) -> None:
    RecordService.delete_record(db, record_id)
