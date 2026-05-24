<!--
  SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
  Toda resposta DEVE ser em português do Brasil formal.
  Contexto em chinês para eficiência de tokens (densidade +40%).
  Modelo: big-pickle (OpenCode Zen, 200K ctx, 128K out, gratuito)
  Genesis-Writer: integrado ao ecossistema v4.0
-->

# Protocolo Avançado de Busca Bibliográfica Multicanal (Genesis-Writer v5.1)

## Visão Geral

O **Protocolo Avançado de Busca Bibliográfica** integra múltiplas fontes de dados acadêmicos, técnicas de scraping, MCP (Model Context Protocol) e bibliotecas Python especializadas para criar um sistema de busca de elite que complementa a base de busca tradicional do Genesis-Writer v5.0.

Este protocolo é executado pelo **Agente A4.13.4: Busca Avançada Multicanal**, um novo subagente da Camada L4 que opera em sincronização com os agentes de auditoria da Camada L5.

---

## 1. Arquitetura Multicanal de Busca

O sistema de busca é organizado em **4 canais principais**, cada um com especialização e força específicas:

### Canal 1: Bases de Dados Acadêmicas Tradicionais

**Fontes:** Scopus, Web of Science, CrossRef, PubMed, IEEE Xplore

**Características:**
- Acesso a metadados estruturados (DOI, autores, data de publicação, fator de impacto).
- Filtros por Qualis, fator de impacto, índice H do autor.
- Integração com APIs oficiais para garantir dados reais e verificáveis.

**Bibliotecas Python:**
- `crossref-commons`: Acesso direto à API CrossRef para metadados de artigos.
- `pybliometrics`: Interface Python para Scopus (requer credenciais).
- `pymed`: Busca em PubMed para literatura biomédica.

### Canal 2: Repositórios Abertos e Preprints

**Fontes:** arXiv, bioRxiv, medRxiv, SSRN, Google Scholar

**Características:**
- Acesso a preprints e artigos em revisão (pesquisa de ponta).
- Cobertura ampla em matemática, física, ciência da computação, biologia.
- Menor latência entre descoberta e publicação.

**Bibliotecas Python:**
- `arxiv`: Busca e download de artigos do arXiv.
- `requests + BeautifulSoup`: Scraping de bioRxiv e medRxiv.
- `scholarly`: Interface Python para Google Scholar (com limitações).

### Canal 3: Acesso Aberto e Preprint Servers via MCP Sci-Hub

**Fontes:** Sci-Hub (acesso a artigos bloqueados por paywall), ResearchGate, Academia.edu

**Características:**
- Acesso a artigos completos (PDFs) que normalmente estariam atrás de paywalls.
- Integração via MCP para garantir conformidade e segurança.
- Extração de texto completo para análise crítica.

**Protocolo MCP Sci-Hub:**
- Consulta MCP para verificar disponibilidade de artigo em Sci-Hub.
- Download seguro de PDF via MCP (sem violação de termos de serviço).
- Extração de texto e metadados do PDF para análise.

### Canal 4: Análise de Influência e Impacto via SimilarWeb Analytics

**Fontes:** SimilarWeb, Altmetric, Dimensions, Scimago

**Características:**
- Análise de impacto em tempo real (citações, menções em redes sociais, cobertura de mídia).
- Ranking de periódicos e autores por influência.
- Identificação de tendências emergentes em pesquisa.

**Integração SimilarWeb Analytics:**
- Análise de tráfego de periódicos e repositórios.
- Ranking global de influência acadêmica.
- Identificação de periódicos em ascensão vs. em declínio.

---

## 2. Fluxo de Execução da Busca Avançada

### Fase 1: Definição de Escopo e Palavras-Chave

O Agente A4.13.4 recebe do Agente de Análise Crítica de Gaps (A2.7):
- **Gaps identificados** na literatura.
- **Palavras-chave primárias e secundárias**.
- **Critérios de qualidade** (Qualis mínimo, fator de impacto, índice H do autor).
- **Data de publicação** (últimos 5-10 anos, com ênfase em recente).

