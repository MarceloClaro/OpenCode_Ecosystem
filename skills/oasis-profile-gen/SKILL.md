---
name: oasis-profile-gen
description: >
  Gera perfis de agente IA (personas) a partir de entidades de um grafo de
  conhecimento. Inspirado pelo OASIS Profile Generator do MiroFish-Offline
  (oasis_profile_generator.py, simulation_config_generator.py).
  Converte nós do grafo (pessoas, organizações, conceitos) em personas
  estruturadas com bio, persona, interesses, MBTI, tópicos e estilo de fala.
  Use quando precisar criar agentes simulados realistas a partir de dados
  reais extraídos de documentos ou bases de conhecimento.
license: MIT
compatibility: opencode
allowed-tools: Read, Grep, Glob, Bash, Write
metadata:
  author: Reversa Engine (padrão MiroFish-Offline OASIS)
  version: "2.0.0"
  domain: simulation
  triggers: perfil, persona, profile, oasis, agente simulado, simulação
  role: generator
  scope: simulation
  output-format: json
  related-skills: code-graphrag, hybrid-graph-retrieval
  inspired-by: MiroFish-Offline oasis_profile_generator.py, simulation_config_generator.py (AgentActivityConfig)
---

# OASIS Profile Generator — Personas de Agente a partir de Grafos

Inspirado pelo **OASIS (Opinion Agent Simulation Immersion System)** do
MiroFish-Offline. Converte entidades de um grafo de conhecimento em perfis
detalhados de agente para simulações multi-plataforma (Twitter, Reddit).

## Arquitetura (Padrão OASIS Profile)

```
MiroFish-Offline:  EntityReader → OasisProfileGenerator → Profile Files (JSON/CSV)
                          ↓                    ↓
                   GraphStorage (Neo4j)    LLM Prompt Templates

OpenCode:         GraphRAG Query → Profile Builder → Profile Output (JSON)
                          ↓                    ↓
                   code-graph.db (SQLite)   Ollama/OpenAI API
```

### Estrutura do Perfil

Cada perfil gerado contém:

| Campo | Tipo | Descrição | Origem |
|-------|------|-----------|--------|
| `name` | string | Nome do agente | Nó do grafo |
| `bio` | string | Biografia resumida | LLM + atributos do nó |
| `persona` | string | Personalidade em primeira pessoa | LLM |
| `interests` | string[] | Lista de interesses | LLM + arestas |
| `mbti` | string | Tipo Myers-Briggs | LLM inferido |
| `topics` | string[] | Tópicos de especialidade | Arestas + LLM |
| `speaking_style` | string | Estilo de fala característico | LLM |
| `activity_config` | object | AgentActivityConfig — nível de atividade, horários, viés, influência | LLM + tipo da entidade |
| `twitter_behavior` | object | Comportamento no Twitter | Config + LLM |
| `reddit_behavior` | object | Comportamento no Reddit | Config + LLM |

#### Subcampos de `activity_config` (AgentActivityConfig)

| Campo | Tipo | Descrição | Origem |
|-------|------|-----------|--------|
| `activity_level` | float (0.0-1.0) | Nível geral de atividade | LLM + tipo da entidade |
| `posts_per_hour` | float | Posts criados por hora | LLM + regra por tipo |
| `comments_per_hour` | float | Comentários por hora | LLM + regra por tipo |
| `active_hours` | int[] | Horas do dia ativo (0-23) | Tipo da entidade + heurística |
| `response_delay_min` | int | Atraso mínimo (min simulados) | LLM + tipo |
| `response_delay_max` | int | Atraso máximo (min simulados) | LLM + tipo |
| `sentiment_bias` | float (-1.0 a 1.0) | Viés de sentimento | LLM inferido |
| `stance` | string | Posição sobre tema central | LLM + arestas |
| `influence_weight` | float (0.0-3.0) | Peso de influência social | Tipo da entidade |

## Quando Usar

| Cenário | Descrição |
|---------|-----------|
| Simulação de agentes | Criar agentes realistas para simular opiniões em rede social |
| Geração de NPCs | Personagens para jogos ou cenários de teste |
| Role-playing | Personas para teste de chatbots ou sistemas de diálogo |
| Análise de stakeholders | Perfis de atores a partir de documentos de análise |
| Onboarding | Personas de usuário para design centrado no humano |

