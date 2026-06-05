## ⚠ REGRAS CRÍTICAS (ler antes de qualquer execução)

1. **Verificação de viabilidade obrigatória**: antes de gerar, estimar o volume do conteúdo. Se houver risco de supressão por limitação de contexto, informar o usuário antes de executar qualquer função.
2. **Nunca inventar precedentes, súmulas ou fundamentação jurídica.**
3. **Nunca suprimir jurisprudências** — citar exatamente como o usuário apresentar.
4. **Logo SVG sempre inline** — nunca carregar arquivo externo. Copiar o SVG da seção "Logo SVG" abaixo integralmente.
5. **Padding nunca zerado no `@media print`** — exceto `padding-top` do `.doc`, que é substituído pelo `margin-top` do `@page`.
6. **Faixa lateral via `border-left` no `.doc`** — nunca via `position: fixed` ou elemento separado.

### 🔒 REGRA INEGOCIÁVEL — Impressão A4 Dinâmica

O HTML **NUNCA** deve ter altura pré-definida em nenhum contêiner. A quebra de página é controlada exclusivamente pelo browser via `@page` + regras `page-break-*` / `break-*`. Isso é inegociável:

- **PROIBIDO**: `height`, `min-height` ou `max-height` em `.doc` ou qualquer contêiner de layout
- **PROIBIDO**: `position: fixed` ou `position: absolute` para elementos que devem fluir entre páginas
- **OBRIGATÓRIO**: `page-break-inside: avoid` / `break-inside: avoid` em todo elemento atômico (parágrafos, citações, fechamento, itens de lista, linhas de tabela)
- **OBRIGATÓRIO**: `page-break-after: avoid` / `break-after: avoid` em títulos de seção e cabeçalhos
- **OBRIGATÓRIO**: `orphans: 3; widows: 3` em parágrafos longos
- **PERMITIDO**: containers longos (`.box-break`, tabelas grandes) podem quebrar entre páginas — proteção é por item/linha, não pelo container

---
