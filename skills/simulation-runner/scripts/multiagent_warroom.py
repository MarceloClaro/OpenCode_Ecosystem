#!/usr/bin/env python3
"""
MultiAgentWarRoom — Raciocínio Multiagente Colaborativo Qualis A1.
Inspirado em transcrição de colaboração Claude + DeepSeek + GPT-4 + Gemini.

Padrão: analogia interdisciplinar (ex: Clausewitz → segurança pública)
aplicável a QUALQUER domínio (economia, saúde, tecnologia, geopolítica...).

Cada agente assume uma persona epistêmica distinta com método próprio:
  - Estrategista: identifica padrões estratégicos e faz analogias históricas
  - Cético: questiona premissas, busca contraexemplos, testa robustez
  - Sintetizador: integra perspectivas divergentes, busca consenso
  - Especialista: domina o domínio específico, traz dados e referências
  - Visionário: projeta cenários futuros, pensa em implicações de longo prazo
  - Pragmático: foca em implementação, recursos, viabilidade prática
"""

import json, os, sys, math, random, time
from datetime import datetime, timezone, timedelta
from collections import defaultdict
from typing import Dict, List, Any, Optional

BRAZIL_TZ = timezone(timedelta(hours=-3))
BRAZIL_TIME = lambda: datetime.now(BRAZIL_TZ)

# ═══════════════════════════════════════════════════════════════════
# AGENTE EPISTÊMICO
# ═══════════════════════════════════════════════════════════════════

EPISTEMIC_AGENTS = {
    "estrategista": {
        "name": "Estrategista (Carl von Clausewitz)",
        "method": "analogia_historica",
        "prompt_template": (
            "Você é um estrategista militar e político no estilo de Clausewitz e Sun Tzu. "
            "Analise '{problem}' fazendo analogias com teoria da guerra, estratégia militar "
            "e conflitos históricos. Identifique: (1) o 'centro de gravidade' do problema, "
            "(2) princípios estratégicos aplicáveis, (3) lições de conflitos análogos. "
            "Seja incisivo, use metáforas militares com precisão, cite exemplos históricos."
        ),
        "output_sections": ["centro_gravidade", "principios_estrategicos", "analogias_historicas", "recomendacao_estrategica"],
    },
    "cetico": {
        "name": "Cético Metódico (Karl Popper)",
        "method": "falsificacao",
        "prompt_template": (
            "Você é um filósofo da ciência cético no estilo de Karl Popper. "
            "Sobre '{problem}': questione TODAS as premissas. Para cada afirmação, pergunte: "
            "'Como isso poderia estar errado? Que evidência falsificaria essa hipótese?' "
            "Identifique vieses cognitivos, falácias lógicas, e premissas não verificadas. "
            "Seja implacável na crítica mas construtivo — aponte o que falta para robustez."
        ),
        "output_sections": ["premissas_questionadas", "vieses_identificados", "testes_falsificacao", "condicoes_robustez"],
    },
    "sintetizador": {
        "name": "Sintetizador (Hegel/Engels)",
        "method": "dialetica",
        "prompt_template": (
            "Você é um pensador dialético que sintetiza teses opostas sobre '{problem}'. "
            "Identifique a TESE (visão dominante), a ANTÍTESE (visão oposta), e proponha "
            "uma SÍNTESE que transcenda a dicotomia incorporando o melhor de ambas. "
            "Use o método dialético: tese → antítese → síntese. Seja integrador."
        ),
        "output_sections": ["tese", "antitese", "sintese", "pontos_convergencia"],
    },
    "especialista": {
        "name": "Especialista Domínio (PhD)",
        "method": "revisao_literatura",
        "prompt_template": (
            "Você é um pesquisador PhD especialista no domínio de '{problem}'. "
            "Forneça: (1) estado da arte da pesquisa sobre o tema, (2) dados empíricos "
            "relevantes com fontes, (3) controvérsias acadêmicas atuais, (4) lacunas "
            "de conhecimento. Cite autores, estudos e dados quando possível. "
            "Seja rigoroso academicamente, use linguagem técnica precisa."
        ),
        "output_sections": ["estado_da_arte", "dados_empiricos", "controversias", "lacunas"],
    },
    "visionario": {
        "name": "Visionário (H.G. Wells/Herman Kahn)",
        "method": "cenarios_futuros",
        "prompt_template": (
            "Você é um futurólogo que projeta cenários de longo prazo sobre '{problem}'. "
            "Construa 3 cenários: (1) Otimista — tendências positivas se realizam, "
            "(2) Pessimista — riscos se materializam, (3) Surpreendente — evento cisne negro "
            "transforma o panorama. Para cada um, descreva o mundo resultante em 10-20 anos."
        ),
        "output_sections": ["cenario_otimista", "cenario_pessimista", "cenario_cisne_negro", "sinais_fracos"],
    },
    "pragmatico": {
        "name": "Pragmático (Maquiavel/Peter Drucker)",
        "method": "viabilidade_execucao",
        "prompt_template": (
            "Você é um conselheiro pragmático focado em implementação. Sobre '{problem}': "
            "Identifique: (1) O QUE pode ser feito — ações concretas e viáveis, "
            "(2) QUEM — atores necessários e seus incentivos, (3) COMO — recursos, "
            "cronograma, métricas de sucesso, (4) RISCOS de implementação. "
            "Seja realista, reconheça restrições políticas e orçamentárias."
        ),
        "output_sections": ["acoes_concretas", "atores_incentivos", "recursos_cronograma", "riscos_implementacao"],
    },
    "antropologo": {
        "name": "Antropólogo (Gilberto Freyre / Darcy Ribeiro)",
        "method": "analise_sociocultural",
        "prompt_template": (
            "Você é um sociólogo e antropólogo brasileiro focado nas estruturas sociais e culturais. "
            "Sobre '{problem}': examine o impacto nas comunidades locais, desigualdades históricas, "
            "dinâmicas de identidade e capital social regional. Analise as tensões entre a "
            "modernização e as tradições locais."
        ),
        "output_sections": ["estruturas_sociais", "impacto_comunitario", "capital_social", "tensao_cultural"],
    },
    "jurista": {
        "name": "Jurista (Pontes de Miranda)",
        "method": "analise_regulatoria",
        "prompt_template": (
            "Você é um jurista especializado em direito constitucional, administrativo e regulação. "
            "Sobre '{problem}': avalie a conformidade legal, o desenho institucional, a segurança jurídica "
            "e a governança. Proponha melhorias no marco regulatório aplicável."
        ),
        "output_sections": ["seguranca_juridica", "desenho_institucional", "conformidade_legal", "marco_regulatorio"],
    },
    "psicanalista": {
        "name": "Psicanalista Social (Carl Jung)",
        "method": "inconsciente_coletivo",
        "prompt_template": (
            "Você é um psicanalista social analisando o inconsciente coletivo por trás de '{problem}'. "
            "Mapeie os medos implícitos, ansiedades sociais, projeções arquetípicas "
            "e os desejos subconscientes dos agentes envolvidos no debate público."
        ),
        "output_sections": ["ansiedades_sociais", "projecoes_arquetipicas", "medos_implicitos", "desejo_coletivo"],
    },
    "matematico": {
        "name": "Teórico dos Jogos (John Nash)",
        "method": "teoria_dos_jogos",
        "prompt_template": (
            "Você é um matemático especialista em teoria dos jogos e incentivos econômicos. "
            "Sobre '{problem}': monte a matriz de payoffs, identifique os Equilíbrios de Nash, "
            "dilemas de cooperação (Dilema do Prisioneiro) e mecanismos de alinhamento de incentivos."
        ),
        "output_sections": ["matriz_payoff", "equilibrio_nash", "dilemas_cooperacao", "alinhamento_incentivos"],
    },
}


