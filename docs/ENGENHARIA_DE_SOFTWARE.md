# Engenharia de Software com Agentes Inteligentes — OpenCode Ecosystem

> "IA + Processo = Software de Verdade. A IA amplifica o que já existe: se existe método, amplifica qualidade. Se existe caos, amplifica caos."
> — Engenharia de Software com Agentes Inteligentes (Sandeco, 2026)

---

## Visão Geral

O OpenCode Ecosystem aplica **disciplinas formais de engenharia de software** a um ecossistema de 186 componentes com agentes inteligentes. Esta documentação descreve como cada disciplina clássica da engenharia de software foi implementada.

| Disciplina | Implementação | Artefatos |
|-----------|---------------|-----------|
| **SDD** (Spec-Driven Development) | Spec antes de código para todos os 186 componentes | `specs/` — 26 arquivos, 5 dimensões por spec |
| **TDD** (Test-Driven Development) | Teste como contrato da spec | `tests/` — 100+ unit tests, 10 cenários de integração |
| **CI/CD** | Pipeline automatizado de 5 gates | `.github/workflows/ci.yml` |
| **Manutenção** (SWEBOK) | Classificação de 186 componentes por categoria | `specs/component-registry.md` |
| **Git Safety** | Commit-before-AI, worktree isolation | `using-git-worktrees` v2.0 |
| **ADR** | 5 decisões arquiteturais documentadas | `specs/adr/` |
| **Arquitetura em Camadas** | 3 camadas: MCP→Skill→Agent | ADR-002 |

---

## 1. Spec-Driven Development (SDD)

### Princípio
> "O agente implementa o que foi especificado. Se a spec estava errada, o agente implementa o erro com eficiência impecável." — Cap. 6

### Implementação
Toda skill, agente e módulo core tem uma **spec de 5 dimensões**:

1. **Comportamento Esperado** — o que faz, fluxo feliz, o que NÃO faz
2. **Usuários e Contexto** — quem usa, volume, ambiente, dependências
3. **Restrições** — limites de segurança, performance, escala, compatibilidade
4. **Casos de Borda** — entrada inválida, timeout, dependência offline, concorrência
5. **Critérios de Aceitação** — verificáveis, cada um coberto por teste

### Fluxo SDD
```
SPEC (5 dimensões) → REVIEW (checklist) → SKILL (implementar) → TEST (validar) → REGISTER (component registry) → CI (validar)
```

### Cobertura
- **186/186 componentes** com spec documentada (100%)
- **10 módulos core** com specs individuais
- **48 skills** com specs por categoria
- **50 agentes** documentados
- **41 MCPs** catalogados
- **8 plugins** especificados

### Template de Spec Mínima
```markdown
# Spec: [nome-do-componente]
## 1. Comportamento Esperado
## 2. Usuários e Contexto 
## 3. Restrições
## 4. Casos de Borda
## 5. Critérios de Aceitação
- [ ] Critério 1
- [ ] Critério 2
```

---

## 2. Test-Driven Development (TDD)

### Princípio
> "O teste é a tradução executável da spec: se o teste passa, a spec foi atendida." — Cap. 6

### Pirâmide de Testes
```
        ╱ E2E ╲          ← 3 cenários críticos (humano revisa)
       ╱ Integração ╲     ← 10 cenários cross-component
      ╱ Unitários ╲       ← 100+ testes (agente gera)
```

### Cenários de Integração (10)
1. Agent → Skill → MCP (cadeia de delegação)
2. Evolution Cycle (SENSE→DISCOVER→INSTALL→VERIFY→EVOLVE→LEARN)
3. Resiliência State Manager (SQLite corrompido → FileStateManager)
4. Health Check Cross-Component
5. Knowledge Graph CRUD
6. IPC Comunicação
7. Plugin Load/Unload
8. Spec Coverage Verification
9. Token Budget Enforcement
10. CI Pipeline Gates

### CI Pipeline (5 Gates)
```
PUSH → [Lint] → [Unit Tests] → [Spec Coverage] → [Integration] → [Health Check] → ✅
```

| Gate | Ferramenta | Critério |
|------|-----------|----------|
| Lint | ruff + eslint | Zero erros |
| Unit Tests | pytest | 100% pass |
| Spec Coverage | spec_coverage.py | ≥ 80% |
| Integration | pytest | 10 cenários passam |
| Health Check | health_check.py | Status OK |

---

## 3. Manutenção (SWEBOK)

### Princípio
> "A manutenção consome 67% do custo total do ciclo de vida do software. A fase que recebe menos atenção no planejamento é a que mais custa." — Pressman, via Cap. 4

### Categorias SWEBOK Aplicadas

| Categoria | % do Esforço | Componentes |
|-----------|-------------|-------------|
| **Evolutiva** | 50% | agent_manager, plugin_manager, task_queue, ai-engineering-harness, reasoning-orchestrator |
| **Adaptativa** | 25% | state_manager, cache, rest_client, state_file, using-git-worktrees |
| **Corretiva** | 21% | errors, validators, code-review, verification-before-completion |
| **Preventiva** | 4% | health service, CI pipeline, maintenance-first, token-efficiency |

