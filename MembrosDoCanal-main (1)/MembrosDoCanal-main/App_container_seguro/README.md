# 🚀 App Containerizada — FastAPI + Docker Seguro

Aplicação FastAPI completa, pronta para rodar no Dockerfile com usuário não-root.

---

## 📁 Estrutura

```
app_projeto/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
└── src/
    ├── __init__.py
    └── app.py
```

---

## ▶️ Como rodar

### Com Docker Compose (recomendado)

```bash
docker compose up --build
```

### Com Docker diretamente

```bash
# Build
docker build -t app-containerizada .

# Run
docker run -p 8000:8000 app-containerizada
```

### Sem Docker (desenvolvimento local)

```bash
pip install -r requirements.txt
uvicorn src.app:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🌐 Acessar

| URL | Descrição |
|-----|-----------|
| http://localhost:8000 | Dashboard visual |
| http://localhost:8000/docs | Swagger UI (testar endpoints) |
| http://localhost:8000/redoc | ReDoc |
| http://localhost:8000/health | Health check |
| http://localhost:8000/info | Info do ambiente |

---

## 🔒 Segurança aplicada (conforme Dockerfile)

1. **Imagem base com tag exata** — `python:3.11.9-alpine3.19` (sem `:latest`)
2. **Alpine Linux** — imagem mínima, menor superfície de ataque
3. **Usuário não-root** — `appuser:appgroup` criado sem privilégios
4. **Cache de dependências** — `requirements.txt` copiado antes do código
5. **Ownership correto** — `--chown=appuser:appgroup` em todos os `COPY`
6. **EXPOSE apenas documenta** — porta não publicada automaticamente
7. **`--no-cache-dir`** — pip não guarda cache na imagem

---

## 📡 Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/` | Dashboard HTML |
| GET | `/health` | Health check |
| GET | `/info` | Info do ambiente |
| GET | `/items` | Listar itens |
| POST | `/items` | Criar item |
| GET | `/items/{id}` | Buscar item |
| PUT | `/items/{id}` | Atualizar item |
| DELETE | `/items/{id}` | Deletar item |
| POST | `/echo` | Ecoar mensagem |
