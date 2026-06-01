# SPEC — Semana 2: Implementação LGPD no Ecossistema OpenCode

## Objetivo
Implementar as 5 skills/agentes propostos na Matriz de Conformidade para elevar a cobertura LGPD de **23% → 80%+** no requisito R5 (Proteção de Dados Pessoais).

## Escopo

| # | Skill/Agente | Lacuna | Gravidade | Status |
|---|-------------|--------|-----------|--------|
| L1 | `lgpd-crypto` | Criptografia/anonimização | Crítica | Pendente |
| L2 | `lgpd-dpo` | Consentimento/DPO | Alta | Pendente |
| L3 | `lgpd-access-control` | Controle de acesso/RBAC | Alta | Pendente |
| L4 | Pipeline RPIA (via ANP) | Relatório de impacto | Média | Pendente |
| L5 | `lgpd-data-subject-rights` | Portabilidade/eliminação | Média | Pendente |

## Arquitetura
- Skills no padrão OpenCode: `SKILL.md` + `scripts/` + `tests/`
- Integração via grafo de conhecimento (arestas `uses`, `depends_on`, `references`)
- Compatível com o ecossistema existente (code-graph.db, entity-ner-reader, ANP)

## Critérios de Sucesso
1. Cobertura R5 ≥ 80% na matriz de conformidade
2. Cada skill implementada com testes unitários
3. Grafo enriquecido com novas entidades e arestas LGPD
4. Documentação de cada skill em PT-BR formal
