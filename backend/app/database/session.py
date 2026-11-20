"""Database session management with SQLite WAL mode and foreign keys enabled."""

from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from backend.app.core.config import get_settings
from backend.app.core.logging import get_logger
from backend.app.database.base import Base

logger = get_logger("database")
settings = get_settings()

# Configure SQLite WAL mode and enforce foreign keys
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enforce WAL journal mode and foreign keys on all SQLite connections."""
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.execute("PRAGMA synchronous=NORMAL;")
    except Exception as e:
        logger.warning(f"Could not set SQLite pragmas: {e}")
    finally:
        cursor.close()


# Engine initialization
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=settings.DEBUG,
    future=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True,
)


def init_db() -> None:
    """Initialize database tables according to model metadata."""
    logger.info("Initializing database schema...")
    # Import models here to register them with Base.metadata
    from backend.app.models import case, evidence, analysis, artifact, note, roi, dossier  # noqa: F401
    Base.metadata.create_all(bind=engine)
    logger.info("Database schema initialized successfully.")


def get_db() -> Generator[Session, None, None]:
    """Dependency that yields a database session and ensures it closes after request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

