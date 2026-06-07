# Formatos de Peca v2.0

Estrutura completa para cada um dos 8 tipos de peca juridica.

## Estrutura HTML Base

```html
<div class="doc">
  <header class="cabecalho">...</header>
  <main class="conteudo">
    <section class="secao">
      <h2>Titulo da Secao</h2>
      <p>Conteudo...</p>
    </section>
  </main>
  <footer class="fechamento">...</footer>
</div>
```

## Tabela de Tipos

| # | Tipo | Sigla | Classes CSS | Secoes Obrigatorias |
|---|------|-------|-------------|---------------------|
| 1 | Peticao Inicial | PI | `peca-pi` | enderecamento, qualificacao, dos-fatos, do-direito, dos-pedidos, fechamento |
| 2 | Contestacao | CT | `peca-ct` | enderecamento, preliminares, merito, dos-pedidos, fechamento |
| 3 | Replica | RP | `peca-rp` | enderecamento, preliminares, merito, dos-pedidos, fechamento |
| 4 | Agravo de Instrumento | AI | `peca-ai` | enderecamento, decisao-recorrida, do-recurso, dos-pedidos, fechamento |
| 5 | Apelacao | AP | `peca-ap` | enderecamento, razoes, preliminares, merito, dos-pedidos, fechamento |
| 6 | Embargos de Declaracao | ED | `peca-ed` | enderecamento, tempestividade, fundamentos, dos-pedidos, fechamento |
| 7 | Contrarrazoes | CR | `peca-cr` | enderecamento, preliminares, contra-razoes, dos-pedidos, fechamento |
| 8 | Parecer | PR | `peca-pr` | enderecamento, relatorio, fundamentacao, conclusao, fechamento |

## Secoes Detalhadas

### Enderecamento (`classe: enderecamento`)

```html
<section class="secao enderecamento">
  <p>EXCELENTISSIMO SENHOR DOUTOR JUIZ DE DIREITO DA ___ VARA ___ DA COMARCA DE ___</p>
</section>
```

### Qualificacao das Partes (`classe: qualificacao`)

```html
<section class="secao qualificacao">
  <p>{{ autor }}, {{ nacionalidade }}, {{ estado_civil }}, {{ profissao }}, portador do CPF sob n. {{ cpf }},</p>
  <p>endereco eletronico {{ email }}, residente e domiciliado {{ endereco }},</p>
  <p>por seu advogado que esta subscreve, vem, respeitosamente, a presenca de Vossa Excelencia, propor</p>
</section>
```

### Dos Fatos (`classe: dos-fatos`)

```html
<section class="secao dos-fatos">
  <h2>I — DOS FATOS</h2>
  <p>{{ narrativa_fatos }}</p>
</section>
```

### Do Direito (`classe: do-direito`)

```html
<section class="secao do-direito">
  <h2>II — DO DIREITO</h2>
  <p>{{ fundamentacao_juridica }}</p>
  <div class="citacao">
    <p>{{ ementa_jurisprudencial }}</p>
    <p class="fonte-julgado">{{ identificacao_julgado }}</p>
  </div>
</section>
```

### Dos Pedidos (`classe: dos-pedidos`)

```html
<section class="secao dos-pedidos">
  <h2>III — DOS PEDIDOS</h2>
  <p>Ante o exposto, requer:</p>
  <ol class="pedidos-lista">
    <li>{{ pedido_1 }}</li>
    <li>{{ pedido_2 }}</li>
  </ol>
  <p>Dá-se a causa o valor de {{ valor_causa }}.</p>
</section>
```

### Fechamento (`classe: fechamento`)

```html
<footer class="fechamento">
  <p>Nestes termos, pede deferimento.</p>
  <p class="local-data">{{ cidade }}, {{ data }}.</p>
  <div class="assinatura">
    <p class="advogado-nome">{{ nome_advogado }}</p>
    <p class="advogado-oab">{{ oab }}</p>
  </div>
</footer>
```

## Secoes Especificas por Tipo

### Decisao Recorrida (AI — Agravo de Instrumento)

```html
<section class="secao decisao-recorrida">
  <h2>I — DA DECISAO RECORRIDA</h2>
  <p>{{ descricao_decisao }}</p>
  <p>Publicacao em {{ data_publicacao }}.</p>
</section>
```

### Do Recurso (AI)

```html
<section class="secao do-recurso">
  <h2>II — DO RECURSO</h2>
  <p>{{ fundamentos_recurso }}</p>
</section>
```

### Preliminares (CT, RP, AP, CR)

```html
<section class="secao preliminares">
  <h2>I — DAS PRELIMINARES</h2>
  <p>{{ preliminares }}</p>
</section>
```

### Tempestividade (ED)

```html
<section class="secao tempestividade">
  <h2>I — DA TEMPESTIVIDADE</h2>
  <p>{{ justificativa_tempestividade }}</p>
</section>
```

### Relatorio (PR — Parecer)

```html
<section class="secao relatorio">
  <h2>I — RELATORIO</h2>
  <p>{{ relatorio_tecnico }}</p>
</section>
```

## Classes CSS de Referencia

| Classe | Elemento | Propriedades |
|--------|----------|--------------|
| `.doc` | Container principal | `border-left: 6px solid #B08A4E; padding: 40px 20px 40px 52px;` |
| `.cabecalho` | Cabecalho | `display: flex; justify-content: space-between; margin-bottom: 30px;` |
| `.secao` | Secao de conteudo | `margin-bottom: 24px;` |
| `.citacao` | Citacao jurisprudencial | `font-style: italic; font-size: 12.5px; margin: 12px 2cm;` |
| `.fonte-julgado` | Identificacao do julgado | `font-style: normal; font-size: 11px; color: #6B5E4E;` |
| `.fechamento` | Fechamento da peca | `margin-top: 40px; text-align: center;` |
| `.assinatura` | Assinatura do advogado | `margin-top: 60px;` |
| `.pedidos-lista` | Lista de pedidos | `list-style: lower-alpha; margin-left: 2cm;` |

---
