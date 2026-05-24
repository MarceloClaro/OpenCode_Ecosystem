<!--
  SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
  Toda resposta DEVE ser em português do Brasil formal.
  Contexto em chinês para eficiência de tokens (densidade +40%).
  Modelo: big-pickle (OpenCode Zen, 200K ctx, 128K out, gratuito)
  Genesis-Writer: integrado ao ecossistema v4.0
-->

# Mapa de Fluxo Completo: Agentes, Camadas e Protocolos

## Genesis-Writer v5.1: Arquitetura de Orquestração Cirúrgica com Busca Bibliográfica Multicanal

Este documento detalha o fluxo operacional completo do Genesis-Writer v5.1, mapeando cada agente, seus subjacentes, as 8 camadas de orquestração, regras de sincronização, protocolos de auditoria e integração de busca bibliográfica avançada com scraping, MCP Sci-Hub e análise de impacto.

---

## NOVIDADES NA VERSÃO v5.1

### 1. Agente A4.13.4: Busca Avançada Multicanal (Novo)

O novo **Agente A4.13.4** representa a evolução máxima da busca bibliográfica, integrando 4 canais de acesso paralelo:

#### **Canal 1: Bases de Dados Tradicionais**
- **Fontes:** Scopus, Web of Science, CrossRef, PubMed
- **Método:** API oficial com autenticação
- **Validação:** Verificação de DOI em tempo real
- **Cobertura:** 95%+ da literatura acadêmica indexada

#### **Canal 2: Repositórios Abertos**
- **Fontes:** arXiv, bioRxiv, medRxiv, SSRN
- **Método:** Scraping inteligente com respeito a robots.txt
- **Validação:** Extração de metadados estruturados
- **Cobertura:** Preprints e publicações de acesso aberto

#### **Canal 3: Acesso a Artigos Completos**
- **Fonte:** MCP Sci-Hub com conformidade de auditoria
- **Método:** Integração segura com trilha de auditoria
- **Validação:** Verificação de integridade de PDF
- **Cobertura:** Textos completos para análise crítica

#### **Canal 4: Análise de Impacto em Tempo Real**
- **Fonte:** SimilarWeb Analytics, Google Scholar, Altmetrics
- **Método:** Cálculo de fator de impacto, índice H, citabilidade
- **Validação:** Comparação com benchmarks de qualidade
- **Cobertura:** Métricas de relevância e influência

### 2. Subagentes Especializados (v5.1)

#### **SA4.13.1: Buscador de Bases Tradicionais**
- Consulta Scopus, Web of Science, CrossRef, PubMed com autenticação
- Implementa retry logic com backoff exponencial
- Normaliza resultados em formato padrão
- Registra cada consulta para auditoria

#### **SA4.13.2: Scraper de Repositórios**
- Extrai metadados de arXiv, bioRxiv, medRxiv, SSRN
- Respeita rate limiting e robots.txt
- Valida estrutura de dados extraída
- Detecta e trata duplicatas

#### **SA4.13.3: Acesso a Artigos Completos**
- Integração MCP Sci-Hub com conformidade
- Extração de texto via pdfplumber/PyPDF2
- Validação de integridade de conteúdo
- Trilha de auditoria de cada acesso

#### **SA4.13.4: Analisador de Impacto**
- Calcula fator de impacto (JIF, SJR, SNIP)
- Computa índice H e índice-i10
- Analisa padrões de citação
- Gera score de relevância ponderado

#### **SA4.13.5: Filtrador de Relevância**
- Análise de similaridade semântica com gaps
- Ranking por TF-IDF e embeddings
- Filtragem por Qualis A1/A2
- Deduplicação por DOI/título/autores

#### **SA4.13.6: Síntese Crítica de Gaps**
- Sintetiza informações para cobrir gaps identificados
- Identifica contradições e convergências
- Propõe novos insights a partir de correlações
- Gera mapa conceitual de relações

