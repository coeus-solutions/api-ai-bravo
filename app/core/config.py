from pydantic_settings import BaseSettings
from typing import Optional, List
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "Recognition Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str

    @property
    def sync_database_url(self) -> str:
        return self.DATABASE_URL

    @property
    def async_database_url(self) -> str:
        return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str

    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS - Allow all origins
    ALLOW_ALL_ORIGINS: bool = True

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "allow"

@lru_cache
def get_settings() -> Settings:
    return Settings() 