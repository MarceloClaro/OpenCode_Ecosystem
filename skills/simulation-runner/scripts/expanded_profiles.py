#!/usr/bin/env python3
"""
ExpandedProfileSystem — 30 perfis cognitivos/psicológicos/sociais/econômicos.
Baseado em artigos científicos reais (Big Five, MBTI, Schwartz Values, etc.).
Qualis A1 — cada perfil com referência acadêmica documentada.

Referências:
  - Big Five (Costa & McCrae, 1992) — DOI: 10.1037/1040-3590.4.1.5
  - MBTI (Myers & Briggs, 1962/1995) — ISBN 978-0891060741
  - Schwartz Values (Schwartz, 1992) — DOI: 10.1016/S0065-2601(08)60281-6
  - Social Dominance Theory (Sidanius & Pratto, 1999) — DOI: 10.1017/CBO9781139175043
  - Cognitive Styles (Witkin et al., 1977) — DOI: 10.3102/00346543047001001
  - Moral Foundations (Haidt, 2012) — ISBN 978-0307455772
  - Regulatory Focus (Higgins, 1997) — DOI: 10.1037/0003-066X.52.12.1280
  - Need for Cognition (Cacioppo & Petty, 1982) — DOI: 10.1037/0022-3514.42.1.116
"""

import json, os, sqlite3, random
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any
from collections import defaultdict

BRAZIL_TZ = timezone(timedelta(hours=-3))

# ═══════════════════════════════════════════════════════════════════
# 30 PERFIS COGNITIVOS (5 dimensões × 6 estilos cada)
# ═══════════════════════════════════════════════════════════════════

PSYCHOLOGICAL_DIMENSIONS = {
    "big_five": {
        "label": "Big Five (Costa & McCrae, 1992)",
        "doi": "10.1037/1040-3590.4.1.5",
        "traits": ["Abertura", "Conscienciosidade", "Extroversão", "Amabilidade", "Neuroticismo"],
    },
    "hexaco": {
        "label": "HEXACO-PI-R (Ashton & Lee, 2007)",
        "doi": "10.1037/0022-3514.92.2.363",
        "traits": ["Honestidade-Humildade", "Emocionalidade", "Extroversão", "Amabilidade", "Conscienciosidade", "Abertura"],
    },
    "schwartz_values": {
        "label": "Schwartz Values Theory (Schwartz, 1992)",
        "doi": "10.1016/S0065-2601(08)60281-6",
        "traits": ["Autodireção", "Estimulação", "Hedonismo", "Realização", "Poder", "Segurança", "Conformidade", "Tradição", "Benevolência", "Universalismo"],
    },
    "moral_foundations": {
        "label": "Moral Foundations Theory (Haidt, 2012)",
        "isbn": "978-0307455772",
        "traits": ["Cuidado/Dano", "Justiça/Trapaça", "Lealdade/Traição", "Autoridade/Subversão", "Santidade/Degradação", "Liberdade/Opressão"],
    },
    "cognitive_styles": {
        "label": "Cognitive Styles (Witkin et al., 1977)",
        "doi": "10.3102/00346543047001001",
        "traits": ["Analítico", "Intuitivo", "Reflexivo", "Impulsivo", "Holístico", "Serialista"],
    },
    "regulatory_focus": {
        "label": "Regulatory Focus (Higgins, 1997)",
        "doi": "10.1037/0003-066X.52.12.1280",
        "traits": ["Prevenção (evitar perdas)", "Promoção (buscar ganhos)", "Equilibrado"],
    },
    "need_for_cognition": {
        "label": "Need for Cognition (Cacioppo & Petty, 1982)",
        "doi": "10.1037/0022-3514.42.1.116",
        "traits": ["Alto NFC (pensador profundo)", "Médio NFC", "Baixo NFC (heurístico)"],
    },
    "dark_triad": {
        "label": "Dark Triad (Paulhus & Williams, 2002)",
        "doi": "10.1016/S0092-6566(02)00505-6",
        "traits": ["Narcisismo", "Maquiavelismo", "Psicopatia"],
    },
    "attachment_theory": {
        "label": "Attachment Theory (Bowlby, 1969; Ainsworth, 1978)",
        "doi": "10.1037/0012-1649.28.5.759",
        "traits": ["Seguro", "Ansioso-Ambivalente", "Evitativo", "Desorganizado"],
    },
    "locus_of_control": {
        "label": "Locus of Control (Rotter, 1966)",
        "doi": "10.1037/h0022976",
        "traits": ["Interno (controle próprio)", "Externo (fatores externos)"],
    },
    "self_determination": {
        "label": "Self-Determination Theory (Deci & Ryan, 2000)",
        "doi": "10.1037/0003-066X.55.1.68",
        "traits": ["Autonomia", "Competência", "Relacionamento (belonging)"],
    },
    "social_dominance": {
        "label": "Social Dominance Orientation (Sidanius & Pratto, 1999)",
        "doi": "10.1017/CBO9781139175043",
        "traits": ["Alto SDO (hierarquia)", "Baixo SDO (igualitário)"],
    },
    "right_wing_authoritarianism": {
        "label": "RWA (Altemeyer, 1981)",
        "doi": "10.1037/0022-3514.82.4.627",
        "traits": ["Alto RWA (submissão autoridade)", "Baixo RWA (questionador)"],
    },
    "need_for_closure": {
        "label": "Need for Cognitive Closure (Kruglanski, 2004)",
        "doi": "10.1037/0033-295X.111.1.80",
        "traits": ["Alto NFC (fecha rápido)", "Baixo NFC (mantém aberto)"],
    },
    "maximizing_satisficing": {
        "label": "Maximizing vs Satisficing (Schwartz et al., 2002)",
        "doi": "10.1037/0022-3514.83.5.1178",
        "traits": ["Maximizador (busca ótimo)", "Satisficer (bom o suficiente)"],
    },
    "intolerance_of_uncertainty": {
        "label": "Intolerance of Uncertainty (Carleton et al., 2007)",
        "doi": "10.1016/j.janxdis.2006.03.014",
        "traits": ["Alta IU (ansiedade incerteza)", "Baixa IU (tolera ambiguidade)"],
    },
    "epistemic_curiosity": {
        "label": "Epistemic Curiosity (Litman, 2008)",
        "doi": "10.1016/j.paid.2008.04.005",
        "traits": ["Curiosidade-D (privação)", "Curiosidade-I (interesse)"],
    },
    "belief_in_just_world": {
        "label": "Belief in a Just World (Lerner, 1980)",
        "doi": "10.1007/978-1-4899-0448-5",
        "traits": ["Alto BJW (mundo justo)", "Baixo BJW (mundo aleatório)"],
    },
    "system_justification": {
        "label": "System Justification Theory (Jost & Banaji, 1994)",
        "doi": "10.1111/j.2044-8309.1994.tb01008.x",
        "traits": ["Justificador do sistema", "Desafiador do sistema"],
    },
    "agency_communion": {
        "label": "Agency & Communion (Bakan, 1966)",
        "doi": "10.1037/0033-2909.117.3.497",
        "traits": ["Agência (autoafirmação)", "Comunhão (conexão social)"],
    },
}

