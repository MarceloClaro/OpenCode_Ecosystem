# Checklist: Fase 1 - Análise Documental (Semanas 1-4)

**Status:** READY TO START | **Data Início:** 2026-06-02  
**Responsável:** Marcelo Claro | **Orientador:** [PPGTE/UFC]

---

## SEMANA 1: Setup + Análise Inicial

### ☐ 1.1 Preparação Ambiental (Dia 1)

- [ ] Verificar OpenCode v4.2 está operacional
  ```bash
  opencode --version
  # Esperado: OpenCode CLI 1.14 (ou superior)
  ```

- [ ] Verificar skills de interesse estão instaladas
  ```bash
  opencode /editais-br --help
  opencode /code-graphrag --help
  ```

- [ ] Criar diretório `fase1_analise/` para artefatos
  ```bash
  mkdir -p C:\Users\marce\OneDrive\Documentos\Antiprojeto\ UFC\fase1_analise
  ```

- [ ] Configurar logging (optional)
  ```bash
  export OPENCODE_LOG_LEVEL=debug
  ```

**Responsável:** Marcelo Claro  
**Prazo:** Segunda-feira, 06:00-09:00 (3h)  
**Checkpoint:** ✅ Confirmação via `opencode --version` e diretório criado

---

### ☐ 1.2 Busca de Editais LGPD (Dia 1-2)

**Ferramenta:** `editais-br` (52 editais curados)

**Comando Base:**
```bash
opencode /editais-br \
  --query "LGPD privacidade dados pessoais pesquisa" \
  --limit 10 \
  --output editais_lgpd.json \
  --formato "json"
```

**Buscas Adicionais (refinamento):**
1. Conformidade LGPD
   ```bash
   opencode /editais-br --query "Lei 13.709 proteção dados" --limit 5
   ```

2. Pesquisa responsável
   ```bash
   opencode /editais-br --query "ética pesquisa integridade acadêmica" --limit 5
   ```

3. Privacidade educacional
   ```bash
   opencode /editais-br --query "privacidade educação estudantes" --limit 5
   ```

4. Conformidade UFC
   ```bash
   opencode /editais-br --query "UFC PPGTE Resolução 39" --limit 5
   ```

**Esperado:**
- ≥ 20 editais relacionados (de 52 curados)
- Estrutura: `{ id, titulo, descricao, categoria, conformidade_lgpd, fonte }`
- Arquivo: `editais_lgpd.json` (~50KB)

**Processamento:**
```python
# Pseudocódigo para consolidação
import json

with open("editais_lgpd.json") as f:
    editais = json.load(f)

conformes_lgpd = [e for e in editais if e.get("conformidade_lgpd", False)]
print(f"Total: {len(editais)}, Conformes LGPD: {len(conformes_lgpd)}")

# Salvar resumo
with open("editais_resumo.txt", "w") as out:
    for e in conformes_lgpd[:10]:
        out.write(f"- {e['titulo']}\n")
```

**Responsável:** Marcelo Claro  
**Prazo:** Terça-feira, 09:00-12:00 (3h)  
**Checkpoint:** ✅ Arquivo `editais_lgpd.json` com ≥ 20 itens + resumo

---

### ☐ 1.3 Mapeamento Arquitetura OpenCode (Dia 2-3)

**Ferramenta:** `code-graphrag` (Grafo de conhecimento)

**Objetivo:** Mapear 125 agentes + 40 MCPs + dependências

**Comando Base:**
```bash
opencode /code-graphrag \
  --entity "Agentes" \
  --depth 3 \
  --filter "OpenCode v4.2" \
  --output graph_agentes.json \
  --formato "json"
```

**Execução Passo-a-Passo:**

1. **Query 1: Listar todos 125 agentes**
   ```bash
   opencode /code-graphrag --query "agentes:*" --limit 125
   ```
   **Esperado:** 125 nós com atributos (nome, tipo, skill parent)

