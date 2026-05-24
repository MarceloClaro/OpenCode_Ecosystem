<!--
  SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
  Toda resposta DEVE ser em português do Brasil formal.
  Contexto em chinês para eficiência de tokens (densidade +40%).
  Modelo: big-pickle (OpenCode Zen, 200K ctx, 128K out, gratuito)
  Genesis-Writer: integrado ao ecossistema v4.0
-->

# Agente A4.13.4: Busca Avançada Multicanal (Genesis-Writer v5.1)

## Identificação do Agente

| Atributo | Valor |
| --- | --- |
| **ID** | A4.13.4 |
| **Nome** | Busca Avançada Multicanal |
| **Camada** | L4 (Specialization & Content Generation) |
| **Tipo** | Subagente de A4.13 (Agente de Busca Bibliográfica Avançada) |
| **Status** | Ativo em v5.1+ |
| **Sincronização** | Agente-Sync-v4 (Qualidade 10/10) |

---

## 1. Missão e Responsabilidades

O Agente A4.13.4 é responsável pela execução de buscas bibliográficas de elite em múltiplos canais, integrando dados de bases acadêmicas tradicionais, repositórios abertos, acesso a artigos via MCP Sci-Hub e análise de impacto em tempo real via SimilarWeb Analytics.

**Missão Principal:** Descobrir, validar e sintetizar a literatura mais relevante, impactante e atual para cobrir gaps teóricos identificados pelo Agente de Análise Crítica de Gaps (A2.7).

---

## 2. Entradas e Saídas

### 2.1 Entradas

O Agente A4.13.4 recebe as seguintes entradas da Camada L2:

| Entrada | Origem | Descrição |
| --- | --- | --- |
| **Gaps Identificados** | A2.7 (Agente de Análise Crítica de Gaps) | Lista de lacunas teóricas e metodológicas a serem cobertas. |
| **Palavras-chave Primárias** | A2.7 | Termos principais para busca (ex: "machine learning", "diagnosis"). |
| **Palavras-chave Secundárias** | A2.7 | Termos complementares (ex: "real-time", "clinical workflow"). |
| **Critérios de Qualidade** | A2.1 (Analisador de Características) | Qualis mínimo, fator de impacto, índice H, data de publicação. |
| **Contexto de Domínio** | A1.5 (Motor de Descoberta de Domínio) | Ontologia do domínio, conceitos-chave, relações. |
| **Orçamento de Busca** | A1.3 (Construtor de Task Graph) | Número máximo de artigos a recuperar (ex: 100-200). |

### 2.2 Saídas

O Agente A4.13.4 produz as seguintes saídas para a Camada L5:

| Saída | Destino | Descrição |
| --- | --- | --- |
| **Artigos Ranqueados** | A5.9 (Citation Impact Auditor) | Lista de 50-100 artigos ranqueados por relevância + impacto. |
| **Textos Completos** | A4.1-A4.9 (MASWOS Writers) | Textos extraídos de PDFs para análise crítica e síntese. |
| **Análise de Gaps** | SA4.13.1 (Síntese Crítica de Gaps) | Relatório de como os gaps são cobertos pela literatura. |
| **Metadados Estruturados** | A5.1 (Validador de Constraints) | Metadados (DOI, autores, ano, fator de impacto) para validação. |
| **Trilha de Auditoria** | A5.6 (Protocolo de Micro-Auditoria) | Registro de todas as buscas, fontes consultadas e decisões. |

---

## 3. Arquitetura Interna

O Agente A4.13.4 é composto por **4 Subagentes de Canal** e **2 Subagentes de Processamento**:

### 3.1 Subagentes de Canal

#### SA4.13.4.1: Buscador de Bases Tradicionais

**Responsabilidade:** Buscar em Scopus, Web of Science, CrossRef, PubMed.

**Processo:**
1. Conectar a APIs oficiais (com credenciais).
2. Executar buscas com palavras-chave primárias e secundárias.
3. Filtrar por Qualis, fator de impacto, índice H, data de publicação.
4. Retornar metadados estruturados (DOI, autores, ano, título, abstract).

**Bibliotecas Python:**
- `crossref-commons`: API CrossRef
- `pybliometrics`: Scopus (requer credenciais)
- `pymed`: PubMed

**Exemplo de Código:**
```python
from crossref.restful import Works

works = Works()
results = works.query(
    'machine learning AND medical diagnosis',
    rows=100,
    sort='score',
    order='desc'
)

for item in results:
    article = {
        'doi': item.get('DOI'),
        'title': item.get('title'),
        'authors': item.get('author'),
        'year': item.get('published-online', {}).get('date-parts', [[None]])[0][0],
        'journal': item.get('container-title'),
        'impact_factor': item.get('is-referenced-by-count')
    }
```

#### SA4.13.4.2: Buscador de Repositórios Abertos

**Responsabilidade:** Buscar em arXiv, bioRxiv, medRxiv, SSRN.

**Processo:**
1. Conectar a APIs de repositórios.
2. Executar buscas com palavras-chave.
3. Filtrar por data de publicação (preferência para recente).
4. Retornar metadados e links para PDFs.

