---
title: "CORRIGENDUM v2 — Retratacao das Solucoes do Problema 1 da IMO 2025"
subtitle: "Reconhecimento de Erro Matematico, Parecer Tecnico e Rota Correta"
version: "2.0.0"
date: "2026-05-25"
status: "RETRATACAO — As versoes 1 e 2 do artigo estao MATEMATICAMENTE INVALIDAS"
parecer_recebido: "Revisao externa independente — corretor rigoroso de olimpiada"
referencias_verificadas:
  - "Evan Chen, IMO 2025 Solution Notes — '0, 1, 3 are the only possible answers'"
  - "Google DeepMind/Gemini, IMO 2025 Solutions — 'the possible values are {0,1,3}'"
---

# CORRIGENDUM v2 — Retratacao

> **Status**: As duas versoes do artigo (`artigo_olimpiada_cora.pdf` e `artigo_olimpiada_cora - v2.pdf`)
> contem uma **resposta matematicamente falsa**. Este documento registra a retratacao formal,
> o diagnostico dos erros cometidos, e a rota correta de solucao conforme referencias
> independentes verificadas.

---

## 1. A Resposta Correta

| Item | Valor |
|------|-------|
| **Resposta correta** | $k \in \{0, 1, 3\}$ para todo $n \geq 3$ |
| **Resposta defendida (ERRADA)** | $k \in \{0, 1, \dots, \lfloor(2n-1)/3\rfloor\}$ |
| **Contraexemplo mínimo** | $n=4$: o artigo declara $k=2$ possivel, mas $k=2$ nao e valor valido |
| **Referencias** | Evan Chen (IMO 2025 Notes) e Google DeepMind/Gemini (IMO 2025 Solutions) |

A resposta correta e **constante** — nao cresce com $n$. Isso e contra-intuitivo, mas decorre
de uma propriedade estrutural profunda do problema.

---

## 2. Diagnostico dos Erros — Versao 1

### 2.1 Erro Fatal: Limitante Superior Nao Provado

| Passo problematico | Por que falha |
|---|---|
| "Usar $n-k$ retas como horizontais $y=1,\dots,n-k$" | Nao e uma reducao legitima — uma configuracao arbitraria pode misturar horizontais, verticais e diagonais. Nao se prova que a substituicao preserva a possibilidade de cobertura pelas ensolaradas restantes. |
| "Argumento de pigeonhole generalizado: $p_i \leq n-2k+i$" | Nao e demonstrado e nao segue dos lemas anteriores. E uma afirmacao nao justificada. |
| Contagem de sobreposicoes | Leva a $k \leq (2n+1)/5$, nao a $k \leq (2n-1)/3$. O refinamento anunciado nao e fornecido. |

### 2.2 Erro Fatal: Construcao Quebrada

A construcao com $n-k$ horizontais e $k$ ensolaradas de inclinacoes $m_j = -1-1/j$ **nao funciona**.
O proprio apendice do artigo demonstra que, para $n=4, k=2$, o ponto $(2,3)$ nao e coberto.

A tentativa de correcao com diagonais no apendice tambem falha: as diagonais $x+y=5$ e $x+y=4$
cobrem 7 pontos, deixando $(1,1), (1,2), (2,1)$. Nenhuma reta ensolarada pode conter dois
destes tres pontos — eles compartilham coordenadas $x$ ou $y$. Portanto, $k=2$ para $n=4$
e **impossivel**, contradizendo a resposta do artigo.

---

## 3. Diagnostico dos Erros — Versao 2

### 3.1 Erro Fatal: Invariante com Prova Contraditoria

A versao 2 afirma que $|p+q| \geq 2$ para toda reta ensolarada, mas imediatamente reconhece
que $m=-2=-2/1$ tem $|p+q| = |-2+1| = 1$. A prova entra em **contradicao consigo mesma**.

Em vez de corrigir a analise aritmetica, o texto declara que o limitante vale
"independentemente da justificativa algebrica" — o que nao e aceitavel como argumento matematico.

### 3.2 Erro Fatal: Contagem de Anti-diagonais

A versao 2 afirma que as $n-k$ diagonais cobrem $x+y = k+2, \dots, n+1$ (correto: $n-k$
anti-diagonais), mas depois escreve que "restam as $k+1$ menores anti-diagonais
$x+y=2,\dots,k+2$", contando $(k+1)(k+2)/2$ pontos — o que **inclui a anti-diagonal
$x+y=k+2$ que havia sido declarada coberta**. Este erro de indice esta no nucleo da prova.

---

## 4. A Rota Correta (Conforme Referencias Independentes)

A solucao correta explora uma **rigidez estrutural** que nao aparece em nenhuma das versoes
do artigo:

### Teorema da Reta Longa de Borda

Para $n \geq 4$, qualquer cobertura valida de $S_n$ por $n$ retas contem **necessariamente**
uma das tres "retas longas" de borda:

