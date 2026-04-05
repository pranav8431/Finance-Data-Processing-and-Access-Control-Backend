from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = 'Finance Dashboard API'
    environment: str = 'dev'
    debug: bool = False

    api_v1_prefix: str = '/api/v1'

    database_url: str = Field(default='sqlite:///./finance.db')

    jwt_secret_key: str = Field(default='change-me-in-env')
    jwt_algorithm: str = 'HS256'
    access_token_expire_minutes: int = 60


@lru_cache
def get_settings() -> Settings:
    return Settings()
