# Integração Anteprojeto UFC com OpenCode v4.2

**Data:** 2026-05-30  
**Status:** Plano de Integração Estratégica  
**Objetivo:** Abandonar Phase 4/C isolado e integrar ao ecossistema OpenCode v4.2 (600+ componentes)

---

## 1. MAPEAMENTO: Anteprojeto ↔ OpenCode v4.2

### 1.1 Objetivo do Anteprojeto
*"Desenvolver e validar um guia prático de uso ético de uma plataforma de IA multiagente como ferramenta de suporte à pesquisa científica assistida no ensino superior"*

### 1.2 Componentes OpenCode v4.2 Aplicáveis

| Fase Anteprojeto | Componente OpenCode | Quantidade | Aplicação |
|------------------|-------------------|-----------|-----------|
| **Fase 1: Análise Documental** | `editais-br` | 52 editais curados | Conformidade LGPD / Resolução PRPPG/UFC nº 39/2025 |
| | `code-graphrag` | Grafo de conhecimento | Mapeamento 125 agentes + dependências |
| | `entity-ner-reader` | NER em grafos | Extração de entidades legais (LGPD, privacidade) |
| **Fase 2: Desenvolvimento Guia** | `criador-artigo` | 49 agentes, 91 arquivos | Pipeline redação 8 estágios (guia prático em módulos) |
| | `SEEKER` | 10 agentes, 78 arquivos | Pesquisa bibliográfica DOI (Tema 03: Ferramentas IA) |
| | `academic-export-abnt` | ABNT/APA/Chicago | Rastreabilidade de citações |
| | `baoyu-markdown-to-html` | Markdown → HTML responsivo | Manual digital interativo |
| **Fase 3: Validação Especialistas** | `agent-forum` (P14) | Multi-agent debate | Fórum com 3 especialistas (IA, Direito, Educação) |
| | `cora-debate` (P18) | V1-V7 verificadores | Verificação formal de afirmações no guia |
| | `reasoning-orchestrator-v11` | 68 tipos raciocínio | Construção argumentativa validada |
| **Fase 3: Estudo Caso (Grupo Focal)** | `baoyu-post-to-wechat` / `html-ppt` | Apresentação interativa | Apresentação para grupo focal (8-12 pesquisadores) |
| | `protocol-anonimato` | LGPD + CEP/TCLE | Anonimização logs / consentimento |
| | `analise-qualitativa` | Análise conteúdo temática | Codificação Bardin (2016) das gravações |
| **Sistema Auditoria** | `cora-debate` | SHA-256 logs | Imutabilidade registros |
| | `sqlite` + `pdf` | Banco de dados + exportação | Armazenamento local seguro |
| | `sequential-thinking` MCP | Rastreabilidade decisões | Cadeia lógica de cada recomendação |

---

## 2. ARQUITETURA DE INTEGRAÇÃO

### 2.1 Fluxo Integrado (Fase 1 → 4)