## Workflow

### Fase 1: EXTRAIR — Obter Entidades do Grafo

1. **Consulte o grafo** — use GraphRAG ou consulta direta ao SQLite
2. **Filtre por tipo** — selecione entidades com labels significativos (excluindo `Entity`, `Node`)
3. **Enriqueça com arestas** — obtenha arestas de entrada/saída e nós relacionados

### Fase 2: GERAR — Produzir Perfis via LLM

1. **Para cada entidade**, monte um prompt com:
   - Nome, summary, atributos
   - Relações (outgoing + incoming)
   - Nós relacionados com seus atributos

2. **Template de Prompt** (melhorado do original):
```
Gere um perfil de agente para simulação baseado na entidade abaixo:

== DADOS DA ENTIDADE ==
Nome: {name}
Resumo: {summary}
Atributos: {attributes}

== RELAÇÕES ==
{related_edges}

== CONTEXTO DO GRAFO ==
{related_nodes}

== PERFIL REQUERIDO ==
Gere um JSON com os campos:
- bio: biografia de 2-3 frases
- persona: voz em primeira pessoa (1 parágrafo)
- interests: lista de 3-5 interesses
- mbti: um dos 16 tipos MBTI mais adequado
- topics: lista de 3-5 tópicos de especialidade
- speaking_style: descrição do estilo de fala (formal, casual, técnico, etc.)
- activity_config: {
    activity_level: float 0.0-1.0 (nível geral de atividade),
    posts_per_hour: float (média de posts por hora),
    comments_per_hour: float (média de comentários por hora),
    active_hours: [int 0-23] (horas do dia em que o agente está ativo),
    response_delay_min: int (atraso mínimo em minutos simulados),
    response_delay_max: int (atraso máximo em minutos simulados),
    sentiment_bias: float -1.0 a 1.0 (viés negativo/positivo),
    stance: "supportive"|"critical"|"neutral"|"curious"|"dismissive",
    influence_weight: float 0.0-3.0 (peso de influência social)
  }
- twitter_behavior: {
    post_frequency: "alta"|"media"|"baixa",
    content_types: ["opiniao", "compartilhamento", "pergunta", ...],
    interaction_style: "engajador"|"observador"|"influenciador"
  }
- reddit_behavior: {
    post_frequency: "alta"|"media"|"baixa",
    subreddits_preference: ["topicos relacionados"],
    comment_style: "analitico"|"humoristico"|"informativo"
  }
```

3. **Gere em paralelo** — use `parallel_count` para gerar múltiplos perfis simultaneamente
4. **Valide o JSON** — verifique se todos os campos obrigatórios estão presentes

### Fase 3: SALVAR — Exportar Perfis

| Formato | Uso | Estrutura |
|---------|-----|-----------|
| JSON | Reddit / uso geral | Lista de objetos completos |
| CSV | Twitter (requerido pelo OASIS) | Campos achatados |

## Tipos de Entidade e Regras de Atividade

Os valores de `activity_config` seguem regras heurísticas por tipo de entidade, derivadas do
`BRAZIL_TIMEZONE_CONFIG` do MiroFish-Offline. O LLM pode ajustar dentro das faixas abaixo:

| Tipo | activity_level | posts_per_hour | active_hours | influence_weight | response_delay |
|------|---------------|----------------|--------------|-----------------|----------------|
| University/Official | 0.1-0.3 | 0.1 | 9-17 | 3.0 | 60-240 min |
| MediaOutlet | 0.4-0.6 | 0.8 | 7-23 | 2.5 | 5-30 min |
| Professor/Expert | 0.4-0.6 | 0.3 | 8-21 | 2.0 | 15-90 min |
| Student | 0.6-0.9 | 0.6 | 8-13, 18-23 | 0.8 | 1-15 min |
| Alumni | 0.4-0.6 | 0.4 | 12-13, 19-23 | 1.0 | 5-30 min |
| Person/Default | 0.5-0.8 | 0.5 | 9-13, 18-23 | 1.0 | 2-20 min |

### Lógica de Aplicação

1. **Identifique o tipo** da entidade no grafo (label do nó)
2. **Use a faixa heurística** como seed para o prompt do LLM
3. **Deixe o LLM ajustar** o valor exato dentro da faixa com base no contexto
4. **Fallback**: se o tipo não estiver na tabela, use `Person/Default`

