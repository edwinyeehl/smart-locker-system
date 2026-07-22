import os
import pytest
import asyncio
import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from src.main import app
from src.core.database import get_db

load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL", 
    f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:5432/smart_locker_test"
)

def ensure_test_database_exists_sync():
    async def _async_init():
        try:
            conn_url = os.getenv(
                "TEST_ADMIN_DATABASE_URL", 
                f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:5432/postgres"
            )
            conn = await asyncpg.connect(conn_url)
            exists = await conn.fetchval("SELECT 1 FROM pg_database WHERE datname = 'smart_locker_test'")
            if not exists:
                await conn.execute("CREATE DATABASE smart_locker_test")
            await conn.close()
        except Exception as e:
            print(f"Notice during test DB setup: {e}")
    try:
        asyncio.run(_async_init())
    except Exception:
        pass

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    ensure_test_database_exists_sync()

@pytest.fixture
async def db_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    from src.core.database import Base
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        
    yield engine
    
    await engine.dispose()

@pytest.fixture
async def db_session(db_engine):
    async_session = sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session

@pytest.fixture(autouse=True)
def override_fastapi_get_db(db_session):
    """Override FastAPI get_db dependency to direct API client calls to smart_locker_test."""
    async def _get_test_db():
        yield db_session
    app.dependency_overrides[get_db] = _get_test_db
    yield
    app.dependency_overrides.clear()