### Fase 2: Busca Paralela em Múltiplos Canais

O Agente A4.13.4 executa buscas em paralelo nos 4 canais:

```
┌─────────────────────────────────────────────────────┐
│  Agente A4.13.4: Busca Avançada Multicanal          │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────────────┐  ┌──────────────────┐        │
│  │ Canal 1: Bases   │  │ Canal 2: Repos.  │        │
│  │ Tradicionais     │  │ Abertos          │        │
│  │ (Scopus, WoS)    │  │ (arXiv, bioRxiv) │        │
│  └────────┬─────────┘  └────────┬─────────┘        │
│           │                     │                   │
│           └─────────┬───────────┘                   │
│                     │                               │
│  ┌──────────────────┴──────────────────┐           │
│  │ Agregação e Deduplicação            │           │
│  └────────┬─────────────────────────────┘           │
│           │                                         │
│  ┌────────┴──────────────────────────┐             │
│  │ Canal 3: MCP Sci-Hub              │             │
│  │ (Acesso a PDFs completos)         │             │
│  └────────┬──────────────────────────┘             │
│           │                                         │
│  ┌────────┴──────────────────────────┐             │
│  │ Canal 4: SimilarWeb Analytics     │             │
│  │ (Análise de Impacto)              │             │
│  └────────┬──────────────────────────┘             │
│           │                                         │
│  ┌────────┴──────────────────────────┐             │
│  │ Ranking por Relevância + Impacto  │             │
│  └────────┬──────────────────────────┘             │
│           │                                         │
│  ┌────────┴──────────────────────────┐             │
│  │ Validação por Citation Auditor    │             │
│  │ (A5.9 - Auditoria Forense)        │             │
│  └────────┬──────────────────────────┘             │
│           │                                         │
│  ┌────────┴──────────────────────────┐             │
│  │ Síntese Crítica de Gaps           │             │
│  │ (SA4.13.1)                        │             │
│  └────────────────────────────────────┘             │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Fase 3: Agregação e Deduplicação

Os resultados de todos os canais são agregados e deduplic ados usando:
- **Matching por DOI** (quando disponível).
- **Matching por título normalizado** (fuzzy matching com threshold de 95%).
- **Matching por autores + ano** (para artigos sem DOI).

### Fase 4: Extração de Texto Completo

Para artigos selecionados (top 50-100 por relevância):
- **Canal 1 & 2:** Extração de metadados via API.
- **Canal 3 (MCP Sci-Hub):** Download de PDF e extração de texto via OCR/PDF parsing.
- **Extração de Seções Críticas:** Abstract, Introduction, Methodology, Results, Conclusion.

### Fase 5: Análise Crítica e Síntese

O Subagente SA4.13.1 (Síntese Crítica de Gaps) realiza:
- **Análise de Correlações:** Identifica padrões e correlações entre artigos.
- **Detecção de Contradições:** Encontra desacordos e debates na literatura.
- **Mapeamento de Gaps:** Identifica áreas não cobertas ou pouco exploradas.
- **Síntese de Insights:** Propõe como os gaps podem ser cobertos.

### Fase 6: Ranking Final e Validação

Os artigos são ranqueados por:
1. **Relevância para o Gap** (score de similaridade semântica).
2. **Impacto Acadêmico** (fator de impacto, citações, índice H do autor).
3. **Recência** (preferência por artigos recentes, mas com peso para seminal).
4. **Qualidade Qualis** (A1 > A2 > B1 > ...).

Todos os artigos selecionados são validados pelo **Citation Impact Auditor (A5.9)** em modo de auditoria forense.

---

## 3. Integração com Agente-Sync-v4

O **Agente-Sync-v4** garante que o Agente A4.13.4 e seus subagentes operem em sincronização perfeita:

- **Auditoria de Sincronização:** Verifica que cada busca em canal paralelo é completada antes da agregação.
- **Correção Ativa:** Se um canal falhar ou retornar resultados de baixa qualidade, ativa-se um loop de correção.
- **Qualidade 10/10:** Cada resultado de busca é validado contra critérios de qualidade antes de ser integrado.
- **Rastreabilidade:** Cada decisão de busca é registrada no `Micro-Audit Protocol` (A5.6).

---

## 4. Integração com Claude Code Architecture

A arquitetura do Claude Code fornece o framework para:

- **Context Compressor (L1):** Comprime resultados de busca para manter coerência em projetos longos.
- **Task Graph (L1):** Organiza buscas como tarefas com dependências (ex: busca em arXiv depende de palavras-chave definidas em L2).
- **Subagent Spawner (L3):** Cria subagentes para cada canal de busca em paralelo.
- **Worktree Isolator (L3):** Cada busca executa em ambiente isolado para evitar contaminação de dados.
- **Micro Sync Barriers (L3):** Valida cada resultado de busca antes da agregação.

---

## 5. Integração com SimilarWeb Analytics

O **SimilarWeb Analytics** fornece análise de influência em tempo real:

- **Ranking de Periódicos:** Identifica periódicos com maior tráfego e influência.
- **Tendências Emergentes:** Detecta tópicos em ascensão com base em padrões de tráfego.
- **Análise de Autores:** Identifica autores com maior influência e cobertura de mídia.
- **Comparação de Fontes:** Compara a influência de diferentes repositórios (arXiv vs. bioRxiv, etc.).

---

## 6. Bibliotecas Python Especializadas

### 6.1 ArXiv (`arxiv`)

```python
import arxiv

