# Plano de Trabalho — Mestrado Profissional PPGQualiSaúde/UFRN

**Edital nº 02/2026 — Turma 2026.2**

---

## Dados do candidato

| Campo | Preenchimento |
|-------|---------------|
| Nome completo | Nadielle D'Arc Batista Dias |
| E-mail | *[e-mail da candidata]* |
| Título do projeto | Otimização da gestão de filas para Atenção Especializada: transparência, fluxo regulatório e redução do tempo de espera |
| Linha de pesquisa | ( X ) Melhoria da Qualidade |
| Projeto estruturante | ( X ) 6. Temáticas Diversas |
| Preferência de orientador(a) 1 | Prof. Zenewton André da Silva Gama |
| Preferência de orientador(a) 2 | Profa. Ana Carolina Patrício de Albuquerque Sousa |

---

## Seção 1 — Apresentação e contexto de trabalho

Atuo na gestão e coordenação do Departamento Integrado de Regulação e Auditoria, onde lido cotidianamente com o gargalo entre a demanda regulada e a oferta de consultas e exames especializados no SUS. Minha trajetória profissional é marcada pela busca de eficiência na alocação de recursos públicos, conciliando o cumprimento de protocolos de regulação (SISREG e complexidade reguladora) com a necessidade de garantir equidade e transparência no acesso.

Identifiquei na gestão da qualidade o arcabouço teórico-metodológico necessário para transformar a regulação — historicamente percebida como processo burocrático — em um sistema de melhoria contínua centrado no usuário. O Mestrado QualiSaúde oferece as ferramentas (ciclos PDSA, indicadores, desenho de intervenções multifacetadas) e o ambiente acadêmico para validar cientificamente as mudanças que pretendo implementar.

---

## Seção 2 — O que você deseja melhorar?

O tempo de espera para consultas e exames na Atenção Especializada é um dos principais indicadores de insatisfação do usuário e de ineficiência sistêmica no SUS. A Política Nacional de Regulação (PNR) e a Portaria de Consolidação nº 3/2017 instituem a regulação do acesso como função essencial do gestor, mas sua implementação permanece fragmentada.

**Problema central:** filas opacas — sem critérios públicos de priorização, sem feedback ao solicitante e sem monitoramento de tempos máximos — geram três consequências graves:

1. **Desigualdade de acesso**: pacientes com mesmo perfil clínico têm tempos de espera radicalmente diferentes a depender da unidade solicitante.
2. **Agravamento clínico**: condições que poderiam ser tratadas precocemente evoluem para estágios mais graves, aumentando o custo e reduzindo a chance de sucesso terapêutico.
3. **Desperdício de recursos**: consultas agendadas e não realizadas (absenteísmo), exames duplicados e encaminhamentos sem critério clínico claro.

**Referencial teórico:** O modelo de Donabedian (estrutura-processo-resultado) fundamenta a análise, e o ciclo PDSA (Plan-Do-Study-Act) orienta as intervenções. Autores como Vecina Neto e Malik (2018), Paim (2019) e a literatura do Institute for Healthcare Improvement (IHI) sobre *redução de filas em sistemas públicos* dão suporte à abordagem.

**Oportunidade de melhoria:** Redesenhar o fluxo regulatório local, transformando a fila de espera em um sistema rastreável, com critérios clínicos transparentes de priorização, prazos máximos por complexidade e devolutiva ao solicitante. A melhoria é oportuna no contexto da regulação municipal/estadual, onde convivem sistemas informatizados subutilizados, lógicas de agendamento manuais e ausência de indicadores de desempenho regulatório.

---

## Seção 3 — Como pretende medir a melhoria?

### Indicadores

| Indicador | Definição operacional | Fonte | Periodicidade |
|-----------|----------------------|-------|---------------|
| Tempo médio de espera (dias) | Período entre a inserção no SISREG e o agendamento da consulta/exame | SISREG | Mensal |
| Taxa de efetividade do agendamento | (Consultas realizadas / Consultas agendadas) x 100 | SIA/SUS | Mensal |
| Percentual de filas com priorização ativa | (Especialidades com classificação de risco documentada / Total de especialidades reguladas) x 100 | Auditoria interna | Trimestral |
| Índice de transparência | Proporção de solicitantes que declaram ter recebido posição na fila | Questionário estruturado | Semestral |
| Taxa de absenteísmo | (Pacientes que não compareceram / Total agendado) x 100 | SISREG | Mensal |

### Método de coleta e análise

Os dados secundários serão extraídos diretamente do SISREG e do SIA/SUS. Os dados primários (transparência) serão coletados por questionário aplicado a uma amostra de médicos solicitantes.

