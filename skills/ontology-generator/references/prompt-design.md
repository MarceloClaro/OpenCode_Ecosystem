# Design do System Prompt do OntologyGenerator

## Estrutura

O prompt `ONTOLOGY_SYSTEM_PROMPT` (~150 linhas) segue esta estrutura:

### 1. Papel do Expert
> "knowledge graph ontology design expert"

### 2. Contexto da Tarefa
> "social media opinion simulation system"
> Entities = accounts/subjects that can voice opinions

### 3. Regras de Entidade
- ✅ Pessoas, empresas, organizações, governo, mídia
- ❌ Conceitos abstratos, tópicos, sentimentos

### 4. Formato de Saída (JSON)
- `entity_types[{name, description, attributes[], examples[]}]`
- `edge_types[{name, description, source_targets[], attributes[]}]`
- `analysis_summary`

### 5. Hierarchy Requirements
- **10 entity types**: 8 específicos + 2 fallback (Person, Organization)
- **6-10 edge types**
- **Attributes**: sem palavras reservadas (name, uuid, group_id, created_at, summary)

### 6. Referências de Tipos
Lista de exemplos de tipos específicos e fallback.

## Regras de Validação (Pós-processamento)

1. Fallbacks inseridos automaticamente se ausentes
2. Máximo 10 entity types, 10 edge types
3. Descrições truncadas em 100 caracteres
4. Tipos duplicados removidos