```
ANTEPROJETO UFC
│
├─ FASE 1: Análise Documental (Meses 1-4)
│  ├─ [editais-br] Buscar normativas LGPD / Resolução PRPPG/UFC nº 39/2025
│  ├─ [code-graphrag] Mapear 125 agentes OpenCode v4.2
│  ├─ [entity-ner-reader] Extrair conceitos legais (privacidade, dados sensíveis)
│  └─ Relatório: CONFORMIDADE_LGPD_OPENCODE.md
│
├─ FASE 2: Desenvolvimento Guia (Meses 5-12)
│  ├─ [criador-artigo] 49 agentes geram 4 módulos:
│  │  ├─ Módulo A: Configuração ética do ambiente
│  │  ├─ Módulo B: Pesquisa bibliográfica DOI
│  │  ├─ Módulo C: Redação acadêmica com auditoria
│  │  └─ Módulo D: Proteção dados sensíveis
│  ├─ [SEEKER] (10 agentes) Research pipeline
│  │  ├─ arXiv search (tecnologia educacional)
│  │  ├─ Semantic Scholar (IA ética)
│  │  ├─ CORE (LGPD + privacidade)
│  │  └─ Aggregate → 50+ fontes verificadas
│  ├─ [academic-export-abnt] Formatação ABNT + DOI tracking
│  └─ [baoyu-markdown-to-html] Converter para web responsivo
│
├─ FASE 3a: Validação por Especialistas (Semana 13)
│  ├─ [agent-forum] (P14) Debate multi-agent
│  │  ├─ Especialista 1 (IA): 68 tipos raciocínio
│  │  ├─ Especialista 2 (Direito): conformidade legal
│  │  ├─ Especialista 3 (Educação): pedagogia
│  │  └─ Q-Score UCB1 para convergência
│  ├─ [cora-debate] (P18) Verificação formal V1-V7
│  │  ├─ V1: Lógica proposicional
│  │  ├─ V2: Contexto histórico-legal
│  │  └─ V3-V7: Múltiplas perspectivas
│  └─ Relatório: VALIDACAO_ESPECIALISTAS.json
│
├─ FASE 3b: Estudo Caso - Grupo Focal (Meses 13-20)
│  ├─ [html-ppt] Apresentação interativa 4 encontros
│  ├─ Coleta:
│  │  ├─ Gravações com [protocol-anonimato] (CEP/TCLE)
│  │  ├─ Questionários Likert (pré/pós)
│  │  └─ Logs de uso (sqlite com hash SHA-256)
│  └─ Análise:
│     ├─ Estatística descritiva (scipy)
│     └─ [analise-qualitativa] Codificação Bardin temática
│
└─ FASE 4: Sistematização (Meses 21-24)
   ├─ Consolidação resultados
   ├─ Redação dissertação (academic-export-abnt + SDD/TDD)
   ├─ Publicação manual digital (responsivo)
   └─ Defesa pública
```

### 2.2 Dependências entre Componentes

```
Entrada: Anteprojeto UFC + OpenCode v4.2 (125 agentes, 40 MCPs, 104 skills)
   │
   ├─→ [editais-br] + [code-graphrag] → Mapeamento Fase 1
   │
   ├─→ [criador-artigo (49)] + [SEEKER (10)] → Draft 4 módulos
   │
   ├─→ [academic-export-abnt] → Refs DOI verificáveis
   │
   ├─→ [baoyu-markdown-to-html] → UI responsiva
   │
   ├─→ [agent-forum (P14)] → Debate especialistas
   │
   ├─→ [cora-debate (P18, V1-V7)] → Verificação formal
   │
   ├─→ [sequential-thinking] MCP → Rastreabilidade
   │
   ├─→ [protocol-anonimato] + [sqlite] + [pdf] → Armazenamento seguro (LGPD)
   │
   ├─→ [html-ppt] → Apresentação grupo focal
   │
   └─→ Saída: Manual Digital + Relatório Conformidade + Dados Estudo Caso
```

---

## 3. COMPONENTES CHAVE (Detalhamento)

### 3.1 Criador-Artigo (49 agentes)
**Localização:** `~/.config/opencode/skills/criador-artigo/`  
**Função:** Pipeline de escrita em 8 estágios com validação por pares

```python
# Pseudocódigo
criador = CriadorArtigo()

# Módulo A: Configuração ética
modulo_a = criador.generate_section(
    topic="Configuração ética do ambiente",
    num_agents=49,
    validadores=5,
    nivel="Mestrado Profissional"
)
# Output: Seção com citações DOI, debate interno V1-V7

# Módulo B: Pesquisa DOI
modulo_b = criador.generate_section(
    topic="Pesquisa bibliográfica com rastreabilidade DOI",
    sources=["arXiv", "Semantic Scholar", "CORE"]
)

# Módulo C: Auditoria integrada
modulo_c = criador.generate_section(
    topic="Redação acadêmica com auditoria",
    audit_level="caixa branca",  # SHA-256 logs
    anti_plagiarism=True
)

# Módulo D: Proteção dados
modulo_d = criador.generate_section(
    topic="Proteção de dados sensíveis (LGPD)",
    referencia_legal="Lei 13.709/2018"
)

# Consolidação e exportação ABNT
guia = criador.consolidate([modulo_a, modulo_b, modulo_c, modulo_d])
guia.export_html(responsive=True)
```

