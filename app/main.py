from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.config import get_settings
from app.core.exceptions import AppError
from app.core.logging import setup_logging

settings = get_settings()
setup_logging()

app = FastAPI(title=settings.app_name, debug=settings.debug)


@app.get('/health', tags=['Health'])
def health_check() -> dict[str, str]:
    return {'status': 'ok'}


@app.exception_handler(AppError)
async def app_error_handler(_, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={'error': {'code': exc.code, 'message': exc.message, 'details': exc.details}},
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={'error': {'code': 'validation_error', 'message': 'Validation failed', 'details': exc.errors()}},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(_, exc: HTTPException):
    code_map = {400: 'bad_request', 401: 'unauthorized', 403: 'forbidden', 404: 'not_found', 409: 'conflict'}
    return JSONResponse(
        status_code=exc.status_code,
        content={
            'error': {
                'code': code_map.get(exc.status_code, 'http_error'),
                'message': exc.detail if isinstance(exc.detail, str) else 'Request failed',
                'details': None if isinstance(exc.detail, str) else exc.detail,
            }
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(_, __):
    return JSONResponse(
        status_code=500,
        content={'error': {'code': 'internal_error', 'message': 'Internal server error', 'details': None}},
    )


app.include_router(api_router, prefix=settings.api_v1_prefix)
app.mount('/ui', StaticFiles(directory='app/static', html=True), name='ui')
