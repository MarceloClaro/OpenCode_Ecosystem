from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import platform
import os

app = FastAPI(
    title="🚀 App Containerizada",
    description="Aplicação FastAPI rodando com segurança em Docker (usuário não-root)",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----- Modelos -----

class Item(BaseModel):
    nome: str
    descricao: Optional[str] = None
    preco: float

class Mensagem(BaseModel):
    texto: str

# Banco de dados em memória
items_db: dict[int, dict] = {}
next_id = 1

# ----- Rotas -----

@app.get("/", response_class=HTMLResponse, tags=["UI"])
async def home():
    """Página inicial com dashboard visual."""
    html = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>App Containerizada</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Syne:wght@400;700;800&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --bg: #0a0e1a;
      --surface: #111827;
      --border: #1e2d40;
      --accent: #00e5ff;
      --accent2: #7c3aed;
      --green: #22c55e;
      --text: #e2e8f0;
      --muted: #64748b;
    }

    body {
      background: var(--bg);
      color: var(--text);
      font-family: 'Syne', sans-serif;
      min-height: 100vh;
      padding: 2rem;
      background-image:
        radial-gradient(ellipse at 20% 20%, rgba(0,229,255,0.06) 0%, transparent 60%),
        radial-gradient(ellipse at 80% 80%, rgba(124,58,237,0.06) 0%, transparent 60%);
    }

    .header {
      display: flex;
      align-items: center;
      gap: 1rem;
      margin-bottom: 3rem;
      padding-bottom: 1.5rem;
      border-bottom: 1px solid var(--border);
    }

    .badge {
      display: inline-flex;
      align-items: center;
      gap: .4rem;
      background: rgba(34,197,94,.1);
      border: 1px solid rgba(34,197,94,.3);
      color: var(--green);
      font-family: 'JetBrains Mono', monospace;
      font-size: .7rem;
      padding: .3rem .8rem;
      border-radius: 999px;
      letter-spacing: .05em;
    }

    .badge::before { content: '●'; font-size: .5rem; }

    h1 { font-size: 2rem; font-weight: 800; letter-spacing: -.02em; }
    h1 span { color: var(--accent); }

    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 1.25rem;
      margin-bottom: 2.5rem;
    }

    .card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 1.5rem;
      position: relative;
      overflow: hidden;
      transition: border-color .2s;
    }

    .card:hover { border-color: var(--accent); }

    .card::before {
      content: '';
      position: absolute;
      inset: 0;
      background: linear-gradient(135deg, rgba(0,229,255,.04), transparent);
      pointer-events: none;
    }

    .card-label {
      font-family: 'JetBrains Mono', monospace;
      font-size: .65rem;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: .1em;
      margin-bottom: .5rem;
    }

    .card-value {
      font-size: 1.6rem;
      font-weight: 800;
      color: var(--accent);
    }

    .card-sub { font-size: .8rem; color: var(--muted); margin-top: .3rem; }

    .section-title {
      font-family: 'JetBrains Mono', monospace;
      font-size: .75rem;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: .1em;
      margin-bottom: 1rem;
    }

    .endpoints {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 12px;
      overflow: hidden;
      margin-bottom: 2rem;
    }

    .endpoint {
      display: grid;
      grid-template-columns: 70px 1fr auto;
      align-items: center;
      gap: 1rem;
      padding: 1rem 1.5rem;
      border-bottom: 1px solid var(--border);
      font-family: 'JetBrains Mono', monospace;
      font-size: .8rem;
      transition: background .15s;
    }

    .endpoint:last-child { border-bottom: none; }
    .endpoint:hover { background: rgba(255,255,255,.02); }

    .method {
      font-weight: 700;
      font-size: .7rem;
      padding: .2rem .5rem;
      border-radius: 4px;
      text-align: center;
    }

    .GET  { background: rgba(34,197,94,.15);  color: #22c55e; }
    .POST { background: rgba(0,229,255,.15);  color: #00e5ff; }
    .PUT  { background: rgba(251,191,36,.15); color: #fbbf24; }
    .DEL  { background: rgba(239,68,68,.15);  color: #ef4444; }

    .ep-path { color: var(--text); }
    .ep-desc { color: var(--muted); font-size: .72rem; }

    .link-btn {
      display: inline-block;
      margin-top: 1rem;
      padding: .7rem 1.5rem;
      background: linear-gradient(135deg, var(--accent), var(--accent2));
      color: #000;
      font-family: 'JetBrains Mono', monospace;
      font-size: .8rem;
      font-weight: 700;
      border-radius: 8px;
      text-decoration: none;
      letter-spacing: .05em;
      transition: opacity .2s;
    }

    .link-btn:hover { opacity: .85; }

    .info-row {
      display: flex;
      flex-wrap: wrap;
      gap: .5rem;
    }

    .info-tag {
      background: rgba(30,45,64,.8);
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: .3rem .8rem;
      font-family: 'JetBrains Mono', monospace;
      font-size: .72rem;
      color: var(--muted);
    }

    .info-tag strong { color: var(--text); }
  </style>
</head>
<body>
  <div class="header">
    <div>
      <h1>App <span>Containerizada</span></h1>
      <p style="color:var(--muted);font-size:.9rem;margin-top:.3rem">FastAPI · Docker · Segura · Não-root</p>
    </div>
    <div style="margin-left:auto">
      <span class="badge">ONLINE</span>
    </div>
  </div>

  <div class="grid" id="stats">
    <div class="card">
      <div class="card-label">Status</div>
      <div class="card-value" style="color:var(--green)">✓ OK</div>
      <div class="card-sub">Todos os sistemas operando</div>
    </div>
    <div class="card">
      <div class="card-label">Usuário do processo</div>
      <div class="card-value" id="sys-user" style="font-size:1.1rem">—</div>
      <div class="card-sub">Não-root por segurança</div>
    </div>
    <div class="card">
      <div class="card-label">Porta</div>
      <div class="card-value">8000</div>
      <div class="card-sub">uvicorn · 0.0.0.0</div>
    </div>
    <div class="card">
      <div class="card-label">Horário (servidor)</div>
      <div class="card-value" id="clock" style="font-size:1.1rem">—</div>
      <div class="card-sub">UTC</div>
    </div>
  </div>

  <p class="section-title">Endpoints disponíveis</p>
  <div class="endpoints">
    <div class="endpoint"><span class="method GET">GET</span><span class="ep-path">/health</span><span class="ep-desc">Health check</span></div>
    <div class="endpoint"><span class="method GET">GET</span><span class="ep-path">/info</span><span class="ep-desc">Info do ambiente</span></div>
    <div class="endpoint"><span class="method GET">GET</span><span class="ep-path">/items</span><span class="ep-desc">Listar itens</span></div>
    <div class="endpoint"><span class="method POST">POST</span><span class="ep-path">/items</span><span class="ep-desc">Criar item</span></div>
    <div class="endpoint"><span class="method GET">GET</span><span class="ep-path">/items/{id}</span><span class="ep-desc">Buscar item por ID</span></div>
    <div class="endpoint"><span class="method PUT">PUT</span><span class="ep-path">/items/{id}</span><span class="ep-desc">Atualizar item</span></div>
    <div class="endpoint"><span class="method DEL">DEL</span><span class="ep-path">/items/{id}</span><span class="ep-desc">Deletar item</span></div>
    <div class="endpoint"><span class="method POST">POST</span><span class="ep-path">/echo</span><span class="ep-desc">Ecoar mensagem</span></div>
  </div>

  <div class="info-row" id="env-info"></div>

  <br>
  <a class="link-btn" href="/docs">📄 Abrir Swagger UI →</a>

  <script>
    fetch('/info').then(r=>r.json()).then(d=>{
      document.getElementById('sys-user').textContent = d.usuario_processo || '—';
      const env = document.getElementById('env-info');
      [
        ['Python', d.python],
        ['OS', d.sistema_operacional],
        ['Host', d.hostname],
        ['Plataforma', d.plataforma],
      ].forEach(([k,v])=>{
        const t = document.createElement('div');
        t.className = 'info-tag';
        t.innerHTML = `${k}: <strong>${v||'—'}</strong>`;
        env.appendChild(t);
      });
    });

    function tick(){
      document.getElementById('clock').textContent = new Date().toUTCString().split(' ').slice(4,5)[0];
    }
    tick(); setInterval(tick,1000);
  </script>
</body>
</html>
"""
    return HTMLResponse(content=html)


@app.get("/health", tags=["Sistema"])
async def health():
    """Verifica se a aplicação está saudável."""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


@app.get("/info", tags=["Sistema"])
async def info():
    """Retorna informações do ambiente de execução."""
    import getpass
    try:
        usuario = getpass.getuser()
    except Exception:
        usuario = os.environ.get("USER", "desconhecido")

    return {
        "aplicacao": "App Containerizada",
        "versao": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "hostname": platform.node(),
        "sistema_operacional": platform.system(),
        "plataforma": platform.platform(),
        "python": platform.python_version(),
        "usuario_processo": usuario,
        "pid": os.getpid(),
        "porta": 8000,
    }


# ----- CRUD de Items -----

@app.get("/items", tags=["Items"])
async def listar_items():
    """Lista todos os itens cadastrados."""
    return {"items": list(items_db.values()), "total": len(items_db)}


@app.post("/items", status_code=201, tags=["Items"])
async def criar_item(item: Item):
    """Cria um novo item."""
    global next_id
    novo = {"id": next_id, **item.model_dump(), "criado_em": datetime.utcnow().isoformat()}
    items_db[next_id] = novo
    next_id += 1
    return novo


@app.get("/items/{item_id}", tags=["Items"])
async def buscar_item(item_id: int):
    """Busca um item pelo ID."""
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    return items_db[item_id]


@app.put("/items/{item_id}", tags=["Items"])
async def atualizar_item(item_id: int, item: Item):
    """Atualiza um item existente."""
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    atualizado = {"id": item_id, **item.model_dump(), "atualizado_em": datetime.utcnow().isoformat()}
    items_db[item_id] = atualizado
    return atualizado


@app.delete("/items/{item_id}", tags=["Items"])
async def deletar_item(item_id: int):
    """Deleta um item pelo ID."""
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    del items_db[item_id]
    return {"mensagem": f"Item {item_id} deletado com sucesso"}


@app.post("/echo", tags=["Utilitários"])
async def echo(msg: Mensagem):
    """Ecoa a mensagem enviada."""
    return {"original": msg.texto, "eco": msg.texto[::-1], "tamanho": len(msg.texto)}
