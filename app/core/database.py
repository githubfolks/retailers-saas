from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from typing import Generator
from contextlib import contextmanager
from app.core.config import settings

db_url = settings.postgres_url
if db_url.startswith('postgresql://'):
    db_url = db_url.replace('postgresql://', 'postgresql+psycopg2://', 1)

engine = create_engine(
    db_url,
    pool_pre_ping=True,
    echo=False,
    pool_size=20,
    max_overflow=40,
    pool_recycle=3600,
    pool_timeout=30,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_session() -> Session:
    """Create a database session for direct use."""
    return SessionLocal()


@contextmanager
def get_task_db():
    """Context manager for Celery tasks — always closes the session on exit."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
