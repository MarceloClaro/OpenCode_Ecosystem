"""Rotas da API de jobs — POST /portais/{id}/crawl e GET /jobs/{id}."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.database import SessionLocal
from api.models.job import Job
from api.models.portal import Portal

router = APIRouter(tags=["jobs"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Depends(get_db)


@router.post("/portais/{portal_id}/crawl", status_code=202)
def iniciar_crawl(portal_id: str, db: Session = db_dependency):
    """Dispara um job de crawl para o portal."""
    try:
        uid = uuid.UUID(portal_id)
    except ValueError as err:
        raise HTTPException(status_code=422, detail="UUID inválido") from err

    portal = db.query(Portal).filter(Portal.id == uid).first()
    if not portal:
        raise HTTPException(status_code=404, detail="Portal não encontrado")

    job = Job(portal_id=uid, tipo="crawl", status="pendente")
    db.add(job)
    db.commit()
    db.refresh(job)

    return {"job_id": str(job.id), "status": job.status, "portal": portal.nome}


@router.get("/jobs/{job_id}")
def obter_job(job_id: str, db: Session = db_dependency):
    """Obtém o status de um job."""
    try:
        uid = uuid.UUID(job_id)
    except ValueError as err:
        raise HTTPException(status_code=422, detail="UUID inválido") from err

    job = db.query(Job).filter(Job.id == uid).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job não encontrado")

    return {
        "id": str(job.id),
        "portal_id": str(job.portal_id),
        "tipo": job.tipo,
        "status": job.status,
        "progresso": job.progresso,
        "mensagem": job.mensagem,
        "resultado": job.resultado,
        "created_at": str(job.created_at) if job.created_at else None,
        "updated_at": str(job.updated_at) if job.updated_at else None,
    }
