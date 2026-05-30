"""Rotas da API de editais — GET /editais e GET /editais/{id}.

Inclui 7 filtros de captação: eixo temático, perfil, mecanismo,
abrangência, status, faixa de valor, TRL.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api.database import SessionLocal
from api.models import Edital  # noqa: E402 — import registra todos os models

router = APIRouter(prefix="/editais", tags=["editais"])


def get_db():
    """Dependency: fornece uma sessão de banco."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Depends(get_db)


@router.get("")
def listar_editais(
    skip: int = Query(0, ge=0, description="Registros para pular"),
    limit: int = Query(20, ge=1, le=100, description="Máximo de registros"),
    # Filtro 1: Eixo temático
    eixo_tematico: str | None = Query(None, description="Filtrar por eixo temático"),
    # Filtro 2: Perfil do proponente
    perfil_elegivel: str | None = Query(None, description="Filtrar por perfil elegível"),
    # Filtro 3: Mecanismo de financiamento
    mecanismo: str | None = Query(None, description="Filtrar por mecanismo de financiamento"),
    # Filtro 4: Abrangência geográfica
    abrangencia_tipo: str | None = Query(
        None, description="Tipo: nacional, regional, estadual, municipal"
    ),
    estado: str | None = Query(None, description="UF (ex: SP, RJ)"),
    # Filtro 5: Status
    status: str | None = Query(None, description="Status do edital"),
    # Filtro 6: Faixa de valor
    valor_min: float | None = Query(None, ge=0, description="Valor mínimo"),
    valor_max: float | None = Query(None, ge=0, description="Valor máximo"),
    # Filtro 7: TRL
    trl_min: int | None = Query(None, ge=1, le=9, description="TRL mínimo"),
    trl_max: int | None = Query(None, ge=1, le=9, description="TRL máximo"),
    # Ordenação
    ordem: str | None = Query("data_publicacao", description="Campo para ordenar"),
    db: Session = db_dependency,
):
    """Lista editais com filtros opcionais e paginação."""
    query = db.query(Edital)

    # Aplica filtros
    if eixo_tematico:
        query = query.filter(Edital.eixos_tematicos.contains([eixo_tematico]))
    if perfil_elegivel:
        query = query.filter(Edital.perfil_elegivel.contains([perfil_elegivel]))
    if mecanismo:
        query = query.filter(Edital.mecanismo_financiamento == mecanismo)
    if abrangencia_tipo:
        query = query.filter(
            Edital.abrangencia_geografica["tipo"].astext == abrangencia_tipo
        )
    if estado:
        query = query.filter(
            Edital.abrangencia_geografica["estados"].contains([estado])
        )
    if status:
        query = query.filter(Edital.status_inscricao == status)
    if valor_min is not None:
        query = query.filter(Edital.valor_max >= valor_min)
    if valor_max is not None:
        query = query.filter(Edital.valor_min <= valor_max)
    if trl_min is not None:
        query = query.filter(Edital.nivel_trl_min >= trl_min)
    if trl_max is not None:
        query = query.filter(Edital.nivel_trl_max <= trl_max)

    # Ordenação padrão
    ordem_coluna = getattr(Edital, ordem, Edital.criado_em)
    query = query.order_by(ordem_coluna.desc())

    editais = query.offset(skip).limit(limit).all()

    return [
        {
            "id": str(e.id),
            "titulo": e.titulo,
            "financiador": e.financiador,
            "url_original": e.url_original,
            "valor_min": e.valor_min,
            "valor_max": e.valor_max,
            "moeda": e.moeda,
            "status": e.status_inscricao or e.status,
            "eixos_tematicos": e.eixos_tematicos or [],
            "perfil_elegivel": e.perfil_elegivel or [],
            "resumo": e.resumo,
            "data_publicacao": str(e.data_publicacao) if e.data_publicacao else None,
            "data_encerramento": str(e.data_encerramento) if e.data_encerramento else None,
        }
        for e in editais
    ]


@router.get("/{edital_id}")
def obter_edital(edital_id: str, db: Session = db_dependency):
    """Obtém um edital específico por ID."""
    try:
        uid = uuid.UUID(edital_id)
    except ValueError as err:
        raise HTTPException(status_code=422, detail="UUID inválido") from err

    edital = db.query(Edital).filter(Edital.id == uid).first()
    if not edital:
        raise HTTPException(status_code=404, detail="Edital não encontrado")

    return {
        "id": str(edital.id),
        "titulo": edital.titulo,
        "financiador": edital.financiador,
        "url_original": edital.url_original,
        "pdf_url": edital.pdf_url,
        "valor_min": edital.valor_min,
        "valor_max": edital.valor_max,
        "moeda": edital.moeda,
        "data_abertura": str(edital.data_abertura) if edital.data_abertura else None,
        "data_encerramento": str(edital.data_encerramento) if edital.data_encerramento else None,
        "eixos_tematicos": edital.eixos_tematicos or [],
        "perfil_elegivel": edital.perfil_elegivel or [],
        "mecanismo_financiamento": edital.mecanismo_financiamento,
        "abrangencia_geografica": edital.abrangencia_geografica,
        "status": edital.status_inscricao or edital.status,
        "nivel_trl_min": edital.nivel_trl_min,
        "nivel_trl_max": edital.nivel_trl_max,
        "score_complexidade": edital.score_complexidade,
        "requisitos_obrigatorios": [],
        "documentos_necessarios": [],
        "contrapartida_exigida": False,
        "resumo": edital.resumo,
        "requisitos_json": edital.requisitos_json,
    }