A análise seguirá desenho de série temporal interrompida (ITS), comparando os 6 meses pré-intervenção com os 12 meses pós-intervenção. Serão utilizados:
- **Run charts** com medianas e limites de controle para cada indicador
- **Teste t pareado** ou **Wilcoxon** para comparar médias pré/pós (previa verificação de normalidade por Shapiro-Wilk)
- **Análise descritiva** estratificada por especialidade e complexidade

Os resultados serão apresentados trimestralmente em reuniões de pactuação com a equipe reguladora e a gestão.

---

## Seção 4 — Que intervenções pretende realizar?

### Intervenção 1: Padronização do fluxo regulatório

| O quê | Elaboração de protocolo escrito de classificação de risco por especialidade, com critérios explícitos e gatilhos de prioridade |
|-------|-----------------------------------------------------------------------------------------------------------------------------|
| Como | Revisão da literatura + oficinas com especialistas reguladores + aprovação em CIB local |
| Quem | Coordenação do Departamento + equipe reguladora + apoio da gestão |
| Quando | Meses 1-3 |
| Risco | Resistência de especialidades à padronização → mitigado por construção participativa |

### Intervenção 2: Painel de monitoramento público

| O quê | Dashboard com status da fila por especialidade, tempo médio e vagas ofertadas |
|-------|--------------------------------------------------------------------------------|
| Como | Ferramenta de Business Intelligence (Power BI ou Metabase) alimentada pelo SISREG |
| Quem | Departamento de TI + coordenação |
| Quando | Meses 2-4 |
| Risco | Disponibilidade técnica da TI → escopo reduzido viável (planilha dinâmica como MVP) |

### Intervenção 3: Feedback ao solicitante

| O quê | Notificação automática sobre posição do paciente na fila e prazo estimado |
|-------|----------------------------------------------------------------------------|
| Como | Integração SISREG × plataforma de mensageria (WhatsApp Business API ou e-mail institucional) |
| Quem | Departamento de TI + coordenação |
| Quando | Meses 4-6 |
| Risco | Custo de implantação → solução escalonável: iniciar com e-mail, evoluir para SMS/WhatsApp |

### Intervenção 4: Auditoria concorrente

| O quê | Revisão semanal de amostra aleatória de solicitações para verificar conformidade com o protocolo |
|-------|--------------------------------------------------------------------------------------------------|
| Como | Técnico da regulação designado + checklist padronizado |
| Quem | Equipe de auditoria interna |
| Quando | Meses 3-12 |
| Risco | Sobrecarga da equipe → amostra de 10% das solicitações, rotativa por especialidade |

### Intervenção 5: Capacitação da equipe reguladora

- 4 oficinas presenciais (uma por trimestre) sobre ferramentas da qualidade: PDSA, fluxograma, diagrama de causa e efeito, carta de controle.
- Conteúdo alinhado às disciplinas do Mestrado, criando ponte teoria-prática.
- Público-alvo: reguladores, auditores, apoiadores administrativos.

---

## Seção 5 — Produtos técnicos possíveis

| Tipo de PTT (CAPES/Saúde Coletiva) | Produto proposto | Aderência ao projeto |
|------------------------------------|------------------|----------------------|
| Manual / Protocolo | Protocolo municipal de regulação ambulatorial por especialidade | Intervenção 1 |
| Tecnologia social / Processo | Painel de transparência de filas para Atenção Especializada | Intervenção 2 |
| Fluxograma / Procedimento técnico | Fluxo regulatório padronizado com tempos máximos e gatilhos de prioridade | Intervenções 1 e 4 |
| Relatório técnico conclusivo | Análise de impacto da intervenção multimodal sobre o tempo de espera | Todas as intervenções |
| Base de dados / Dataset | Série histórica anonimizada de indicadores regulatórios (pré e pós) | Todas as intervenções |
| Curso de curta duração | "Gestão de filas no SUS: ferramentas da qualidade para regulação" | Intervenção 5 |

---

# Guia para apresentação oral (10 minutos)

## Roteiro cronometrado

