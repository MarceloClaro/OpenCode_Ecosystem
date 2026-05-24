---
name: triagem-juridica
description: "Skill do ecossistema OpenCode - triagem-juridica"
---


name: triagem-juridica
description: >
  Triagem jurídica de leads e consultas: classifica area do direito, avalia
  urgencia, identifica dados essenciais e encaminhamento correto. Use quando
  usuario mencionar "triar", "classificar consulta", "qualificar lead juridico",
  "primeiro atendimento", "encaminhamento", "triagem de demanda" ou similar.
---

---
name: triagem-juridica
description: >
  Triagem jurídica de leads e consultas: classifica area do direito, avalia
  urgencia, identifica dados essenciais e encaminhamento correto. Use quando
  usuario mencionar "triar", "classificar consulta", "qualificar lead juridico",
  "primeiro atendimento", "encaminhamento", "triagem de demanda" ou similar.
---

# Triagem Jurídica — Classificacao e Encaminhamento de Demandas



## Principio Central

Todo contato juridico novo deve passar por triagem sistematica: identificar
area do direito, nivel de urgencia, dados essencias e melhor fluxo de
encaminhamento. Nunca diagnosticar resultado, apenas classificar e direcionar.


> *Detalhes de "Fluxo de Triagem" em `references/`*



## Regras de Compliance OAB

- Nao fazer promessa de resultado
- Nao dar opiniao juridica sem contrato firmado
- Nao cobrar consulta inicial sem combinado
- Sempre informar: "Isso e uma triagem inicial, nao constitui consulta juridica"



## Output Padrao

Apos triagem, apresentar:

```
[DADOS COLETADOS]
Nome: [nome]
CPF: [cpf]
Contato: [telefone] | [email]

[CLASSIFICACAO]
Area: [CODIGO] - [nome da area]
Urgencia: [Nivel]
Resumo: [ate 5 linhas]

[DADOS DA DEMANDA]
Tipo: [descricao]
Contra-parte: [nome/empresa]
Valor estimado (se aplicavel): [R$ X ou "a definir"]
Documentos mencionados: [lista breve]

[ENCAMINHAMENTO SUGERIDO]
Proxima acao: [agendar/encaminhar/pedir docs]
Prazo ideal: [DD/MM/AAAA]
Documentos necessarios: [lista]
```



## Integracao com MCPs

- Usar websearch para verificar urgencia de prazos (ex: "prazo contestacao [vara] [comarca]")
- Usar Wikipedia para identificar conceitos juridicos desconhecidos
- Usar fetch para consultar site do TJ para jurisprudencia rapida