2. **Query 2: Listar 40 MCPs**
   ```bash
   opencode /code-graphrag --query "mcp:*" --limit 40
   ```
   **Esperado:** 40 nós MCP (websearch, code-runner, sequential-thinking, ...)

3. **Query 3: Relações agente ↔ MCP**
   ```bash
   opencode /code-graphrag --relationship "agente_usa_mcp" --limit 200
   ```
   **Esperado:** ~200 edges (cada agente usa 1-3 MCPs)

4. **Query 4: Relações skill ↔ agente**
   ```bash
   opencode /code-graphrag --relationship "skill_contem_agente" --limit 150
   ```
   **Esperado:** ~150 edges (12 skills × ~10 agentes/skill)

**Processamento:**
```python
# Converter grafo para tabela de dependências
import json

with open("graph_agentes.json") as f:
    grafo = json.load(f)

# Contar agentes por tipo
agentes_por_tipo = {}
for node in grafo["nodes"]:
    tipo = node.get("type", "unknown")
    agentes_por_tipo[tipo] = agentes_por_tipo.get(tipo, 0) + 1

print("Distribuição de agentes:")
for tipo, count in sorted(agentes_por_tipo.items(), key=lambda x: x[1], reverse=True):
    print(f"  {tipo}: {count}")

# Total
print(f"Total nós: {len(grafo['nodes'])}")
print(f"Total edges: {len(grafo['edges'])}")
```

**Responsável:** Marcelo Claro  
**Prazo:** Quarta-feira, 09:00-15:00 (6h)  
**Checkpoint:** ✅ Arquivo `graph_agentes.json` com 125+ nós + 40 MCPs + edges

---

## SEMANA 2: Consolidação Relatório Fase 1

### ☐ 2.1 Extração de Conceitos Legais (Dia 4-5)

**Ferramenta:** `entity-ner-reader` (NER em grafos)

**Objetivo:** Extrair entidades relacionadas a LGPD, privacidade, ética

**Execução:**

1. **Entidades do documento ANTEPROJETO**
   ```bash
   opencode /entity-ner-reader \
     --arquivo "ANTEPROJETO_PPGTE_2026.md" \
     --tipos "LEI,CONFORMIDADE,PRIVACIDADE,ÉTICA" \
     --output entidades_anteprojeto.json
   ```

2. **Entidades do OpenCode (grafo)**
   ```bash
   opencode /entity-ner-reader \
     --grafo graph_agentes.json \
     --tipos "SKILL,MCP,AGENTE,VALIDACAO" \
     --output entidades_opencode.json
   ```

3. **Cruzamento: Anteprojeto ↔ OpenCode**
   ```python
   # Pseudocódigo
   anteprojeto_entities = load("entidades_anteprojeto.json")
   opencode_entities = load("entidades_opencode.json")
   
   # Mapeamento: Lei 13.709 → protocol-anonimato
   # Verificação formal → cora-debate V1-V7
   # Pesquisa → SEEKER (10 agentes)
   # Etc.
   
   mapeamento = match_entities(anteprojeto_entities, opencode_entities)
   save(mapeamento, "mapeamento_conceitos.json")
   ```

**Responsável:** Marcelo Claro  
**Prazo:** Quinta-feira, 09:00-14:00 (5h)  
**Checkpoint:** ✅ Arquivo `mapeamento_conceitos.json` com correspondências

---

### ☐ 2.2 Análise de Conformidade (Dia 5-6)

**Objetivo:** Produzir relatório CONFORMIDADE_LGPD_OPENCODE.md

**Estrutura do Relatório:**