### 3.2 SEEKER (10 agentes)
**Localização:** `~/.config/opencode/skills/basis-research/`  
**Função:** Pesquisa bibliográfica com 10+ fontes acadêmicas

```python
seeker = SEEKER()

# Busca por tema (Fase 2)
resultados = seeker.search_batch(
    queries=[
        "IA multiagente educação",
        "ética IA pesquisa",
        "LGPD privacidade dados",
        "rastreabilidade DOI"
    ],
    sources=["arXiv", "OpenAlex", "Semantic Scholar", "CORE", "PubMed"],
    limit_per_query=50
)

# Validação de referências
for resultado in resultados:
    resultado.validate_doi()
    resultado.extract_abstract()
    resultado.bibtex_export(style="ABNT")
```

### 3.3 Agent-Forum (P14 - Multi-agent Debate)
**Localização:** `~/.config/opencode/skills/agent-forum/`  
**Função:** Debate estruturado com 3 especialistas

```python
forum = AgentForum(
    moderador="PhD Auditor (Nash Solver)",
    debate_fases=4  # OPEN → DISCUSS → SYNTHESIZE → CONCLUDE
)

# Fase 3a: Validação por especialistas
especialista_1 = Agent(
    nome="Especialista IA",
    background="Computer Science + Ethics",
    reasoning_types=68,  # Completo
    strategy="Inductive + Deductive"
)

especialista_2 = Agent(
    nome="Especialista Direito",
    background="Direito Digital + LGPD",
    reasoning_types=["legal", "compliance", "precedent"],
    strategy="Normativo"
)

especialista_3 = Agent(
    nome="Especialista Educação",
    background="Tecnologia Educacional",
    reasoning_types=["pedagogico", "didatico", "socioconstructivista"],
    strategy="Construtivista"
)

# Debate
debate = forum.orchestrate(
    topic="Conformidade guia prático com LGPD + ética IA",
    agents=[especialista_1, especialista_2, especialista_3],
    documento="GUIA_PRATICO_MODULOS_1-4.md",
    timeout=120,
    convergence_threshold=0.85  # Q-Score UCB1
)

# Relatório com múltiplas perspectivas
debate.generate_report("VALIDACAO_ESPECIALISTAS.json")
```

### 3.4 Cora-Debate (P18 - Verificação Formal)
**Localização:** `~/.config/opencode/skills/cora-debate/`  
**Função:** Verificação com 7 verificadores (V1-V7)

```python
cora = CoraDebate(
    verificadores_ativos=7,  # V1: Lógica, V2: Contexto, V3-V7: Perspectivas
    q_score_ucb1=True,
    self_consistency_k=7,
    calibracao_platt=True
)

# Afirmações a verificar (extraídas do guia)
afirmacoes = [
    "O ecossistema tem 125 agentes especializados",
    "SHA-256 logs garantem imutabilidade",
    "LGPD proíbe inserir dados inéditos em plataformas externas",
    "Debate entre agentes usa 38 tipos de raciocínio e 10 estratégias Nash"
]

for afirmacao in afirmacoes:
    validacao = cora.verify(afirmacao)
    print(f"{afirmacao}: V1-V7 confidence={validacao.confidence:.2f}")
```

### 3.5 Protocol-Anonimato (LGPD + CEP)
**Localização:** `~/.config/opencode/skills/protocol-anonimato/`  
**Função:** Conformidade LGPD + CEP/TCLE para grupo focal

```python
protocol = ProtocoloAnonimato(
    etica_aprovacao="CEP UFC",
    conformidade_lgpd=True,
    anonimizar=True
)

# Geração TCLE
tcle = protocol.generate_tcle(
    titulo="Estudo Caso: IA Multiagente na Pesquisa",
    pesquisadores=["Marcelo Claro", "Orientador"],
    duracao_encontros="4 encontros de 2h",
    direitos="Direito de retirada, acesso aos dados, sigilo"
)

# Coleta de dados com proteção
logs_codificados = protocol.anonymize_logs(
    logs_brutos="Sessão X - Pesquisador Y.json",
    parametro_anonimato="PES_001"  # Substitui nome
)

# Armazenamento seguro (local, não cloud)
sqlite_db = SQLiteVault(
    arquivo="grupo_focal_anonimizado.db",
    hash_algorithm="SHA-256",
    senha_criptografia="gerada_aleatoriamente"
)
```