**Bibliotecas Python:**
- `arxiv`: arXiv API
- `requests + BeautifulSoup`: Scraping de bioRxiv/medRxiv

**Exemplo de Código:**
```python
import arxiv

client = arxiv.Client()
search = arxiv.Search(
    query='cat:cs.AI AND (neural networks OR deep learning)',
    max_results=100,
    sort_by=arxiv.SortCriterion.SubmittedDate,
    sort_order=arxiv.SortOrder.Descending
)

for result in client.results(search):
    article = {
        'arxiv_id': result.entry_id.split('/abs/')[-1],
        'title': result.title,
        'authors': [author.name for author in result.authors],
        'published': result.published,
        'summary': result.summary,
        'pdf_url': result.pdf_url
    }
```

#### SA4.13.4.3: Buscador via MCP Sci-Hub

**Responsabilidade:** Acessar artigos completos via MCP Sci-Hub e extrair texto.

**Processo:**
1. Para cada artigo com DOI, consultar MCP Sci-Hub para disponibilidade.
2. Se disponível, fazer download seguro do PDF via MCP.
3. Extrair texto completo usando `pdfplumber` ou `PyPDF2`.
4. Armazenar texto para análise crítica.

**Bibliotecas Python:**
- `pdfplumber`: Extração de texto de PDFs
- `PyPDF2`: Parsing de PDFs

**Exemplo de Código:**
```python
import pdfplumber
import requests

# Consultar MCP Sci-Hub
mcp_response = mcp_client.call(
    'scihub/check_availability',
    params={'doi': '10.1038/nature12373'}
)

if mcp_response['available']:
    # Download via MCP
    pdf_data = mcp_client.call(
        'scihub/download_pdf',
        params={'doi': '10.1038/nature12373'}
    )
    
    # Extração de texto
    with pdfplumber.open(pdf_data) as pdf:
        full_text = ""
        for page in pdf.pages:
            full_text += page.extract_text()
        
        # Extração de seções críticas
        abstract = extract_section(full_text, 'Abstract')
        methodology = extract_section(full_text, 'Methodology')
        results = extract_section(full_text, 'Results')
```

#### SA4.13.4.4: Analisador de Impacto via SimilarWeb

**Responsabilidade:** Analisar impacto de periódicos e autores via SimilarWeb Analytics.

**Processo:**
1. Para cada periódico identificado, consultar SimilarWeb para tráfego e influência.
2. Calcular score de impacto (tráfego + ranking global).
3. Identificar periódicos em ascensão vs. em declínio.
4. Retornar análise de tendências.

**Integração SimilarWeb:**
```python
import sys
sys.path.append('/opt/.manus/.sandbox-runtime')
from data_api import ApiClient

client = ApiClient()

# Análise de tráfego de periódico
result = client.call_api(
    'SimilarWeb/get_visits_total',
    path_params={'domain': 'nature.com'},
    query={'country': 'world', 'granularity': 'monthly', 'start_date': '2025-07', 'end_date': '2025-12'}
)

# Ranking global
ranking = client.call_api(
    'SimilarWeb/get_global_rank',
    path_params={'domain': 'nature.com'}
)

# Análise de fontes de tráfego
traffic_sources = client.call_api(
    'SimilarWeb/get_traffic_sources_desktop',
    path_params={'domain': 'nature.com'},
    query={'country': 'world', 'granularity': 'monthly', 'start_date': '2025-07', 'end_date': '2025-12'}
)
```

### 3.2 Subagentes de Processamento

#### SA4.13.4.5: Agregador e Deduplicador

**Responsabilidade:** Agregar resultados dos 4 canais e eliminar duplicatas.

**Processo:**
1. Coletar resultados de todos os 4 subagentes de canal.
2. Deduplica por DOI (quando disponível).
3. Deduplica por título normalizado (fuzzy matching, threshold 95%).
4. Deduplica por autores + ano.
5. Retornar lista única de artigos.

**Exemplo de Código:**
```python
from fuzzywuzzy import fuzz
import pandas as pd

def deduplicate_articles(articles):
    unique_articles = []
    seen_dois = set()
    seen_titles = set()
    
    for article in articles:
        # Verificar DOI
        if article.get('doi') and article['doi'] in seen_dois:
            continue
        
        # Verificar título
        title_normalized = article['title'].lower().strip()
        is_duplicate = False
        for seen_title in seen_titles:
            if fuzz.ratio(title_normalized, seen_title) > 95:
                is_duplicate = True
                break
        
        if not is_duplicate:
            unique_articles.append(article)
            if article.get('doi'):
                seen_dois.add(article['doi'])
            seen_titles.add(title_normalized)
    
    return unique_articles
```

#### SA4.13.4.6: Ranqueador por Relevância + Impacto

**Responsabilidade:** Rankear artigos por relevância para o gap + impacto acadêmico.

**Processo:**
1. Calcular score de relevância (similaridade semântica com gap).
2. Calcular score de impacto (fator de impacto + citações + índice H).
3. Calcular score de recência (preferência para artigos recentes).
4. Calcular score de qualidade Qualis (A1 > A2 > B1 > ...).
5. Combinar scores em ranking final.

