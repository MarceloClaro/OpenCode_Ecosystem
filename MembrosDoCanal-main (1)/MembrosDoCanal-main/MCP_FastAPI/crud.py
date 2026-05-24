from sqlalchemy.orm import Session
from models import RMA
from schemas import RMACreate

def create_rma(db: Session, rma: RMACreate):
    db_rma = RMA(**rma.dict())
    db.add(db_rma)
    db.commit()
    db.refresh(db_rma)
    return db_rma

def get_rmas(db: Session, skip: int = 0, limit: int = 100):
    return db.query(RMA).offset(skip).limit(limit).all()

def get_rma_by_id(db: Session, rma_id: int):
    return db.query(RMA).filter(RMA.id == rma_id).first()

def get_rmas_by_customer(db: Session, name: str):
    return db.query(RMA).filter(RMA.customer_name.ilike(f"%{name}%")).all()
