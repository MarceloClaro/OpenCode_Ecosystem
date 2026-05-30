---
feature: filtros-captacao
status: planning
created: 2026-05-08
updated: 2026-05-08
---

# Spec: Filtros Essenciais de Captação

> Taxonomia completa dos filtros que o sistema deve suportar na API e na interface de busca.
> Referência para os endpoints `GET /editais` e a UI de filtros dinâmicos (HTMX).

---

## 1. Área de Atuação / Eixo Temático

**Descrição:** Filtro primário que direciona a busca para o setor específico do projeto.

**Taxonomia proposta:**

| Eixo | Subcategorias |
|---|---|
| `tecnologia_industrial` | Indústria 4.0, automação, manufatura avançada, IoT industrial |
| `inovacao` | Deep tech, SaaS, hardware, patentes, spin-offs acadêmicas |
| `impacto_social` | Direitos humanos, inclusão, diversidade, desenvolvimento comunitário |
| `economia_criativa` | Audiovisual, música, literatura, design, games, moda |
| `saude_publica` | Epidemologia, biotech, saúde digital, dispositivos médicos |
| `conservacao_ambiental` | Clima, biodiversidade, energias renováveis, economia circular |
| `educacao` | Edtech, formação técnica, alfabetização científica, EAD |
| `agricultura` | Agritech, agricultura familiar, segurança alimentar, bioinsumos |
| `ciencia_pesquisa` | Pesquisa básica, pesquisa aplicada, divulgação científica |
| `civic_tech` | Governo digital, dados abertos, transparência, participação |

**Referências em portais reais:**
- Rede GIFE → filtra por "tese de investimento" do financiador
- SalicComparar → utiliza códigos CNAE cultural
- Plataforma Carlos Chagas (CNPq) → áreas do conhecimento CNPq/CAPES

**Campo no modelo:** `eixos_tematicos: list[str]`

---

## 2. Perfil do Proponente / Natureza Jurídica (Público-Alvo)

**Descrição:** Define quem está habilitado a receber o recurso. Fundamental para evitar leitura de editais incompatíveis com o CNPJ do usuário.

**Taxonomia:**

| Perfil | Descrição | Exemplos de financiadores |
|---|---|---|
| `osc` | Organização da Sociedade Civil (associações, fundações) | Fundo Brasil, Conecta MROSC, Prosas |
| `startup_early_stage` | Startup em estágio inicial (pré-seed, seed) | InovAtiva, SEBRAE Startups |
| `startup_deep_tech` | Startup de base tecnológica profunda | FINEP, EMBRAPII |
| `mpe` | Micro e Pequena Empresa | SEBRAE, FINEP Inovacred |
| `empresa_medio_grande` | Empresa de médio e grande porte | BNDES, FINEP |
| `ict` | Instituição Científica e Tecnológica (universidades, institutos) | CNPq, CAPES, FAPs |
| `pesquisador_individual` | Pessoa física pesquisadora | CNPq (bolsas), FAPs |
| `coletivo` | Coletivos informais, grupos sem CNPJ | Fundo Brasil, alguns editais municipais |
| `pessoa_fisica` | Pessoa física (artista, produtor cultural) | Lei Rouanet, editais de cultura |
| `governo` | Órgãos públicos (municipal, estadual, federal) | BNDES, ministérios |
| `cooperativa` | Cooperativas e associações de produtores | Editais de agricultura familiar |

**Campo no modelo:** `perfil_elegivel: list[str]`

---

## 3. Mecanismo de Financiamento

**Descrição:** Classifica a modelagem financeira do repasse.

**Taxonomia:**

| Mecanismo | Descrição | Exemplos |
|---|---|---|
| `subvencao_economica` | Recurso não reembolsável para inovação | FINEP Subvenção, EMBRAPII |
| `grant_direto` | Doação direta sem contrapartida financeira | Fundo Brasil, GIFE, fundações internacionais |
| `credito_subsidiado` | Empréstimo com juros abaixo do mercado | FINEP Inovacred, BNDES |
| `matchfunding` | Cofinanciamento — financiador iguala o valor captado | EMBRAPII, alguns editais SEBRAE |
| `renuncia_fiscal` | Dedução de imposto devido (incentivo fiscal) | Lei Rouanet, Lei do Bem, Lei de Incentivo ao Esporte |
| `premio` | Premiação em dinheiro por mérito | Editais de premiação, hackathons |
| `bolsa` | Bolsa de pesquisa/extensão para pessoa física | CNPq, CAPES, FAPs |
| `equity` | Investimento com participação societária | Editais de corporate venture, aceleradoras |
| `outro` | Outros mecanismos não categorizados | — |

