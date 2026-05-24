from pydantic import BaseModel
from datetime import datetime

class RMABase(BaseModel):
    customer_name: str
    product_serial: str
    reason: str
    status: str = "Pendente"

class RMACreate(RMABase):
    pass

class RMAOut(RMABase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
