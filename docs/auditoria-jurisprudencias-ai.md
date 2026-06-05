# Auditoria de Mapeamento — Jurisprudencias.ai

**Data**: 04/06/2026  
**Token**: `jur_b0b9c8719...` (plano gratuito)  
**Ambiente**: Windows 11, PowerShell 5.1, curl.exe  

---

## 1. Endpoints da API REST

| Endpoint | Método | Parâmetros | Status | Observações |
|----------|--------|------------|--------|-------------|
| `/api/v1/courts` | GET | — | ✅ 200 | Lista todos os tribunais disponíveis |
| `/api/v1/courts/{id}/decisions` | GET | `q` (obrigatório, FTS5), `page` (0-based), `pub_from`, `pub_to` (ISO), `trial_from`, `trial_to` | ✅ 200 | Busca textual com FTS5 |
| `/api/v1/courts/{id}/decisions/lookup` | GET | `n` (número do processo) | ✅ 200/404 | Consulta por número do processo |

**Formato de resposta (search)**: Array JSON de objetos com:
- `process_number` — número do processo
- `publication_date` — data de publicação (ISO)
- `trial_date` — data do julgamento (ISO)
- `excerpt` — ementa truncada
- `url` — link para o tribunal de origem

**Formato de resposta (lookup)**: Objeto único com:
- `summary` — ementa completa em Markdown
- `url` — link para o tribunal de origem
- `court` — slug do tribunal

---

## 2. Tribunais Confirmados (plano gratuito)

| Tribunal | Slug | Decisões | Observações |
|----------|------|----------|-------------|
| STF | `stf` | ~396K | API própria bloqueada por AWS WAF; API deles funciona |
| STJ | `stj` | ~420K | ✅ Testado |
| TST | `tst` | ~331K | ✅ Testado (via count no `/courts`) |
| TRF-3 | `trf3` | ~590K | ✅ Testado |
| TRF-4 | `trf4` | ~1.5M | ✅ Testado (via count) |
| TJPR | `tjpr` | ~416K | ✅ Testado (via count) |
| TJRJ | `tjrj` | ~194K | ✅ Testado (via count) |
| TJRS | `tjrs` | ~2.7M | ✅ Testado |
| TJSC | `tjsc` | ~723K | ✅ Testado (via count) |
| TJSP | `tjsp` | ~3.5M | ✅ Testado |
| CARF | `carf` | ~162K | ✅ Testado |

**Total aproximado**: ~10,9 milhões de decisões indexadas.

---

## 3. Operadores FTS5 Confirmados

| Operador | Exemplo | Funciona |
|----------|---------|----------|
| Frase exata | `"dano moral"` | ✅ |
| AND | `responsabilidade AND dano` | ✅ |
| OR | `indenização OR reparação` | ✅ |
| NOT | `indenização NOT veículo` | ✅ |
| Prefixo | `indeniza*` (inferido) | ✅ (padrão FTS5) |
| Data | `pub_from=2025-01-01&pub_to=2025-12-31` | ✅ |

---

## 4. Limites do Plano Gratuito

| Recurso | Limite | Evidência |
|---------|--------|-----------|
| Buscas (`search_decisions`) | **5/dia** | Confirmado pelo usuário + erro `rate_limit_exceeded` (429) ao exceder |
| Consultas (`lookup_decision`) | **Ilimitado** (aparentemente) | Funcionou após rate limit estourado |
| Tribunais disponíveis | **11** | Retornados por `GET /courts` |
| Histórico de buscas | Não disponível no gratuito | — |

**Mensagem de erro ao exceder limite**:
```json
{"error":{"code":"rate_limit_exceeded","message":"Daily API limit reached. Upgrade your plan for higher limits.","status":429}}
```

**Headers `X-RateLimit-*`**: Não foi possível capturar — `Invoke-WebRequest` indisponível em NonInteractive mode. Presentes nas respostas conforme documentação.

---

## 5. Paginação

- `page` é **0-based** (page=0 = primeira página)
- Retorna **10 resultados por página** (fixo, aparentemente)
- page=100 retorna array vazio (fim dos resultados)
- Após rate limit estourado, todas as buscas retornam 429

---

## 6. Servidor MCP

| Item | Detalhe |
|------|---------|
| URL | `jurisprudencias.ai/mcp` |
| Transporte | Streamable HTTP |
| Autenticação | OAuth 2.0 DCR + PKCE |
| Ferramentas | `list_courts` (sem params), `search_decisions` (q, court_slug, page, pub_from/pub_to, trial_from/trial_to), `lookup_decision` (court_slug, decision_number) |
| Clientes compatíveis | Claude Desktop, Claude Code (MCP Connector) |

---

## 7. Skill do Claude Code

| Item | Detalhe |
|------|---------|
| URL oficial | `jurisprudencias.ai/claude-skill.md` |
| Instalação local | `~/.config/opencode/skills/jurisprudencia.md` |
| Tamanho | 8,8 KB |
| Auto-update | Referencia `localhost:3000` — placeholder |
| Ferramenta permitida | `Bash(curl *)` |

---

## 8. Observações Técnicas

1. **STF via API própria**: Bloqueado por AWS WAF com `challenge` → HTTP 202 sem corpo. A API do Jurisprudencias.ai contorna isso — STF funciona normalmente via eles.
2. **JUIT, DataJud, MPF**: URLs não resolvem (DNS sem resposta) a partir deste ambiente.
3. **Token expiração**: Não documentado. Assumir que não expira enquanto a conta estiver ativa.
4. **Discrepância de tribunais**: Blog (31 mar 2026) afirma "100+ tribunais em planos pagos" — plano gratuito mostra 11.
5. **curl.exe vs Invoke-WebRequest**: `curl.exe -s` funciona em NonInteractive mode; `Invoke-WebRequest` não.
6. **Autocomplete `/` na query**: Documentado, não testado.

---

## 9. Comandos Úteis (PowerShell)

```powershell
# Busca textual
curl.exe -s -H "Authorization: Bearer $env:JURISPRUDENCIAS_API_TOKEN" `
  "https://jurisprudencias.ai/api/v1/courts/tjsp/decisions?q=dano+moral&page=0"

# Consulta por número
curl.exe -s -H "Authorization: Bearer $env:JURISPRUDENCIAS_API_TOKEN" `
  "https://jurisprudencias.ai/api/v1/courts/stf/decisions/lookup?n=ARE%201587011%20AgR"

# Listar tribunais
curl.exe -s -H "Authorization: Bearer $env:JURISPRUDENCIAS_API_TOKEN" `
  "https://jurisprudencias.ai/api/v1/courts"
```

---

## 10. Recomendações

1. **Upgrade de plano** se precisar de mais de 5 buscas/dia ou tribunais adicionais
2. **Usar `lookup_decision`** sempre que possível (não consome limite de busca)
3. **Cache local** das decisões consultadas para evitar re-busca
4. **Monitorar** se o token realmente não expira
5. **Configurar MCP** via Claude Desktop para uso interativo sem curl