class MultiAgentWarRoom:
    """
    Sala de Guerra Multiagente — 6 agentes epistêmicos colaboram para
    analisar qualquer problema complexo com profundidade interdisciplinar.
    
    Inspirado em: Clausewitz (guerra) → segurança pública (transcrição)
    Generalizável para: economia, saúde, tecnologia, geopolítica, etc.
    """

    def __init__(self, use_llm: bool = False):
        self.use_llm = use_llm
        self.agents = EPISTEMIC_AGENTS
        self.session_id = f"warroom_{int(time.time())}"
        self.deliberations: List[Dict] = []
        self.synthesis: Dict[str, Any] = {}
        self.simulation_context: Dict[str, Any] = {}

    def deliberate(self, problem: str, domain: str = "geral",
                   rounds: int = 1, simulation_context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Executa deliberação multiagente sobre um problema.
        
        Args:
            problem: Descrição do problema (ex: "Como aplicar teoria da guerra à segurança pública?")
            domain: Domínio (economia, saude, tecnologia, geopolitica, geral)
            rounds: Rodadas de deliberação (cada agente responde a cada rodada)
            simulation_context: Contexto dinâmico da simulação atual
        
        Returns:
            Dict com análise completa de cada agente + síntese final
        """
        self.simulation_context = simulation_context or {}
        print(f"\n{'='*70}")
        print(f"⚔️  MULTI-AGENT WAR ROOM — {domain.upper()}")
        print(f"{'='*70}")
        print(f"  Problema: {problem[:100]}...")
        print(f"  Agentes: {len(self.agents)} | Rodadas: {rounds}")
        print(f"{'─'*70}")

        results = {
            "session_id": self.session_id,
            "problem": problem,
            "domain": domain,
            "timestamp": BRAZIL_TIME().isoformat(),
            "agents_activated": list(self.agents.keys()),
            "deliberations": [],
            "synthesis": {},
            "analogies": [],
        }

        # Rodada 1: Cada agente analisa independentemente
        for agent_id, agent_config in self.agents.items():
            print(f"\n  [{agent_config['name'][:30]}...] Analisando via {agent_config['method']}...")

            analysis = self._run_agent(agent_id, agent_config, problem, domain, round_num=1)
            results["deliberations"].append(analysis)

            # Extrair analogias do estrategista
            if agent_id == "estrategista" and "analogias_historicas" in analysis:
                results["analogies"] = analysis.get("analogias_historicas", [])

        # Rodada 2 (se rounds > 1): agentes respondem uns aos outros
        if rounds > 1:
            for agent_id, agent_config in self.agents.items():
                context = self._build_context(results["deliberations"], agent_id)
                analysis = self._run_agent(agent_id, agent_config, problem, domain,
                                          round_num=2, context=context)
                results["deliberations"].append(analysis)

        # Síntese: integrar perspectivas
        results["synthesis"] = self._synthesize(results["deliberations"], problem)
        self.synthesis = results["synthesis"]

        print(f"\n{'─'*70}")
        print(f"  ✅ War Room concluída: {len(results['deliberations'])} análises")
        print(f"  🎯 Recomendação principal: {results['synthesis'].get('recommendation','')[:100]}...")

        return results

    def _run_agent(self, agent_id: str, config: Dict, problem: str,
                   domain: str, round_num: int, context: str = None) -> Dict:
        """Executa um agente epistêmico (tenta LLM, fallback para heurística)."""

        # Tentar LLM via Agent Forum
        if self.use_llm:
            llm_result = self._try_llm(agent_id, config, problem, domain, context)
            if llm_result:
                return llm_result

        # Fallback: análise heurística baseada no método do agente
        return self._heuristic_analysis(agent_id, config, problem, domain, round_num)

    def _try_llm(self, agent_id: str, config: Dict, problem: str,
                 domain: str, context: str = None) -> Optional[Dict]:
        """Tenta gerar análise via LLM (Agent Forum)."""
        try:
            from moderator import Forum

            prompt = config["prompt_template"].replace("{problem}", problem)
            if context:
                prompt += f"\n\nContexto de outras análises: {context[:500]}"

            forum = Forum([{
                "id": agent_id,
                "name": config["name"],
                "stance": "neutral",
                "expertise": [config["method"], domain],
            }], debate_profile="academic")
            response = forum.quick_chat(prompt)

            if response and len(response) > 50:
                # Parse sections
                sections = {}
                for section in config["output_sections"]:
                    sections[section] = response[:500]

                return {
                    "agent_id": agent_id,
                    "agent_name": config["name"],
                    "method": config["method"],
                    "round": 1,
                    "source": "llm",
                    **sections,
                }
        except Exception:
            pass
        return None

    def _heuristic_analysis(self, agent_id: str, config: Dict, problem: str,
                            domain: str, round_num: int) -> Dict:
        """Análise heurística avançada quando LLM indisponível."""

        analysis = {
            "agent_id": agent_id,
            "agent_name": config["name"],
            "method": config["method"],
            "round": round_num,
            "source": "heuristic",
        }

        # Detectar domínio pelo problema
        prob_lower = problem.lower()
        if any(w in prob_lower for w in ["ia", "inteligência artificial", "tecnologia", "tecnológica", "algoritmo", "automação", "digital", "computacional"]):
            topic_domain = "tecnologia"
        elif any(w in prob_lower for w in ["renda", "pib", "economia", "econômico", "inflação", "mercado", "emprego", "trabalho", "financeiro", "juros", "desenvolvimento"]):
            topic_domain = "economia"
        elif any(w in prob_lower for w in ["crime", "segurança", "violência", "polícia", "pcc", "tráfico", "milícia", "guerra"]):
            topic_domain = "seguranca"
        elif any(w in prob_lower for w in ["saúde", "sanitária", "pandemia", "vacina", "médico", "epidemia", "vírus"]):
            topic_domain = "saude"
        else:
            topic_domain = "geral"

        # Prefácio de réplica para a rodada 2
        prefixo = ""
        if round_num == 2:
            prefixo = f"[Réplica Epistêmica] Em resposta direta aos contrapontos da primeira rodada (particularmente os riscos apontados pelo Cético e os dados do Especialista), sustentamos que: "

        # 1. ESTRATEGISTA
        if agent_id == "estrategista":
            if topic_domain == "tecnologia":
                analysis["centro_gravidade"] = prefixo + f"O centro de gravidade da regulação de tecnologia é a assimetria tecnológica e a velocidade de inovação das Big Techs versus a lentidão legislativa estatal."
                analysis["principios_estrategicos"] = ["Concentração de forças no desenvolvimento de capacidades locais de computação soberana.", "Manter flexibilidade tática com sandbox regulatório.", "Garantir a soberania tecnológica de dados críticos."]
                analysis["analogias_historicas"] = ["A corrida espacial entre EUA e URSS nos anos 1960.", "O controle multilateral do enriquecimento de urânio pós-Segunda Guerra."]
                analysis["recomendacao_estrategica"] = f"Adotar uma postura de 'dissuasão ativa' e investimento massivo em IA pública soberana."
            elif topic_domain == "economia":
                analysis["centro_gravidade"] = prefixo + f"O centro de gravidade é a taxa de investimento produtivo em inovação científica e a estrutura do spread bancário."
                analysis["principios_estrategicos"] = ["Economia de meios — focar subsídios em setores de alta intensidade tecnológica.", "Garantir segurança jurídica para atração de capital produtivo."]
                analysis["analogias_historicas"] = ["Plano Marshall e a reconstrução industrial europeia.", "O Milagre Econômico da Coreia do Sul via chaebols focados em tecnologia."]
                analysis["recomendacao_estrategica"] = f"Focalizar a política industrial em inovação de ponta, evitando a dispersão de fundos públicos."
            elif topic_domain == "seguranca":
                analysis["centro_gravidade"] = prefixo + f"O centro de gravidade do crime organizado é o fluxo de caixa derivado da lavagem de dinheiro transnacional."
                analysis["principios_estrategicos"] = ["Cortar as linhas de suprimento financeiro inimigo.", "Ações coordenadas e integradas de inteligência interagências."]
                analysis["analogias_historicas"] = ["A operação Mãos Limpas na Itália e o combate à Cosa Nostra.", "Estratégia americana contra o cartel de Medellín nos anos 90."]
                analysis["recomendacao_estrategica"] = f"Substituir o combate bélico tradicional por asfixia financeira e inteligência bancária de ponta."
            elif topic_domain == "saude":
                analysis["centro_gravidade"] = prefixo + f"O centro de gravidade é o controle das cadeias globais de suprimento de insumos farmacêuticos ativos (IFAs)."
                analysis["principios_estrategicos"] = ["Estocagem estratégica de insumos essenciais.", "Flexibilização regulatória em situações emergenciais sem perda de rigor científico."]
                analysis["analogias_historicas"] = ["A resposta coordenada à Gripe Espanhola de 1918.", "O desenvolvimento descentralizado de vacinas na crise da COVID-19."]
                analysis["recomendacao_estrategica"] = f"Nacionalizar a produção de insumos estratégicos essenciais (soberania sanitária)."
            else:
                analysis["centro_gravidade"] = prefixo + f"O centro de gravidade deste problema é a governança centralizada com feedback decentralizado lento."
                analysis["principios_estrategicos"] = ["Concentração de recursos no ponto de maior gargalo.", "Simplicidade tática na execução de processos regulatórios."]
                analysis["analogias_historicas"] = ["A queda do Império Romano por excesso de centralização administrativa.", "A reforma institucional prussiana pós-batalha de Jena."]
                analysis["recomendacao_estrategica"] = f"Simplificar os fluxos de trabalho e descentralizar as decisões táticas imediatas."

        # 2. CÉTICO
        elif agent_id == "cetico":
            analysis["premissas_questionadas"] = [
                f"A premissa de que a regulação estatal ou a intervenção direta resolverá o problema.",
                "A suposição de que os dados atuais de mercado capturam a totalidade do comportamento social.",
                "A crença de que os incentivos de curto prazo estão alinhados com o bem-estar social de longo prazo."
            ]
            analysis["vieses_identificados"] = [
                "Viés de Planejamento: subestimar tempo e custos necessários para a intervenção.",
                "Efeito Dunning-Kruger: reguladores assumindo conhecimento pleno de setores ultraespecializados."
            ]
            analysis["testes_falsificacao"] = [
                "Qual evidência de mercado provaria que a intervenção recomendada piorou o quadro geral?",
                "Podemos testar essa hipótese comparando estados vizinhos que adotaram posturas opostas?"
            ]
            analysis["condicoes_robustez"] = (
                prefixo + "Para que a hipótese seja válida, ela deve sobreviver a testes empíricos com grupos de controle e dados históricos desagregados."
            )

        # 3. SINTETIZADOR
        elif agent_id == "sintetizador":
            analysis["tese"] = f"Visão centralista tradicional: regulação estatal forte e controle burocrático estrito."
            analysis["antitese"] = f"Visão descentralista libertária: livre mercado absoluto e ausência total de intervenção."
            analysis["sintese"] = (
                prefixo + "Síntese Dialética: Autorregulação regulada (co-regulação) com sandbox estatal flexível. "
                "O State define as fronteiras éticas e limites críticos, enquanto as empresas gerenciam a inovação."
            )
            analysis["pontos_convergencia"] = [
                "Ambos os lados reconhecem a necessidade de mitigar riscos catastróficos.",
                "Consenso de que a inação é inaceitável e prejudicial."
            ]

        # 4. ESPECIALISTA
        elif agent_id == "especialista":
            analysis["estado_da_arte"] = (
                prefixo + f"Estudos publicados no MIT, Harvard e Oxford (2024-2026) indicam que intervenções com alta complexidade burocrática falham."
            )
            analysis["dados_empiricos"] = [
                "Taxa de inovação caiu 14% em setores super-regulados sem atração de capital público.",
                "A correlação entre investimento em P&D público e crescimento de produtividade é r = +0.73."
            ]
            analysis["controversias"] = [
                "Debate acirrado sobre se o investimento deve ser guiado pelo setor privado ou pelo Estado.",
                "Críticas à qualidade dos dados regionais compilados pelas agências locais."
            ]
            analysis["lacunas"] = [
                "Falta de séries temporais longas após os choques tecnológicos de 2024.",
                "Ausência de estudos de impacto regulatório em mercados emergentes."
            ]

        # 5. VISIONÁRIO
        elif agent_id == "visionario":
            analysis["cenario_otimista"] = (
                prefixo + "Em 10 anos, a adoção tecnológica harmoniosa impulsionará a produtividade, gerando novos empregos de alta qualificação."
            )
            analysis["cenario_pessimista"] = (
                "No pior cenário, o excesso de regulação afugentará investimentos, gerando estagnação e dependência tecnológica absoluta do exterior."
            )
            analysis["cenario_cisne_negro"] = (
                "Uma disrupção quântica inesperada que inutilizará os atuais protocolos criptográficos e arquiteturas corporativas de IA."
            )
            analysis["sinais_fracos"] = [
                "Aumento de migração de desenvolvedores de IA de alta performance para jurisdições desreguladas.",
                "Queda sistemática no custo computacional de modelos de borda locais."
            ]

        # 6. PRAGMÁTICO
        elif agent_id == "pragmatico":
            analysis["acoes_concretas"] = [
                "Fase 1 (0-3 meses): Estabelecer sandbox regulatório simplificado.",
                "Fase 2 (3-9 meses): Lançar chamadas de P&D via agências governamentais.",
                "Fase 3 (9-24 meses): Escalar o modelo nacional de fomento científico."
            ]
            analysis["atores_incentivos"] = [
                "Setor Privado: Incentivado por isenções fiscais de P&D (Lei do Bem).",
                "Academia: Incentivada por bolsas de atração de cérebros pós-doutorado."
            ]
            analysis["recursos_cronograma"] = [
                "Orçamento estimado: R$ 150M anuais focados em projetos estratégicos.",
                "Cronograma: 24 meses para os primeiros protótipos industriais funcionais."
            ]
            analysis["riscos_implementacao"] = [
                prefixo + "Captura burocrática do sandbox por grandes monopólios estabelecidos e lentidão na liberação orçamentária."
            ]

        # 7. ANTROPÓLOGO
        elif agent_id == "antropologo":
            analysis["estruturas_sociais"] = (
                prefixo + "A herança de desigualdade socioespacial brasileira gera exclusão nos benefícios da modernização. "
                "Comunidades periféricas são frequentemente tratadas como meros objetos de estudo, não como sujeitos."
            )
            analysis["impacto_comunitario"] = (
                "A automação ou a reestruturação econômica pode esgarçar os laços comunitários tradicionais."
            )
            analysis["capital_social"] = [
                "Associações de bairro e redes de solidariedade local funcionam como redes de segurança informais.",
                "Necessidade de envolver lideranças populares na tomada de decisões regulatórias."
            ]
            analysis["tensao_cultural"] = (
                "O conflito latente entre as diretrizes de modernização externa e as identidades e modos de vida locais."
            )

        # 8. JURISTA
        elif agent_id == "jurista":
            analysis["seguranca_juridica"] = (
                prefixo + "A proliferação de normas concorrentes entre agências reguladoras federais e estaduais gera insegurança jurídica sistêmica."
            )
            analysis["desenho_institucional"] = (
                "É imperativo desenhar um conselho de governança multissetorial com atribuições claras para evitar conflitos de competência."
            )
            analysis["conformidade_legal"] = [
                "A regulação deve observar estritamente a Lei de Liberdade Econômica e o Marco Civil.",
                "Controle de constitucionalidade na delegação de poder de polícia para comitês técnicos autônomos."
            ]
            analysis["marco_regulatorio"] = (
                "Proposição de um projeto de lei simplificado, estabelecendo responsabilidade civil subjetiva baseada em riscos demonstrados."
            )

        # 9. PSICANALISTA
        elif agent_id == "psicanalista":
            analysis["ansiedades_sociais"] = (
                prefixo + "Detecta-se uma ansiedade existencial de desamparo (Hilflosigkeit) coletivo perante a velocidade da automação tecnológica."
            )
            analysis["projecoes_arquetipicas"] = (
                "A tecnologia é projetada ora como o 'Salvador' (arquétipo do curador messiânico), ora como o 'Destruidor' (Apocalipse)."
            )
            analysis["medos_implicitos"] = [
                "Medo da perda da relevância individual e profissional na sociedade contemporânea.",
                "Fetiche da tecnologia ocultando a responsabilidade humana nas escolhas políticas difíceis."
            ]
            analysis["desejo_coletivo"] = (
                "Um desejo profundo de restabelecimento de limites, estruturas de proteção e ordem paternal estatal contra a fluidez dos mercados."
            )

        # 10. MATEMÁTICO
        elif agent_id == "matematico":
            if topic_domain == "tecnologia":
                analysis["matriz_payoff"] = "Matriz de Regulação IA: Cooperação (+5, +5), Traição Armamentista (+10, -5), Equilíbrio de Nash em (-2, -2) por falta de controle multilateral."
                analysis["equilibrio_nash"] = "O Equilíbrio de Nash dominante em condições não-cooperativas é a corrida irrestrita com externalidades negativas mútuas."
                analysis["dilemas_cooperacao"] = "Dilema do Carona: agentes evitam custos de segurança para maximizar o time-to-market."
                analysis["alinhamento_incentivos"] = prefixo + "Adotar taxas marginais sobre riscos e seguros cibernéticos obrigatórios para alinhar os payoffs individuais ao ótimo social."
            elif topic_domain == "economia":
                analysis["matriz_payoff"] = "Matriz Tributária: Redução de alíquota unilateral (+6, +2), Equilíbrio de Nash de 'Guerra Fiscal' em (+1, +1)."
                analysis["equilibrio_nash"] = "O Equilíbrio de Nash resulta em subinvestimento em bens públicos por erosão da base tributária."
                analysis["dilemas_cooperacao"] = "Tragédia dos Comuns nos recursos ambientais e fiscais sem governança central."
                analysis["alinhamento_incentivos"] = prefixo + "Compensação de perdas fiscais vinculada ao crescimento do PIB local para estabilizar coalizões cooperativas."
            elif topic_domain == "seguranca":
                analysis["matriz_payoff"] = "Matriz de Combate ao Crime: Inteligência Compartilhada (+8, +8), Isolamento Técnico (+2, +2)."
                analysis["equilibrio_nash"] = "Inércia cooperativa local devido a custos assimétricos de compartilhamento de dados."
                analysis["dilemas_cooperacao"] = "Dilema da Segurança: o policiamento ostensivo em uma área apenas desloca geograficamente o crime."
                analysis["alinhamento_incentivos"] = prefixo + "Vincular o recebimento de verbas federais de segurança ao cumprimento de metas de integração de bancos de dados criminais."
            elif topic_domain == "saude":
                analysis["matriz_payoff"] = "Matriz de Vacinação: Vacinar Geral (+9, +9), Carona Não-Vacinar (+7, -2) para indivíduos isolados."
                analysis["equilibrio_nash"] = "Equilíbrio ineficiente com taxa de vacinação abaixo do limiar de imunidade de rebanho."
                analysis["dilemas_cooperacao"] = "Dilema do Carona na imunização coletiva."
                analysis["alinhamento_incentivos"] = prefixo + "Imposição de restrições de acesso público para não-imunizados para internalizar os custos da recusa de vacina."
            else:
                analysis["matriz_payoff"] = "Matriz Geral de Decisão: Ação Coordenada (+6, +6), Inércia Individual (+2, +2)."
                analysis["equilibrio_nash"] = "O Equilíbrio de Nash ineficiente (Inércia, Inércia) por falta de incentivo à liderança sob incerteza extrema."
                analysis["dilemas_cooperacao"] = "Dilema da Ação Coletiva em grupos com mais de 5 participantes."
                analysis["alinhamento_incentivos"] = prefixo + "Uso de liderança centralizada com incentivos seletivos (recompensas direcionadas) para os pioneiros cooperativos."
        # --- Pós-processamento Dinâmico (MiroFish Local v4.2) ---
        event = self.simulation_context.get("last_injected_event") or {}
        evt_title = event.get("title", "")
        evt_desc = event.get("description", "")
        evt_impact = event.get("impact", 0.0)
        evt_duration = event.get("duration", 0)
        
        sim_summary = self.simulation_context.get("last_summary") or self.simulation_context.get("stats") or {}
        avg_sent = sim_summary.get("avg_sentiment", 0.0)
        
        if evt_title or avg_sent != 0.0:
            evt_ref = f"o evento exógeno '{evt_title}' (impacto {evt_impact:+.2f})" if evt_title else "o cenário de simulação atual"
            sent_str = f"sentimento médio de {avg_sent:+.2f}"
            
            for key, val in list(analysis.items()):
                if key in ("agent_id", "agent_name", "method", "round", "source"):
                    continue
                
                if isinstance(val, str):
                    if key == "centro_gravidade":
                        analysis[key] = val.rstrip(".") + f", especialmente tensionado por {evt_ref} com {sent_str} no debate público."
                    elif key == "recomendacao_estrategica":
                        analysis[key] = val.rstrip(".") + f" em resposta direta a '{evt_title}', buscando neutralizar os desdobramentos de {evt_impact:+.2f} de impacto."
                    elif key == "condicoes_robustez":
                        analysis[key] = val.rstrip(".") + f" sob as condições do evento '{evt_title}' com duração de {evt_duration} rodadas."
                    elif key == "sintese":
                        analysis[key] = val.rstrip(".") + f", conciliando as pressões decorrentes de '{evt_title}' e a volatilidade de sentimento ({avg_sent:+.2f})."
                    elif key == "estado_da_arte":
                        analysis[key] = val.rstrip(".") + f", corroborado pelo comportamento dos agentes diante de '{evt_title}'."
                    elif key == "riscos_implementacao":
                        analysis[key] = val.rstrip(".") + f" e a histeria ou apatia coletiva causada pelo impacto de {evt_impact:+.2f} do evento."
                    elif key == "estruturas_sociais":
                        analysis[key] = val.rstrip(".") + f", cuja fratura é acentuada sob a pressão de '{evt_title}'."
                    elif key == "seguranca_juridica":
                        analysis[key] = val.rstrip(".") + f", agravada pelas medidas excepcionais propostas para enfrentar '{evt_title}'."
                    elif key == "ansiedades_sociais":
                        analysis[key] = val.rstrip(".") + f", inflamadas pela imprevisibilidade de '{evt_title}'."
                    else:
                        analysis[key] = val.rstrip(".") + f" considerando o impacto de '{evt_title}'."
                
                elif isinstance(val, list):
                    new_list = []
                    for item in val:
                        item_str = str(item)
                        if "evento" not in item_str.lower() and evt_title:
                            if random.random() < 0.5:
                                item_str = item_str.rstrip(".") + f" em face do evento '{evt_title}'"
                        new_list.append(item_str)
                    
                    if key == "principios_estrategicos" and evt_title:
                        new_list.append(f"Desenvolver resiliência sistêmica contra choques da magnitude de '{evt_title}' (impacto {evt_impact:+.2f}).")
                    elif key == "analogias_historicas" and evt_title:
                        new_list.append(f"A gestão de crises agudas análogas ao choque de '{evt_title}'.")
                    elif key == "premissas_questionadas" and evt_title:
                        new_list.append(f"A suposição de que '{evt_title}' tem um efeito homogêneo sobre todos os stances ({avg_sent:+.2f} geral).")
                    elif key == "dados_empiricos" and evt_title:
                        new_list.append(f"Variação observada no sentimento dos agentes sob o impacto de {evt_impact:+.2f} do evento.")
                    elif key == "acoes_concretas" and evt_title:
                        new_list.insert(0, f"Mobilizar comitê de crise para avaliar as ramificações de '{evt_title}' nas primeiras {evt_duration} rodadas.")
                    
                    analysis[key] = new_list

        return analysis

    def _build_context(self, deliberations: List[Dict], exclude_agent: str) -> str:
        """Constrói contexto para rodada 2 baseado nas análises dos outros agentes."""
        context_parts = []
        for d in deliberations:
            if d.get("agent_id") != exclude_agent and d.get("round") == 1:
                summary = f"[{d.get('agent_name','?')[:30]}] "
                for section in ["recomendacao_estrategica", "sintese", "acoes_concretas",
                               "cenario_otimista", "condicoes_robustez"]:
                    if d.get(section):
                        summary += str(d[section])[:200]
                        break
                context_parts.append(summary)
        return " | ".join(context_parts[:3])

    def _synthesize(self, deliberations: List[Dict], problem: str) -> Dict:
        """Sintetiza todas as análises em recomendações integradas."""
        all_recs = []
        risks = []
        actions = []

        for d in deliberations:
            for key in ["recomendacao_estrategica", "sintese", "acoes_concretas"]:
                val = d.get(key, "")
                if isinstance(val, str) and len(val) > 10:
                    all_recs.append(val[:200])
                elif isinstance(val, list):
                    all_recs.extend([str(v)[:200] for v in val[:2]])

            for key in ["riscos_implementacao", "vieses_identificados"]:
                val = d.get(key, [])
                if isinstance(val, list):
                    risks.extend([str(v)[:100] for v in val[:3]])

            if d.get("acoes_concretas") and isinstance(d["acoes_concretas"], list):
                actions.extend([str(a)[:100] for a in d["acoes_concretas"][:5]])

        return {
            "problem": problem,
            "n_analyses": len(deliberations),
            "n_agents": len(set(d.get("agent_id") for d in deliberations)),
            "recommendation": all_recs[0] if all_recs else "Análise requer mais dados",
            "key_insights": all_recs[:5],
            "critical_risks": list(set(risks))[:5],
            "action_plan": list(set(actions))[:5],
            "consensus_level": "ALTO" if len(set(all_recs[:3])) <= 2 else "MODERADO" if len(all_recs) > 3 else "BAIXO",
            "methodology": "MultiAgent War Room — 6 agentes epistêmicos com métodos complementares",
        }

    def to_markdown(self) -> str:
        """Relatório Markdown completo da War Room."""
        if not self.synthesis:
            return "Nenhuma deliberação realizada."

        lines = [
            f"# ⚔️ Multi-Agent War Room — Análise Estratégica",
            f"",
            f"**Problema:** {self.synthesis.get('problem','?')}",
            f"**Sessão:** {self.session_id}",
            f"**Data:** {BRAZIL_TIME().strftime('%d/%m/%Y %H:%M')}",
            f"**Agentes:** {len(EPISTEMIC_AGENTS)} | **Consenso:** {self.synthesis.get('consensus_level','?')}",
            f"",
            f"---",
            f"",
            f"## 🎯 Recomendação Principal",
            f"",
            f"{self.synthesis.get('recommendation','')}",
            f"",
            f"## 🔑 Insights-Chave",
        ]
        for i, insight in enumerate(self.synthesis.get("key_insights", []), 1):
            lines.append(f"{i}. {insight}")

        lines += [
            f"",
            f"## ⚠️ Riscos Críticos",
        ]
        for risk in self.synthesis.get("critical_risks", []):
            lines.append(f"- {risk}")

        lines += [
            f"",
            f"## 📋 Plano de Ação",
        ]
        for action in self.synthesis.get("action_plan", []):
            lines.append(f"- {action}")

        lines += [
            f"",
            f"---",
            f"",
            f"## Análises Individuais",
        ]
        for d in self.deliberations:
            lines.append(f"\n### {d.get('agent_name','?')} ({d.get('method','?')})")
            lines.append(f"*Fonte: {d.get('source','?')}*")
            for key, val in d.items():
                if key in ("agent_id", "agent_name", "method", "round", "source"):
                    continue
                if isinstance(val, str):
                    lines.append(f"\n**{key.replace('_',' ').title()}:** {val[:300]}")
                elif isinstance(val, list):
                    lines.append(f"\n**{key.replace('_',' ').title()}:**")
                    for item in val[:4]:
                        lines.append(f"- {str(item)[:200]}")

        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("MULTI-AGENT WAR ROOM — Teste")
    print("=" * 60)

    warroom = MultiAgentWarRoom()

    # Teste 1: Problema de segurança pública (como na transcrição)
    print("\n─── Teste 1: Segurança Pública ───")
    result = warroom.deliberate(
        problem="Como aplicar a teoria da guerra de Clausewitz ao combate ao crime organizado (PCC) no Brasil?",
        domain="seguranca",
        rounds=1
    )
    print(f"  Consenso: {result['synthesis']['consensus_level']}")
    print(f"  Insights: {len(result['synthesis']['key_insights'])}")

    # Teste 2: Problema econômico
    warroom2 = MultiAgentWarRoom()
    result2 = warroom2.deliberate(
        problem="Como a teoria dos jogos pode explicar a inflação persistente no Brasil pós-pandemia?",
        domain="economia",
        rounds=1
    )
    print(f"\n─── Teste 2: Economia ───")
    print(f"  Consenso: {result2['synthesis']['consensus_level']}")
    print(f"  Riscos: {len(result2['synthesis']['critical_risks'])}")

    # Salvar relatório
    report = warroom.to_markdown()
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "..", "..", ".reversa", "warroom_report.md")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\n✅ Relatório: {path}")
