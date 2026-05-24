from fastapi import APIRouter
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta

router = APIRouter()

# Configurar conexão SQLite
engine = create_engine('sqlite:///database/db.sqlite3', connect_args={"check_same_thread": False})

@router.get("/buscar_clientes_inativos")
async def buscar_clientes_inativos(dias: int = 60):
    try:
        limite_data = (datetime.now() - timedelta(days=dias)).isoformat()
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT id, name, last_purchase FROM clients WHERE last_purchase < :limite_data"),
                {"limite_data": limite_data}
            )
            rows = result.fetchall()
            inativos = [{"id": row[0], "name": row[1], "last_purchase": row[2]} for row in rows]
        return {"inativos": inativos}
    except Exception as e:
        return {"error": str(e)}