**Campo no modelo:** `mecanismo_financiamento: str`

---

## 4. Abrangência Geográfica / Georreferenciamento

**Descrição:** Delimita a busca pelo território onde o projeto será executado ou onde o proponente está sediado.

**Estrutura:**

```json
{
  "tipo": "nacional",       // nacional | regional | estadual | municipal
  "regioes": ["sudeste"],   // opcional se tipo=regional
  "estados": ["SP"],        // opcional se tipo=estadual
  "municipios": []          // opcional se tipo=municipal
}
```

**Referências em portais reais:**
- Mapa da Cultura → repositórios georreferenciados, visualização em mapa
- Mapa das OSCs (IPEA) → dados por município/estado

**Campo no modelo:** `abrangencia_geografica: AbrangenciaGeografica`

---

## 5. Status do Edital / Janela de Submissão

**Descrição:** Organiza os resultados com base na linha do tempo da oportunidade.

**Taxonomia:**

| Status | Descrição | Comportamento no sistema |
|---|---|---|
| `inscricoes_abertas` | Aceitando submissões neste momento | Destaque prioritário na UI |
| `em_breve` | Edital anunciado, data de abertura futura | Alertas de planejamento antecipado |
| `encerrado` | Prazo de submissão expirado | Arquivado — útil para estudo de editais passados |
| `fluxo_continuo` | Aceita propostas durante todo o ano | Tag especial, sem data de encerramento |
| `suspenso` | Temporariamente pausado | Alerta na UI |
| `cancelado` | Cancelado definitivamente | Arquivado |

**Campo no modelo:** `status: Literal['inscricoes_abertas', 'em_breve', 'encerrado', 'fluxo_continuo', 'suspenso', 'cancelado']`

---

## 6. Faixa de Valor / Limite de Orçamento

**Descrição:** Filtra as oportunidades pelo teto de financiamento ou ticket médio oferecido.

**Faixas sugeridas para UI:**

| Faixa | Range | Exemplos típicos |
|---|---|---|
| `micro` | Até R$ 50 mil | Editais municipais, prêmios, bolsas |
| `pequeno` | R$ 50 mil – R$ 200 mil | SEBRAE, editais estaduais de cultura |
| `medio` | R$ 200 mil – R$ 1 milhão | FINEP Inovacred, FAPs, GIFE |
| `grande` | R$ 1 milhão – R$ 5 milhões | FINEP Subvenção, BNDES |
| `mega` | Acima de R$ 5 milhões | BNDES, Horizon Europe, grants internacionais |

**Campos no modelo:** `valor_min: float | None`, `valor_max: float | None`

**Funcionalidade complementar (fase 2+):**
- Cruzamento com painel de "Itens Orçamentários" (referência: SalicComparar)
- Conversão automática de moedas estrangeiras (USD, EUR → BRL)

---

## 7. Nível de Maturidade Tecnológica (TRL — Technology Readiness Level)

**Descrição:** Filtro vital em plataformas de inovação (FINEP, SEBRAE, MCTI). Classifica se o projeto é pesquisa básica, protótipo ou solução pronta para escala comercial.

**Escala TRL (1–9):**

| TRL | Nome | Descrição | Típico em |
|---|---|---|---|
| 1 | Princípio básico | Pesquisa fundamental, observação de princípios | CNPq Universal, FAPs |
| 2 | Conceito formulado | Hipótese e aplicação conceitual formulada | Editais acadêmicos |
| 3 | Prova de conceito | Validação experimental em laboratório | PIPE Fase 1, FAPs |
| 4 | Validação em lab | Tecnologia validada em ambiente de laboratório | PIPE Fase 2, EMBRAPII |
| 5 | Ambiente relevante | Validação em ambiente simulando o real | FINEP Subvenção |
| 6 | Demonstração | Protótipo demonstrado em ambiente operacional | SEBRAE, EMBRAPII |
| 7 | Sistema real | Protótipo operando em ambiente real | FINEP Inovacred |
| 8 | Sistema completo | Tecnologia finalizada e qualificada | BNDES, editais de escala |
| 9 | Missão operacional | Tecnologia comprovada em escala comercial | Editais de exportação, APEX |

