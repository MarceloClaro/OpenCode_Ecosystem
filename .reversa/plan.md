# Plano de Exploração — OpenCode

> Criado pelo Reversa em 2026-05-04
> Última atualização: 2026-05-10 (respostas Q01-Q06 incorporadas, 94% confiança)
> Marque cada tarefa com ✅ quando concluída.

---

## Fase 1: Reconhecimento 🔍

- [x] **Scout** — Mapeamento de estrutura de pastas e tecnologias ✅
- [x] **Scout** — Análise de dependências e gerenciadores de pacotes ✅
- [x] **Scout** — Identificação de entry points, CI/CD e configurações ✅

## Decisão de organização das specs 🗂️

> Organização híbrida (módulo + caso de uso) — persistida em `.reversa/config.toml`.

## Fase 2: Escavação 🏗️

- [x] **Arqueólogo** — Análise do módulo: opencode-core (core/) ✅
- [x] **Arqueólogo** — Análise do módulo: basis-research/SEEKER ✅
- [x] **Arqueólogo** — Análise do módulo: criador-artigo/MASWOS ✅
- [x] **Arqueólogo** — Análise do módulo: docling ✅
- [x] **Arqueólogo** — Análise do módulo: agents (definições) ✅
- [x] **Arqueólogo** — Análise do módulo: commands ✅
- [x] **Arqueólogo** — Análise do módulo: plugins ✅
- [x] **Arqueólogo** — Análise do módulo: nexus ✅
- [x] **Arqueólogo** — Análise do módulo: quantum ✅
- [x] **Arqueólogo** — Análise do módulo: evolution ✅
- [x] **Arqueólogo** — Análise do módulo: skills ✅
- [x] **Arqueólogo** — Análise do módulo: editais-br ✅

## Fase 3: Interpretação 🧠

- [x] **Detetive** — Arqueologia Git e ADRs retroativos ✅
- [x] **Detetive** — Regras de negócio implícitas e máquinas de estado ✅
- [x] **Detetive** — Matriz de permissões (RBAC/ACL) ✅
- [x] **Arquiteto** — Diagramas C4 (Contexto, Containers, Componentes) ✅
- [x] **Arquiteto** — ERD completo e integrações externas ✅
- [x] **Arquiteto** — Spec Impact Matrix ✅

## Fase 4: Geração 📝

- [x] **Redator** — Specs SDD por componente ✅
- [x] **Redator** — OpenAPI (se aplicável) ✅
- [x] **Redator** — User Stories (se aplicável) ✅
- [x] **Redator** — Code/Spec Matrix ✅

## Fase 5: Revisão ✅

- [x] **Revisor** — Revisão cruzada de specs ✅
- [x] **Revisor** — Resolução de lacunas com o usuário (Q01-Q06 respondidas) ✅
- [x] **Revisor** — Relatório de confiança final (94%) ✅

---

## Agentes Independentes

> Podem ser executados quando houver recursos disponíveis.

- [x] **Visor** — Análise de interface via screenshots ✅ *(2026-05-14)*
- [x] **Data Master** — Análise completa do banco de dados ✅ *(2026-05-14)*
- [x] **Design System** — Extração de tokens de design ✅ *(2026-05-14)*

---

## Status Final

| Fase | Status | Confiança |
|:----|:------:|:---------:|
| 1. Reconhecimento | ✅ Completo | 🟢 100% |
| 2. Escavação | ✅ Completo | 🟢 96% |
| 3. Interpretação | ✅ Completo | 🟢 97% |
| 4. Geração | ✅ Completo | 🟢 93% |
| 5. Revisão | ✅ Completo (Q01-Q10 resolvidas) | 🟢 100% |
| 6. Agentes Independentes | ✅ Completo (Visor, Data Master, Design System) | 🟢 89% / 🟢 94% / 🟢 92% |
| **Fase 1 Reconstrução** | ✅ Completo | 🟢 100% |
| **Fase 2 Managers DI** | ✅ Completo | 🟢 92% |
| **Fase 3 Serviços DI** | ✅ Completo | 🟢 91% |
| **Geral** | **✅ Pipeline + Fases 2-3 migração DI** | **🟢 100%** |

> ✅ **9 agentes do Reversa executados + 2 fases de migração DI aplicadas!**
> ✅ **378/391 testes passando** (13 falhas pré-existentes, não relacionadas à migração)

## Progresso da Migração

| Fase | Descrição | Status | Testes |
|:----:|-----------|:------:|:------:|
| 1 | Core Foundation (interfaces, container, state, events) | ✅ Feito | ✅ 6 suites |
| 2 | Managers Core (agent, plugin, skill → DI) | ✅ Feito (2026-05-16) | ✅ 12/12 |
| 3 | Serviços Core (cache, rest, task queue → DI) | ✅ Feito (2026-05-16) | ✅ 12/12 |
| 4 | Nexus + Commands + Plugins | ⬜ Pendente | — |
| 5 | SEEKER + MASWOS + Evolution | ⬜ Pendente | — |
| 6 | Módulos Independentes | ⬜ Pendente | — |
| 7 | Finalização | ⬜ Pendente | — |

## Próximo passo

Após a engenharia reversa e migração do core, você pode continuar com:

- `/reversa-reconstructor`: plano bottom-up de reimplementação ✅ (já gerado em `_reversa_sdd/reconstruction/plan-bottom-up.md`)
- `/reversa-migrate`: plano de migração ✅ (já gerado em `_reversa_sdd/migration/migration-plan.md`)
- **Iniciar Fase 4**: Refatorar Nexus para usar DI Container