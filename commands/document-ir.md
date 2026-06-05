# /document-ir — Pipeline de Documentação Estruturada

Comando para gerar documentos com pipeline de 7 estágios e 16 tipos de bloco.

## Subcomandos

### `/document-ir compose <title> <document_type> <audience> [max_words]`

Executa pipeline completo de composição de documento.

| Parâmetro     | Descrição                                          | Obrigatório |
|---------------|----------------------------------------------------|-------------|
| title         | Título do documento                                | Sim         |
| document_type | report, proposal, analysis, manual                 | Sim         |
| audience      | executive, technical, general, academic            | Sim         |
| max_words     | Orçamento máximo de palavras                       | Não (padrão: 2000) |

Exemplo:
```
/document-ir compose "Relatório Q1 2026" report executive 3000
```

### `/document-ir add-block <type> <content> [position] [confidence] [anchor_id]`

Adiciona um bloco ao documento em composição.

| Parâmetro  | Descrição                                    | Obrigatório |
|------------|----------------------------------------------|-------------|
| type       | heading1, heading2, heading3, paragraph, ... | Sim         |
| content    | Conteúdo do bloco (entre aspas)              | Sim         |
| position   | Ordem no documento                           | Não (auto)  |
| confidence | 0.0-1.0                                      | Não (0.5)   |
| anchor_id  | ID para referência cruzada                   | Não         |

Exemplo:
```
/document-ir add-block heading1 "Introdução" 0 1.0 intro-h1
/document-ir add-block paragraph "Texto do parágrafo" 1 0.8
/document-ir add-block metric_card "ROI: 145%" 2 0.9 roi-metric
```

### `/document-ir add-anchor <anchor_id> <target> <block_type>`

Adiciona uma âncora de referência cruzada.

| Parâmetro | Descrição              | Obrigatório |
|-----------|------------------------|-------------|
| anchor_id | Identificador único    | Sim         |
| target    | Referência alvo        | Sim         |
| block_type| Tipo do bloco alvo     | Sim         |

Exemplo:
```
/document-ir add-anchor roi-metric "#roi" metric_card
```

### `/document-ir render [format]`

Renderiza o documento atual.

| Parâmetro | Descrição                   | Obrigatório |
|-----------|-----------------------------|-------------|
| format    | markdown (padrão), json     | Não         |

Exemplo:
```
/document-ir render markdown
```

### `/document-ir validate`

Valida blocos e âncoras atuais contra JSON Schema.

### `/document-ir clear`

Limpa documento em composição.

### `/document-ir status`

Exibe estado atual do documento (blocos, âncoras, palavras).

## Exemplos

```
# Relatório executivo completo
/document-ir compose "Análise de Mercado 2026" report executive 2000
/document-ir add-block heading1 "Sumário Executivo" 0 1.0
/document-ir add-block paragraph "Mercado cresceu 22% em 2026." 1 0.9
/document-ir add-block metric_card "Participação: 34%" 2 0.85 share-metric
/document-ir add-block heading2 "Recomendações" 3 1.0
/document-ir add-block bullet_list "Expandir região NE\nInvestir em P&D" 4 0.8
/document-ir add-anchor share-metric "#participacao" metric_card
/document-ir render markdown
/document-ir validate
```

## Retorno

O comando retorna JSON com:
- `status`: "ok" ou "error"
- `operation`: nome da operação
- `data`: dados da operação (documento, blocos, validação)
- `error`: mensagem de erro (se aplicável)