## Dual-format Output

O OASIS Profile Generator pode exportar no formato nativo do MiroFish-Offline
(Twitter CSV) ou no formato completo com todos os campos.

### JSON (Full Detail)

Recomendado para o ecossistema OpenCode. Contém todos os campos incluindo
`activity_config` com seus 9 subcampos.

```json
{
  "name": "João Silva",
  "bio": "...",
  "persona": "...",
  "interests": ["..."],
  "mbti": "ENFP",
  "topics": ["..."],
  "speaking_style": "casual",
  "activity_config": {
    "activity_level": 0.8,
    "posts_per_hour": 1.2,
    "comments_per_hour": 2.5,
    "active_hours": [18, 19, 20, 21, 22, 23],
    "response_delay_min": 1,
    "response_delay_max": 15,
    "sentiment_bias": 0.3,
    "stance": "supportive",
    "influence_weight": 0.8
  },
  "twitter_behavior": { ... },
  "reddit_behavior": { ... }
}
```

### CSV (Twitter-optimized)

Formato achatado requerido pelo pipeline Twitter do OASIS original.
Campos comuns + `activity_config` são convertidos em colunas planas.

| Coluna | Origem |
|--------|--------|
| `name`, `bio` | Perfil |
| `mbti` | Perfil |
| `persona` | Perfil |
| `speaking_style` | Perfil |
| `interests` | Perfil (join por pipe `\|`) |
| `topics` | Perfil (join por pipe `\|`) |
| `activity_level` | `activity_config.activity_level` |
| `posts_per_hour` | `activity_config.posts_per_hour` |
| `comments_per_hour` | `activity_config.comments_per_hour` |
| `active_hours` | `activity_config.active_hours` (join por pipe) |
| `sentiment_bias` | `activity_config.sentiment_bias` |
| `stance` | `activity_config.stance` |
| `influence_weight` | `activity_config.influence_weight` |

Use `--format csv` para gerar CSV e `--format json` (padrão) para JSON completo.

## Melhorias em Relação ao Original

| Aspecto | Original (MiroFish-Offline) | Melhoria (OpenCode) |
|---------|----------------------------|---------------------|
| Fonte de dados | Neo4j graph_storage | SQLite code-graph.db + qualquer JSON |
| Paralelismo | Implementado | Usa Task Agent para paralelismo real |
| Validação | Básica (try/except) | Schema validation pós-geração |
| Extensibilidade | Apenas OASIS | Templates customizáveis por domínio |
| Fallback | Sem LLM → perfil vazio | Fallback com regras heurísticas |
| Rastreabilidade | Nenhuma | INFERIDO / CONFIRMADO por campo |
| AgentActivityConfig | Inline fixo | 9 subcampos gerados por LLM + tipo da entidade |
| Regras por tipo | Apenas entidade genérica | 6 tipos (University, Media, Professor, Student, Alumni, Default) |
| Dual-format | CSV apenas (Twitter) | JSON (full detail) + CSV (Twitter-optimized) |
| Horários ativos | Fixo (CHINA_TIMEZONE) | Adaptável por tipo + heurística (BRAZIL_TIMEZONE) |

## Prompt Templates Customizáveis

Para domínios específicos, crie templates em `references/prompts/`:

- `default.md` — Template genérico (usado por padrão)
- `academic.md` — Para perfis acadêmicos/pesquisadores
- `corporate.md` — Para perfis corporativos/executivos
- `healthcare.md` — Para profissionais de saúde

## Exemplo de Uso

```bash
# Gerar perfis a partir de uma consulta GraphRAG
/oasis-profile --graph mirofish_abc123 --entities tipos:Person,Organization --parallel 5

# Gerar a partir de arquivo JSON
/oasis-profile --input entities.json --output profiles.json

# Gerar com template específico
/oasis-profile --graph mirofish_abc123 --template academic
```

## Referências

- Código original: `oasis_profile_generator.py` (MiroFish-Offline)
- Código original: `simulation_config_generator.py` (MiroFish-Offline)
- Estruturas de dados: `EntityNode`, `FilteredEntities` em `entity_reader.py`
- SKILL relacionada: `code-graphrag` (fonte de dados do grafo)