```markdown
# Relatório de Conformidade: LGPD × OpenCode v4.2

## 1. Resumo Executivo
- Conformidade geral: X%
- Componentes críticos: protocol-anonimato, sqlite, sequential-thinking
- Recomendações: Y pontos

## 2. Análise por Princípio LGPD

### 2.1 Transparência (Art. 6, I)
- OpenCode: sequential-thinking MCP garante rastreabilidade
- Status: ✅ CONFORME

### 2.2 Acesso (Art. 18)
- OpenCode: sqlite local + exports (no cloud)
- Status: ✅ CONFORME

### 2.3 Direito ao Esquecimento (Art. 17)
- OpenCode: protocol-anonimato remove PII
- Status: ✅ CONFORME

... (mais 6 princípios LGPD)

## 3. Mapeamento: Anteprojeto → Componentes OpenCode

| Requisito Anteprojeto | Componente OpenCode | Conformidade |
|--|--|--|
| Auditoria caixa branca | sequential-thinking + cora-debate | ✅ |
| Rastreabilidade DOI | academic-export-abnt + SEEKER | ✅ |
| Conformidade LGPD | protocol-anonimato | ✅ |
| Debate especialistas | agent-forum P14 | ✅ |
| Verificação formal | cora-debate P18 (V1-V7) | ✅ |

## 4. Recomendações

1. Iniciar Fase 2 com criador-artigo (49 agentes) — pipeline validado
2. Usar SEEKER para pesquisa DOI — 10+ fontes confiáveis
3. Configurar CEP/TCLE com protocol-anonimato antes grupo focal
4. Ativar sequential-thinking MCP para logs — SHA-256 imutável

## 5. Conclusão

OpenCode v4.2 está **100% conformidade LGPD** para uso em anteprojeto PPGTE 2026.

---
**Data:** 2026-06-12  
**Autor:** Marcelo Claro  
**Orientador:** [PPGTE/UFC]
```

**Processamento:**
```bash
# Gerar documento final
cat > CONFORMIDADE_LGPD_OPENCODE.md << 'EOF'
# [Conteúdo acima]
EOF

# Validar (opcional)
opencode /code-review --arquivo "CONFORMIDADE_LGPD_OPENCODE.md" --tipo "markdown"
```

**Responsável:** Marcelo Claro  
**Prazo:** Sexta-feira, 09:00-17:00 (8h, incluindo refinamentos)  
**Checkpoint:** ✅ Arquivo `CONFORMIDADE_LGPD_OPENCODE.md` ≥ 3000 palavras

---

### ☐ 2.3 Revisão e Aprovação Preliminar (Dia 7)

- [ ] Auto-review do relatório
  - [ ] Leitura completa de `CONFORMIDADE_LGPD_OPENCODE.md`
  - [ ] Verificação de citações (5+ referências mínimo)
  - [ ] Checagem de conformidade (100% vs 95%+ aceitável)

- [ ] Agendamento com orientador
  ```
  Assunto: Revisão Fase 1 - Análise Conformidade LGPD
  Anexo: CONFORMIDADE_LGPD_OPENCODE.md
  ```

- [ ] Feedback integrado (se necessário)

**Responsável:** Marcelo Claro + Orientador  
**Prazo:** Sexta-feira 17:00 - Segunda-feira 09:00  
**Checkpoint:** ✅ Relatório aprovado (ou com plano de correção)

---

## SEMANA 3-4: Refinamentos + Preparação Fase 2

### ☐ 3.1 Documentação Técnica (Dia 8-10)

- [ ] Criar README.md para fase1_analise/
  ```markdown
  # Fase 1: Análise Documental
  
  ## Artefatos
  - editais_lgpd.json (20+ editais LGPD)
  - graph_agentes.json (125 agentes + 40 MCPs)
  - mapeamento_conceitos.json (Anteprojeto ↔ OpenCode)
  - CONFORMIDADE_LGPD_OPENCODE.md (Relatório final)
  
  ## Como Reproduzir
  ```

- [ ] Backup dos artefatos
  ```bash
  tar -czf fase1_analise_backup.tar.gz fase1_analise/
  ```

