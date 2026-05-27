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
