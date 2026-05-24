---
name: gerador-contratos
description: "Skill do ecossistema OpenCode - gerador-contratos"
---


name: gerador-contratos
description: >
  Gerador de contratos juridicos em HTML otimizado para PDF, com identidade
  visual profissional. Contratos sociais, procuraes, acordos, termos,
  compromissos. Use quando usuario mencionar "gerar contrato", "redigir
  acordo", "contrato social", "procurao", "termo de", "documento juridico
  em PDF", "HTML de contrato".
---

---
name: gerador-contratos
description: >
  Gerador de contratos juridicos em HTML otimizado para PDF, com identidade
  visual profissional. Contratos sociais, procuraes, acordos, termos,
  compromissos. Use quando usuario mencionar "gerar contrato", "redigir
  acordo", "contrato social", "procurao", "termo de", "documento juridico
  em PDF", "HTML de contrato".
---

# Gerador de Contratos Juridicos HTML

Gera arquivos `.html` otimizados para exportacao em PDF via browser
(Ctrl+P → Salvar como PDF → Margens: Padrao → Graficos de fundo: ativado).



## Conteudo de Referencia

Para manter esta skill leve, dados densos foram movidos para arquivos de referencia:

- [`references/tipos-contrato.md`](references/tipos-contrato.md) — Tipos Contrato


## Fluxo de Geracao

1. Identificar **tipo de contrato** e **partes** envolvidas
2. Verificar se escritorio ja configurado (dados de cabealho)
3. Se nao configurado, rodar wizard de configuracao
4. Coletar dados especificos do contrato
5. Gerar HTML completo
6. Salvar em `[tipo]_[partes]_data.html`
7. Presentar com `present_files`


> *Detalhes de "Preenchimento de Dados" em `references/`*


> *Detalhes de "Estrutura HTML" em `references/`*



## Regras de Exportacao

```
Ctrl+P → Salvar como PDF
Margens: Padrao
Graficos de fundo: ATIVADO ← obrigatorio
Escala: 100%
```



## Checklist de Verificacao

- [ ] Partes identificadas com nome/qualificacao/CNPJ/CPF
- [ ] Objeto descrito com precisao
- [ ] Prazo ou duracao definido
- [ ] Clausula de rescisao presente
- [ ] Clausula de foro competente incluida
- [ ] Assinatura com espaco para 2 vias


