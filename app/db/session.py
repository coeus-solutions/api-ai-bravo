from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings
from app.core.constants import DB_CONNECTION_POOL_SIZE, DB_MAX_OVERFLOW, DB_POOL_TIMEOUT
import ssl

settings = get_settings()

# Create SSL context for secure database connections
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Configure engine with SSL and other production settings
engine = create_async_engine(
    settings.async_database_url,
    pool_size=DB_CONNECTION_POOL_SIZE,
    max_overflow=DB_MAX_OVERFLOW,
    pool_timeout=DB_POOL_TIMEOUT,
    pool_pre_ping=True,  # Enable connection health checks
    pool_recycle=300,    # Recycle connections every 5 minutes
    echo=False,
    connect_args={
        "ssl": ssl_context,
        "server_settings": {
            "application_name": "recognition_platform"
        }
    }
)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close() 