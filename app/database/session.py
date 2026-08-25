from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from config.settings import settings


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy database models.
    """
    pass


# ---------------------------------------------------------
# Database Engine
# ---------------------------------------------------------

connect_args = {}

# SQLite requires this option for FastAPI/Streamlit-style
# applications where multiple threads may access the DB.
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {
        "check_same_thread": False
    }


engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    echo=settings.DATABASE_ECHO,
)


# ---------------------------------------------------------
# Session Factory
# ---------------------------------------------------------

SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


# ---------------------------------------------------------
# Database Dependency
# ---------------------------------------------------------

def get_db() -> Generator[Session, None, None]:
    """
    Provide a database session to API routes/services.

    The session is automatically closed after use.
    """

    db = SessionLocal()

    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# ---------------------------------------------------------
# Create Tables
# ---------------------------------------------------------

def create_tables() -> None:
    """
    Create all registered database tables.

    Import models before calling this function so that
    SQLAlchemy knows about all model classes.
    """

    from app.database.models import (  # noqa: F401
        claim,
        policy,
        patient,
        document,
        adjudication,
    )

    Base.metadata.create_all(bind=engine)