**Fórmula de Ranking:**
```
Score Final = (0.4 × Relevância) + (0.3 × Impacto) + (0.2 × Recência) + (0.1 × Qualis)

Onde:
- Relevância: Similaridade semântica (0-1)
- Impacto: (Fator de Impacto + Citações Normalizadas + Índice H) / 3
- Recência: (Ano Atual - Ano Publicação) / 10 (capped at 1)
- Qualis: A1=1.0, A2=0.8, B1=0.6, B2=0.4, ...
```

---

## 4. Fluxo de Execução Detalhado

```
┌─────────────────────────────────────────────────────────────┐
│ Agente A4.13.4: Busca Avançada Multicanal                  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────────┐
        │ Receber Entradas (Gaps, Palavras-chave)
        └───────────────────────────────────────┘
                            │
                ┌───────────┼───────────┐
                │           │           │
                ▼           ▼           ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ SA4.13.4.1
        │ Bases    │ │ SA4.13.4.2
        │ Tradicionais
        │ (Scopus) │ │ Repositórios
        │          │ │ (arXiv)
        │          │ │          │
        └────┬─────┘ └────┬─────┘ └────┬─────┘
             │            │            │
             │            │            ▼
             │            │      ┌──────────┐
             │            │      │ SA4.13.4.3
             │            │      │ MCP Sci-Hub
             │            │      │ (PDFs)
             │            │      └────┬─────┘
             │            │           │
             └────────────┼───────────┘
                          │
                          ▼
        ┌─────────────────────────────────────┐
        │ SA4.13.4.5: Agregador e Deduplicador
        └─────────────────────────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────────┐
        │ SA4.13.4.4: Análise de Impacto
        │ (SimilarWeb Analytics)
        └─────────────────────────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────────┐
        │ SA4.13.4.6: Ranqueador
        │ (Relevância + Impacto)
        └─────────────────────────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────────┐
        │ Validação por A5.9 (Citation Auditor)
        │ Modo: Auditoria Forense
        └─────────────────────────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────────┐
        │ SA4.13.1: Síntese Crítica de Gaps
        │ (Análise de como gaps são cobertos)
        └─────────────────────────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────────┐
        │ Saída: Artigos Validados + Análise
        └─────────────────────────────────────┘
```

---

## 5. Sincronização com Agente-Sync-v4

O Agente A4.13.4 opera sob o regime de **Agente-Sync-v4**, garantindo:

| Aspecto | Mecanismo |
| --- | --- |
| **Qualidade 10/10** | Cada resultado é validado contra critérios de qualidade antes de integração. |
| **Sincronia Total** | Todos os 4 canais executam em paralelo com sincronização de barreira. |
| **Correção Ativa** | Se um canal falhar, ativa-se loop de correção (retry com parâmetros ajustados). |
| **Rastreabilidade** | Cada decisão é registrada no `Micro-Audit Protocol` (A5.6). |

---

## 6. Métricas de Desempenho

| Métrica | Meta | Método de Medição |
| --- | --- | --- |
| **Cobertura de Gaps** | 95%+ | % de gaps cobertos por artigos relevantes |
| **Precisão de Relevância** | 90%+ | % de artigos relevantes entre os recuperados |
| **Impacto Médio** | > 4 | Fator de impacto médio dos artigos |
| **Recência** | 60%+ | % de artigos dos últimos 2 anos |
| **Tempo de Execução** | < 5 min | Tempo total para 100+ artigos |
| **Conformidade de Auditoria** | 100% | % de artigos validados com sucesso |

---

## 7. Tratamento de Erros e Fallbacks

| Erro | Tratamento |
| --- | --- |
| **Falha de Conexão com API** | Retry com backoff exponencial (até 3 tentativas) |
| **Limite de Taxa Excedido** | Aguardar e retry (respeitar headers de rate-limit) |
| **Artigo Não Encontrado** | Registrar em log e continuar com próximo |
| **PDF Inacessível via Sci-Hub** | Tentar ResearchGate/Academia.edu como fallback |
| **Metadados Incompletos** | Usar informações parciais e marcar para revisão manual |

---

## 8. Integração com Outras Camadas

| Camada | Agente | Tipo de Integração |
| --- | --- | --- |
| **L2** | A2.7 (Análise de Gaps) | Recebe gaps identificados como entrada |
| **L4** | A4.1-A4.9 (MASWOS Writers) | Fornece textos completos para síntese |
| **L5** | A5.9 (Citation Auditor) | Valida todos os artigos em modo forense |
| **L5** | A5.1 (Validador de Constraints) | Valida metadados contra constraints |
| **L6** | A6.3 (Loop de Feedback) | Recebe feedback sobre qualidade de busca |

---

Este agente representa a integração de elite de múltiplas fontes bibliográficas, técnicas de scraping avançadas e análise de impacto em tempo real, garantindo que o Genesis-Writer v5.1 tenha acesso à literatura mais relevante, impactante e atual do mundo acadêmico.
