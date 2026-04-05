from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_roles
from app.models.user import User, UserRole
from app.schemas.dashboard import DashboardSummaryResponse
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix='/dashboard', tags=['Dashboard'])


@router.get('/summary', response_model=DashboardSummaryResponse)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.viewer, UserRole.analyst, UserRole.admin)),
) -> DashboardSummaryResponse:
    return DashboardService.get_summary(db)
