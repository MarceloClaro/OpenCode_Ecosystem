<!-- Conteudo extraido de pecas-juridicas-html/SKILL.md via progressive-disclosure -->

## 🔧 WIZARD DE CONFIGURAÇÃO (primeira execução)

Na primeira vez que o usuário acionar esta skill, ou quando o usuário pedir para "configurar a skill de peças", o Claude deve conduzir um wizard **etapa por etapa**, perguntando uma etapa de cada vez e aguardando a resposta antes de avançar.

### Instruções para o Claude

- Conduzir **uma etapa por vez**. Não despejar todas as perguntas de uma vez.
- Mostrar os valores padrão entre parênteses. Se o usuário responder "ok", "pode ser", "padrão" ou equivalente, usar o padrão.
- Se o usuário disser "usar padrões para o resto", pular as etapas restantes e usar todos os padrões.
- Ao final, gerar um **resumo completo** em formato copiável e pedir confirmação.
- Após confirmação, informar ao usuário que ele pode copiar o resumo para as User Preferences (Settings > Profile) para não precisar repetir a configuração em conversas futuras.

### ETAPA 1 — Dados do Escritório

Texto sugerido para o Claude:

```
Vamos configurar sua skill de peças jurídicas HTML! Vou te guiar passo a passo.

Primeiro, preciso dos dados do seu escritório para o cabeçalho das peças:

1. Nome completo do advogado titular (ex.: João da Silva Santos)
2. OAB (ex.: OAB/SP 123.456)
3. Razão social do escritório (ex.: Silva Santos Sociedade de Advogados)
4. Sigla para o logo — geralmente 2 letras (ex.: SS)
5. Nome curto para o logo (ex.: SILVA SANTOS)
6. OAB da Sociedade, se houver (ex.: OAB/SP 12.345 — ou deixe em branco)
```

### ETAPA 2 — Endereço e Contato

```
Agora os dados de contato que aparecem no cabeçalho:

1. Endereço completo (ex.: Rua das Flores, 100 · Centro · CEP 01.234-000 · São Paulo — SP)
2. Cidade-UF para fechamento das peças (ex.: São Paulo-SP)
3. E-mail de contato (ex.: contato@escritorio.com)
4. Telefone fixo (ex.: (11) 3000-0000 — ou deixe em branco)
5. Telefone celular (ex.: (11) 99000-0000)
```

### ETAPA 3 — Tipografia

```
Agora vamos definir as fontes. A skill usa duas famílias tipográficas:

• Fonte de títulos (cabeçalhos, seções, logo, assinatura)
  Padrão: Space Grotesk — moderna, geométrica, profissional
  Alternativas comuns: Montserrat, Raleway, Poppins, Inter, Roboto Slab

• Fonte do corpo (parágrafos, citações, texto corrido)
  Padrão: DM Sans — limpa, legível, contemporânea
  Alternativas comuns: Source Sans 3, Lato, Noto Sans, Open Sans, Merriweather (serifada)

Quer manter os padrões ou prefere outras fontes?
(Todas devem estar disponíveis no Google Fonts para carregar corretamente)
```

### ETAPA 4 — Tamanhos e Espaçamento

```
Tamanhos de fonte e espaçamento:

• Tamanho do corpo do texto (padrão: 15px ≈ 12pt Word)
• Tamanho das citações jurisprudenciais (padrão: 12.5px ≈ 10pt)
• Espaçamento entre linhas (padrão: 1.65 — equivalente a ~1,5 do Word)
• Recuo da primeira linha dos parágrafos (padrão: 2cm)
• Margem esquerda do documento (padrão: 32mm — inclui respiro da faixa lateral)
• Margem direita (padrão: 20mm)

Quer ajustar algum desses valores ou manter os padrões?
```

### ETAPA 5 — Cores e Identidade Visual

```
Paleta de cores da peça:

• Cor do texto principal (padrão: #1A1714 — preto quente)
• Cor de destaque / faixa lateral (padrão: #B08A4E — dourado)
• Cor de texto secundário (padrão: #6B5E4E — marrom acinzentado)
• Cor das linhas divisórias (padrão: #DDD6C8 — bege claro)
• Largura da faixa lateral (padrão: 6px)

Se você tem as cores do seu escritório em hex, pode informar aqui.
Ou quer manter a paleta padrão?
```

### ETAPA 6 — Estilo das Citações Jurisprudenciais

```
Como você quer que as citações de jurisprudência apareçam?

• Formato sanduíche (padrão): tese → ementa itálica recuada → fonte → aplicação ao caso
• Recuo da citação: esquerda (padrão: 2cm) + direita (padrão: 10px)
• Fonte do julgado — onde aparece a identificação (tribunal, número, relator)?
  - Abaixo da ementa, em linha separada (padrão)
  - Ao final da própria ementa, entre parênteses
• Estilo visual: itálico (padrão) ou entre aspas sem itálico?

Quer manter o padrão ou ajustar?
```

### ETAPA 7 — Regras de Redação

```
Preferências de redação para as peças:

• Pedidos/requerimentos formatados como: a) b) c) (padrão), ou I, II, III, ou 1, 2, 3?
• Valores monetários: sempre número + extenso? (padrão: sim — R$ 10.000,00 (dez mil reais))
• Latim e estrangeirismos em itálico? (padrão: sim)
• Nome do escritório aparece no corpo da petição? (padrão: não — só no cabeçalho)
• Limite de linhas por parágrafo (padrão: 4–5 linhas impressas em A4)
• Construção em blocos ou peça inteira de uma vez? (padrão: blocos — fundamentação, pedidos, fechamento separados, para manter controle e precisão)

Quer ajustar alguma dessas regras?
```

### ETAPA 8 — Confirmação e Resumo

Ao final, o Claude deve gerar um resumo estruturado assim:

```
Perfeito! Aqui está o resumo da sua configuração:

══════════════════════════════════════
CONFIGURAÇÃO — PEÇAS JURÍDICAS HTML
══════════════════════════════════════

DADOS DO ESCRITÓRIO
• Advogado: [nome]
• OAB: [oab]
• Razão Social: [razão social]
• Sigla: [sigla]  |  Nome curto: [nome curto]
• OAB Sociedade: [oab sociedade ou "—"]

CONTATO
• Endereço: [endereço]
• Cidade-UF: [cidade-uf]
• E-mail: [email]
• Telefones: [tel1] · [tel2]

TIPOGRAFIA
• Títulos: [fonte títulos]
• Corpo: [fonte corpo]
• Tamanho corpo: [fs]  |  Citações: [fs-cita]
• Espaçamento: [line-height]  |  Recuo: [recuo]

CORES
• Texto: [ink]  |  Destaque: [gold]
• Secundário: [muted]  |  Divisórias: [rule]
• Faixa lateral: [largura]

CITAÇÕES
• Formato: [sanduíche / outro]
• Fonte do julgado: [abaixo / inline]
• Estilo: [itálico / aspas]

REDAÇÃO
• Pedidos: [a) b) c) / I, II, III / 1, 2, 3]
• Valores: [número + extenso / só número]
• Parágrafos: [máx linhas]
• Construção: [blocos / inteira]

══════════════════════════════════════

Está tudo certo? Se quiser ajustar algo, me diga qual etapa.

💡 Dica: copie o bloco acima e cole em Settings > Profile > User Preferences.
Assim o Claude já terá seus dados em qualquer conversa futura.
```

---
