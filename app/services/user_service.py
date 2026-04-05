from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.core.security import create_password_hash
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    @staticmethod
    def create_user(db: Session, payload: UserCreate) -> User:
        user = User(
            name=payload.name,
            email=payload.email.lower(),
            role=payload.role,
            status=payload.status,
            password_hash=create_password_hash(payload.password),
        )
        db.add(user)
        try:
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            raise ConflictError(message='Email already exists') from exc
        db.refresh(user)
        return user

    @staticmethod
    def list_users(db: Session) -> list[User]:
        return db.execute(select(User).order_by(User.id.asc())).scalars().all()

    @staticmethod
    def get_user(db: Session, user_id: int) -> User:
        user = db.get(User, user_id)
        if not user:
            raise NotFoundError(message='User not found')
        return user

    @staticmethod
    def update_user(db: Session, user_id: int, payload: UserUpdate) -> User:
        user = UserService.get_user(db, user_id)

        if payload.name is not None:
            user.name = payload.name
        if payload.email is not None:
            user.email = payload.email.lower()
        if payload.role is not None:
            user.role = payload.role
        if payload.status is not None:
            user.status = payload.status

        try:
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            raise ConflictError(message='Email already exists') from exc
        db.refresh(user)
        return user
