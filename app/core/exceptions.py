from typing import Any


class AppError(Exception):
    def __init__(self, *, code: str, message: str, status_code: int, details: Any = None) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class NotFoundError(AppError):
    def __init__(self, message: str = 'Resource not found', details: Any = None) -> None:
        super().__init__(code='not_found', message=message, status_code=404, details=details)


class ConflictError(AppError):
    def __init__(self, message: str = 'Resource conflict', details: Any = None) -> None:
        super().__init__(code='conflict', message=message, status_code=409, details=details)


class ForbiddenError(AppError):
    def __init__(self, message: str = 'Forbidden', details: Any = None) -> None:
        super().__init__(code='forbidden', message=message, status_code=403, details=details)


class UnauthorizedError(AppError):
    def __init__(self, message: str = 'Unauthorized', details: Any = None) -> None:
        super().__init__(code='unauthorized', message=message, status_code=401, details=details)


class BadRequestError(AppError):
    def __init__(self, message: str = 'Bad request', details: Any = None) -> None:
        super().__init__(code='bad_request', message=message, status_code=400, details=details)
