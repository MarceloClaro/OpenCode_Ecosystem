"""Modelo Edital — representa um edital extraído de um portal."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.database import Base


class Edital(Base):
    __tablename__ = "editais"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    portal_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("portais.id"), nullable=False, index=True)

    titulo: Mapped[str] = mapped_column(String(500), nullable=False)
    url_original: Mapped[str] = mapped_column(String(1000), nullable=False, unique=True)
    pdf_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    data_publicacao: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Status do pipeline
    status: Mapped[str] = mapped_column(
        String(30), default="pendente", index=True
    )  # pendente, extraido, analisado, erro

    # Dados extraídos (JSONB)
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    requisitos_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Campos estruturados (output do Agente 1)
    financiador: Mapped[str | None] = mapped_column(String(300), nullable=True)
    valor_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    valor_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    moeda: Mapped[str] = mapped_column(String(10), default="BRL")
    data_abertura: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    data_encerramento: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    eixos_tematicos: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    perfil_elegivel: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    mecanismo_financiamento: Mapped[str | None] = mapped_column(String(200), nullable=True)
    abrangencia_geografica: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status_inscricao: Mapped[str | None] = mapped_column(String(30), nullable=True)
    nivel_trl_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    nivel_trl_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    score_complexidade: Mapped[int | None] = mapped_column(Integer, nullable=True)
    resumo: Mapped[str | None] = mapped_column(Text, nullable=True)

    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    portal = relationship("Portal", back_populates="editais")
