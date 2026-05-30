# editais-br — Claude Code

> Engenheiro de software pleno. Soluções simples e diretas. Sem over-engineering.

## Protocolo obrigatório — toda sessão

1. Leia `.claude/memory/MEMORY.md` — stack, estado atual, idioma (`pt-br`)
2. Leia `.claude/specs/INDEX.md` — qual issue está em andamento
3. Consulte `.claude/memory/lessons.md` antes de qualquer decisão técnica
4. Ao pausar → atualize a spec correspondente e o `INDEX.md`
5. Ao descobrir algo relevante → registre em `lessons.md` ou `decisions.md`

## Regras inegociáveis deste projeto

- **TDD red/green** — teste antes do código, sempre
- **Uma issue por vez** — não abra escopo além da issue atual
- **Desacoplamento** — cada conector/extractor/agent é independente
- **OOP** — herdar de `BaseConnector`, `BaseExtractor`, `BaseAgent`
- **Branch por issue** — `feat/issue-N-descricao`
- **PR fecha issue** — `Closes #N` no body
- **Nunca commitar `.env`**
- **Stop-the-line** — falha inesperada → pare, preserve evidência, re-planeje

## Mapa de navegação

| Preciso de | Onde está |
|---|---|
| Contexto, stack, estado atual | `.claude/memory/MEMORY.md` |
| Qual issue trabalhar agora | `.claude/specs/INDEX.md` |
| Spec completa do sistema | `.claude/specs/sistema-monitoramento-editais.md` |
| Erros a evitar | `.claude/memory/lessons.md` |
| Decisões arquiteturais | `.claude/memory/decisions.md` |
| URLs oficiais dos portais | `.claude/references.md` |
| Issues abertas | `gh issue list --repo ecodelearn/editais-br --state open` |

## Definition of Done

Uma issue só é **done** quando:
- [ ] Testes passando (`pytest`)
- [ ] Código revisado (sem lógica desnecessária)
- [ ] Spec atualizada em `.claude/specs/`
- [ ] PR aberto com `Closes #N`

## Padrões globais

→ https://github.com/ecodelearn/claude-memories/blob/main/global-index.md