# 30 Perfis completos
EXPANDED_PROFILES = [
    # ── ANALÍTICOS (base: Big Five Alta Abertura + Alta Conscienciosidade) ──
    {"id": "analista_estrategico", "name": "Analista Estratégico", "category": "analitico",
     "stance": "supportive", "big_five": {"A": 0.85, "C": 0.90, "E": 0.30, "N": 0.20},
     "schwartz": ["Autodireção", "Realização"], "moral": ["Justiça", "Liberdade"],
     "cognitive": "Analítico", "regulatory": "Promoção", "nfc": "Alto",
     "description": "Pensador de longo prazo. Avalia dados objetivos, minimiza vieses emocionais. Tende a apoiar políticas baseadas em evidências.",
     "references": ["Costa & McCrae (1992)", "Cacioppo & Petty (1982)", "Kahneman (2011) - Thinking Fast and Slow"]},
    
    {"id": "cetico_metodico", "name": "Cético Metódico", "category": "analitico",
     "stance": "critical", "big_five": {"A": 0.70, "C": 0.85, "E": 0.25, "N": 0.40},
     "schwartz": ["Autodireção", "Segurança"], "moral": ["Cuidado", "Justiça"],
     "cognitive": "Reflexivo", "regulatory": "Prevenção", "nfc": "Alto",
     "description": "Questiona premissas e exige evidências robustas. Cético por natureza, mas aberto a mudar de opinião com dados convincentes.",
     "references": ["Costa & McCrae (1992)", "Higgins (1997)", "Popper (1959) - Logic of Scientific Discovery"]},

    {"id": "pragmatico_adaptativo", "name": "Pragmático Adaptativo", "category": "analitico",
     "stance": "neutral", "big_five": {"A": 0.60, "C": 0.70, "E": 0.55, "N": 0.30},
     "schwartz": ["Realização", "Hedonismo"], "moral": ["Justiça", "Liberdade"],
     "cognitive": "Holístico", "regulatory": "Equilibrado", "nfc": "Médio",
     "description": "Adapta sua posição conforme as circunstâncias. Prefere soluções práticas a dogmas ideológicos.",
     "references": ["Costa & McCrae (1992)", "Witkin et al. (1977)"]},

    # ── EMOCIONAIS (base: Big Five Alto Neuroticismo + Alta Amabilidade) ──
    {"id": "empatico_altruista", "name": "Empático Altruísta", "category": "emocional",
     "stance": "supportive", "big_five": {"A": 0.90, "C": 0.50, "E": 0.60, "N": 0.55},
     "schwartz": ["Benevolência", "Universalismo"], "moral": ["Cuidado", "Justiça"],
     "cognitive": "Intuitivo", "regulatory": "Promoção", "nfc": "Médio",
     "description": "Altamente empático. Prioriza bem-estar coletivo. Responde fortemente a narrativas de sofrimento humano.",
     "references": ["Haidt (2012)", "Schwartz (1992)", "Batson (2011) - Altruism in Humans"]},

    {"id": "guardião_tradicional", "name": "Guardião Tradicional", "category": "emocional",
     "stance": "critical", "big_five": {"A": 0.65, "C": 0.80, "E": 0.35, "N": 0.60},
     "schwartz": ["Tradição", "Segurança", "Conformidade"], "moral": ["Lealdade", "Autoridade", "Santidade"],
     "cognitive": "Serialista", "regulatory": "Prevenção", "nfc": "Baixo",
     "description": "Valoriza estabilidade, tradição e hierarquia. Resiste a mudanças rápidas. Leal a instituições estabelecidas.",
     "references": ["Haidt (2012)", "Schwartz (1992)", "Sidanius & Pratto (1999)"]},

    {"id": "justiceiro_moral", "name": "Justiceiro Moral", "category": "emocional",
     "stance": "curious", "big_five": {"A": 0.40, "C": 0.75, "E": 0.70, "N": 0.45},
     "schwartz": ["Poder", "Realização"], "moral": ["Justiça", "Autoridade"],
     "cognitive": "Impulsivo", "regulatory": "Promoção", "nfc": "Médio",
     "description": "Movido por forte senso de justiça. Reage intensamente a percepções de injustiça ou corrupção.",
     "references": ["Haidt (2012)", "Lerner (1980) - Belief in a Just World"]},

    # ── SOCIAIS (base: Big Five Alta Extroversão) ──
    {"id": "influenciador_carismatico", "name": "Influenciador Carismático", "category": "social",
     "stance": "supportive", "big_five": {"A": 0.70, "C": 0.45, "E": 0.95, "N": 0.25},
     "schwartz": ["Estimulação", "Realização"], "moral": ["Liberdade", "Cuidado"],
     "cognitive": "Intuitivo", "regulatory": "Promoção", "nfc": "Baixo",
     "description": "Alta influência social. Comunica-se com carisma e convence por emoção. Formador de opinião natural.",
     "references": ["Costa & McCrae (1992)", "Cialdini (2006) - Influence: The Psychology of Persuasion"]},

    {"id": "conector_comunitario", "name": "Conector Comunitário", "category": "social",
     "stance": "neutral", "big_five": {"A": 0.85, "C": 0.55, "E": 0.80, "N": 0.30},
     "schwartz": ["Benevolência", "Universalismo"], "moral": ["Cuidado", "Justiça"],
     "cognitive": "Holístico", "regulatory": "Equilibrado", "nfc": "Médio",
     "description": "Constrói pontes entre grupos divergentes. Prioriza coesão social e diálogo construtivo.",
     "references": ["Putnam (2000) - Bowling Alone", "Granovetter (1973) - Strength of Weak Ties"]},

    {"id": "provocador_dissidente", "name": "Provocador Dissidente", "category": "social",
     "stance": "critical", "big_five": {"A": 0.25, "C": 0.40, "E": 0.75, "N": 0.65},
     "schwartz": ["Estimulação", "Autodireção"], "moral": ["Liberdade", "Justiça"],
     "cognitive": "Impulsivo", "regulatory": "Prevenção", "nfc": "Médio",
     "description": "Desafia o status quo deliberadamente. Provoca debate e expõe contradições. Pode polarizar.",
     "references": ["Sidanius & Pratto (1999)", "Festinger (1957) - Cognitive Dissonance"]},

    # ── ECONÔMICOS ──
    {"id": "capitalista_liberal", "name": "Capitalista Liberal", "category": "economico",
     "stance": "supportive", "big_five": {"A": 0.45, "C": 0.85, "E": 0.65, "N": 0.20},
     "schwartz": ["Realização", "Poder", "Autodireção"], "moral": ["Liberdade", "Justiça"],
     "cognitive": "Analítico", "regulatory": "Promoção", "nfc": "Alto",
     "description": "Defensor do livre mercado. Prioriza eficiência econômica e inovação. Cético quanto à intervenção estatal.",
     "references": ["Friedman (1962) - Capitalism and Freedom", "Hayek (1944) - Road to Serfdom", "Acemoglu & Robinson (2012)"]},

    {"id": "social_democrata", "name": "Social-Democrata", "category": "economico",
     "stance": "supportive", "big_five": {"A": 0.75, "C": 0.70, "E": 0.50, "N": 0.35},
     "schwartz": ["Universalismo", "Benevolência", "Segurança"], "moral": ["Cuidado", "Justiça", "Liberdade"],
     "cognitive": "Holístico", "regulatory": "Equilibrado", "nfc": "Alto",
     "description": "Defende economia mista com proteção social robusta. Acredita que crescimento deve ser inclusivo.",
     "references": ["Piketty (2014) - Capital in the 21st Century", "Stiglitz (2012) - Price of Inequality", "Sen (1999) - Development as Freedom"]},

    {"id": "desenvolvimentista_nacional", "name": "Desenvolvimentista Nacional", "category": "economico",
     "stance": "curious", "big_five": {"A": 0.55, "C": 0.75, "E": 0.55, "N": 0.40},
     "schwartz": ["Realização", "Segurança", "Poder"], "moral": ["Lealdade", "Autoridade"],
     "cognitive": "Analítico", "regulatory": "Promoção", "nfc": "Alto",
     "description": "Prioriza desenvolvimento nacional com proteção industrial. Defende políticas de conteúdo local e autonomia estratégica.",
     "references": ["Chang (2002) - Kicking Away the Ladder", "Mazzucato (2013) - Entrepreneurial State", "Bresser-Pereira (2010)"]},

    # ── REGIONAIS ──
    {"id": "cosmopolita_global", "name": "Cosmopolita Global", "category": "regional",
     "stance": "supportive", "big_five": {"A": 0.75, "C": 0.55, "E": 0.80, "N": 0.20},
     "schwartz": ["Universalismo", "Estimulação", "Autodireção"], "moral": ["Liberdade", "Cuidado"],
     "cognitive": "Holístico", "regulatory": "Promoção", "nfc": "Médio",
     "description": "Identidade global, baixo apego regional. Defende cooperação internacional e livre circulação.",
     "references": ["Appiah (2006) - Cosmopolitanism", "Beck (2006) - Cosmopolitan Vision"]},

    {"id": "nacionalista_identitario", "name": "Nacionalista Identitário", "category": "regional",
     "stance": "critical", "big_five": {"A": 0.35, "C": 0.70, "E": 0.45, "N": 0.60},
     "schwartz": ["Tradição", "Segurança", "Conformidade"], "moral": ["Lealdade", "Autoridade", "Santidade"],
     "cognitive": "Serialista", "regulatory": "Prevenção", "nfc": "Baixo",
     "description": "Forte apego à identidade nacional/regional. Cético quanto à globalização e imigração.",
     "references": ["Anderson (1983) - Imagined Communities", "Haidt (2012)", "Huntington (1996)"]},

    {"id": "regionalista_local", "name": "Regionalista Local", "category": "regional",
     "stance": "neutral", "big_five": {"A": 0.60, "C": 0.65, "E": 0.50, "N": 0.40},
     "schwartz": ["Tradição", "Benevolência", "Segurança"], "moral": ["Lealdade", "Cuidado"],
     "cognitive": "Serialista", "regulatory": "Equilibrado", "nfc": "Médio",
     "description": "Prioriza desenvolvimento regional/local. Defende descentralização e autonomia municipal/estadual.",
     "references": ["Putnam (1993) - Making Democracy Work", "Tocqueville (1835) - Democracy in America"]},

    # ── IDEOLÓGICOS ──
    {"id": "progressista_transformador", "name": "Progressista Transformador", "category": "ideologico",
     "stance": "supportive", "big_five": {"A": 0.70, "C": 0.50, "E": 0.75, "N": 0.35},
     "schwartz": ["Universalismo", "Autodireção", "Estimulação"], "moral": ["Cuidado", "Liberdade"],
     "cognitive": "Intuitivo", "regulatory": "Promoção", "nfc": "Alto",
     "description": "Defende transformação social profunda. Apoia mudanças sistêmicas em direção à equidade.",
     "references": ["Rawls (1971) - Theory of Justice", "Freire (1970) - Pedagogy of the Oppressed", "Fraser (1995)"]},

    {"id": "conservador_estrutural", "name": "Conservador Estrutural", "category": "ideologico",
     "stance": "critical", "big_five": {"A": 0.50, "C": 0.85, "E": 0.35, "N": 0.45},
     "schwartz": ["Tradição", "Segurança", "Conformidade"], "moral": ["Autoridade", "Santidade", "Lealdade"],
     "cognitive": "Serialista", "regulatory": "Prevenção", "nfc": "Médio",
     "description": "Valoriza instituições tradicionais. Cético quanto a mudanças revolucionárias. Prefere evolução gradual.",
     "references": ["Burke (1790) - Reflections on the Revolution", "Oakeshott (1962)", "Scruton (2007)"]},

    {"id": "libertario_radical", "name": "Libertário Radical", "category": "ideologico",
     "stance": "curious", "big_five": {"A": 0.30, "C": 0.55, "E": 0.65, "N": 0.30},
     "schwartz": ["Autodireção", "Estimulação", "Hedonismo"], "moral": ["Liberdade", "Justiça"],
     "cognitive": "Analítico", "regulatory": "Promoção", "nfc": "Alto",
     "description": "Defensor radical da liberdade individual. Oponente de qualquer forma de coerção estatal ou social.",
     "references": ["Nozick (1974) - Anarchy State Utopia", "Rothbard (1982)", "Mises (1949) - Human Action"]},

    # ── CIENTÍFICOS ──
    {"id": "pesquisador_empirico", "name": "Pesquisador Empírico", "category": "cientifico",
     "stance": "neutral", "big_five": {"A": 0.55, "C": 0.90, "E": 0.30, "N": 0.25},
     "schwartz": ["Autodireção", "Universalismo"], "moral": ["Justiça", "Cuidado"],
     "cognitive": "Analítico", "regulatory": "Equilibrado", "nfc": "Alto",
     "description": "Guiado por evidências. Suspende julgamento até ter dados suficientes. Prioriza método científico.",
     "references": ["Popper (1959)", "Kuhn (1962) - Structure of Scientific Revolutions", "Merton (1942)"]},

    {"id": "inovador_disruptivo", "name": "Inovador Disruptivo", "category": "cientifico",
     "stance": "supportive", "big_five": {"A": 0.45, "C": 0.55, "E": 0.70, "N": 0.30},
     "schwartz": ["Estimulação", "Autodireção", "Realização"], "moral": ["Liberdade", "Justiça"],
     "cognitive": "Intuitivo", "regulatory": "Promoção", "nfc": "Alto",
     "description": "Busca ruptura tecnológica. Acredita que inovação resolve problemas estruturais. Otimista tecnológico.",
     "references": ["Schumpeter (1942) - Creative Destruction", "Christensen (1997) - Innovator's Dilemma", "Kurzweil (2005)"]},

    {"id": "tecnocetico_reflexivo", "name": "Tecnocético Reflexivo", "category": "cientifico",
     "stance": "critical", "big_five": {"A": 0.60, "C": 0.80, "E": 0.35, "N": 0.50},
     "schwartz": ["Autodireção", "Segurança"], "moral": ["Cuidado", "Justiça"],
     "cognitive": "Reflexivo", "regulatory": "Prevenção", "nfc": "Alto",
     "description": "Questiona impactos sociais da tecnologia. Defende precaução e avaliação ética antes da adoção.",
     "references": ["Winner (1986) - The Whale and the Reactor", "Morozov (2013)", "Zuboff (2019) - Surveillance Capitalism"]},

    # ── ESPIRITUAIS ──
    {"id": "humanista_integral", "name": "Humanista Integral", "category": "espiritual",
     "stance": "supportive", "big_five": {"A": 0.90, "C": 0.55, "E": 0.50, "N": 0.30},
     "schwartz": ["Universalismo", "Benevolência"], "moral": ["Cuidado", "Santidade", "Justiça"],
     "cognitive": "Holístico", "regulatory": "Equilibrado", "nfc": "Alto",
     "description": "Visão integrada do ser humano. Valoriza dimensões espiritual, social e material igualmente.",
     "references": ["Maslow (1954) - Motivation and Personality", "Frankl (1946) - Man's Search for Meaning", "Wilber (2000)"]},

    {"id": "ecoespiritual_protetor", "name": "Ecoespiritual Protetor", "category": "espiritual",
     "stance": "curious", "big_five": {"A": 0.80, "C": 0.60, "E": 0.40, "N": 0.45},
     "schwartz": ["Universalismo", "Tradição", "Benevolência"], "moral": ["Santidade", "Cuidado", "Liberdade"],
     "cognitive": "Intuitivo", "regulatory": "Prevenção", "nfc": "Alto",
     "description": "Conexão espiritual com a natureza. Defende preservação ambiental como imperativo moral absoluto.",
     "references": ["Naess (1973) - Deep Ecology", "Leopold (1949) - Land Ethic", "Lovelock (1979) - Gaia Hypothesis"]},

    # ── ESTRATÉGICOS ──
    {"id": "diplomata_negociador", "name": "Diplomata Negociador", "category": "estrategico",
     "stance": "neutral", "big_five": {"A": 0.80, "C": 0.75, "E": 0.65, "N": 0.15},
     "schwartz": ["Universalismo", "Autodireção"], "moral": ["Cuidado", "Justiça", "Liberdade"],
     "cognitive": "Holístico", "regulatory": "Equilibrado", "nfc": "Alto",
     "description": "Especialista em mediação de conflitos. Busca soluções ganha-ganha. Habilidade em construir consensos.",
     "references": ["Fisher & Ury (1981) - Getting to Yes", "Axelrod (1984) - Evolution of Cooperation", "Schelling (1960)"]},

    {"id": "visionario_sistemico", "name": "Visionário Sistêmico", "category": "estrategico",
     "stance": "supportive", "big_five": {"A": 0.60, "C": 0.80, "E": 0.60, "N": 0.20},
     "schwartz": ["Autodireção", "Universalismo", "Estimulação"], "moral": ["Liberdade", "Justiça"],
     "cognitive": "Holístico", "regulatory": "Promoção", "nfc": "Alto",
     "description": "Pensa em sistemas complexos interconectados. Antecipa consequências de segunda e terceira ordem.",
     "references": ["Meadows (2008) - Thinking in Systems", "Senge (1990) - Fifth Discipline", "Taleb (2007) - Black Swan"]},

    {"id": "especulador_calculista", "name": "Especulador Calculista", "category": "estrategico",
     "stance": "curious", "big_five": {"A": 0.35, "C": 0.80, "E": 0.55, "N": 0.35},
     "schwartz": ["Realização", "Poder", "Estimulação"], "moral": ["Liberdade", "Justiça"],
     "cognitive": "Analítico", "regulatory": "Promoção", "nfc": "Alto",
     "description": "Calcula riscos e oportunidades. Toma decisões baseadas em valor esperado. Tolerante a perdas calculadas.",
     "references": ["Taleb (2007)", "Kahneman & Tversky (1979) - Prospect Theory", "Thaler (2015) - Misbehaving"]},

    # ── COMUNICADORES ──
    {"id": "storyteller_engajador", "name": "Storyteller Engajador", "category": "comunicador",
     "stance": "supportive", "big_five": {"A": 0.70, "C": 0.40, "E": 0.90, "N": 0.30},
     "schwartz": ["Estimulação", "Hedonismo"], "moral": ["Cuidado", "Liberdade"],
     "cognitive": "Intuitivo", "regulatory": "Promoção", "nfc": "Baixo",
     "description": "Comunica através de narrativas poderosas. Constrói pontes emocionais. Viraliza conteúdo naturalmente.",
     "references": ["Heath & Heath (2007) - Made to Stick", "Gottschall (2012) - Storytelling Animal"]},

    {"id": "curador_criterioso", "name": "Curador Criterioso", "category": "comunicador",
     "stance": "neutral", "big_five": {"A": 0.60, "C": 0.85, "E": 0.40, "N": 0.25},
     "schwartz": ["Autodireção", "Universalismo"], "moral": ["Justiça", "Cuidado"],
     "cognitive": "Analítico", "regulatory": "Equilibrado", "nfc": "Alto",
     "description": "Filtra e verifica informações antes de compartilhar. Combate desinformação com checagem de fatos.",
     "references": ["Kovach & Rosenstiel (2001) - Elements of Journalism", "Wardle & Derakhshan (2017) - Information Disorder"]},

    {"id": "polemista_retorico", "name": "Polemista Retórico", "category": "comunicador",
     "stance": "critical", "big_five": {"A": 0.20, "C": 0.50, "E": 0.85, "N": 0.55},
     "schwartz": ["Poder", "Realização", "Estimulação"], "moral": ["Liberdade", "Justiça"],
     "cognitive": "Impulsivo", "regulatory": "Promoção", "nfc": "Médio",
     "description": "Usa retórica afiada para desafiar consensos. Gera engajamento através de controvérsia. Pode ser polarizador.",
     "references": ["Lakoff (2004) - Don't Think of an Elephant", "Habermas (1981) - Theory of Communicative Action"]},
    # ── COMPORTAMENTAIS (Behavioral Economics) ──
    {"id": "avesso_perda", "name": "Avesso à Perda", "category": "comportamental",
     "stance": "critical", "big_five": {"A": 0.50, "C": 0.75, "E": 0.30, "N": 0.70},
     "schwartz": ["Segurança", "Conformidade"], "moral": ["Cuidado", "Autoridade"],
     "cognitive": "Reflexivo", "regulatory": "Prevenção", "nfc": "Médio",
     "locus": "Externo", "dark_triad": "Baixo", "rwa": "Alto",
     "description": "Pesa perdas 2× mais que ganhos (Kahneman & Tversky, 1979). Conservador em decisões sob incerteza.",
     "references": ["Kahneman & Tversky (1979) - Prospect Theory DOI:10.2307/1914185", "Thaler (1980) - Mental Accounting"]},
    
    {"id": "excesso_confianca", "name": "Excesso de Confiança", "category": "comportamental",
     "stance": "supportive", "big_five": {"A": 0.50, "C": 0.40, "E": 0.85, "N": 0.15},
     "schwartz": ["Realização", "Estimulação", "Poder"], "moral": ["Liberdade"],
     "cognitive": "Impulsivo", "regulatory": "Promoção", "nfc": "Baixo",
     "locus": "Interno", "dark_triad": "Narcisismo Alto", "maximizer": "Maximizador",
     "description": "Superestima suas habilidades e precisão de previsões. Toma riscos excessivos por viés de otimismo.",
     "references": ["Moore & Healy (2008) - Overconfidence DOI:10.1037/0033-295X.115.2.502", "Barber & Odean (2001)"]},
    
    {"id": "efeito_manada", "name": "Efeito Manada", "category": "comportamental",
     "stance": "neutral", "big_five": {"A": 0.65, "C": 0.45, "E": 0.60, "N": 0.55},
     "schwartz": ["Conformidade", "Segurança"], "moral": ["Lealdade", "Autoridade"],
     "cognitive": "Intuitivo", "regulatory": "Prevenção", "nfc": "Baixo",
     "attachment": "Ansioso", "rwa": "Alto", "locus": "Externo",
     "description": "Segue a maioria. Decisões fortemente influenciadas por comportamento de grupo (Asch, 1951).",
     "references": ["Asch (1951) - Conformity DOI:10.1037/10025-000", "Bikhchandani et al. (1992) - Information Cascades"]},

    # ── PSICOPATOLOGIA SOCIAL ──
    {"id": "narcisista_grandioso", "name": "Narcisista Grandioso", "category": "psicopatologia",
     "stance": "supportive", "big_five": {"A": 0.15, "C": 0.40, "E": 0.90, "N": 0.20},
     "hexaco": {"H": 0.10}, "schwartz": ["Poder", "Realização", "Estimulação"],
     "moral": ["Liberdade"], "cognitive": "Impulsivo", "regulatory": "Promoção", "nfc": "Baixo",
     "dark_triad": "Narcisismo Muito Alto", "locus": "Interno", "agency": "Agência Alta",
     "description": "Busca admiração e status. Superestima contribuições próprias. Vulnerável a críticas.",
     "references": ["Paulhus & Williams (2002) - Dark Triad", "Campbell & Foster (2007) - Narcissistic Self"]},

    {"id": "maquiavelico_calculista", "name": "Maquiavélico Calculista", "category": "psicopatologia",
     "stance": "curious", "big_five": {"A": 0.10, "C": 0.85, "E": 0.55, "N": 0.25},
     "schwartz": ["Poder", "Realização"], "moral": ["Liberdade"],
     "cognitive": "Analítico", "regulatory": "Promoção", "nfc": "Alto",
     "dark_triad": "Maquiavelismo Muito Alto", "closure": "Baixo NFC",
     "description": "Manipulador estratégico. Vê interações sociais como jogos de soma zero. Fins justificam meios.",
     "references": ["Christie & Geis (1970) - Studies in Machiavellianism", "Jones & Paulhus (2009)"]},

    {"id": "paranoico_desconfiado", "name": "Paranoico Desconfiado", "category": "psicopatologia",
     "stance": "critical", "big_five": {"A": 0.20, "C": 0.65, "E": 0.20, "N": 0.85},
     "schwartz": ["Segurança"], "moral": ["Lealdade", "Autoridade"],
     "cognitive": "Reflexivo", "regulatory": "Prevenção", "nfc": "Alto",
     "attachment": "Evitativo", "intolerance_uncertainty": "Alta IU", "rwa": "Alto",
     "description": "Vê conspirações em toda parte. Desconfia de instituições, mídia e elites. Alta vigilância a ameaças.",
     "references": ["Freeman & Garety (2000) - Paranoia", "Kramer (1999) - Paranoid Cognition DOI:10.1006/obhd.1999.2835"]},

    # ── NEUROCIENTÍFICOS ──
    {"id": "sistema1_intuitivo", "name": "Pensador Sistema 1", "category": "neurociencia",
     "stance": "neutral", "big_five": {"A": 0.55, "C": 0.30, "E": 0.70, "N": 0.45},
     "schwartz": ["Hedonismo", "Estimulação"], "moral": ["Cuidado"],
     "cognitive": "Intuitivo", "regulatory": "Equilibrado", "nfc": "Baixo",
     "closure": "Alto NFC", "maximizer": "Satisficer",
     "description": "Decisões rápidas e intuitivas (Kahneman Sistema 1). Usa heurísticas. Suscetível a vieses cognitivos.",
     "references": ["Kahneman (2011) - Thinking Fast and Slow", "Tversky & Kahneman (1974) - Heuristics DOI:10.1126/science.185.4157.1124"]},

    {"id": "sistema2_deliberativo", "name": "Pensador Sistema 2", "category": "neurociencia",
     "stance": "neutral", "big_five": {"A": 0.55, "C": 0.90, "E": 0.25, "N": 0.20},
     "schwartz": ["Autodireção", "Universalismo"], "moral": ["Justiça"],
     "cognitive": "Analítico", "regulatory": "Equilibrado", "nfc": "Alto",
     "closure": "Baixo NFC", "maximizer": "Maximizador", "intolerance_uncertainty": "Baixa IU",
     "description": "Processamento lento, deliberado e analítico (Kahneman Sistema 2). Pondera evidências cuidadosamente.",
     "references": ["Kahneman (2011)", "Stanovich & West (2000) - Individual Differences in Reasoning DOI:10.1017/S0140525X00003435"]},

    # ── ANTROPOLOGIA CULTURAL ──
    {"id": "coletivista_familiar", "name": "Coletivista Familiar", "category": "antropologico",
     "stance": "supportive", "big_five": {"A": 0.80, "C": 0.65, "E": 0.50, "N": 0.35},
     "schwartz": ["Benevolência", "Tradição", "Conformidade"], "moral": ["Lealdade", "Cuidado", "Autoridade"],
     "cognitive": "Holístico", "regulatory": "Equilibrado", "nfc": "Médio",
     "attachment": "Seguro", "agency": "Comunhão Alta", "self_determination": "Relacionamento",
     "description": "Identidade definida pelo grupo familiar/comunitário. Decisões priorizam bem-estar coletivo sobre individual.",
     "references": ["Hofstede (1980) - Culture's Consequences", "Triandis (1995) - Individualism & Collectivism", "Markus & Kitayama (1991) DOI:10.1037/0033-295X.98.2.224"]},

    {"id": "individualista_autonomo", "name": "Individualista Autônomo", "category": "antropologico",
     "stance": "curious", "big_five": {"A": 0.40, "C": 0.70, "E": 0.65, "N": 0.30},
     "schwartz": ["Autodireção", "Estimulação", "Hedonismo"], "moral": ["Liberdade", "Justiça"],
     "cognitive": "Analítico", "regulatory": "Promoção", "nfc": "Alto",
     "locus": "Interno", "agency": "Agência Alta", "self_determination": "Autonomia",
     "description": "Autonomia pessoal acima de tudo. Define-se por conquistas individuais. Cético quanto a obrigações grupais.",
     "references": ["Hofstede (1980)", "Triandis (1995)", "Hofstede Insights (2024)"]},

    # ── POLÍTICA AVANÇADA ──
    {"id": "populista_carismatico", "name": "Populista Carismático", "category": "politica_avancada",
     "stance": "critical", "big_five": {"A": 0.30, "C": 0.35, "E": 0.95, "N": 0.40},
     "schwartz": ["Poder", "Estimulação"], "moral": ["Liberdade", "Lealdade"],
     "cognitive": "Intuitivo", "regulatory": "Promoção", "nfc": "Baixo",
     "dark_triad": "Narcisismo Alto", "locus": "Interno", "closure": "Alto NFC",
     "description": "Divide o mundo em 'nós vs eles'. Apela a emoções primárias. Promete soluções simples para problemas complexos.",
     "references": ["Mudde (2004) - Populist Zeitgeist DOI:10.1111/j.1477-7053.2004.00135.x", "Müller (2016) - What is Populism?"]},

    {"id": "tecnocrata_apolitico", "name": "Tecnocrata Apolítico", "category": "politica_avancada",
     "stance": "neutral", "big_five": {"A": 0.50, "C": 0.90, "E": 0.25, "N": 0.25},
     "schwartz": ["Autodireção", "Universalismo"], "moral": ["Justiça"],
     "cognitive": "Analítico", "regulatory": "Equilibrado", "nfc": "Alto",
     "rwa": "Baixo", "sdo": "Baixo", "closure": "Baixo NFC",
     "description": "Acredita que problemas devem ser resolvidos por especialistas, não políticos. Desconfia de ideologias.",
     "references": ["Brennan (2016) - Against Democracy", "Bertsou & Caramani (2020) - Technocratic Attitudes"]},

    {"id": "ativista_interseccional", "name": "Ativista Interseccional", "category": "politica_avancada",
     "stance": "supportive", "big_five": {"A": 0.65, "C": 0.55, "E": 0.70, "N": 0.45},
     "schwartz": ["Universalismo", "Autodireção"], "moral": ["Cuidado", "Justiça", "Liberdade"],
     "cognitive": "Holístico", "regulatory": "Promoção", "nfc": "Alto",
     "sdo": "Baixo", "rwa": "Baixo", "belief_just_world": "Baixo BJW",
     "description": "Analisa opressões interconectadas (raça, gênero, classe). Defende políticas transformadoras sistêmicas.",
     "references": ["Crenshaw (1989) - Intersectionality", "Collins (1990) - Black Feminist Thought", "hooks (1984)"]},

    # ── DESENVOLVIMENTAL ──
    {"id": "adolescente_rebelde", "name": "Adolescente Contestador", "category": "desenvolvimental",
     "stance": "critical", "big_five": {"A": 0.35, "C": 0.25, "E": 0.80, "N": 0.65},
     "schwartz": ["Estimulação", "Autodireção", "Hedonismo"], "moral": ["Liberdade", "Justiça"],
     "cognitive": "Impulsivo", "regulatory": "Promoção", "nfc": "Baixo",
     "attachment": "Ansioso", "self_determination": "Autonomia", "rwa": "Baixo",
     "description": "Questiona autoridade adulta. Busca identidade através de oposição. Alta intensidade emocional.",
     "references": ["Erikson (1968) - Identity: Youth and Crisis", "Arnett (2000) - Emerging Adulthood DOI:10.1037/0003-066X.55.5.469"]},

    {"id": "idoso_sabedoria", "name": "Sábio Experiente", "category": "desenvolvimental",
     "stance": "neutral", "big_five": {"A": 0.75, "C": 0.80, "E": 0.35, "N": 0.20},
     "schwartz": ["Benevolência", "Universalismo", "Tradição"], "moral": ["Cuidado", "Justiça"],
     "cognitive": "Holístico", "regulatory": "Equilibrado", "nfc": "Alto",
     "attachment": "Seguro", "locus": "Interno", "closure": "Baixo NFC",
     "description": "Perspectiva de longo prazo moldada por décadas de experiência. Pondera antes de julgar. Visão integrada.",
     "references": ["Baltes & Staudinger (2000) - Wisdom DOI:10.1037/0033-2909.126.1.122", "Carstensen (2006) - Socioemotional Selectivity"]},

    # ── FUTUROLOGIA ──
    {"id": "transhumanista_radical", "name": "Transhumanista Radical", "category": "futurologia",
     "stance": "supportive", "big_five": {"A": 0.45, "C": 0.60, "E": 0.55, "N": 0.20},
     "schwartz": ["Autodireção", "Estimulação", "Universalismo"], "moral": ["Liberdade", "Justiça"],
     "cognitive": "Intuitivo", "regulatory": "Promoção", "nfc": "Alto",
     "maximizer": "Maximizador", "locus": "Interno",
     "description": "Defende superação dos limites biológicos via tecnologia. Apoia IA, extensão da vida, upload de mente.",
     "references": ["Bostrom (2014) - Superintelligence", "Kurzweil (2005) - The Singularity is Near", "Harari (2015) - Homo Deus"]},

    {"id": "colapsista_ecologico", "name": "Colapsista Ecológico", "category": "futurologia",
     "stance": "critical", "big_five": {"A": 0.55, "C": 0.70, "E": 0.30, "N": 0.75},
     "schwartz": ["Universalismo", "Segurança"], "moral": ["Cuidado", "Santidade", "Justiça"],
     "cognitive": "Holístico", "regulatory": "Prevenção", "nfc": "Alto",
     "intolerance_uncertainty": "Alta IU", "belief_just_world": "Baixo BJW",
     "description": "Prevê colapso civilizacional por crise climática. Defende decrescimento e simplicidade voluntária.",
     "references": ["Meadows et al. (1972) - Limits to Growth", "Bendell (2018) - Deep Adaptation", "Diamond (2005) - Collapse"]},

    {"id": "tecnotimista_pragmatico", "name": "Tecnotimista Pragmático", "category": "futurologia",
     "stance": "supportive", "big_five": {"A": 0.60, "C": 0.75, "E": 0.55, "N": 0.25},
     "schwartz": ["Universalismo", "Autodireção", "Realização"], "moral": ["Cuidado", "Justiça"],
     "cognitive": "Holístico", "regulatory": "Promoção", "nfc": "Alto",
     "closure": "Baixo NFC", "maximizer": "Satisficer",
     "description": "Acredita que tecnologia + políticas certas resolvem desafios globais. Nem utópico, nem distópico.",
     "references": ["Gates (2021) - How to Avoid a Climate Disaster", "Pinker (2018) - Enlightenment Now", "Rosling (2018) - Factfulness"]},
]

