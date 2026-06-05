"""FastAPI application — editais-br."""

from pathlib import Path

from fastapi import FastAPI, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from jinja2 import Environment, FileSystemLoader

from api.auth import AuthMiddleware, ADMIN_USER, ADMIN_PASSWORD, LOGIN_PAGE
from api.database import SessionLocal
from api.models.edital import Edital
from api.routers.editais import router as editais_router
from api.routers.jobs import router as jobs_router
from api.routers.buscar import router as buscar_router

app = FastAPI(
    title="editais-br",
    description="Sistema de monitoramento e análise automática de editais de fomento",
    version="0.1.0",
)

app.include_router(editais_router)
app.include_router(jobs_router)
app.include_router(buscar_router)
app.add_middleware(AuthMiddleware)

jinja_env = Environment(loader=FileSystemLoader("templates"))


def render(name: str, context: dict) -> HTMLResponse:
    """Renderiza um template Jinja2 contornando bug Python 3.14."""
    template_path = Path("templates") / name
    source = template_path.read_text()
    template = jinja_env.from_string(source)
    return HTMLResponse(template.render(context))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Página de login."""
    if request.cookies.get("session_user") == ADMIN_USER:
        return RedirectResponse(url="/", status_code=302)
    return HTMLResponse(LOGIN_PAGE.replace("{error}", ""))


@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    """Processa login."""
    if username == ADMIN_USER and password == ADMIN_PASSWORD:
        response = RedirectResponse(url="/", status_code=302)
        response.set_cookie("session_user", ADMIN_USER, httponly=True, max_age=86400)
        return response
    return HTMLResponse(LOGIN_PAGE.replace("{error}", '<div class="error">Usuário ou senha inválidos</div>'), status_code=401)


@app.get("/portais", response_class=HTMLResponse)
async def portais(request: Request):
    """Lista de portais monitorados."""
    db = next(get_db())
    try:
        from api.models.portal import Portal
        portais_list = db.query(Portal).order_by(Portal.nome).all()
        return render("portais.html", {"request": request, "portais": portais_list})
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    eixo_tematico: str | None = Query(None),
    status: str | None = Query(None),
    valor_min: str | None = Query(None),
    valor_max: str | None = Query(None),
    perfil_elegivel: str | None = Query(None),
):
    """Dashboard com filtros HTMX."""
    # Converte strings vazias do form HTML para None
    vmin = float(valor_min) if valor_min and valor_min.strip() else None
    vmax = float(valor_max) if valor_max and valor_max.strip() else None

    # Padrão: só editais com inscrições abertas
    if not status:
        status = "inscricoes_abertas"
    elif status == "todos":
        status = None

    if request.headers.get("HX-Request"):
        db = next(get_db())
        try:
            query = db.query(Edital)
            if eixo_tematico:
                query = query.filter(Edital.eixos_tematicos.contains([eixo_tematico]))
            if status:
                query = query.filter(Edital.status_inscricao == status)
            if vmin is not None:
                query = query.filter(Edital.valor_max >= vmin)
            if vmax is not None:
                query = query.filter(Edital.valor_min <= vmax)
            if perfil_elegivel:
                query = query.filter(Edital.perfil_elegivel.contains([perfil_elegivel]))

            editais = query.order_by(Edital.criado_em.desc()).limit(100).all()
            editais_data = [
                {
                    "id": str(e.id),
                    "titulo": e.titulo,
                    "financiador": e.financiador,
                    "valor_min": e.valor_min,
                    "valor_max": e.valor_max,
                    "moeda": e.moeda,
                    "status": e.status_inscricao or e.status,
                    "eixos_tematicos": e.eixos_tematicos or [],
                    "resumo": e.resumo,
                }
                for e in editais
            ]
            return render("partials/edital_table.html", {"request": request, "editais": editais_data})
        finally:
            db.close()

    return render("dashboard.html", {"request": request})


@app.get("/edital/{edital_id}", response_class=HTMLResponse)
async def edital_detail(request: Request, edital_id: str):
    """Página de detalhe do edital."""
    import uuid

    try:
        uid = uuid.UUID(edital_id)
    except ValueError:
        return HTMLResponse("ID inválido", status_code=422)

    db = next(get_db())
    try:
        edital = db.query(Edital).filter(Edital.id == uid).first()
        if not edital:
            return HTMLResponse("Edital não encontrado", status_code=404)

        data = {
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
            "contrapartida_exigida": False,
            "resumo": edital.resumo,
            "raw_text": edital.raw_text,
            "requisitos_json": edital.requisitos_json,
        }
        return render("detail.html", {"request": request, "edital": data})
    finally:
        db.close()