**Campo no modelo:** `nivel_trl_min: int | None`, `nivel_trl_max: int | None`

**Observação:** Este filtro é menos explícito em portais sociais e culturais, sendo obrigatório apenas para editais de inovação tecnológica. Para portais não-tecnológicos, o campo será `None`.

---

## Mapeamento: Filtros vs Portais

| Portal | Área/Eixo | Perfil | Mecanismo | Geografia | Status | Valor | TRL |
|---|---|---|---|---|---|---|---|
| Prosas | ✅ | ✅ OSC | ✅ | ✅ | ✅ | ✅ | ❌ |
| FINEP | ✅ | ✅ ICT/empresa | ✅ crédito/subvenção | ✅ | ✅ | ✅ | ✅ |
| SEBRAE | ✅ | ✅ MPE/startup | ✅ | ✅ | ✅ | ✅ | ✅ |
| CNPq | ✅ | ✅ pesquisador/ICT | ✅ bolsa/grant | ✅ | ✅ | ✅ | ❌ |
| Rede GIFE | ✅ tese invest. | ✅ OSC | ✅ grant | ✅ | ✅ | ✅ | ❌ |
| SalicComparar | ✅ CNAE | ✅ PF/OSC | ✅ renúncia | ✅ | ✅ | ✅ itens orç. | ❌ |
| FAPs | ✅ | ✅ ICT/pesquisador | ✅ bolsa/grant | ✅ estadual | ✅ | ✅ | ✅ |
| Horizon Europe | ✅ | ✅ consórcios | ✅ grant | ✅ | ✅ | ✅ EUR | ✅ |

---

## Impacto na API

### Query params do `GET /editais`

```
GET /editais?
  eixo_tematico=inovacao,tecnologia_industrial
  &perfil_elegivel=startup_early_stage,mpe
  &mecanismo_financiamento=subvencao_economica,grant_direto
  &abrangencia_tipo=nacional
  &abrangencia_estado=SP
  &status=inscricoes_abertas,fluxo_continuo
  &valor_min=50000
  &valor_max=1000000
  &trl_min=4
  &trl_max=7
  &data_abertura_ate=2026-12-31
  &page=1
  &limit=20
```

### Resposta com facetas (para UI de filtros)

```json
{
  "total": 42,
  "facetas": {
    "eixos_tematicos": [
      {"valor": "inovacao", "contagem": 23},
      {"valor": "tecnologia_industrial", "contagem": 14}
    ],
    "perfil_elegivel": [
      {"valor": "startup_early_stage", "contagem": 18},
      {"valor": "mpe", "contagem": 22}
    ],
    "mecanismo_financiamento": [...],
    "abrangencia": [...],
    "status": [...],
    "faixas_valor": [...],
    "nivel_trl": [...]
  },
  "editais": [...]
}
```

---

## Integração com Agente 1 (Extrator)

O Agente 1 deve extrair todos os 7 campos de filtro do texto do edital. Prompt engineering deve incluir:

- **Área/Eixo:** classificar conforme taxonomia acima, com múltiplos eixos se aplicável
- **Perfil:** identificar todas as naturezas jurídicas mencionadas como elegíveis
- **Mecanismo:** modelagem financeira (subvenção, crédito, renúncia, matchfunding, etc.)
- **Abrangência:** extrair tipo e localização geográfica explícita
- **Status:** determinar com base nas datas (se data_abertura > hoje → "em_breve", se data_encerramento < hoje → "encerrado", etc.)
- **Valor:** extrair valor mínimo e máximo quando explícito
- **TRL:** extrair nível exigido (geralmente mencionado como "TRL 4-6", "maturidade tecnológica nível 5")

Campos não encontrados no texto devem ser retornados como `null`/`None`, nunca inventados.