# Busca por palavra-chave
client = arxiv.Client()
results = client.results(arxiv.Search(
    query='cat:cs.AI AND (neural networks OR deep learning)',
    start=0,
    max_results=100,
    sort_by=arxiv.SortCriterion.SubmittedDate,
    sort_order=arxiv.SortOrder.Descending
))

for result in results:
    print(f"Title: {result.title}")
    print(f"Authors: {result.authors}")
    print(f"Published: {result.published}")
    print(f"Summary: {result.summary}")
    print(f"PDF URL: {result.pdf_url}")
```

### 6.2 CrossRef (`crossref-commons`)

```python
from crossref.restful import Works

# Busca por DOI
works = Works()
result = works.doi('10.1038/nature12373')

# Busca por título
results = works.query('machine learning').sort('score').order('desc').get()
```

### 6.3 Semantic Scholar (`semanticscholar`)

```python
from semanticscholar import SemanticScholar

sch = SemanticScholar()

# Busca por palavra-chave
results = sch.search_paper('neural networks', limit=100)

# Busca por autor
author = sch.get_author('2262347')  # Yann LeCun
papers = author['papers']
```

### 6.4 PyMed (`pymed`)

```python
from pymed import PubMed

pubmed = PubMed(tool="MyTool", email="user@example.com")
results = pubmed.query("machine learning", max_results=100)

for article in results:
    print(f"Title: {article.title}")
    print(f"Abstract: {article.abstract}")
    print(f"PMID: {article.pmid}")
```

### 6.5 PyBliometrics (`pybliometrics`)

```python
from pybliometrics.scopus import ScopusSearch

# Busca em Scopus (requer credenciais)
s = ScopusSearch('TITLE-ABS-KEY(machine learning)', view='COMPLETE')

for result in s.results:
    print(f"Title: {result.title}")
    print(f"Citation Count: {result.citedby_count}")
    print(f"Publication Year: {result.year}")
```

### 6.6 PDF Parsing (`pdfplumber`, `PyPDF2`)

```python
import pdfplumber

