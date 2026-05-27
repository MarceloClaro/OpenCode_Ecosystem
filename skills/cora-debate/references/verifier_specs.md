# Especificacao dos Verificadores Simbolicos (V1-V6)

## V1: Analise Dimensional

**Objetivo**: Verificar consistencia dimensional de equacoes fisicas.

**Metodo**: Mapeamento de unidades para dimensoes fundamentais (MLT: Massa, Comprimento, Tempo).

**Exemplo**:
```
Input:  F = m * a
LHS: F -> [M][L][T]^-2 (forca)
RHS: m*a -> [M] * [L][T]^-2 = [M][L][T]^-2
Resultado: CONSISTENTE
```

**Limitacoes**:
- Nao detecta fatores constantes errados (ex: F = 2*m*a passaria)
- Requer dicionario de unidades pre-definido

---

## V2: Verificador Algebrico

**Objetivo**: Verificar identidades algebricas via simplificacao simbolica (SymPy).

**Metodo**: 
1. Converter afirmacao para igualdade SymPy
2. Simplificar `lhs - rhs`
3. Verificar se resultado == 0

**Exemplo**:
```python
expr = "(x + y)^2 - (x^2 + 2*x*y + y^2)"
# SymPy simplifica para 0 -> VERDADEIRO
```

**Limitacoes**:
- Requer SymPy >= 1.12
- Nao lida com inducao matematica ou provas por contradicao
- Falha em identidades trigonometricas complexas sem `sp.trigsimp`

---

## V3: Contraexemplos

**Objetivo**: Refutar afirmacoes universais encontrando contraexemplos.

**Metodo**: Busca randomizada no dominio especificado.

**Algoritmo**:
```
for i in range(max_attempts):
    x = random(DOMINIO)
    if not P(x):
        counterexamples.append(x)
        if len(counterexamples) >= 3:
            break
return len(counterexamples) == 0
```

**Dominios suportados**:
- `integer`: x in [-100, 100]
- `real`: x in [-100.0, 100.0]

**Limitacoes**:
- Nao prova afirmacoes verdadeiras (apenas falha em refutar)
- Limitada a dominio de busca finito
- Nao lida com quantificadores aninhados

---

## V4: Verificador Estatistico

**Objetivo**: Validar conclusoes estatisticas com testes formais.

**Testes implementados**:
| Teste | Funcao | Interpretacao |
|-------|--------|---------------|
| Shapiro-Wilk | `scipy.stats.shapiro` | p > 0.05 -> normal |
| Pearson r | `scipy.stats.pearsonr` | p < 0.05 -> correlacao significativa |
| Cohen's d | Manual | |d| > 0.8 -> efeito grande |

**Exemplo**:
```python
dados = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
# Shapiro-Wilk: W=0.970, p=0.892 -> NAO rejeita normalidade
```

**Limitacoes**:
- Requer SciPy >= 1.10
- Shapiro-Wilk limitado a n <= 5000
- Nao implementa testes nao-parametricos (Mann-Whitney, Kruskal-Wallis)

---

## V5: Verificador Numerico

**Objetivo**: Verificar precisao de calculos numericos com tolerancia IEEE 754.

**Metodo**: Erro absoluto e relativo contra tolerancia.

**Criterios de aprovacao**:
1. `|computed - expected| < tolerance` (erro absoluto)
2. `|computed - expected| / max(|expected|, 1e-10) < tolerance` (erro relativo)

**Parametros**:
- `tolerance`: 1e-6 (padrao, adequado para float64)

**Exemplo**:
```
computed = 3.14159, expected = 3.1415926535
erro_abs = 2.65e-6, erro_rel = 8.45e-7
PASSOU (ambos < 1e-6)
```

**Limitacoes**:
- Nao detecta cancelamento catastrofico
- Nao verifica estabilidade numerica do algoritmo

---

## V6: Verificador de EDO/EDP

**Objetivo**: Verificar se uma funcao proposta e solucao de equacao diferencial.

**Metodo**: Substituicao simbolica via SymPy `dsolve` / `checkodesol`.

**Exemplo**:
```python
eq = "diff(y, x) - y"  # dy/dx = y
sol = "exp(x)"         # y = e^x
# SymPy verifica: diff(exp(x), x) - exp(x) = 0 -> VERDADEIRO
```

**Limitacoes**:
- Requer SymPy >= 1.12
- Nao resolve EDPs nao-lineares
- Falha em solucoes implicitas

**Refinamento EVO-8 (v2.0)**:
- Metodo primario: `sympy.checkodesol` para verificacao formal
- Fallback: substituicao simbolica direta

---

## V7: Verificador de Rastreabilidade Bibliografica (DOI)

**Objetivo**: Verificar que afirmacoes factuais em textos academicos possuem respaldo em DOI verificavel.