### 3. Protocolo de Sincronização Multicanal

```
┌─────────────────────────────────────────────────────────────┐
│           EXECUÇÃO PARALELA DE 4 CANAIS                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Canal 1          Canal 2          Canal 3          Canal 4 │
│  (Bases)          (Repos)          (Artigos)        (Impacto)│
│    │                │                 │                │    │
│    ├─ Scopus        ├─ arXiv          ├─ Sci-Hub      ├─ JIF│
│    ├─ WoS           ├─ bioRxiv        ├─ PDF Extract  ├─ H-idx
│    ├─ CrossRef      ├─ medRxiv        ├─ Validação    ├─ Citações
│    └─ PubMed        └─ SSRN           └─ Auditoria    └─ Score
│                                                             │
│                    ↓ AGREGAÇÃO ↓                           │
│                                                             │
│  • Deduplicação por DOI/Título/Autores                     │
│  • Ranking por Relevância + Impacto + Recência + Qualis    │
│  • Validação Forense de Todas as Citações                  │
│  • Extração de Trechos Originais para Análise Crítica      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 4. Validação de Confiança Zero

Cada citação passa por 7 níveis de validação:

1. **Verificação de DOI:** CrossRef API
2. **Verificação de URL:** Teste de acessibilidade
3. **Verificação de Trecho:** Extração e comparação
4. **Análise de Impacto:** Fator de impacto e índice H
5. **Validação Semântica:** Relevância com gaps
6. **Análise Crítica:** Contradições e convergências
7. **Auditoria Forense:** Trilha completa de origem

### 5. Métricas de Qualidade v5.1

| Métrica | Target | Validação |
|---------|--------|-----------|
| Cobertura de Gaps | 95%+ | Comparação com literatura |
| Precisão de Relevância | 90%+ | Análise manual de amostra |
| Fator de Impacto Médio | > 4 | Scopus/WoS |
| Conformidade de Auditoria | 100% | Trilha forense |
| Taxa de Deduplicação | 99%+ | Comparação DOI/Título |
| Tempo de Busca | < 5 min | Execução paralela |

---

## FLUXO DE EXECUÇÃO COMPLETO v5.1

```
1. Usuário inicia novo projeto (artigo Qualis A1, livro 12 capítulos, tese)
   ↓
2. L0: Meta-Coordenação
   - A0.1: Orquestrador Mestre recebe requisição
   - A0.2: Gerente de Sessão inicializa estado
   - A0.3: Porteiro de Permissões valida acesso
   - A0.4: Harness de Veracidade valida fontes iniciais
   ↓
3. L1: Descoberta de Conhecimento
   - A1.1: Registrador de Skills injeta habilidades
   - A1.2: Compressor de Contexto otimiza espaço
   - A1.3: Construtor de Task Graph mapeia tarefas
   - A1.4: Armazenador de Memória persiste conhecimento
   - A1.5: Motor de Descoberta de Domínio extrai ontologia
   - A1.6: Motor de Insights de Variáveis Cruzadas identifica correlações
   ↓
4. L2: Raciocínio Autônomo
   - A2.1: Analisador de Características perfila problema
   - A2.2: Seletor de Raciocínio escolhe entre 38 sub-tipos
   - A2.3: Configurador de Parâmetros otimiza sensibilidade
   - A2.4: Validador de Estratégia testa eficácia
   - A2.5: Auto-Reflexor questiona pressupostos
   - A2.6: Metodologia-Agente Mapper associa metodologias
   - A2.7: Agente de Análise Crítica de Gaps identifica lacunas
   ↓
5. L3: Execução Fracionada
   - A3.1: Gerador de Subagentes cria agentes especializados
   - A3.2: Gerente de Quadro estrutura capítulos/seções
   - A3.3: Coordenador de Dependências ordena tarefas
   - A3.4: Construtor de Quadro cria estrutura hierárquica
   - A3.5: Executor de Tarefas delega trabalho
   - A3.6: Barreira de Sincronização Micro valida progressão
   - A3.7: Fracionador de Conteúdo divide em unidades atômicas
   ↓
