import hashlib
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.domain.models import Engineer

def hash_password(password: str) -> str:
    """Hash password string using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

async def create_engineer(db: AsyncSession, username: str, password: str, engineer_code: str) -> Engineer:
    """Create a new engineer account with hashed credentials."""
    password_hash = hash_password(password)
    engineer = Engineer(
        username=username,
        password_hash=password_hash,
        engineer_code=engineer_code
    )
    db.add(engineer)
    await db.flush()
    return engineer

async def authenticate_engineer(db: AsyncSession, username: str, password: str) -> Engineer | None:
    """Authenticate an engineer by username and password."""
    password_hash = hash_password(password)
    result = await db.execute(
        select(Engineer).where(
            Engineer.username == username,
            Engineer.password_hash == password_hash
        )
    )
    return result.scalar_one_or_none()