| Reta | Tipo | Pontos cobertos | Ensolarada? |
|------|------|----------------|-------------|
| $y = 1$ | Horizontal | $n$ pontos: $(1,1), (2,1), \dots, (n,1)$ | Nao ($m=0$) |
| $x = 1$ | Vertical | $n$ pontos: $(1,1), (1,2), \dots, (1,n)$ | Nao ($m=\infty$) |
| $x+y = n+1$ | Diagonal | $n$ pontos: $(1,n), (2,n-1), \dots, (n,1)$ | Nao ($m=-1$) |

### Reducao por Inducao

1. **Remover** a reta longa de borda (sempre nao-ensolarada) da configuracao
2. Isso reduz o problema de $n$ para $n-1$ **sem alterar** $k$
3. Por inducao, $k$ deve ser viavel para $n=3$

### Caso Base $n=3$

Para $n=3$, $S_3 = \{(1,1),(1,2),(2,1),(1,3),(2,2),(3,1)\}$ (6 pontos, 3 retas).

Analise direta:
- $k = 0$: 3 diagonais $x+y=2,3,4$ cobrem tudo.
- $k = 1$: 2 nao-ensolaradas + 1 ensolarada. Possivel (construcao conhecida).
- $k = 2$: 1 nao-ensolarada + 2 ensolaradas. **Impossivel** (as 2 ensolaradas nao conseguem cobrir os pontos restantes).
- $k = 3$: 3 ensolaradas. **Possivel** (construcao com 3 retas de inclinacao $m=1$ com offsets distintos).

### Conclusao

$$k \in \{0, 1, 3\} \quad \text{para todo } n \geq 3$$

---

## 5. Por Que a Verificacao Simbolica Cora-Debate (V1-V6) Falhou

A secao de verificacao simbolica em ambas as versoes do artigo e **irrelevante** para a
validade da solucao. Os verificadores V1-V6 checaram consistencia superficial de formulas:

| Verificador | O que checou | Por que nao detectou o erro |
|------------|-------------|---------------------------|
| V1 (Dimensional) | Consistencia adimensional | Nao testa logica combinatoria |
| V2 (Algebrico) | Inequacao $k(3k-2n+1)\leq 0$ | Verifica uma formula **assumida**, nao sua derivacao |
| V3 (Contraexemplos) | Busca para $n=3..50$ | Nao testa a **construcao** — testa o limitante assumido |
| V4 (Estatistico) | Correlacao de Pearson | Correlacao alta nao implica correcao matematica |
| V5 (Numerico) | Precisao de ponto flutuante | Irrelevante para combinatoria |
| V6 (PDE/EDO) | Nao aplicavel | -- |
| Calibracao Platt | ECE da confianca | Calibracao de confianca em resposta errada e inutil |

**Licao**: Verificacao simbolica testa **consistencia interna** de formulas, nao **validade
matematica** de demonstracoes. O contraexemplo $n=4, k=2$ estava documentado no proprio
apendice do artigo e nao foi detectado por nenhum verificador.

---

## 6. Licoes Aprendidas

| # | Licao |
|---|-------|
| 1 | **Verificar a resposta contra referencias independentes** antes de construir provas longas. Evan Chen e Google DeepMind publicaram a resposta correta. |
| 2 | **Testar casos pequenos manualmente** ($n=3,4,5$) antes de generalizar. O caso $n=4, k=2$ teria revelado o erro imediatamente. |
| 3 | **Verificacao simbolica (V1-V6) nao substitui prova combinatoria**. Ela complementa, mas nao valida. |
| 4 | **Construcoes devem ser testadas exaustivamente** para casos pequenos. O algoritmo de verificacao deveria ter testado a construcao, nao apenas o limitante. |
| 5 | **A estrutura de "retas longas de borda"** e o insight central que faltou em todas as abordagens (A, B e C). |

---

## 7. Compromissos

| Acao | Prazo | Status |
|------|-------|--------|
| Retratar formalmente as versoes 1 e 2 do artigo | Imediato | ✅ Este documento |
| Corrigir o artigo com a solucao correta ($k \in \{0,1,3\}$) | Q2 2026 | 📋 Pendente |
| Refatorar verificacao simbolica para testar **construcoes**, nao apenas limitantes | Q3 2026 | 📋 Pendente |
| Adicionar verificacao exaustiva de casos pequenos ao pipeline Cora-Debate | Q3 2026 | 📋 Pendente |

---

> **Nota final**: Este corrigendum existe porque o ecossistema OpenCode adota o principio de
> **transparencia radical**. Erros matematicos sao documentados com a mesma precisao que
> acertos. A resposta correta ($k \in \{0,1,3\}$) e a rota de solucao (reducao por retas
> longas de borda) sao creditos dos autores originais da IMO 2025 e dos solucionadores
> independentes (Evan Chen, Google DeepMind). O merito das observacoes preliminares corretas
> (definicao de $S_n$, cardinalidade, Lema 1) permanece.

> **Parecer recebido em**: 2026-05-25
> **Avaliador**: Corretor rigoroso de olimpiada (independente)
> **Nota atribuida**: 1,0/10 (versao 1), 1,0-1,5/10 (versao 2)
> **Veredito**: Solucoes matematicamente invalidas — retratacao formal emitida
