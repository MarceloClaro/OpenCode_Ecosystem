# Estratégia: Integração Anteprojeto UFC com OpenCode v4.2

**Status:** APROVADO | **Data:** 2026-05-30 | **Decisor:** Marcelo Claro

---

## RESUMO EXECUTIVO

### O Que Mudou?
**De:** Phase 4/C isolado (validação autossuficiente)  
**Para:** Integração com OpenCode v4.2 (600+ componentes existentes)

### Por Quê?
1. **Eficiência:** Reutilizar 125 agentes, 40 MCPs, 68 tipos raciocínio já validados
2. **Rastreabilidade:** Evitar reinventar roda; usar componentes com histórico de uso
3. **Qualidade:** criador-artigo (49 agentes), SEEKER (10 agentes), cora-debate (V1-V7) são MVP
4. **Conformidade:** protocol-anonimato já implementa LGPD/CEP/TCLE

### Impacto
- **Antes:** ~120 linhas Phase 4/C code × 60 problemas = overhead
- **Depois:** Usar `/artigo`, `/seeker`, `/agent-forum` via CLI ou API
- **Ganho:** Foco em anteprojeto (pesquisa + educação), não em infraestrutura

---

## MAPEAMENTO RÁPIDO: Fases ↔ Componentes

| Fase Anteprojeto | Componente OpenCode | Status |
|------------------|-------------------|--------|
| **Fase 1: Análise Documental** | `editais-br` (52 editais) | ✅ Pronto |
| | `code-graphrag` (grafo) | ✅ Pronto |
| **Fase 2: Desenvolvimento Guia** | `criador-artigo` (49 agentes) | ✅ Pronto |
| | `SEEKER` (10 agentes) | ✅ Pronto |
| | `academic-export-abnt` | ✅ Pronto |
| | `baoyu-markdown-to-html` | ✅ Pronto |
| **Fase 3a: Especialistas** | `agent-forum` P14 | ✅ Pronto |
| | `cora-debate` P18 (V1-V7) | ✅ Pronto |
| **Fase 3b: Grupo Focal** | `html-ppt` | ✅ Pronto |
| | `protocol-anonimato` | ✅ Pronto |
| | `sequential-thinking` MCP | ✅ Pronto |

**Nenhuma dependência bloqueadora.** Tudo pronto para uso.

---

## EXECUÇÃO: 4 FASES, 24 SEMANAS

### ⏰ **Semanas 1-4: Fase 1 (Análise)**
```bash
opencode /editais-br --query "LGPD privacidade" --limit 10
opencode /code-graphrag --entity "Agentes" --depth 3
```
**Saída:** `CONFORMIDADE_LGPD_OPENCODE.md`

### ⏰ **Semanas 5-12: Fase 2 (Guia)**
```bash
opencode /artigo --modules 4 --agents 49 --output_format "markdown_html"
opencode /seeker --query "IA educação LGPD" --limit 50 --export_bibtex
```
**Saída:** `GUIA_PRATICO_MODULOS_1-4.html` + 50+ referências

### ⏰ **Semana 13: Fase 3a (Validação)**
```bash
opencode /agent-forum --especialistas 3 --documento "GUIA.html" --fases 4
opencode /cora-debate --documento "GUIA.html" --verificadores 7
```
**Saída:** `VALIDACAO_ESPECIALISTAS.json` (Q-Score ≥ 0.85)

### ⏰ **Semanas 13-20: Fase 3b (Grupo Focal)**
```bash
opencode /protocol-anonimato --gerar_tcle --pesquisadores 8-12
opencode /html-ppt --template "tech-sharing" --slides 4
# Coleta: 4 encontros × 2h + logs anonimizados
```
**Saída:** `dados_grupo_focal_anonimizado.db` + análise temática

### ⏰ **Semanas 21-24: Fase 4 (Sistematização)**
```bash
opencode /analise-qualitativa --metodo "bardin" --export "analise_tematica.json"
opencode /academic-export-abnt --output "dissertacao_final.pdf"
```
**Saída:** `DISSERTACAO_PPGTE_2026.pdf` + `GUIA_PRATICO_DIGITAL.html`

---

## MÉTRICAS DE SUCESSO (GO/NO-GO)

### Fase 1 ✅
- [ ] Relatório CONFORMIDADE ≥ 95% cobertura (125 agentes × 40 MCPs)
- [ ] Grafo em code-graphrag com dependências mapeadas

### Fase 2 ✅
- [ ] 4 módulos (A-D) em HTML responsivo
- [ ] ≥ 50 referências com DOI verificável
- [ ] Debate criador-artigo convergiu (consensus ≥ 0.85)

### Fase 3a ✅
- [ ] Debate 3 especialistas convergiu (Q-Score ≥ 0.85)
- [ ] Cora-Debate V1-V7 validou 100% afirmações críticas
- [ ] VALIDACAO_ESPECIALISTAS.json ≥ 95% confiança

