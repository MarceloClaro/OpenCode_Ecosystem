---
name: ontology-generator
description: >
  Geração de ontologias para grafos de conhecimento social. Inspirado pelo
  OntologyGenerator do MiroFish-Offline, analisa textos e requisitos de
  simulação para produzir definições de tipos de entidades e
  relacionamentos adequadas para simulação de opinião em mídias sociais.
  Use quando precisar definir tipos de entidades e arestas para um novo
  domínio de conhecimento.
license: MIT
compatibility: opencode
allowed-tools: Read, Grep, Glob, Bash, Write, Sqlite
metadata:
  author: Reversa Engine (padrão MiroFish-Offline ontology_generator.py)
  version: "1.0.0"
  domain: knowledge
  triggers: ontology, ontologia, tipo, tipos, entidade, edge, relação, schema, taxonomia
  role: analyst
  scope: knowledge
  output-format: json
  related-skills: entity-ner-reader, code-graphrag, graph-builder-pipeline
  inspired-by: MiroFish-Offline OntologyGenerator (ontology_generator.py)
---

# Ontology Generator — Geração Automática de Ontologias para Grafos

Inspirado pelo **OntologyGenerator** do MiroFish-Offline (`ontology_generator.py`).
Analisa textos e requisitos de simulação para gerar definições formais de
tipos de entidades e relacionamentos para grafos de conhecimento.

## Princípios

O OntologyGenerator segue um design rigoroso baseado em **hierarquia de tipos**:

```
10 Entity Types (obrigatório):
├── 8 Tipos Específicos (baseados no texto)
│   ├── Ex: Student, Professor, University, Journalist
│   └── Cada um com attributes + examples
└── 2 Tipos Fallback (sempre presentes)
    ├── Person    → para qualquer pessoa não categorizada
    └── Organization → para qualquer organização não categorizada

6-10 Edge Types com source_targets:
├── Ex: WORKS_FOR(Employee→Company), STUDIES_AT(Student→University)
└── Cada edge define source→target válidos
```

## Componentes

### OntologyGenerator
Serviço principal que:
1. Concatena textos de documentos (com limite de 50K chars para LLM)
2. Envia para LLM via `chat_json()` com system prompt especializado
3. Valida e pós-processa o resultado (garante 10 tipos, 2 fallbacks)
4. Retorna `{entity_types, edge_types, analysis_summary}`

### System Prompt (`ONTOLOGY_SYSTEM_PROMPT`)
Prompt especializado (~150 linhas) que instrui o LLM a:
- Identificar papéis sociais (pessoas, organizações, mídia, governo)
- Evitar conceitos abstratos como tipos de entidade
- Seguir hierarquia estrita (8 específicos + 2 fallback)
- Usar PascalCase para tipos, UPPER_SNAKE_CASE para edges
- Gerar attributes sem palavras reservadas (name, uuid, etc.)

### Validação e Pós-processamento
- Fallbacks (Person, Organization) inseridos automaticamente se ausentes
- Limite de 10 entity types e 10 edge types (compatível com Zep API)
- Descrições truncadas em 100 caracteres
- Campos ausentes preenchidos com defaults

## Quando Usar

| Cenário | Descrição |
|---------|-----------|
| Novo domínio | "Preciso de tipos para um grafo sobre regulação de IA" |
| Ontologia inicial | "Quais entidades e relações existem neste texto?" |
| Preparação de grafo | "Gere a ontologia antes de construir o grafo" |
| Simulação social | "Defina papéis para simulação de opinião pública" |
| Extensão de tipos | "Adicione tipos específicos para este novo cenário" |

## Workflow

### Gerar Ontologia

```
python scripts/generate_ontology.py --text "documento.txt" --requirement "Simular reações à regulação de IA"
```

1. Lê o(s) documento(s) de entrada
2. Envia para o LLM com o system prompt especializado
3. Valida e processa o resultado
4. Salva como JSON (`ontology.json`)

### Validar Ontologia

```
python scripts/generate_ontology.py validate --input ontology.json
```

Verifica:
- 10 entity types (exatos)
- 2 fallback types (Person, Organization)
- Nomes PascalCase / UPPER_SNAKE_CASE
- Attributes sem palavras reservadas
- Edge types com source_targets

### Converter para SQLite

```
python scripts/generate_ontology.py schema --input ontology.json --output schema.sql
```

Gera comandos CREATE TABLE a partir da ontologia.

## Exemplo de Saída (JSON)

```json
{
  "entity_types": [
    {"name": "Student", "description": "A student enrolled in an educational institution",
     "attributes": [{"name": "full_name", "type": "text", "description": "Full name"}],
     "examples": ["Alice Chen"]},
    {"name": "Professor", "description": "A professor or academic researcher",
     "attributes": [{"name": "full_name", "type": "text"}, {"name": "department", "type": "text"}],
     "examples": ["Dr. Smith"]},
    {"name": "Person", "description": "Any individual not fitting other specific person types",
     "attributes": [{"name": "full_name", "type": "text"}, {"name": "role", "type": "text"}],
     "examples": ["anonymous netizen"]},
    {"name": "Organization", "description": "Any organization not fitting other specific types",
     "attributes": [{"name": "org_name", "type": "text"}, {"name": "org_type", "type": "text"}],
     "examples": ["small business"]}
  ],
  "edge_types": [
    {"name": "WORKS_FOR", "description": "Employment relationship",
     "source_targets": [{"source": "Person", "target": "Organization"}],
     "attributes": []}
  ],
  "analysis_summary": "Text focuses on academic integrity in higher education..."
}
```

## Escala de Confiança

- 🟢 **CONFIRMADO** — Campo validado pelo pós-processamento
- 🟡 **INFERIDO** — Tipo gerado pelo LLM, requer revisão humana
- 🔴 **LACUNA** — Tipo fallback usado (sem tipo específico correspondente)

## Regras

### MUST DO
- Garantir exatamente 10 entity types (2 fallback)
- Validar attributes sem palavras reservadas
- Oferecer fallback automático para Person/Organization
- Limitar texto de entrada a 50K chars para o LLM
- Salvar ontologia como JSON rastreável

### MUST NOT DO
- Aceitar tipos abstratos (conceitos, sentimentos, tópicos) como entidades
- Ignorar a hierarquia de tipos (específicos → fallback)
- Gerar attributes com nome/uuid/group_id
- Exceder 10 entity types ou 10 edge types
