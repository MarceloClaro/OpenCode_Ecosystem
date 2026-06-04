# Guia de Configuracao — Execucao com Privilegios Administrativos

**Versao:** 1.0 | **Data:** 2026-06-04

---

## Problema

A politica WDAC (Windows Defender Application Control) no Windows 11 bloqueia
o carregamento de DLLs nativas de C-extensions do Python, afetando:

- `numpy._core._multiarray_umath` → bloqueado
- `scipy.optimize._slsqplib` → bloqueado
- Todos os `.pyd` em `site-packages/`

**Consequencia:** Testes que importam numpy/scipy falham com `ImportError: DLL load failed`.

---

## Solucoes (em ordem de preferencia)

### 1. Executar como Administrador (Recomendado)

```powershell
# Via script automatico
powershell -ExecutionPolicy Bypass -File run_as_admin.ps1

# Ou manualmente
Start-Process powershell -Verb RunAs
cd "C:\Users\marce\OneDrive\Documentos\Antiprojeto UFC"
python -m pytest artigo/evaluations/tests/ -v --tb=short
```

O script `run_as_admin.ps1` solicita elevacao automaticamente e executa
a suite completa.

### 2. Adicionar excecao WDAC (Permanente)

```powershell
# Abrir PowerShell como Administrador
# Adicionar regra de path para Python
Add-MpPreference -ExclusionPath "C:\Users\marce\AppData\Local\Programs\Python"
Add-MpPreference -ExclusionProcess "python.exe"

# Verificar
Get-MpPreference | Select-Object ExclusionPath, ExclusionProcess
```

### 3. Usar Python via Windows Store (Alternativo)

```powershell
# Desinstalar Python atual
# Instalar da Microsoft Store
# Executar: python -m pip install numpy scipy pytest
```

A versao da Store usa caminhos diferentes que podem nao ser afetados pelo WDAC.

### 4. Desabilitar WDAC temporariamente (NAO recomendado)

```powershell
# Somente para debugging — reabilitar apos!
Set-ExecutionPolicy -ExecutionPolicy Unrestricted -Scope Process
```

---

## Verificacao

```powershell
python -c "import numpy; print('OK:', numpy.__version__)"
python -c "from scipy import stats; print('OK: scipy.stats')"
```

Se ambos imprimirem "OK", a configuracao esta funcionando.

---

## Fallback Automatico

O ecossistema ja configura fallback automatico: testes que dependem de
numpy/scipy sao automaticamente ignorados (`pytest.mark.skipif`) quando
as bibliotecas nao estao disponiveis.

Isso garante que o ecossistema funcione em modo reduzido em maquinas com
restricoes WDAC, executando apenas os testes que nao dependem de C-extensions.

---

## Status Atual

| Configuracao | numpy | scipy | Testes Afetados |
|-------------|:-----:|:-----:|:---------------:|
| Sem admin | ❌ | ❌ | D9 (12 testes skipados) |
| Com admin | ✅ | ✅ | Nenhum (todos passam) |
| Com excecao WDAC | ✅ | ✅ | Nenhum |

---

**Guia Admin Config** · 2026-06-04 · OpenCode Ecosystem v4.7.1