### Fase 3b ✅
- [ ] 8-12 pesquisadores completaram 4 encontros
- [ ] Likert pré/pós Δ ≥ 1.5 (escala 5)
- [ ] ≥ 5 códigos temáticos identificados (Bardin)
- [ ] 0 vazamentos LGPD (auditoria CEP/TCLE)

### Fase 4 ✅
- [ ] Dissertação ≥ 30 páginas + Qualis A1 (∨ A2)
- [ ] Manual digital responsivo (web)
- [ ] Defesa pública com banca aprovadora

---

## RISCOS E MITIGAÇÃO

| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|--------|-----------|
| `criador-artigo` não converge em 12 semanas | Baixa (49 agentes testados) | Alto | Usar MASWOS fallback; estender para 14 semanas |
| SEEKER não encontra 50 referências | Muito Baixa (10+ fontes) | Médio | Expandir sources; manual search last resort |
| Especialistas não convergem (Q-Score < 0.85) | Baixa (agent-forum validado) | Médio | Adicionar 4ª especialista ou estender debate |
| Grupo focal < 8 pesquisadores | Médio | Alto | Recrutamento em múltiplas unidades UFC |
| CEP rejeita protocolo | Muito Baixa (protocol-anonimato compliance) | Crítico | Preparar antecepar: CEP pré-análise em semana 1 |

---

## ALTERNATIVAS CONSIDERADAS E REJEITADAS

### ❌ Superhuman (Google DeepMind)
- Custo computacional: 1-5s/problema vs OpenCode 0.002s
- Custo financeiro desconhecido
- Black-box (vs OpenCode transparency)
- **Decisão:** Usar como Phase D (integração futura), não Phase atual

### ❌ Phase 4/C Isolado
- Reinventar roda (125 agentes já existem)
- Overhead de manutenção
- Sem aproveitamento ecosystem
- **Decisão:** Abandonado. Usar OpenCode v4.2 como backbone

### ✅ **Integração OpenCode v4.2** (SELECIONADO)
- Reutiliza 600+ componentes validados
- Foco em pesquisa, não infraestrutura
- Conformidade LGPD integrada
- Rastreabilidade e auditoria caixa branca

---

## ARTIFACTS DE REFERÊNCIA

| Documento | Localização | Propósito |
|-----------|------------|----------|
| Anteprojeto Original | `ANTEPROJETO_PPGTE_2026.md` | Escopo e objetivos |
| Plano Integração | `INTEGRACAO_OPENCODE_V42.md` | Este documento (detalhado) |
| Checklist Execução | `CHECKLIST_EXECUCAO.md` | Task-by-task (próximo) |
| OpenCode v4.2 Docs | `~/.config/opencode/AGENTS.md` | 600+ componentes |

---

## COMUNICAÇÃO PARA ORIENTADOR

### Email Proposto

---

**Assunto:** Estratégia Anteprojeto PPGTE 2026 — Integração com OpenCode v4.2

Prezado Professor,

Após análise crítica, decidimos **integrar o anteprojeto ao ecossistema OpenCode v4.2** (600+ componentes) em vez de desenvolver validação isolada (Phase 4/C).

**Justificativa:**
1. **Reutilização:** 125 agentes, 40 MCPs, 68 tipos raciocínio já testados
2. **Eficiência:** Foco em pesquisa (guia prático + grupo focal), não infraestrutura
3. **Conformidade:** LGPD/CEP/TCLE já implementados em protocol-anonimato
4. **Rastreabilidade:** SHA-256 logs, auditoria caixa branca integrada

**Cronograma:**
- Semanas 1-4: Análise Documental (editais-br + code-graphrag)
- Semanas 5-12: Desenvolvimento Guia (criador-artigo + SEEKER)
- Semana 13: Validação Especialistas (agent-forum + cora-debate)
- Semanas 13-20: Estudo Caso (grupo focal 8-12 pesquisadores)
- Semanas 21-24: Sistematização e defesa

**Componentes-chave:**
- `criador-artigo`: 49 agentes, 8 estágios de validação
- `SEEKER`: 10 agentes, 10+ fontes acadêmicas
- `agent-forum` P14: Debate 3 especialistas (IA, Direito, Educação)
- `cora-debate` P18: V1-V7 verificadores formais
- `protocol-anonimato`: LGPD conformance + CEP/TCLE

**Próximo passo:** Agendamento para discussão e aprovação desta estratégia.

Atenciosamente,  
Marcelo Claro

---

## ASSINATURA E APROVAÇÃO

| Papel | Nome | Assinatura | Data |
|------|------|-----------|------|
| Pesquisador | Marcelo Claro | _________________ | 2026-05-30 |
| Orientador | [PPGTE/UFC] | _________________ | __________ |
| Banca Avaliadora | | | |

---

**Fim do Resumo Estratégico**
