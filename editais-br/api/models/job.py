"""Modelo Job — representa uma tarefa do pipeline (crawl, extract, analyze)."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    portal_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("portais.id"), nullable=False, index=True)
    tipo: Mapped[str] = mapped_column(String(30), nullable=False)  # crawl, extract, analyze
    status: Mapped[str] = mapped_column(
        String(20), default="pendente", index=True
    )  # pendente, executando, concluido, falhou

    progresso: Mapped[int] = mapped_column(Integer, default=0)  # 0-100
    mensagem: Mapped[str | None] = mapped_column(Text, nullable=True)
    resultado: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    edital_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("editais.id"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    portal = relationship("Portal", back_populates="jobs")
