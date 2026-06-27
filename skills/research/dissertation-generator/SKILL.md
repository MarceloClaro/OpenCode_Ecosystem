# Dissertation Generator Skill v1.0
# SPEC-052: Autonomous Academic Production Pipeline

## Overview
Gera dissertações acadêmicas completas a partir de um outline, com pipeline autônomo:
**Outline → Capítulos LaTeX → Compilação → PDF + Áudio + DOCX**

## Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                  DISSERTATION GENERATOR v1.0                │
│                                                              │
│  INPUT: Outline (tema, objetivos, estrutura)                 │
│                                                              │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐ │
│  │ OUTLINE  │──▶│ CHAPTERS │──▶│ COMPILE  │──▶│  OUTPUT  │ │
│  │ ANALYZER │   │ WRITER   │   │ ENGINE   │   │ PACKAGER │ │
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘ │
│       │              │              │              │         │
│       ▼              ▼              ▼              ▼         │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐ │
│  │ Structure│   │ LaTeX    │   │ pdflatex │   │ PDF      │ │
│  │ + Scope  │   │ + BibTeX │   │ + biber  │   │ + Audio  │ │
│  │ + Refs   │   │ + Figures│   │ + TTS    │   │ + DOCX   │ │
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘ │
│                                                              │
│  FEEDBACK LOOP:                                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ Anti-AI Scanner ←→ Anti-Plagiarism ←→ Quality Score    │ │
│  │        │                  │                │            │ │
│  │        └──────────────────┴────────────────┘            │ │
│  │                    AUTO-CORRECTION                       │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Pipeline Phases

### Phase 1: OUTLINE ANALYSIS
**Input:** Tema + objetivos do usuário
**Output:** Outline estruturado com:
- Capítulos (H1)
- Seções (H2)
- Subseções (H3)
- Objetivo de cada capítulo
- Fontes principais por capítulo
- Palavras-chave

**Commands:**
```python
# Analisa outline e gera estrutura
python dissertation_generator.py analyze --topic "Tema" --objectives "objetivos"
```

### Phase 2: CHAPTER WRITING
**Input:** Outline estruturado
**Output:** Arquivos `.tex` por capítulo

**Features:**
- Escrita acadêmica formal (PT-BR)
- Citações com `\cite{}` integradas
- Tabelas e figuras TikZ
- Notas de rodapé com resenhas críticas
- Anti-AI: vocabulário variado, sem clichês
- Cross-references automáticas

**Quality Gates:**
1. Anti-AI Scanner score ≥ 85
2. Anti-Plagiarism score ≥ 85 (A)
3. Todas as citações com DOI verificado
4. Tabelas dentro das margens

### Phase 3: COMPILE ENGINE
**Input:** Arquivos `.tex` + `referencias.bib`
**Output:** PDF compilado

**Pipeline:**
```bash
pdflatex → biber → pdflatex → pdflatex
```

**Validation:**
- 0 undefined references
- 0 errors
-Warnings < 10 (cosméticos)

### Phase 4: OUTPUT PACKAGER
**Input:** PDF compilado
**Output:** PDF + Áudio MP3 + DOCX

**Sub-pipelines:**
1. **PDF→Audio:** edge-tts com voz pt-BR-FranciscaNeural
2. **PDF→DOCX:** pandoc com citeproc + APA style

## Usage Examples

### Example 1: Generate Dissertation from Topic
```bash
# User provides topic and objectives
/dissertation generate \
  --topic "Metodologias Ativas na Educação Brasileira" \
  --objectives "Investigar ABP e ABPr" \
  --chapters 5 \
  --output ./minha-dissertacao/
```

### Example 2: Compile Existing LaTeX
```bash
# User has .tex files, wants PDF + Audio + DOCX
/dissertation compile \
  --input ./dissertacao-latex/ \
  --formats pdf,audio,docx
```

### Example 3: Quality Check
```bash
# Run anti-AI and anti-plagiarism scanners
/dissertation quality \
  --input ./dissertacao.pdf \
  --threshold 85
```

## Integration with Ecosystem

### MCPs Used:
- **sura-papers**: Academic paper search
- **arxiv-mcp**: Preprint search
- **latest-science**: Latest research
- **scihub**: Full-text access

### Skills Used:
- **anti-ai-scanner**: Quality scoring
- **anti-plagiarism-scanner**: Originality check
- **potentiality-estimator-v2**: Research gaps
- **SEEKER**: Deep research

### Agents Used:
- **marceloclaro**: Orchestration
- **master-orchestrator**: Pipeline execution
- **code-reviewer**: Quality validation
- **linguistic-corrector**: PT-BR grammar

## Configuration

```json
{
  "dissertation_generator": {
    "version": "1.0",
    "default_chapters": 5,
    "default_language": "pt-BR",
    "citation_style": "apa",
    "quality_threshold": 85,
    "tts_voice": "pt-BR-FranciscaNeural",
    "tts_rate": "-5%",
    "auto_compile": true,
    "auto_audio": true,
    "auto_docx": true
  }
}
```

## Learning from Past Cycles

### R26 Lessons Applied:
1. **Encoding issues**: UTF-8 BOM detection for LaTeX files
2. **Reference management**: biblatex+biber over natbib+apalike
3. **Citation footnotes**: (1) Original, (2) Translation, (3) Critical review
4. **Anti-AI scoring**: Thresholds adjusted to 85 (not 100)
5. **Figure/table margins**: Always check overfull hbox
6. **Audio generation**: edge-tts with chunking for long texts
7. **DOCX conversion**: pandoc with citeproc for bibliography

### Metacognitive Improvements:
- Self-evaluation after each phase
- Anomaly detection in compilation errors
- Auto-correction for common LaTeX issues
- Learning from anti-AI scanner patterns
