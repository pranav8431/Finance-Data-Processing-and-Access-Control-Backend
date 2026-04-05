from collections.abc import Callable

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import TokenPayloadError, decode_token
from app.db.session import get_db_session
from app.models.user import User, UserRole, UserStatus

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/auth/login')


def get_db() -> Session:
    yield from get_db_session()


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        payload = decode_token(token)
        user_id = int(payload.get('sub', '0'))
    except (TokenPayloadError, ValueError):
        raise UnauthorizedError(message='Invalid authentication credentials')

    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if not user:
        raise UnauthorizedError(message='Invalid authentication credentials')
    return user


def require_active_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.status != UserStatus.active:
        raise ForbiddenError(message='Inactive users are not allowed')
    return current_user


def require_roles(*roles: UserRole) -> Callable[[User], User]:
    def role_dependency(current_user: User = Depends(require_active_user)) -> User:
        if current_user.role not in roles:
            raise ForbiddenError(message='Insufficient permissions')
        return current_user

    return role_dependency