| Minuto | Conteúdo | Dica |
|--------|----------|------|
| **0'00–1'00** | **Abertura**: quem sou, onde trabalho, qual o problema central das filas na AE | Contexto profissional + problema em 3 frases |
| **1'00–2'30** | **Oportunidade de melhoria**: as 3 consequências das filas opacas (desigualdade, agravamento, desperdício) + referencial Donabedian/PDSA | Cite 1 dado concreto do seu serviço |
| **2'30–4'00** | **Indicadores**: mostre os 5 indicadores (tabela mental), destaque tempo médio de espera como primário | "O que não se mede não se gerencia" |
| **4'00–6'00** | **Intervenções**: apresente o combo multimodal — protocolo, painel, feedback, auditoria, capacitação | Use a lógica "padronizar → monitorar → comunicar → verificar → sustentar" |
| **6'00–7'00** | **Viabilidade**: escopo de 12 meses, equipe existente, ferramentas disponíveis, baixo custo incremental | Mostre que é factível, não ambicioso demais |
| **7'00–8'00** | **Produtos técnicos**: destaque o protocolo e o painel como PTTs principais | Alinhe com o que a CAPES valoriza |
| **8'00–9'00** | **Impacto esperado**: redução do tempo de espera, aumento da transparência, modelo replicável | "Este projeto pode ser piloto para outros municípios" |
| **9'00–10'00** | **Encerramento**: síntese dos 3 pilares (medir + intervir + sustentar) + alinhamento com o QualiSaúde | Termine com frase de impacto |

## Regras da apresentação

- **Sem recurso audiovisual** (edital, item 61) — apenas sua fala.
- **Máximo 10 minutos** — cronometre nos ensaios. A banca pode interromper se estourar.
- **Tom técnico, não político** — foque em metodologia e evidência, não em crítica à gestão.
- **Esteja preparado para ser interrompido** — a banca pode pedir esclarecimentos durante a apresentação.

---

# Preparação para arguição (20 minutos)

## Perguntas esperadas da banca

### Sobre o método

| Pergunta | Resposta esperada |
|----------|-------------------|
| Por que série temporal interrompida e não um ensaio controlado? | Porque a intervenção é no nível do serviço, não individual. ITS é o padrão-ouro para estudos de melhoria da qualidade (JBI, SQUIRE 2.0). Não há grupo controle viável na regulação. |
| Como vai garantir que a melhoria observada não é devida a fatores externos? | Documentação de cointervenções (mudanças na gestão, novas portarias) e análise de sensibilidade excluindo períodos atípicos. |
| Qual o tamanho da amostra para o questionário de transparência? | Amostra de conveniência com todos os médicos solicitantes de 3 especialidades piloto (estimativa: 30-50 respondentes). Suficiente para estatística descritiva. |

### Sobre a viabilidade

| Pergunta | Resposta esperada |
|----------|-------------------|
| O SISREG permite a extração de dados que você precisa? | Sim, o SISREG possui módulo de relatórios. Em caso de limitação técnica, a ouvidoria municipal obriga a alimentação de dados de fila por lei. |
| Como lidar com a resistência dos médicos reguladores? | Engajamento precoce nas oficinas, mostrando que o protocolo reduz carga de decisão individual e padroniza critérios — proteção jurídica para o regulador. |
| Qual o custo estimado do painel? | Ferramentas gratuitas (Metabase ou Google Looker Studio) + horas de TI já alocadas. Custo marginal próximo de zero. |

### Sobre o alinhamento acadêmico

| Pergunta | Resposta esperada |
|----------|-------------------|
| Como este projeto se insere na linha Melhoria da Qualidade? | Porque atua sobre processo (fluxo regulatório), utiliza métodos da qualidade (PDSA, indicadores) e gera produtos técnicos reconhecidos pela CAPES. |
| Qual a diferença entre seu projeto e o projeto "Temáticas Diversas"? | Temáticas Diversas acolhe propostas transversais que não se encaixam nos projetos 1-5. Meu projeto poderia futuramente dialogar com os projetos Qualidade na APS (fronteira entre APS e AE) ou Segurança no Macrossistema (governança regulatória). |
| Que disciplina do programa é mais relevante para seu projeto? | Qualidade em Serviços de Saúde (fundamentação) + Métodos e Técnicas de Pesquisa (desenho) + Sistemas de Informação em Saúde (extração de dados). |

---

## Checklist final

- [ ] Inscrição no SIGAA dentro do prazo (17/03 a 17/04/2026)
- [ ] Isenção de taxa, se aplicável (até 27/03/2026)
- [ ] Documentação anexada: diploma, currículo Lattes, plano de trabalho e demais itens do art. 28
- [ ] Plano de Trabalho preenchido no Google Forms: https://forms.gle/GyNgQjkPLyonXVAC7
- [ ] Cópia em PDF do Plano salva e anexada à inscrição
- [ ] Ensaios da apresentação oral cronometrados (mínimo 3 ensaios)
- [ ] Leitura da banca: conheça o perfil dos professores que avaliarão
- [ ] Preparação de respostas para perguntas acima (mínimo 2 rodadas de simulação)

---

*Documento gerado em 04/06/2026 com base no Edital nº 02/2026 do PPGQualiSaúde/UFRN.*