6. L4: Especialização e Conteúdo
   - A4.1-A4.9: MASWOS Writing Agents redação especializada
   - A4.10: Agente de Especialização Emergente adapta capacidades
   - A4.11: Agente de Análise Estatística realiza análises
   - A4.12: Agente de Machine Learning desenvolve modelos
   - A4.13.4: Busca Avançada Multicanal (v5.1)
     * Canal 1: Consulta Scopus, WoS, CrossRef, PubMed
     * Canal 2: Scraping arXiv, bioRxiv, medRxiv, SSRN
     * Canal 3: Acesso MCP Sci-Hub a artigos completos
     * Canal 4: Análise SimilarWeb de impacto
     * Agregação paralela com deduplicação
     * Validação forense de todas as citações
   ↓
7. L5: Auditoria Científica
   - A5.1: Validador de Constraints aplica 500+ regras
   - A5.2: Auditor Qualis A1 avalia qualidade
   - A5.3: Validador de Citações verifica autenticidade
   - A5.4: Validador de Referências Cruzadas
   - A5.5: Detector de Plágio
   - A5.6: Protocolo de Micro-Auditoria registra tudo
   - A5.7: Harness de Validação Estatística valida análises
   - A5.8: Auditor de Modelo de ML valida modelos
   - A5.9: Citation Impact Auditor verifica impacto
   ↓
8. L6: Observabilidade e Feedback
   - A6.1: Monitor de Eventos coleta eventos
   - A6.2: Agregador de Feedback compila feedback
   - A6.3: Gerador de Feedback cria recomendações
   - A6.4: Motor de Meta-Aprendizado otimiza ciclos futuros
   - A6.5: Simulador de Banca Examinadora simula revisão crítica
   ↓
9. L7: Saída e Entregáveis
   - A7.1: Integrador Final consolida arquivos fracionados
   - A7.2: Gerador de Relatórios produz relatório de qualidade
   - A7.3: Gerador de Trilha de Auditoria cria rastreabilidade
   - A7.4: Entregador Verificado entrega resultado final
   ↓
10. Documento final entregue com:
    - Conteúdo coeso e fluido
    - Citações 100% verificadas e auditáveis
    - Análises estatísticas validadas
    - Modelos de ML auditados
    - Relatório de qualidade Qualis A1
    - Trilha de auditoria forense completa
    - Insights de variáveis cruzadas descobertos
```

---

## INTEGRAÇÃO COM AGENTE-SYNC-v4

O Genesis-Writer v5.1 integra o **agente-sync-v4** para garantir:

- **Sincronização Perfeita:** Todos os 45+ agentes operando em harmonia
- **Loops de Correção Ativa:** Se um canal falhar, outro assume
- **Qualidade 10/10:** Garantia de excelência em cada operação
- **Auditoria Total:** Cada decisão rastreável e verificável

---

## CONCLUSÃO

O Genesis-Writer v5.1 representa a evolução máxima de um sistema de escrita científica autônomo, combinando:

✅ **Orquestração Cirúrgica:** 45+ agentes em 8 camadas com sincronização micro-granular
✅ **Busca Bibliográfica de Elite:** 4 canais paralelos com acesso global a literatura
✅ **Auditoria Forense Total:** 100% de rastreabilidade e verificabilidade
✅ **Rigor Científico:** Validação de confiança zero em dados, análises e citações
✅ **Descoberta de Insights:** Cruzamento de variáveis para encontrar o que outros não veem
✅ **Qualidade Garantida:** Simulação de banca examinadora para nota 10/10

Este sistema está pronto para produzir ciência de impacto real com transparência total e excelência acadêmica inigualável.
