from datetime import UTC, datetime, timedelta
from decimal import Decimal, InvalidOperation
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings

pwd_context = CryptContext(schemes=['pbkdf2_sha256'], deprecated='auto')


class TokenPayloadError(ValueError):
    pass


def create_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str, role: str, status: str) -> str:
    settings = get_settings()
    expire = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {'sub': subject, 'role': role, 'status': status, 'exp': expire}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError as exc:
        raise TokenPayloadError('Invalid or expired token') from exc


def decimal_to_string(value: Decimal) -> str:
    try:
        return format(value.quantize(Decimal('0.01')), 'f')
    except (InvalidOperation, AttributeError):
        return '0.00'
