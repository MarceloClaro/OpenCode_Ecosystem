---
name: plan-generator
description: >
  Gera planos de execução para engenharia reversa em etapas incrementais,
  inspirado pelo simulation_config_generator.py do MiroFish. Produz planos
  com escopo definido, módulos identificados, tarefas geradas e dependências
  resolvidas — tudo em stages para evitar estouro de contexto.
  Use quando precisar planejar uma análise de engenharia reversa ou qualquer
  pipeline multi-estágio de análise de código.
license: MIT
compatibility: opencode
allowed-tools: Read, Grep, Glob, Write
metadata:
  author: Reversa Engine (padrão MiroFish)
  version: "1.0.0"
  domain: planning
  triggers: plan, generate plan, planejar, gerar plano, planning
  role: planner
  scope: planning
  output-format: markdown
  related-skills: architecture-designer, spec-miner, planning-and-task-breakdown
  inspired-by: MiroFish simulation_config_generator.py (geração em 4 etapas)
---

# Plan Generator — Geração de Planos em Etapas

Inspirado pelo `simulation_config_generator.py` do MiroFish, que gera
configurações complexas de simulação em **4 etapas sequenciais** para
evitar estouro de contexto e garantir consistência:

```
MiroFish:   Time Config → Event Config → Agent Config → Platform Config
OpenCode:   Scope → Modules → Tasks → Dependencies → Resources
```

## Arquitetura (Geração em Stage)

```
┌────────────────────────────────────────────────────────────┐
│                    PLAN GENERATOR                           │
│  (Inspirado no simulation_config_generator.py do MiroFish)  │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  Stage 1: SCOPE ───► Stage 2: MODULES ───► Stage 3: TASKS │
│  (definição do      (identificação dos   (geração das       │
│   escopo)            módulos)             tarefas)          │
│                                                             │
│  Stage 4: DEPS ───► Stage 5: RESOURCES                     │
│  (resolução de      (estimativa de                         │
│   dependências)      recursos)                              │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

## Quando Usar

| Cenário | Descrição |
|---------|-----------|
| Nova análise Reversa | Gerar o plano completo de engenharia reversa |
| Projeto legado grande | Dividir em módulos e etapas gerenciáveis |
| Auditoria de código | Planejar cobertura por área (security, perf, arch) |
| Onboarding em codebase | Plano de exploração para novos desenvolvedores |

## Workflow (5 Stages)

### Stage 1: SCOPE — Definição de Escopo

**Input:** Repositório/diretório alvo, contexto do projeto

1. **Identifique o tipo de projeto:**
   - Web app (frontend + backend)
   - API/microserviço
   - CLI / ferramenta
   - Biblioteca / framework
   - Monorepo
   - Mobile app

2. **Identifique a stack principal:**
   - Linguagem(s) predominante(s)
   - Framework(s)
   - Banco de dados
   - Infraestrutura (Docker, cloud, etc.)

3. **Defina o escopo da análise:**
   ```
   Escopo: [completo | módulos específicos | camada específica]
   Profundidade: [essencial | completo | detalhado]
   Foco: [estrutura | segurança | performance | arquitetura | tudo]
   ```

**Output:** Declaração de escopo com objetivos claros e critérios de sucesso.

### Stage 2: MODULES — Identificação de Módulos

**Input:** Escopo definido + varredura do filesystem

1. **Mapeie a estrutura de diretórios** (use `glob`)
2. **Identifique módulos funcionais:**
   - Por diretório (cada subdiretório `src/` geralmente é um módulo)
   - Por arquivo de entrada (main, index, router)
   - Por framework (controllers, services, models, components)

3. **Classifique cada módulo:**
   ```
   | Módulo | Tipo | Tamanho | Linguagem | Prioridade |
   |--------|------|---------|-----------|------------|
   | auth/  | core  | 2.1KB  | Python    | alta       |
   | api/   | core  | 15KB   | Python    | alta       |
   | utils/ | support | 3KB | Python    | média      |
   ```

**Output:** Lista de módulos com classificação e prioridade.

### Stage 3: TASKS — Geração de Tarefas

**Input:** Módulos identificados

Para cada módulo, gere tarefas específicas baseadas no tipo:

```
Módulo: [nome]
Tipo: [core | support | config | test | docs]
Tarefas:
  1. [Análise de estrutura] — mapear arquivos e dependências
  2. [Análise de lógica] — extrair regras de negócio
  3. [Análise de segurança] — checklist OWASP específico do módulo
  4. [Documentação] — gerar especificações
