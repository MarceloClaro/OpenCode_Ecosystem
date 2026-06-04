## STATUS DO PROJETO — 31/05/2026

# A Proteção da Personalidade Humana na Era da Inteligência Artificial: Contribuições da Encíclica Magnifica Humanitas para o Direito Contemporâneo

## Resumo do Projeto

Monografia de conclusão do curso de Direito para submissão ao **PPGTE/UFC**. Pesquisa jurídico-teórica, qualitativa, abordagem hermenêutico-crítica, investigando como os fundamentos antropológicos e éticos da **Encíclica Magnifica Humanitas** (Leão XIV, 25/05/2026) podem contribuir para a proteção da personalidade humana na era da inteligência artificial.

---

## Concluído

### Planejamento e Metodologia
- [x] Elaboração do planejamento de pesquisa completo (`planejamento_pesquisa.md`)
  - Problema, 4 hipóteses (H1–H4), 5 objetivos específicos (OE1–OE5)
  - Metodologia: jurídico-teórica, qualitativa, hermenêutico-crítica
  - Sumário em 6 capítulos + referências + anexos
  - Protocolo de fichamento e auditoria de citações (5 critérios, nota 0–10)
  - Plano de busca bibliográfica (6 bases, 10 descritores)
  - Cronograma em 8 fases
  - Referências iniciais (15 obras)

### Leitura da Fonte Primária
- [x] Leitura completa do texto integral da **Encíclica Magnifica Humanitas** (`pesquisa/magnifica_humanitas_texto_integral.txt`, 3117 linhas)
  - Introdução (§1–16), Cap. I (§17–45), Cap. II (§46–73)
  - Cap. III (§90–130) — núcleo temático sobre IA
  - Cap. IV (§131–178), Cap. V (§179–218), Conclusão (§219–232), Notas Finais
- [x] Leitura de materiais de apoio

### Protocolo de Fichamento
- [x] Criação do protocolo de fichamento (`fichamentos/README.md`)
  - Estrutura obrigatória com 5 critérios de auditoria
  - Nota de confiança (0–10)
  - Convenção de nomenclatura: N001_Autor_PalavraChave.md

### Estrutura do Projeto
- [x] Criação da estrutura de diretórios (`manuscrito/`, `fichamentos/`, `pesquisa/`, `referencias/`, `anexos/`)
- [x] Remoção de artefatos obsoletos da raiz do projeto

### Estrutura LaTeX do Manuscrito
- [x] Criação de `manuscrito/main.tex` — documento principal com preâmbulo abnTeX2
- [x] Criação de `manuscrito/pacotes.tex` — pacotes e configurações
- [x] Criação de `manuscrito/refs.bib` — referências bibliográficas (76+ entradas)
- [x] Definição do ambiente `fichamento` no preâmbulo
- [x] Definição dos comandos `\MH` e `\MHn{n}`

### Capítulos Escritos
- [x] **Capítulo 1** — Introdução (`manuscrito/cap1-introducao.tex`)
- [x] **Capítulo 2** — Fundamentos Antropológicos e Éticos (`manuscrito/cap2-fundamentos-antropologicos.tex`)
- [x] **Capítulo 3** — IA e Desafios à Personalidade (`manuscrito/cap3-ia-desafios.tex`)
- [x] **Capítulo 4** — Proteção Jurídica no Brasil (`manuscrito/cap4-protecao-juridica.tex`)
- [x] **Capítulo 5** — Contribuições para Regulação da IA (`manuscrito/cap5-contribuicoes-magnifica.tex`)
- [x] **Capítulo 6** — Conclusão (`manuscrito/cap6-conclusao.tex`)
- [ ] **Anexo de Fichamentos** (`manuscrito/anexo-fichamentos.tex`) — criado, aguarda compilação

### Controle de Qualidade
- [x] Correção de label duplicado `sec:principios-eticos` → `sec:principios-eticos-mh`
- [x] Varredura completa de citações: 53 chaves usadas, 50 em refs.bib
- [x] Expansão de refs.bib: +23 entradas adicionadas
- [x] Correção de chaves: `MH2026` → `LeaoXIV2026MH`, `UniaoEuropeia2016GDPR` → `UE2016GDPR`, `Rodotà2008PDA` → `Rodota2008PDA`
- [x] **Cotejo de citações MH → manuscrito** (`docs/cotejo-citacoes-mh.md`)
  - Varredura de 19 ocorrências de `\cite{LeaoXIV2026MH}` em todos os capítulos
  - Cotejo contra os 5 parágrafos fichados (§3, §89, §101, §186, §232)
  - 2 edições aplicadas em `cap3-ia-desafios.tex`: `\cite[§3]` (L138) e `\cite[§232]` (L166)
  - Demais 17 ocorrências mantidas sem `[§XX]` por não corresponderem a citações diretas fichadas

---

## Concluído (31/05/2026)

- [x] **Compilação e validação do PDF final** (91 págs, 499548 bytes, 0 erros)
- [x] Revisão de consistência das citações — cotejo formal em `docs/cotejo-citacoes-mh.md`
- [x] Adição de fichamentos documentais ao anexo (cotejo + STATUS)

---

## Próximos Passos

### Revisão Final
1. Revisão de redação dos capítulos (pendente)
2. Verificar consistência dos fichamentos com o texto
3. Ajustar numeração e referências cruzadas se necessário
4. Revisão final da formatação ABNT

---

## Informações Críticas

- **Encíclica**: Publicada em 25/05/2026, assinada em 15/05/2026
- **Autor da Encíclica**: Leão XIV
- **Numeração real**: §1–232 (difere do sumário preliminar)
- **Capítulo III** (§90–130): núcleo temático sobre IA
- **Formatação**: abnTeX2 (conforme anteprojeto PPGTE/UFC)
- **Projeto autônomo**: sem dependência do ecossistema OpenCode
- **refs.bib**: 73+ entradas, crescimento de 50→73 na expansão
- **Chaves normalizadas**: sem acentos, sem duplicatas
