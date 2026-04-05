from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SAEnum, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class UserRole(str, Enum):
    viewer = 'viewer'
    analyst = 'analyst'
    admin = 'admin'


class UserStatus(str, Enum):
    active = 'active'
    inactive = 'inactive'


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole, name='user_role'), nullable=False)
    status: Mapped[UserStatus] = mapped_column(
        SAEnum(UserStatus, name='user_status'), nullable=False, default=UserStatus.active
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    records = relationship('FinancialRecord', back_populates='creator', cascade='all,delete-orphan')
