from sqlalchemy import Column, Integer, String, DateTime
from database import Base
from datetime import datetime

class RMA(Base):
    __tablename__ = "rmas"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, index=True)
    product_serial = Column(String, index=True)
    reason = Column(String)
    status = Column(String, default="Pendente")
    created_at = Column(DateTime, default=datetime.utcnow)
