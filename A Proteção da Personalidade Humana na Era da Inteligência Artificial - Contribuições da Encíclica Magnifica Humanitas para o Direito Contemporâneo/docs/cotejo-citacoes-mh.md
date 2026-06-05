# Cotejo de Citações — MH → Manuscrito

## Objetivo

Mapear todas as ocorrências de `\cite{LeaoXIV2026MH}` nos capítulos do manuscrito
e verificar se cada uma constitui citação direta de um dos 5 parágrafos fichados
da **Magnifica Humanitas** (§3, §89, §101, §186, §232), adicionando `[§XX]`
exclusivamente nas citações diretas que correspondem a transcrições literais do
fichamento.

## Metodologia

1. **Fonte de referência**: 5 parágrafos extraídos e documentados em
   `manuscrito/anexo-fichamentos.tex`.
2. **Varredura**: `\cite{LeaoXIV2026MH}` em todos os `cap*.tex`.
3. **Critério de inclusão**: somente citação direta com correspondência textual
   exata ao fichamento recebe `[§XX]`. Paráfrases, alusões e parágrafos
   referenciados apenas por número **não** recebem a anotação.

## Resultados

### Ocorrências de `\cite{LeaoXIV2026MH}` — 19 totais

| Capítulo | Total | Diretas fichadas | Editadas |
|----------|-------|------------------|----------|
| cap1     | 5     | 0                | 0        |
| cap2     | 1     | 0                | 0        |
| cap3     | 11    | 2                | 2        |
| cap4     | 2     | 0                | 0        |
| cap5     | 0     | 0                | 0        |
| cap6     | 0     | 0                | 0        |

### Alterações realizadas (2)

| Arquivo | Linha | § | Citação |
|---------|-------|---|---------|
| `cap3-ia-desafios.tex` | 138 | 3 | `\cite[§3]{LeaoXIV2026MH}` — "a pessoa humana não pode ser reduzida a um perfil ou a um conjunto de dados" |
| `cap3-ia-desafios.tex` | 166 | 232 | `\cite[§232]{LeaoXIV2026MH}` — "a tecnologia deve servir à pessoa humana, e não o contrário" |

### Citações diretas de parágrafos NÃO fichados (mantidas sem `[§XX]`)

| Arquivo | Linha | § | Razão |
|---------|-------|---|-------|
| `cap5-contribuicoes-magnifica.tex` | 52 | 125 | não fichado; já referenciado inline como "§125" |
| `cap5-contribuicoes-magnifica.tex` | 61 | 105 | não fichado; já tem `\MH{} (§105)` inline |
| `cap5-contribuicoes-magnifica.tex` | 70 | 189 | não fichado; já referenciado inline textual |

### Citações fichadas sem `\cite` no texto (já referenciadas inline)

| § | Local | Forma |
|---|-------|-------|
| 89 | `cap6-conclusao.tex:97` | `\MH{} (§89)` — paráfrase, não citação direta |
| 101 | `cap6-conclusao.tex:32` | Referido na lista `§3, §101, §186, §232` |
| 186 | `cap6-conclusao.tex:32` | Idem |

## Regra estabelecida

- Se a citação direta corresponde a parágrafo **fichado** → `\cite[§N]{LeaoXIV2026MH}`
- Se a citação direta corresponde a parágrafo **não fichado** → `\cite{LeaoXIV2026MH}` (sem `[§N]`)
- Se o parágrafo fichado já está referenciado inline sem `\cite` → manter como está

## Comandos utilizados para verificação

```bash
# Contar ocorrências de \cite{LeaoXIV2026MH}
Select-String -Pattern "\\cite\{LeaoXIV2026MH\}" manuscrito/cap*.tex

# Verificar parágrafos fichados
Select-String -Pattern "§\d+" manuscrito/cap*.tex

# Verificar \MH{} inline
Select-String -Pattern "\\MH\{\}" manuscrito/cap*.tex

# Verificar ocorrências de \cite no cap6
Select-String -Pattern "\\cite\{LeaoXIV2026MH\}" manuscrito/cap6-conclusao.tex
```

## Status

**Concluído.** 2 edições aplicadas em `cap3-ia-desafios.tex`. Nenhuma outra
citação requeria modificação. Todas as 19 ocorrências de `\cite{LeaoXIV2026MH}`
foram verificadas contra o fichamento.
