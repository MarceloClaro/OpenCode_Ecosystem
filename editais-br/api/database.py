"""Database engine e session — SQLAlchemy 2 + PostgreSQL."""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

POSTGRES_URL = os.getenv(
    "POSTGRES_URL",
    "postgresql://editais:changeme@postgres:5432/editais",
)

engine = create_engine(POSTGRES_URL, echo=False, pool_size=10, max_overflow=20)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass
