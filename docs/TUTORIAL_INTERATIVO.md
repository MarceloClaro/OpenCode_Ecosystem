# Tutorial Interativo — OpenCode Ecosystem

**Guia para Novos Usuarios** | **Nivel:** Iniciante a Intermediario  
**Tempo estimado:** 30 minutos | **Pre-requisito:** Python basico

---

## 1. O Que E o OpenCode Ecosystem

O OpenCode Ecosystem e uma plataforma de IA que coordena **125 agentes especializados**
para automatizar tarefas academicas como pesquisa bibliografica, redacao cientifica,
verificacao de qualidade LaTeX e validacao de raciocinio matematico.

Diferente de um chatbot tradicional, o ecossistema divide o trabalho entre dezenas
de agentes que colaboram, debatem entre si e verificam mutuamente seus resultados
antes de apresenta-los ao usuario. Todo resultado e rastreavel a uma fonte (DOI, arXiv)
ou a um teste automatizado (TDD).

---

## 2. Pre-Requisitos

| Ferramenta | Versao Minima | Como Verificar |
|------------|:------------:|----------------|
| Python | 3.10+ | `python --version` |
| Git | 2.40+ | `git --version` |
| pdflatex | TeX Live 2023+ | `pdflatex --version` (opcional) |
| pip | 23.0+ | `pip --version` |

---

## 3. Instalacao em 3 Passos

### Passo 1: Clonar o Repositorio

```bash
git clone https://github.com/MarceloClaro/OpenCode_Ecosystem.git
cd OpenCode_Ecosystem
```

### Passo 2: Criar Ambiente Virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### Passo 3: Instalar Dependencias

```bash
pip install pytest numpy scipy
```

**Saida esperada:**
```
Successfully installed pytest-9.0.3 numpy-1.24.4 scipy-1.10.1 ...
```

---

## 4. Primeira Execucao: Diagnostico Rapido

```bash
python menu.py --quick
```

**Saida esperada:**
```
============================================================
  OpenCode Ecosystem — Diagnostico Rapido
============================================================
  Artefatos descobertos:
    .tex: 3 arquivos
    Testes: 30 suites
    Pipelines: 2 scripts
    Backups: 4 versoes
    Insights: 5 documentos
============================================================
  Executando TDD...
    16/16 GREEN — Todos os quality gates passando
============================================================
```

---

## 5. Executando os Testes

### Suite Rapida (5 minutos)

```bash
python -m pytest artigo/evaluations/tests/test_d1_matematica.py -v
```

**Saida esperada:**
```
test_d1_matematica.py::test_pitagoras PASSED
test_d1_matematica.py::test_gauss_summation PASSED
test_d1_matematica.py::test_fatorial PASSED
...
12 passed in 0.45s
```

### Suite Completa (10 minutos)

```bash
python -m pytest artigo/evaluations/tests/ -v --tb=short
```

**Saida esperada:**
```
test_d1_matematica.py .......                                              [  5%]
test_d2_fisica.py ........                                                 [ 10%]
test_d9_metodologia.py ...............                                     [ 20%]
test_anticircularidade.py ..............                                   [ 30%]
test_evolucao_m4.py .......                                                [ 35%]
...
206 passed in 45.23s
```

### Validacao Externa (5 minutos)

```bash
python artigo/evaluations/tests/test_exaustivo_final.py
```

**Saida esperada:**
```
============================================================
  VALIDACAO EXTERNA — Project Euler + Rosalind
============================================================
  PE001 — Multiplos de 3 e 5: 233168... PASS
  PE002 — Fibonacci pares: 4613732... PASS
  ...
  ROSALIND DNA — Contagem de nucleotideos: OK... PASS
  ...
============================================================
  RESULT: 34/34 passed, 0 failed
============================================================
```

---

## 6. Compilando Documentos LaTeX

### Compilar Artigo

```bash
# Windows
cd artigo
pdflatex artigo_150_questoes.tex
pdflatex artigo_150_questoes.tex

# Verificar qualidade
python tests/run_all_tests.py
```

**Saida esperada:**
```
============================================================
  TDD QUALITY REPORT
============================================================
  Gate 1 — Compilation: 5/5 PASS
  Gate 2 — Structure:  6/6 PASS
  Gate 3 — Quality:    5/5 PASS
============================================================
  TOTAL: 16/16 GREEN
  Overfull boxes: 0
  Underfull boxes: 0
  LaTeX errors: 0
============================================================
```

---

## 7. Criando um Novo SPEC

### Template

```markdown
# SPEC-XXX: Nome do Novo Componente

## 1. Objetivo
Descrever o que este SPEC valida.

## 2. Criterios de Aceitacao (formato TDD)

| # | Criterio | Como Testar | Resultado Esperado |
|---|----------|-------------|-------------------|
| 1 | Exemplo | `assert func() == valor` | True |

## 3. Teste TDD

```python
def test_meu_criterio():
    resultado = minha_funcao(entrada)
    assert resultado == esperado
```

### Exemplo Real: SPEC-009 (D1 Matematica)

```python
# artigo/evaluations/tests/test_d1_matematica.py

def test_pitagoras():
    """D1-N2-01: Teorema de Pitagoras — hipotenusa de triangulo 3-4-5."""
    a, b = 3, 4
    c = math.sqrt(a**2 + b**2)
    assert abs(c - 5) < 1e-10

def test_gauss_summation():
    """D1-N2-02: Formula de Gauss — soma 1..100 = 5050."""
    n = 100
    result = n * (n + 1) // 2
    assert result == 5050
```

---

## 8. Registrando um Plugin

Edite `.menu_registry.json`:

```json
{
  "commands": {
    "meu-comando": {
      "description": "Minha ferramenta customizada de analise",
      "script": "meus_scripts/analisar.py",
      "runtime": "python",
      "category": "FERRAMENTAS"
    }
  }
}
```

Execute:

```bash
python menu.py --list
```

**Saida esperada:**
```
FERRAMENTAS:
  [N] Meu Comando — Minha ferramenta customizada de analise
```

O comando aparece automaticamente no menu, sem editar `menu.py`.

---

## 9. Debugging Comum

### Problema 1: `ModuleNotFoundError: No module named 'numpy'`

```bash
pip install numpy scipy
```

### Problema 2: `pdflatex: command not found`

Instale o TeX Live:
- Windows: https://tug.org/texlive/
- Ubuntu: `sudo apt install texlive-latex-base texlive-latex-extra`
- Mac: `brew install --cask mactex`

### Problema 3: `ImportError: cannot import name '...'`

Execute do diretorio raiz do projeto:
```bash
cd "C:\Users\marce\OneDrive\Documentos\Antiprojeto UFC"
set PYTHONPATH=%CD%
python -m pytest artigo/evaluations/tests/ -v
```

### Problema 4: Testes demorando muito (>5 min)

Use pytest com paralelismo:
```bash
pip install pytest-xdist
python -m pytest artigo/evaluations/tests/ -n 4 -v
```

### Problema 5: `AssertionError` em teste especifico

1. Execute o teste isolado com verbose: `pytest tests/test_X.py::test_Y -vv`
2. Verifique o historico: `cat orchestration/fix_history.json`
3. Consulte a SPEC correspondente: `SPEC_XXX.md`

---

## 10. Proximos Passos

| Nivel | Documento | Topico |
|:-----:|-----------|--------|
| Aprofundar | `docs/ARQUITETURA_ECOSYSTEM.md` | Arquitetura completa (125 agentes, pipeline) |
| Contribuir | `docs/ARQUITETURA_ECOSYSTEM.md#8` | Como contribuir: agentes, skills, SPECs |
| Auditar | `AVALIACAO_SWOT_TDD_ECOSYSTEM.md` | Avaliacao completa SWOT+TDD |
| Publicar | `artigo/orchestration/FRAMEWORK.md` | Framework SDD+TDD+AutoEvolve |
| Validar | `artigo/AVALIACAO_MATURIDADE_20260530.md` | Resultados CORA-Eval (hardware real) |

---

## A. Comandos de Referencia Rapida

```bash
# Diagnostico
python menu.py --quick          # Verificar saude do ecossistema

# Testes
pytest artigo/evaluations/tests/ -v           # Todos os testes cientificos
pytest artigo/evaluations/tests/ -v -k "d1"   # Apenas D1 (matematica)
python artigo/tests/run_all_tests.py          # Quality gates LaTeX

# Compilacao
cd artigo && pdflatex artigo_150_questoes.tex  # Compilar artigo
python orchestration/refinement_loop.py         # Pipeline AutoEvolve

# Inspecao
cat orchestration/fix_history.json             # Historico de correcoes
python menu.py --list                          # Listar artefatos
```

---

**Tutorial Interativo** · 2026-06-04 · OpenCode Ecosystem v4.7.1
