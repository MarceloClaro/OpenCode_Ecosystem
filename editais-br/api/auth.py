"""Autenticação simples via sessão + senha (MVP).

Protege todas as rotas exceto /health, /docs, /openapi.json e /login.
Credenciais via variáveis de ambiente: ADMIN_USER, ADMIN_PASSWORD.
"""

import os
from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from starlette.middleware.base import BaseHTTPMiddleware

ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "editais2026")

PUBLIC_PATHS = {"/health", "/docs", "/openapi.json", "/redoc", "/login", "/static", "/buscar"}


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware que verifica sessão de login em todas as rotas."""

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Rotas públicas
        if path in PUBLIC_PATHS or path.startswith("/docs") or path.startswith("/openapi"):
            return await call_next(request)

        # Verifica sessão
        session_user = request.cookies.get("session_user")
        if session_user != ADMIN_USER:
            # API: retorna 401
            if path.startswith("/editais") or path.startswith("/portais") or path.startswith("/jobs"):
                raise HTTPException(status_code=401, detail="Autenticação necessária")
            # Web: redireciona para login
            return RedirectResponse(url="/login", status_code=302)

        return await call_next(request)


LOGIN_PAGE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>editais-br — Login</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: #1a1a2e; display: flex; align-items: center; justify-content: center; min-height: 100vh; }
        .login-box { background: white; padding: 2.5rem; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.3); width: 100%; max-width: 400px; }
        h1 { color: #1a1a2e; margin-bottom: 0.5rem; }
        .error { color: #dc3545; margin-top: 0.5rem; }
    </style>
</head>
<body>
    <div class="login-box">
        <h1>📋 editais-br</h1>
        <p class="text-muted mb-4">Monitoramento de editais de fomento</p>
        <form method="post" action="/login">
            <div class="mb-3">
                <label class="form-label">Usuário</label>
                <input type="text" name="username" class="form-control" required autofocus>
            </div>
            <div class="mb-3">
                <label class="form-label">Senha</label>
                <input type="password" name="password" class="form-control" required>
            </div>
            <button type="submit" class="btn btn-primary w-100">Entrar</button>
            {error}
        </form>
    </div>
</body>
</html>"""
