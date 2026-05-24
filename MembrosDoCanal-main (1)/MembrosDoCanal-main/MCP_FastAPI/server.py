from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, crud, schemas
from database import SessionLocal, engine, Base
from fastapi_mcp import FastApiMCP

Base.metadata.create_all(bind=engine)

app = FastAPI(title="API de RMA")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/rmas/", response_model=schemas.RMAOut)
async def create_rma(rma: schemas.RMACreate, db: Session = Depends(get_db)):
    return crud.create_rma(db, rma)

@app.get("/rmas/", response_model=list[schemas.RMAOut])
async def read_rmas(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_rmas(db, skip=skip, limit=limit)

@app.get("/rmas/{rma_id}", response_model=schemas.RMAOut)
async def read_rma_by_id(rma_id: int, db: Session = Depends(get_db)):
    rma = crud.get_rma_by_id(db, rma_id)
    if not rma:
        raise HTTPException(status_code=404, detail="RMA não encontrado")
    return rma

@app.get("/rmas/cliente/{nome}", response_model=list[schemas.RMAOut])
async def read_rma_by_cliente(nome: str, db: Session = Depends(get_db)):
    return crud.get_rmas_by_customer(db, nome)

# Add MCP server to the FastAPI app
mcp = FastApiMCP(app)

# Mount the MCP server to the FastAPI app
mcp.mount()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)