---

## 4. EXECUÇÃO PASSO-A-PASSO

### 4.1 Fase 1: Análise Documental (Semanas 1-4)

**Passo 1:** Invocar `editais-br`
```bash
opencode /editais-br --query "LGPD privacidade dados pessoais" --limit 10
```
**Esperado:** 10 editais relacionados a conformidade LGPD

**Passo 2:** Invocar `code-graphrag`
```bash
opencode /code-graphrag --entity "Agentes OpenCode" --depth 3
```
**Esperado:** Grafo com 125 agentes + dependências

**Saída:** `CONFORMIDADE_LGPD_OPENCODE.md` (relatório técnico)

---

### 4.2 Fase 2: Desenvolvimento Guia (Semanas 5-12)

**Passo 3:** Invocar `criador-artigo`
```bash
opencode /artigo --topic "Guia Prático IA Multiagente" \
  --modules 4 \
  --agents 49 \
  --validation_level "mestrado" \
  --output_format "markdown_html"
```
**Esperado:** 4 módulos MD → HTML responsivo

**Passo 4:** Enriquecer com `SEEKER`
```bash
opencode /seeker --query "IA educação LGPD ética" \
  --sources "arXiv,Semantic Scholar,CORE" \
  --limit 50 \
  --export_bibtex "referencias_guia.bib"
```
**Esperado:** 50+ referências com DOI verificáveis

**Saída:** `GUIA_PRATICO_MODULOS_1-4.html` + `referencias_guia.bib`

---

### 4.3 Fase 3a: Validação por Especialistas (Semana 13)

**Passo 5:** Invocar `agent-forum` (P14)
```bash
opencode /agent-forum \
  --topic "Validação Guia Prático LGPD + Ética" \
  --especialistas 3 \
  --documento "GUIA_PRATICO_MODULOS_1-4.html" \
  --fases 4 \
  --timeout 120
```
**Esperado:** Debate convergente (Q-Score ≥ 0.85)

**Passo 6:** Invocar `cora-debate` (P18)
```bash
opencode /cora-debate \
  --documento "GUIA_PRATICO_MODULOS_1-4.html" \
  --verificadores 7 \
  --verify_claims \
  --export_json "validacao_cora_v1-v7.json"
```
**Esperado:** 7 verificadores validam cada afirmação

**Saída:** `VALIDACAO_ESPECIALISTAS.json` + `validacao_cora_v1-v7.json`

---

### 4.4 Fase 3b: Estudo Caso (Semanas 13-20)

**Passo 7:** Preparar apresentação
```bash
opencode /html-ppt --template "tech-sharing" \
  --slides "Guia Prático Módulos A-D" \
  --output "apresentacao_grupo_focal.html"
```

**Passo 8:** Conformidade LGPD
```bash
opencode /protocol-anonimato \
  --gerar_tcle \
  --pesquisadores 8-12 \
  --conformidade_lgpd \
  --export_pdf "TCLE_assinado.pdf"
```

**Passo 9:** Coleta de dados (4 encontros)
- Encontro 1: Apresentação guia módulo A
- Encontro 2: Prática módulo B (pesquisa DOI)
- Encontro 3: Prática módulo C (auditoria)
- Encontro 4: Feedback módulo D + discussão

**Captura:** Gravações + logs (anonimizados) + Likert pré/pós

**Saída:** `dados_grupo_focal_anonimizado.db` (SQLite)

---

### 4.5 Fase 4: Sistematização (Semanas 21-24)

**Passo 10:** Análise qualitativa
```bash
opencode /analise-qualitativa \
  --dados "dados_grupo_focal_anonimizado.db" \
  --metodo "bardin" \
  --export "analise_tematica.json"
```

**Passo 11:** Redação dissertação
```bash
opencode /academic-export-abnt \
  --sections [
    "introducao_anteprojeto.md",
    "conformidade_fase1.md",
    "guia_pratico_modulos.html",
    "validacao_especialistas.json",
    "estudo_caso_grupo_focal.md",
    "analise_tematica.json"
  ] \
  --output "dissertacao_final.pdf" \
  --template "ppgte"
```

