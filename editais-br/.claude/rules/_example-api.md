---
paths:
  - "src/api/**"
  - "src/routes/**"
  - "src/controllers/**"
  - "src/handlers/**"
---

> **TEMPLATE** — personalize para seu projeto ou delete se não se aplicar.
> Esta rule carrega automaticamente apenas quando Claude trabalha com arquivos que correspondem aos paths acima.
> Renomeie para `api.md` e remova este aviso quando estiver pronto.

# Convenções de API — [project-name]

<!-- Adicione suas regras específicas de API aqui. Exemplos: -->

<!-- ## Endpoints
- Nomenclatura REST: substantivos no plural, sem verbos (/users, não /getUsers)
- Versionamento: /api/v1/...
- Shape padrão de resposta: { data, error, meta }

## Validação
- Valide todos os inputs na borda do sistema (zod / joi / class-validator)
- Nunca confie em IDs fornecidos pelo cliente para autorização — sempre verifique ownership

## Tratamento de erros
- HTTP 400: erro do cliente (input inválido)
- HTTP 401: não autenticado
- HTTP 403: não autorizado (autenticado mas sem permissão)
- HTTP 422: validação falhou
- HTTP 500: erro do servidor — nunca exponha stack traces ao cliente

## Segurança
- Sanitize todos os inputs do usuário
- Apenas queries parametrizadas — nunca concatenação de strings em SQL
- Rate-limit em endpoints sensíveis (auth, reset de senha) -->