**Metodo**:
1. Extrair todos os DOIs do texto via regex (`10.\d{4,}/...`)
2. Identificar padroes de afirmacao factual sem DOI proximo (ate 200 caracteres)
3. Validar formato dos DOIs fornecidos

**Padroes de afirmacao detectados**:
- "Estudos mostram que..."
- "Conforme a literatura..."
- "Evidencias sugerem..."
- "E comprovado que..."

**Exemplo**:
```
Input:  "Estudos mostram que IA melhora educacao."
Output: ALERTA - afirmacao factual sem DOI de respaldo
```

**Criterios de aprovacao**:
- Zero afirmacoes factuais sem DOI de respaldo proximo
- Todos os DOIs fornecidos no formato valido

**Integracao com ecossistema**: Conecta-se ao CT-006 do pipeline TDD academico (EVO-8).

---

## V8: Verificador de Anonimato/Privacidade

**Objetivo**: Detectar identificadores diretos e indiretos em documentos que exigem anonimato (anteprojetos, artigos para revisao cega).

**Metodo**:
1. Busca por identificadores diretos: nomes proprios compostos, CPF, RG, e-mail
2. Busca por identificadores indiretos: perfis GitHub, metricas especificas (N estrelas + M forks), mencao de autoria
3. Busca por nomes de produtos publicos que permitem busca reversa do autor

**Protocolo EVO-8**: Identificadores indiretos sao tao perigosos quanto nomes. Qualquer combinacao que permita busca reversa em 30 segundos e considerada violacao.

**Exemplo**:
```
Input:  "A plataforma OpenCode (17 estrelas, 7 forks) foi desenvolvida por..."
Output: ALERTA - nome_produto_publico + metricas GitHub = identificacao indireta
```

**Severidades**:
- ALTA: nome proprio, CPF, e-mail, perfil GitHub, metricas unicas
- MEDIA: nome de produto publico (sugestao: substituir por descricao generica)

**Integracao**: Conecta-se ao CT-001 do pipeline TDD academico e a ADR security-001 (EVO-8).

---

## V9: Verificador de Conformidade Normativa (LGPD/Etica)

**Objetivo**: Verificar conformidade de textos academicos com a LGPD (Lei 13.709/2018) e a Resolucao PRPPG/UFC nº 39/2025.

**Frameworks suportados**:
- `lgpd`: Lei Geral de Protecao de Dados Pessoais
- `etica_pesquisa`: Resolucao PRPPG/UFC 39/2025 (uso de IA na pesquisa)

**Checks LGPD**:
| ID | Verificacao | Art. LGPD |
|----|-------------|-----------|
| dados_pessoais_processamento | Dados pessoais mencionados com protecao? | Art. 6º, 7º |
| dados_sensiveis | Dados sensiveis com consentimento/CEP? | Art. 11 |
| transferencia_internacional | Transferencia para nuvem/externo com garantias? | Art. 33 |
| direitos_titular | Direitos do titular (acesso, exclusao) mencionados? | Art. 17-21 |

**Checks Etica em Pesquisa**:
| ID | Verificacao | Norma |
|----|-------------|-------|
| declaracao_ia | Uso de IA declarado? | Res. 39/2025 |
| plagio_ia | IA como assistente (nao autora)? | Res. 39/2025 |
| reprodutibilidade | Resultados auditaveis/reprodutiveis? | Res. 39/2025 |
| consentimento_participantes | TCLE e CEP para participantes? | Res. 39/2025 |

**Metodo**: Para cada check, busca trigger pattern no texto. Se trigger presente mas safeguard ausente, dispara ALERTA.

**Exemplo**:
```
Input:  "Dados pessoais serao enviados para nuvem OpenAI."
Output: ALERTA - transferencia_internacional sem garantias (Art. 33 LGPD)
```

**Integracao**: Conecta-se ao CT-009 do pipeline TDD academico (declaracao de IA) e ao Modulo D do guia pratico (LGPD).

---

## Resumo de Versoes (EVO-8)

| Verificador | v1.0 | v2.0 (EVO-8) |
|------------|------|---------------|
| V1 | Analise dimensional basica (10 unidades) | +40 unidades, +equivalencias |
| V2 | SymPy simplify | Mantido estavel |
| V3 | Random search [-100,100] | SymPy solve + grid search + random fallback |
| V4 | Shapiro-Wilk, Pearson r | +Bootstrap CI, +Mann-Whitney, +Cohen's d, +one-sample t-test |
| V5 | Tolerancia IEEE 754 | Mantido estavel |
| V6 | Substituicao manual | checkodesol + substituicao fallback |
| V7 | — | **[NOVO]** Rastreabilidade DOI |
| V8 | — | **[NOVO]** Anonimato/Privacidade |
| V9 | — | **[NOVO]** Conformidade LGPD/Etica |