**Saída:** `DISSERTACAO_PPGTE_2026.pdf` + `GUIA_PRATICO_DIGITAL.html`

---

## 5. DECISÕES ARQUITETURAIS

| Decisão | Justificativa | Restrição |
|---------|---------------|-----------|
| **Usar OpenCode v4.2 existente** | 600+ componentes já validados; 125 agentes; 40 MCPs; 68 tipos raciocínio | Evita reinventar Phase 4/C isolado |
| **criador-artigo para guia** | 49 agentes, 8 estágios, validação integrada (MASWOS v4.6) | Escalável para 4 módulos |
| **SEEKER para referências** | 10 agentes, 10+ fontes acadêmicas, verificação DOI automática | Cobre Tema 03 (Ferramentas IA) |
| **agent-forum para especialistas** | P14 orquestração, 4 fases debate, Nash equilibrium | Convergência Q-Score ≥ 0.85 |
| **cora-debate para verificação** | P18 formal verification, V1-V7, self-consistency K=7 | Rastreabilidade lógica |
| **protocol-anonimato para LGPD** | CEP/TCLE, SQLite local, SHA-256, sem cloud | Conformidade Lei 13.709/2018 |
| **Sequential-thinking MCP** | Rastreabilidade de cada decisão | Auditoria caixa branca |

---

## 6. MÉTRICAS DE SUCESSO

### Fase 1 (Análise)
- ✅ Relatório CONFORMIDADE_LGPD_OPENCODE.md com 100% cobertura (125 agentes × 40 MCPs mapeados)
- ✅ Grafo de dependências atualizado em code-graphrag

### Fase 2 (Guia)
- ✅ 4 módulos (A-D) em HTML responsivo
- ✅ 50+ referências com DOI verificável
- ✅ Debate interno 49 agentes convergiu (consensus ≥ 0.85)

### Fase 3a (Especialistas)
- ✅ Debate 3 especialistas convergiu (Q-Score ≥ 0.85)
- ✅ Cora-Debate V1-V7 validou 100% afirmações críticas
- ✅ Relatório VALIDACAO_ESPECIALISTAS.json ≥ 95% confiança

### Fase 3b (Grupo Focal)
- ✅ 8-12 pesquisadores completaram 4 encontros
- ✅ Questionário Likert pré/pós com Δ ≥ 1.5 pontos (escala 5)
- ✅ Análise temática identificou ≥ 5 códigos principais
- ✅ 0 vazamentos de dados (LGPD conformidade)

### Fase 4 (Entrega)
- ✅ Dissertação PPGTE com ≥ 30 páginas, Qualis A1
- ✅ Manual Digital interativo publicado (responsivo, web)
- ✅ Defesa pública com banca aprovadora

---

## 7. CRONOGRAMA INTEGRADO

| Fase | Atividade | Semanas | Componentes OpenCode |
|------|-----------|---------|---------------------|
| 1 | Análise Documental | 1-4 | editais-br, code-graphrag, entity-ner-reader |
| 2 | Desenvolvimento Guia | 5-12 | criador-artigo (49), SEEKER (10), academic-export-abnt, baoyu-markdown-to-html |
| 3a | Validação Especialistas | 13 | agent-forum (P14), cora-debate (P18) |
| 3b | Estudo Caso (Grupo Focal) | 13-20 | html-ppt, protocol-anonimato, sqlite, sequential-thinking MCP |
| 4 | Sistematização | 21-24 | academic-export-abnt, analise-qualitativa |

---

## 8. PRÓXIMOS PASSOS

1. **Semana 1:** Iniciar Fase 1 com `editais-br` + `code-graphrag`
2. **Semana 5:** Transição para Fase 2, invocar `criador-artigo`
3. **Semana 13:** Validação com `agent-forum` + `cora-debate`
4. **Semana 21:** Análise e redação final

**Responsável:** Marcelo Claro  
**Orientador:** [PPGTE/UFC]  
**Data de início:** 2026-06-02

---

**Fim do Plano de Integração**
