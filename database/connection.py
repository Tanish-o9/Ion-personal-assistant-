import os
import logging
from typing import Generator
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session

logger = logging.getLogger(__name__)

# Configurable DATABASE_URL with automatic fallback to local SQLite for lightweight development
DEFAULT_DB_URL = "sqlite:///./ion.db"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DB_URL)

# For SQLite, check_same_thread must be False for multi-threaded FastAPI execution
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db() -> None:
    """
    Initializes database schema and creates all tables.
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully at '%s'", DATABASE_URL)
    except Exception as exc:
        logger.error("Failed to initialize database: %s", exc)

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency yielding database session with automatic transaction cleanup.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """
    Context manager yielding database session for background or synchronous execution.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