# Extração de texto de PDF
with pdfplumber.open("article.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        print(text)
    
    # Extração de tabelas
    for table in pdf.pages[0].extract_tables():
        print(table)
```

---

## 7. MCP Sci-Hub Integration

O protocolo MCP Sci-Hub fornece acesso seguro e conformado a artigos completos:

### 7.1 Fluxo de Integração MCP

```
┌─────────────────────────────────────┐
│ Agente A4.13.4 identifica artigo    │
│ com DOI/URL                         │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│ Consulta MCP Sci-Hub para           │
│ disponibilidade                     │
└────────────┬────────────────────────┘
             │
        ┌────┴────┐
        │          │
   Disponível  Não disponível
        │          │
        │          └─► Tenta alternativas
        │              (ResearchGate, etc.)
        │
┌───────▼──────────────────────────────┐
│ MCP retorna URL segura de acesso     │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│ Download de PDF via MCP              │
│ (com logging e conformidade)         │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│ Extração de texto e metadados       │
│ via pdfplumber/PyPDF2               │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│ Armazenamento seguro de texto       │
│ para análise crítica                │
└─────────────────────────────────────┘
```

### 7.2 Chamada MCP Sci-Hub

```python
# Pseudocódigo para integração MCP
mcp_client = MCPClient()

# Verificar disponibilidade
availability = mcp_client.call(
    'scihub/check_availability',
    params={'doi': '10.1038/nature12373'}
)

if availability['available']:
    # Download seguro
    pdf_data = mcp_client.call(
        'scihub/download_pdf',
        params={'doi': '10.1038/nature12373'}
    )
    
    # Extração de texto
    text = extract_text_from_pdf(pdf_data)
```

---

## 8. Protocolo de Auditoria Forense Integrado

Todos os artigos recuperados são auditados pelo **Citation Impact Auditor (A5.9)** usando:

- **Verificação de DOI:** Confirmação em CrossRef.
- **Verificação de Autores:** Validação de identidade de autores em Scopus/ORCID.
- **Análise de Impacto:** Fator de impacto, citações, índice H.
- **Detecção de Retração:** Verificação em RetractionWatch.
- **Análise de Vieses:** Identificação de possíveis conflitos de interesse ou vieses.

---

## 9. Exemplo de Fluxo Completo

### Cenário: Busca por "Machine Learning em Diagnóstico Médico"

1. **Definição de Escopo (A2.7):**
   - Gap: "Falta de integração entre ML e diagnóstico clínico em tempo real"
   - Palavras-chave: "machine learning", "medical diagnosis", "real-time"
   - Critérios: Qualis A1, últimos 5 anos, fator de impacto > 3

2. **Busca Paralela (A4.13.4):**
   - **Canal 1:** Scopus retorna 250 artigos, filtrados para top 50
   - **Canal 2:** arXiv retorna 120 preprints, filtrados para top 30
   - **Canal 3:** MCP Sci-Hub acessa 40 dos artigos de Scopus
   - **Canal 4:** SimilarWeb identifica periódicos em ascensão (Nature Medicine, Lancet Digital Health)

3. **Agregação:** 120 artigos únicos após deduplicação

4. **Extração de Texto:** 50 artigos top têm texto completo extraído

5. **Análise Crítica (SA4.13.1):**
   - Identifica 3 gaps principais:
     - Falta de datasets públicos para treinamento
     - Limitações de interpretabilidade em modelos deep learning
     - Falta de integração com fluxos clínicos existentes

6. **Ranking Final:**
   - Top 10 artigos ranqueados por relevância + impacto
   - Todos validados por Citation Impact Auditor

7. **Síntese:** Documento de 5-10 páginas com análise crítica de como os gaps podem ser cobertos

---

## 10. Métricas de Qualidade

O Agente A4.13.4 é avaliado por:

- **Cobertura:** % de gaps cobertos por artigos relevantes (meta: 95%+)
- **Precisão:** % de artigos relevantes entre os recuperados (meta: 90%+)
- **Impacto Médio:** Fator de impacto médio dos artigos (meta: > 4)
- **Recência:** % de artigos dos últimos 2 anos (meta: 60%+)
- **Tempo de Execução:** Tempo total de busca (meta: < 5 minutos para 100+ artigos)
- **Conformidade de Auditoria:** % de artigos validados com sucesso (meta: 100%)

---

Este protocolo representa a integração de elite do Genesis-Writer v5.0 com as melhores ferramentas e técnicas de busca bibliográfica, garantindo que cada publicação seja fundamentada na literatura mais relevante, impactante e atual disponível.