- [ ] Commit para git (opcional)
  ```bash
  git add fase1_analise/
  git commit -m "Fase 1: Análise documental e conformidade LGPD (semanas 1-4)"
  ```

**Responsável:** Marcelo Claro  
**Prazo:** Segunda-feira 09:00-12:00 (3h)  
**Checkpoint:** ✅ Documentação completa + backup

---

### ☐ 3.2 Planejamento Fase 2 (Dia 10-11)

**Objetivo:** Preparar inputs para criador-artigo (49 agentes)

- [ ] Definir 4 módulos do guia
  - [ ] Módulo A: Configuração ética do ambiente (estrutura)
  - [ ] Módulo B: Pesquisa bibliográfica com rastreabilidade DOI
  - [ ] Módulo C: Redação acadêmica com auditoria integrada
  - [ ] Módulo D: Proteção dados sensíveis conforme LGPD

- [ ] Preparar brief para criador-artigo
  ```json
  {
    "projeto": "Guia Prático IA Multiagente para Pesquisa",
    "modulos": [
      {
        "numero": "A",
        "titulo": "Configuração Ética do Ambiente",
        "tamanho_esperado": "3000-4000 palavras",
        "requisitos": [
          "Alinhado com 5 princípios Floridi (2023)",
          "Exemplos práticos com OpenCode v4.2",
          "Checklist implementação"
        ]
      },
      ...
    ],
    "contexto": "Mestrado Profissional PPGTE/UFC",
    "nivel_formalidade": "acadêmico",
    "prazo": "8 semanas (semanas 5-12)"
  }
  ```

- [ ] Agendamento com orientador para kickoff Fase 2

**Responsável:** Marcelo Claro  
**Prazo:** Quarta-feira 14:00-17:00 (3h)  
**Checkpoint:** ✅ Brief de Fase 2 pronto, agendamento confirmado

---

### ☐ 3.3 Lições Aprendidas Fase 1 (Dia 11-12)

- [ ] Documentar dificuldades encontradas
- [ ] Registrar tempo real vs. estimado
- [ ] Identificar otimizações para Fase 2

**Template:**
```markdown
# Lições Aprendidas - Fase 1

## O Que Funcionou
- editais-br permitiu encontrar 25 editais em 30min
- code-graphrag mapeou 125 agentes + deps em 2h
- Estimativa realista (12h work vs 14h planejado)

## O Que Não Funcionou
- (se houver)

## Otimizações para Fase 2
- ...
```

**Responsável:** Marcelo Claro  
**Prazo:** Quinta-feira 09:00-12:00 (3h)  
**Checkpoint:** ✅ Documento de lições aprendidas

---

## MÉTRICAS DE CONCLUSÃO FASE 1

| Métrica | Meta | Alcançado |
|---------|------|-----------|
| Editais LGPD encontrados | ≥ 20 | ___ |
| Agentes mapeados | ≥ 125 | ___ |
| MCPs catalogados | ≥ 40 | ___ |
| Conformidade relatório | ≥ 95% | ___ |
| Palavras relatório | ≥ 3000 | ___ |
| Aprovação orientador | Sim | ___ |
| Horas reais (vs 60h planejado) | ≤ 70h | ___ |

---

## PRÓXIMOS PASSOS (FASE 2)

**Data de Início:** Segunda-feira, 30 Junho 2026  
**Componente Principal:** `criador-artigo` (49 agentes)  
**Entrada:** Brief de 4 módulos (pronto em Fase 1)  
**Saída Esperada:** GUIA_PRATICO_MODULOS_1-4.html + referências ABNT

**Documento de Planejamento:** `CHECKLIST_EXECUCAO_FASE2.md` (a criar em semana 4 Fase 1)

---

**Assinado:** Marcelo Claro | **Data:** 2026-05-30  
**Status:** ✅ PRONTO PARA INICIAR  
**Próximo Checkpoint:** Segunda-feira 2026-06-02, 06:00

---

**Fim do Checklist Fase 1**
