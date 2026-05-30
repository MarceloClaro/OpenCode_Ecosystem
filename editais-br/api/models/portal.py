"""Modelo Portal — representa um portal de editais monitorado."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.database import Base


class Portal(Base):
    __tablename__ = "portais"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    nome: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    base_url: Mapped[str] = mapped_column(String(500), nullable=False)
    mode: Mapped[str] = mapped_column(String(20), nullable=False, default="http")  # 'http' ou 'browser'
    crawl_interval_hours: Mapped[int] = mapped_column(Integer, default=24)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    editais = relationship("Edital", back_populates="portal")
    jobs = relationship("Job", back_populates="portal")