```

**Estratégia de batching** (como o MiroFish faz com agent configs):
- Módulos core → tarefas individuais (máximo detalhe)
- Módulos support → tarefas agrupadas
- Módulos config/docs → tarefa única

**Output:** Lista completa de tarefas organizadas por módulo.

### Stage 4: DEPS — Resolução de Dependências

**Input:** Tarefas geradas

1. **Identifique dependências entre tarefas:**
   ```
   Tarefa A (mapear DB schema) → Tarefa B (analisar queries) → Tarefa C (otimizar queries)
   ```

2. **Identifique paralelismo:**
   - Tarefas independentes podem rodar em paralelo
   - Tarefas com dependência formam pipeline

3. **Gere o grafo de dependências:**
   ```
   Pipeline Principal:
     ├── Stage 1: Scout (análise de superfície)
     ├── Stage 2: Archaeologist (análise profunda) ──[depende de Stage 1]
     │   ├── 2.1: Módulo Auth ──[independe de 2.2]
     │   └── 2.2: Módulo API  ──[independe de 2.1]
     ├── Stage 3: Detective ──[depende de Stage 2]
     └── Stage 4: Writer ──[depende de Stage 3]
   ```

**Output:** Grafo de dependências com tasks paralelas identificadas.

### Stage 5: RESOURCES — Estimativa de Recursos

**Input:** Tarefas com dependências resolvidas

Estime para cada tarefa:

```
| Tarefa | Arquivos | Linhas | Tokens (est.) | Complexidade |
|--------|----------|--------|---------------|-------------|
| Scout  | ~50      | ~10K   | ~250K         | baixa       |
| Arch.  | ~120     | ~30K   | ~750K         | alta        |
```

**Fórmula de estimativa:**
```
Tokens Estimados = Linhas de código × 2.5 × Fator de Complexidade
Tempo Estimado = Tokens / 2000 (assumindo 2K tokens/min de análise)

Fator de Complexidade:
- Baixa: 1.0 (scripts, configs)
- Média: 1.5 (APIs, serviços)
- Alta: 2.0 (lógica de negócio complexa, algoritmos)
```

**Output:** Tabela de estimativas com recomendações de checkpoint.

## Output Template

````markdown
# Plano de Análise — [projeto]

## Escopo
**Tipo:** [web/mobile/cli/lib/monorepo]
**Stack:** [linguagens, frameworks, DB]
**Profundidade:** [essencial/completo/detalhado]
**Foco:** [estrutura/segurança/performance/arquitetura/tudo]

## Módulos Identificados
| Módulo | Tipo | Tamanho | Prioridade | Agente Responsável |
|--------|------|---------|------------|-------------------|

## Tarefas
### Pipeline Principal
1. [Stage 1 — Nome]
   - [ ] Tarefa 1.1
   - [ ] Tarefa 1.2

### Tarefas Paralelas
| Tarefa | Módulo | Agente | Estimativa |
|--------|--------|--------|------------|

## Grafo de Dependências
```
[ASCII graph do pipeline]
```

## Estimativas
| Fase | Tokens (est.) | Tempo (est.) | Checkpoints |
|------|---------------|--------------|-------------|

## Recomendações
- [Checkpoints sugeridos]
- [Riscos identificados]
- [Dicas de execução]
````

## Regras

### MUST DO
- Gerar em stages (nunca tudo de uma vez)
- Identificar tarefas paralelas para acelerar execução
- Incluir estimativas de tokens/tempo
- Sugerir checkpoints para evitar estouro de contexto
- Listar riscos e dependências críticas

### MUST NOT DO
- Pular a etapa de dependências
- Assumir que todas tarefas são sequenciais
- Ignorar o tamanho real dos módulos
- Deixar de identificar gargalos de execução
