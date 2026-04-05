from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import UnauthorizedError
from app.core.security import create_access_token, verify_password
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse


class AuthService:
    @staticmethod
    def login(db: Session, payload: LoginRequest) -> TokenResponse:
        stmt = select(User).where(User.email == payload.email.lower())
        user = db.execute(stmt).scalar_one_or_none()
        if not user or not verify_password(payload.password, user.password_hash):
            raise UnauthorizedError(message='Invalid email or password')

        settings = get_settings()
        token = create_access_token(subject=str(user.id), role=user.role.value, status=user.status.value)
        return TokenResponse(access_token=token, expires_in_seconds=settings.access_token_expire_minutes * 60)
