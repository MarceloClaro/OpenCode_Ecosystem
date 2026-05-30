---
title: "TSAC — Rastreabilidade de Citações"
version: "4.6"
banned_words: 87
annotations: 46
---

# TSAC — Traceable Source-Anchored Citation

## Definição

TSAC (Traceable Source-Anchored Citation) é o sistema de rastreabilidade de citações do OpenCode Ecosystem. Cada afirmação derivada de fonte externa é ancorada em uma referência verificável com trilha de auditoria completa.

## Arquitetura

```
┌──────────────────────────────────────────────────────────────────┐
│                    TSAC — CICLO DE RASTREABILIDADE                 │
│                                                                   │
│  FONTE ──▶ EXTRAÇÃO ──▶ ANCORAGEM ──▶ VERIFICAÇÃO ──▶ AUDITORIA  │
│   │           │            │             │              │          │
│   ▼           ▼            ▼             ▼              ▼          │
│  DOI       SEEKER       [TSAC-###]    Cora-Debate    Audit Trail  │
│  URL       Parser       46 anotações   V3 CrossRef   JSON/MD      │
│                                                                   │
│  ┌───────────────────────────────────────────────────────────┐   │
│  │  EXEMPLO DE ANOTAÇÃO TSAC:                                │   │
│  │                                                            │   │
│  │  "O investimento em P&D privado apresenta correlação      │   │
│  │   positiva com inovação tecnológica [TSAC-001]."           │   │
│  │                                                            │   │
│  │  [TSAC-001] World Bank (2023). WDI Indicators.             │   │
│  │  DOI: 10.xxxx/wdi2023 · Acessado: 2026-05-20              │   │
│  │  Verificação: Cora-Debate V3 ✅ · Confiança: 0.97         │   │
│  └───────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

## 87 Palavras Banidas (Anti-AI Vocabulary)

### Categorias de Palavras Proibidas

| Categoria | Exemplos | Quantidade |
|-----------|----------|:----------:|
| Advérbios formulaicos | notavelmente, significativamente, fundamentalmente | 12 |
| Conectores AI | além disso, ademais, outrossim, por conseguinte | 8 |
| Hipérboles | crucial, essencial, vital, imprescindível | 6 |
| Anglicismos | implementar (no sentido de realizar), endereçar (problema) | 10 |
| Travessões | — (em-dash) | 1 |
| Estruturas ternárias | "não apenas X, mas também Y, e ainda Z" | 4 |
| Perguntas retóricas | "Mas o que isso significa?" | 3 |
| Clichês acadêmicos | "à luz de", "no contexto de", "na contemporaneidade" | 15 |
| Generalizações | "é amplamente reconhecido", "a literatura demonstra" | 8 |
| Jargão vazio | "disruptivo", "paradigmático", "holístico" | 10 |
| Voz passiva abusiva | "pode ser observado", "deve ser notado" | 6 |
| Redundâncias | "planejamento prévio", "consenso geral" | 4 |

### Matriz de Substituição

| Palavra Banida | Substituição Recomendada |
|----------------|--------------------------|
| notavelmente | Remove-se (advérbio vazio) |
| crucial | importante, relevante, determinante |
| implementar | executar, aplicar, realizar |
| à luz de | com base em, segundo |
| disruptivo | inovador, transformador |
| holístico | integrado, abrangente |

## 46 Anotações TSAC Auditáveis

| ID | Fonte | Tipo | Confiança |
|:--:|-------|:----:|:---------:|
| TSAC-001 | World Bank WDI 2023 | Dados | 0.99 |
| TSAC-002 | OECD Science & Tech 2024 | Dados | 0.99 |
| TSAC-003 | WHO Global Health 2024 | Dados | 0.99 |
| TSAC-004 | UNESCO Education 2023 | Dados | 0.99 |
| TSAC-005 | FAO Food Security 2024 | Dados | 0.98 |
| TSAC-006 | IBGE PNAD 2023 | Dados | 0.99 |
| TSAC-007 | arXiv:2301.xxxxx | Paper | 0.97 |
| TSAC-008 | PubMed:3829xxxx | Paper | 0.98 |
| TSAC-009 | Semantic Scholar:S2xxxx | Paper | 0.97 |
| TSAC-010 | OpenAlex:Wxxxx | Paper | 0.96 |
| ... | ... | ... | ... |
| TSAC-046 | CORE:xxxxx | Paper | 0.95 |

## Verificação Automática

```python
# TSAC Verifier
from criador_artigo.banca.ptbr_corrector import detectar_cjk
from skills.agent_forum.scripts.phd_auditor import verificar_referencias

artigo = open("artigo.tex").read()

# 1. Verificar CJK (zero-tolerance)
cjk = detectar_cjk(artigo)
assert len(cjk) == 0, f"CJK encontrado: {cjk}"

# 2. Verificar TSAC annotations
tsac = verificar_referencias(artigo)
assert all(t.confianca >= 0.95 for t in tsac), "Referências com baixa confiança"

# 3. Cross-validate DOIs
dois = [t.doi for t in tsac]
validados = crossref_validate(dois)
assert len(validados) == len(dois), "DOIs não validados"
```

## Relatório de Auditoria

Cada artigo gera um `audit_trail.json` com:
- 46 anotações TSAC com DOI, URL, data de acesso
- Hash SHA256 do conteúdo referenciado
- Timestamp de verificação Cora-Debate V3
- Score de confiança (0.95-0.99)
- Status de validação CrossRef