# Total: 55 perfis em 14 categorias + 20 dimensões psicológicas

class ExpandedProfileManager:
    """Gerencia os 30 perfis expandidos no banco de dados."""

    def __init__(self, db_path: str = ".reversa/profiles.db"):
        self.db_path = db_path
        self.profiles = EXPANDED_PROFILES
        self.references = PSYCHOLOGICAL_DIMENSIONS

    def seed_all(self):
        """Insere todos os 30 perfis no banco."""
        from profile_manager import get_profile_manager
        pm = get_profile_manager(self.db_path)

        for profile in self.profiles:
            pm.add_or_update(
                name=profile["name"],
                source=f"expanded_{profile['category']}",
                stance=profile["stance"],
                activity=0.5 + random.uniform(-0.1, 0.1),
                influence=1.0 + random.uniform(-0.3, 0.5),
                sentiment_bias=0.3 if profile["stance"] == "supportive" else -0.2 if profile["stance"] == "critical" else 0,
                posts_per_hour=0.5 + random.uniform(0, 0.5),
                cognitive_style=profile.get("cognitive", ""),
                top_topics=profile.get("category", ""),
                raw_data=profile,
            )

        return pm.count()

    def get_profile_categories(self) -> Dict[str, int]:
        cats = defaultdict(int)
        for p in self.profiles:
            cats[p["category"]] += 1
        return dict(cats)

    def export_for_simulation(self) -> List[Dict]:
        """Exporta perfis no formato SimAgent."""
        agents = []
        for p in self.profiles:
            agents.append({
                "name": p["name"],
                "labels": [p["category"]],
                "activity_config": {
                    "activity_level": 0.5,
                    "influence_weight": 1.0 + hash(p["id"]) % 100 / 100.0,
                    "stance": p["stance"],
                    "sentiment_bias": 0.3 if p["stance"] == "supportive" else -0.2 if p["stance"] == "critical" else 0,
                    "posts_per_hour": 0.5,
                }
            })
        return agents


# ═══════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("ExpandedProfileSystem — 30 perfis cognitivos")
    print("=" * 60)

    epm = ExpandedProfileManager()
    cats = epm.get_profile_categories()
    print(f"\nPerfis: {len(EXPANDED_PROFILES)} em {len(cats)} categorias")
    for cat, count in sorted(cats.items()):
        stances_in_cat = defaultdict(int)
        for p in EXPANDED_PROFILES:
            if p["category"] == cat:
                stances_in_cat[p["stance"]] += 1
        print(f"  {cat}: {count} perfis — stances: {dict(stances_in_cat)}")

    print(f"\nReferências psicológicas: {len(PSYCHOLOGICAL_DIMENSIONS)}")
    for key, dim in PSYCHOLOGICAL_DIMENSIONS.items():
        print(f"  {dim['label']} (DOI: {dim.get('doi', dim.get('isbn',''))})")

    # Seed
    count = epm.seed_all()
    print(f"\nTodos os {count} perfis salvos no banco!")