### Design Patterns para Manutenibilidade
- **Repository** — separa negócio do banco (camada de dados isolada)
- **Strategy** — comportamento intercambiável (3+ variações)
- **Observer** — desacopla emissor do receptor (eventos pub/sub)
- **Singleton** — instância única para recursos compartilhados
- **Factory Method** — cria objetos sem acoplar a classes concretas

### Arquitetura em 3 Camadas
```
┌─────────────────────────┐
│  Agentes (125)          │ ← Comportamento autônomo
├─────────────────────────┤
│  Skills (106)           │ ← Capacidades especializadas  
├─────────────────────────┤
│  MCPs (41) + Plugins    │ ← Infraestrutura
└─────────────────────────┘
```
Regra: uma camada só conhece a imediatamente inferior. Nunca o contrário.

---

## 4. Git Safety Protocol

### Princípio
> "Sem Git, o agente não tem memória do que o código era antes. Velocidade sem reversibilidade é carro sem freio." — Cap. 3

### Protocolo Commit-Antes-de-Agent
```
1. COMMIT checkpoint (estado atual funcionando)
2. WORKTREE ou BRANCH (isolar experimento)
3. AGENTE (instruir, gerar, iterar)
4. AVALIAR (testar, revisar diff)
5. DECIDIR (merge ou restore/revert)
```

### Worktree Isolation
Para experimentos arriscados, worktree isola completamente:
```bash
git worktree add -b feat/experimento ../projeto-exp
# Agente trabalha na pasta isolada
# Se funcionar: merge. Se não: git worktree remove.
```

### Convenção de Branches
- `feat/` — nova funcionalidade
- `fix/` — correção de bug
- `refactor/` — reorganização sem mudança de comportamento
- `chore/` — infraestrutura, dependências
- `spec/` — documentação de especificação

---

## 5. Architecture Decision Records (ADRs)

| ID | Decisão | Status |
|----|---------|--------|
| ADR-001 | Token Budget Rígido para Skills (≤2.500 tokens) | active |
| ADR-002 | Arquitetura em 3 Camadas (MCP→Skill→Agent) | active |
| ADR-003 | DI Container como Backbone de Integração | active |
| ADR-004 | Progressive Disclosure como Padrão de Design | active |
| ADR-005 | Unified State Manager (SQLite + File) | active |
| ADR-006 | Spec-First para Todas as Novas Skills | active |
| ADR-007 | CI Pipeline com Spec Coverage Gate | proposed |
| ADR-008 | Component Registry com SWEBOK Categories | proposed |

---

## 6. AI Engineering Harness

### 5 Regras
0. **Git Checkpoint Obrigatório** — commit antes de cada ação significativa do agente
1. **Worktree para Experimentos** — isolamento total para mudanças arriscadas
2. **Spec Antes de Código** — nunca instruir agente sem spec documentada
3. **Teste como Contrato** — cada critério de aceitação tem teste automatizado
4. **Revisão Humana Obrigatória** — ler diff, rodar testes, questionar antes de aceitar

### Checklist Anti-Vibe-Coding
- [ ] Fiz commit do estado atual?
- [ ] Criei branch isolada?
- [ ] Tenho spec mínima documentada?
- [ ] Usei worktree para experimento arriscado?
- [ ] Revisei o diff antes de aceitar?
- [ ] Rodei os testes depois da mudança?

---

## 7. Métricas de Qualidade

| Métrica | Valor Atual | Meta | Status |
|---------|------------|------|--------|
| Cobertura de Spec | 100% (186/186) | ≥ 95% | 🟢 |
| Testes Unitários | 100+ | ≥ 100 | 🟢 |
| Testes de Integração | 10 cenários | ≥ 10 | 🟢 |
| CI Pipeline Gates | 5 | 5 | 🟢 |
| ADRs Documentadas | 5 | ≥ 3 | 🟢 |
| Component Registry | 100% | 100% | 🟢 |
| Health Check Automatizado | Sim | Sim | 🟢 |
| Zero CJK Leaks | Sim | Sim | 🟢 |

---

## 8. Estrutura de Documentação

```
specs/                              ← Documentação de engenharia
├── adr/ (5 ADRs)                   ← Decisões arquiteturais
├── core/ (10 specs)                ← Módulos Python
├── skills/ (48 skills)             ← Especificações por categoria 
├── agents/ (50 agentes)            ← Pipeline completa
├── mcps/ (41 MCPs)                 ← Ativos + inativos
├── plugins/ (8 plugins)            ← Principais + lib
├── integration/ (CI + harness)     ← Pipeline e testes
├── SDD-ONBOARDING.md               ← Fluxo spec-first
├── component-registry.md           ← 186 entradas SWEBOK
└── spec-coverage-report.md         ← Relatório de cobertura

scripts/
├── spec_coverage.py                ← Verificação automatizada
└── health_check.py                 ← Health check automático

tests/
└── integration/
    └── test_ecosystem_integration.py ← 10 cenários cross-component

.github/workflows/
└── ci.yml                          ← 5 gates CI
```

---

## Referências

- **Livro base:** Engenharia de Software com Agentes Inteligentes (Sandeco, 2026)
- **SWEBOK:** IEEE Software Engineering Body of Knowledge
- **Pressman:** Engenharia de Software — Uma Abordagem Profissional
- **Standish Group:** CHAOS Report 2020 (31% projetos bem-sucedidos)
- **Manifesto Ágil:** 4 valores, 12 princípios (Snowbird, 2001)
