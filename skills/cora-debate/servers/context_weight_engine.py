# =====================================================================
# CONTEXT WEIGHT ENGINE v1.0 — EVO-8
# Pesos flexíveis para ativação/desativação de verificadores Cora-Debate
# Baseado em: tema, lema, domínio, necessidade do usuário
# =====================================================================
"""
Arquitetura do Sistema de Pesos Contextuais:

┌──────────────────────────────────────────────────────────────────┐
│                   CONTEXT WEIGHT ENGINE                            │
│                                                                    │
│  INPUT: afirmação + tema_opcional + lema_opcional                  │
│     │                                                              │
│     ├── Classificador de Tema (keyword + embedding)                │
│     │   └── 9 domínios: matemática, física, estatística,           │
│     │       acadêmico, jurídico/LGPD, ética, computação,           │
│     │       engenharia, geral                                     │
│     │                                                              │
│     ├── Classificador de Lema (padrão estrutural)                  │
│     │   └── 6 tipos: afirmação_factual, demonstração,              │
│     │       hipótese, norma, dado_estatístico, definição           │
│     │                                                              │
│     ├── Perfil de Pesos (9 temas × 9 verificadores)                │
│     │   └── Cada verificador recebe peso 0.0-1.0                   │
│     │       0.0 = desativado | 0.5 = moderado | 1.0 = máximo       │
│     │                                                              │
│     └── OUTPUT: vetor de ativação [w1, w2, ..., w9]               │
│                                                                    │
│  INTEGRAÇÃO: Q-Score UCB1 usa pesos como prior para exploração    │
└──────────────────────────────────────────────────────────────────┘
"""

import re
import json
import math
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field

# =====================================================================
# Tipos de Dados
# =====================================================================

@dataclass
class VerifierWeight:
    """Peso de um verificador para um domínio específico."""
    verifier_id: str
    weight: float  # 0.0 (desativado) a 1.0 (peso máximo)
    active: bool   # Se False, verificador não executa
    reason: str    # Justificativa do peso

@dataclass
class DomainProfile:
    """Perfil de pesos para um domínio/tema."""
    domain_id: str
    domain_name: str
    description: str
    weights: Dict[str, VerifierWeight]  # V1..V9 → VerifierWeight
    total_active: int
    priority_verifiers: List[str]  # Ordem de prioridade

@dataclass
class ContextResult:
    """Resultado da classificação contextual."""
    domain: DomainProfile
    lemma_type: str
    confidence: float  # 0-1
    activation_vector: Dict[str, float]  # V1..V9 → weight
    active_verifiers: List[str]
    disabled_verifiers: List[str]
    reasoning: str

# =====================================================================
# Classificador de Tema (Keyword-based + Regras)
# =====================================================================

class ThemeClassifier:
    """Classifica o tema/domínio de uma afirmação para ativar o perfil correto."""

    # Palavras-chave por domínio (alta precisão)
    DOMAIN_KEYWORDS = {
        "matematica": [
            r'\b(?:teorema|prova|demonstra[çc][aã]o|lema|corol[áa]rio|axioma|conjectura)\b',
            r'\b(?:equa[çc][aã]o|fun[çc][aã]o|integral|derivada|limite|s[ée]rie|matriz|vetor)\b',
            r'\b(?:conjunto|grupo|anel|corpo|espa[çc]o\s+vetorial|topologia)\b',
            r'\b(?:n[uú]mero\s+(?:primo|real|complexo|inteiro|racional|irracional))\b',
            r'\b(?:sqrt|log|sen|cos|tan|exp|ln|lim|inf|sup|max|min)\b',
        ],
        "fisica": [
            r'\b(?:for[çc]a|massa|acelera[çc][aã]o|velocidade|energia|momento|trabalho)\b',
            r'\b(?:newton|joule|watt|pascal|hertz|ampere|volt|ohm|tesla|weber)\b',
            r'\b(?:termodin[aâ]mica|entropia|temperatura|press[aã]o|volume|calor)\b',
            r'\b(?:qu[aâ]ntic|relatividad|eletromagnet|mec[aâ]nica\s+(?:cl[aá]ssica|qu[aâ]ntica))\b',
            r'\b(?:F\s*=\s*m\s*\*?\s*a|E\s*=\s*m\s*\*?\s*c\^?2|F\s*=\s*G)\b',
        ],
        "estatistica": [
            r'\b(?:m[ée]dia|mediana|desvio\s+padr[aã]o|vari[aâ]ncia|correla[çc][aã]o)\b',
            r'\b(?:p[- ]?valor|signific[aâ]ncia|hip[óo]tese\s+(?:nula|alternativa))\b',
            r'\b(?:regress[aã]o|classifica[çc][aã]o|cluster|amostra|popula[çc][aã]o)\b',
            r'\b(?:shapiro|pearson|spearman|mann.whitney|wilcoxon|anova|qui.quadrado)\b',
            r'\b(?:bootstrap|intervalo\s+de\s+confian[çc]a|bayes|distribui[çc][aã]o)\b',
        ],
        "academico": [
            r'\b(?:artigo|disserta[çc][aã]o|tese|anteprojeto|monografia|paper)\b',
            r'\b(?:ABNT|DOI|refer[êe]ncia|bibliogr[aá]fica|cita[çc][aã]o|abstract)\b',
            r'\b(?:mestrado|doutorado|p[oó]s.gradua[çc][aã]o|orientador|banca)\b',
            r'\b(?:qualis|peri[oó]dico|CAPES|CNPq|FAPESP|PPGTE|UFC)\b',
            r'\b(?:palavras?.chave|resumo|introdu[çc][aã]o|metodologia|conclus[aã]o)\b',
        ],
        "juridico_lgpd": [
            r'\b(?:LGPD|Lei\s+(?:Geral|n[º°]\s*13\.?709)|prote[çc][aã]o\s+de\s+dados)\b',
            r'\b(?:titular|controlador|operador|DPO|encarregado|ANPD)\b',
            r'\b(?:consentimento|finalidade|necessidade|transpar[êe]ncia|seguran[çc]a)\b',
            r'\b(?:art\.?\s*\d+|inciso|caput|par[aá]grafo|al[íi]nea|revoga[çc][aã]o)\b',
            r'\b(?:san[çc][aã]o|multa|penalidade|infra[çc][aã]o|fiscaliza[çc][aã]o)\b',
        ],
        "etica_pesquisa": [
            r'\b(?:[ée]tica|pl[aá]gio|autoria|integridade\s+acad[êe]mica|m[aá]\s+conduta)\b',
            r'\b(?:TCLE|CEP|comit[êe]\s+de\s+[ée]tica|consentimento\s+(?:livre|esclarecido))\b',
            r'\b(?:Resolu[çc][aã]o\s+(?:PRPPG|CNS|CONEP)|n[º°]\s*(?:39|466|510))\b',
            r'\b(?:anonimato|anonimiza[çc][aã]o|pseudonimiza[çc][aã]o|confidencialidade)\b',
            r'\b(?:declara[çc][aã]o\s+de\s+(?:uso\s+de\s+)?IA|Anexo\s+IV)\b',
        ],
        "computacao": [
            r'\b(?:algoritmo|complexidade|O\(|NP|P=NP|Turing|aut[ôo]mato)\b',
            r'\b(?:compilador|interpretador|bytecode|assembly|kernel|driver)\b',
            r'\b(?:thread|processo|concorr[êe]ncia|paralelismo|deadlock|sem[aá]foro)\b',
            r'\b(?:hash|SHA|MD5|RSA|AES|criptografia|chave\s+(?:p[uú]blica|privada))\b',
        ],
        "engenharia": [
            r'\b(?:circuito|resistor|capacitor|indutor|transistor|diodo)\b',
            r'\b(?:estrutura|viga|pilar|laje|funda[çc][aã]o|concreto|a[çc]o)\b',
            r'\b(?:escoamento|vaz[aã]o|tubula[çc][aã]o|bomba|v[aá]lvula|press[aã]o)\b',
            r'\b(?:controle|realimenta[çc][aã]o|PID|estabilidade|fun[çc][aã]o\s+de\s+transfer[êe]ncia)\b',
        ],
        "geral": [
            r'.*',  # Fallback: qualquer coisa não classificada
        ],
    }

    # Prioridade de domínios (domínios mais específicos primeiro)
    DOMAIN_PRIORITY = [
        "fisica", "matematica", "estatistica", "juridico_lgpd",
        "etica_pesquisa", "academico", "computacao", "engenharia", "geral"
    ]

    @classmethod
    def classify(cls, text: str) -> Tuple[str, float, Dict[str, float]]:
        """
        Classifica o texto em um domínio.
        Retorna: (domain_id, confidence, scores_por_dominio)
        """
        text_lower = text.lower()
        scores = {}

        for domain in cls.DOMAIN_PRIORITY:
            if domain == "geral":
                continue
            score = 0.0
            for pattern in cls.DOMAIN_KEYWORDS[domain]:
                matches = re.findall(pattern, text_lower)
                # Pontuação: cada match único soma, múltiplos matches do mesmo padrão saturam
                unique_hits = len(set(re.findall(pattern, text_lower)))
                score += min(unique_hits * 0.15, 1.0)  # Satura em ~7 hits por padrão
            scores[domain] = min(score / max(len(cls.DOMAIN_KEYWORDS[domain]) * 0.1, 1.0), 1.0)

        # Seleciona o domínio de maior score
        if scores:
            best_domain = max(scores, key=scores.get)
            confidence = scores[best_domain]
        else:
            best_domain = "geral"
            confidence = 0.3

        # Se confiança for muito baixa, cai para geral
        if confidence < 0.15:
            best_domain = "geral"
            confidence = 0.3

        scores["geral"] = 0.3  # Sempre tem peso base
        return best_domain, confidence, scores

# =====================================================================
# Classificador de Lema (Tipo de Afirmação)
# =====================================================================

class LemmaClassifier:
    """Classifica o tipo de lema/afirmação para ajuste fino de pesos."""

    LEMMA_TYPES = {
        "afirmacao_factual": {
            "patterns": [
                r'\b(?:estudos?\s+(?:mostram|apontam|indicam|demonstram|sugerem))\b',
                r'\b(?:conforme|segundo|de\s+acordo\s+com)\b',
                r'\b(?:[eé]\s+(?:comprovado|demonstrado|sabido|conhecido|consenso))\b',
                r'\b(?:a\s+(?:literatura|pesquisa|ci[êe]ncia)\s+(?:mostra|indica|aponta))\b',
            ],
            "boost_verifiers": ["V7", "V8"],  # DOI + anonimato
            "suppress_verifiers": ["V2", "V3", "V6"],  # Não precisa de álgebra
        },
        "demonstracao": {
            "patterns": [
                r'\b(?:prova|demonstra[çc][aã]o|teorema|lema|corol[áa]rio)\b',
                r'\b(?:portanto|logo|consequentemente|donde\s+se\s+conclui)\b',
                r'\b(?:Q\.?E\.?D\.?|∎|□|■)\b',
                r'\b(?:por\s+(?:indu[çc][aã]o|contradi[çc][aã]o|redu[çc][aã]o))\b',
            ],
            "boost_verifiers": ["V2", "V3", "V6"],
            "suppress_verifiers": ["V7", "V8", "V9"],
        },
        "hipotese": {
            "patterns": [
                r'\b(?:hip[oó]tese|suponha|assuma|considere|seja)\b',
                r'\b(?:se\s+\.\.\.\s+ent[ãa]o|caso|no\s+caso\s+de)\b',
                r'\b(?:predi[çc][aã]o|previs[aã]o|proje[çc][aã]o|cen[áa]rio)\b',
            ],
            "boost_verifiers": ["V4", "V5"],
            "suppress_verifiers": ["V7"],
        },
        "norma": {
            "patterns": [
                r'\b(?:deve|n[aã]o\s+deve|[eé]\s+(?:obrigat[oó]rio|vedado|proibido|permitido))\b',
                r'\b(?:conforme\s+(?:a\s+)?(?:lei|norma|resolu[çc][aã]o|regulamento|edital))\b',
                r'\b(?:art\.?\s*\d+|inciso|caput|par[aá]grafo)\b',
                r'\b(?:em\s+conformidade|nos\s+termos|segundo\s+disp[oõ]e)\b',
            ],
            "boost_verifiers": ["V9"],
            "suppress_verifiers": ["V1", "V3", "V6"],
        },
        "dado_estatistico": {
            "patterns": [
                r'\b(?:m[ée]dia|mediana|percentil|desvio|vari[aâ]ncia|correla[çc][aã]o)\b',
                r'\b(?:p\s*[<>]\s*0?\.\d+|p\s*=\s*0?\.\d+|IC\s*95%)\b',
                r'\b(?:n\s*=\s*\d+|amostra\s+de\s+\d+|N\s*=\s*\d+)\b',
                r'\b(?:%\s*de|porcentagem|propor[çc][aã]o|taxa\s+de)\b',
            ],
            "boost_verifiers": ["V4", "V5", "V7"],
            "suppress_verifiers": ["V1", "V6"],
        },
        "definicao": {
            "patterns": [
                r'\b(?:define.se|entende.se|consiste|refere.se|[eé]\s+definido\s+como)\b',
                r'\b(?:conceito|defini[çc][aã]o|termo|significado|gloss[áa]rio)\b',
                r'\b(?:i\.?e\.?|isto\s+[eé]|ou\s+seja|em\s+outras\s+palavras)\b',
            ],
            "boost_verifiers": ["V2"],
            "suppress_verifiers": ["V4", "V5", "V7"],
        },
    }

    @classmethod
    def classify(cls, text: str) -> Tuple[str, float, Dict[str, float]]:
        """Classifica o tipo de lema e retorna ajustes de peso."""
        text_lower = text.lower()
        scores = {}

        for lemma_type, config in cls.LEMMA_TYPES.items():
            score = 0.0
            for pattern in config["patterns"]:
                if re.search(pattern, text_lower):
                    score += 1.0 / len(config["patterns"])
            scores[lemma_type] = min(score, 1.0)

        if scores:
            best = max(scores, key=scores.get)
            confidence = scores[best]
        else:
            best = "afirmacao_factual"
            confidence = 0.1

        if confidence < 0.2:
            best = "afirmacao_factual"
            confidence = 0.1

        return best, confidence, scores

    @classmethod
    def get_boosts(cls, lemma_type: str) -> Tuple[List[str], List[str]]:
        """Retorna quais verificadores impulsionar e quais suprimir."""
        config = cls.LEMMA_TYPES.get(lemma_type, {})
        return config.get("boost_verifiers", []), config.get("suppress_verifiers", [])

# =====================================================================
# Perfis de Domínio (Pesos Flexíveis)
# =====================================================================

class DomainProfiles:
    """Matriz de pesos: 9 domínios × 9 verificadores."""

    # Perfis pré-calibrados (EVO-8)
    # weight 0.0 = desativado | 0.3 = baixo | 0.5 = médio | 0.7 = alto | 1.0 = máximo

    PROFILES = {
        "matematica": {
            "V1": 0.1, "V2": 1.0, "V3": 0.9, "V4": 0.2,
            "V5": 0.7, "V6": 0.8, "V7": 0.1, "V8": 0.0, "V9": 0.0,
            "_description": "Álgebra, teoremas, demonstrações. Foco: V2+V3+V6.",
        },
        "fisica": {
            "V1": 1.0, "V2": 0.7, "V3": 0.4, "V4": 0.6,
            "V5": 0.8, "V6": 0.9, "V7": 0.3, "V8": 0.0, "V9": 0.0,
            "_description": "Análise dimensional, equações diferenciais. Foco: V1+V6+V5.",
        },
        "estatistica": {
            "V1": 0.0, "V2": 0.3, "V3": 0.4, "V4": 1.0,
            "V5": 0.6, "V6": 0.1, "V7": 0.5, "V8": 0.2, "V9": 0.2,
            "_description": "Testes de hipótese, correlação, bootstrap. Foco: V4+V5.",
        },
        "academico": {
            "V1": 0.0, "V2": 0.1, "V3": 0.1, "V4": 0.4,
            "V5": 0.2, "V6": 0.0, "V7": 1.0, "V8": 0.9, "V9": 0.9,
            "_description": "Anteprojetos, artigos, teses. Foco: V7+V8+V9.",
        },
        "juridico_lgpd": {
            "V1": 0.0, "V2": 0.1, "V3": 0.2, "V4": 0.1,
            "V5": 0.0, "V6": 0.0, "V7": 0.6, "V8": 0.7, "V9": 1.0,
            "_description": "Conformidade legal, LGPD, normativas. Foco: V9+V8.",
        },
        "etica_pesquisa": {
            "V1": 0.0, "V2": 0.0, "V3": 0.1, "V4": 0.2,
            "V5": 0.0, "V6": 0.0, "V7": 0.8, "V8": 0.95, "V9": 1.0,
            "_description": "Ética, plágio, anonimato, consentimento. Foco: V9+V8+V7.",
        },
        "computacao": {
            "V1": 0.0, "V2": 0.8, "V3": 0.7, "V4": 0.3,
            "V5": 0.9, "V6": 0.1, "V7": 0.4, "V8": 0.3, "V9": 0.1,
            "_description": "Algoritmos, complexidade, criptografia. Foco: V5+V2+V3.",
        },
        "engenharia": {
            "V1": 0.9, "V2": 0.6, "V3": 0.3, "V4": 0.5,
            "V5": 0.8, "V6": 0.7, "V7": 0.2, "V8": 0.0, "V9": 0.0,
            "_description": "Circuitos, estruturas, controle. Foco: V1+V5+V6.",
        },
        "geral": {
            "V1": 0.3, "V2": 0.3, "V3": 0.3, "V4": 0.3,
            "V5": 0.3, "V6": 0.1, "V7": 0.5, "V8": 0.4, "V9": 0.4,
            "_description": "Fallback: todos ativos com pesos balanceados.",
        },
    }

    @classmethod
    def get_profile(cls, domain_id: str) -> Dict[str, float]:
        """Retorna o perfil de pesos para um domínio."""
        profile = cls.PROFILES.get(domain_id, cls.PROFILES["geral"])
        return {k: v for k, v in profile.items() if not k.startswith("_")}

    @classmethod
    def get_description(cls, domain_id: str) -> str:
        return cls.PROFILES.get(domain_id, {}).get("_description", "Perfil geral")

    @classmethod
    def list_domains(cls) -> List[Dict[str, str]]:
        return [
            {"id": k, "description": v.get("_description", "")}
            for k, v in cls.PROFILES.items()
        ]

# =====================================================================
# Motor de Pesos Contextuais
# =====================================================================

class ContextWeightEngine:
    """
    Motor principal que orquestra a classificação de tema + lema
    e gera o vetor de ativação final para os verificadores.
    """

    def __init__(self):
        self.theme_classifier = ThemeClassifier()
        self.lemma_classifier = LemmaClassifier()
        self.profiles = DomainProfiles()
        self.threshold_active = 0.16  # Abaixo disso, verificador é desativado

    def compute(self, statement: str, domain_hint: Optional[str] = None,
                lemma_hint: Optional[str] = None) -> ContextResult:
        """
        Calcula o vetor de ativação para uma afirmação.
        
        Args:
            statement: Texto da afirmação a ser verificada
            domain_hint: Domínio sugerido pelo usuário (opcional, override)
            lemma_hint: Tipo de lema sugerido (opcional, override)
        
        Returns:
            ContextResult com vetor de ativação e metadados
        """
        # 1. Classificar domínio
        if domain_hint and domain_hint in self.profiles.PROFILES:
            domain_id = domain_hint
            domain_confidence = 1.0
            domain_scores = {domain_hint: 1.0}
        else:
            domain_id, domain_confidence, domain_scores = self.theme_classifier.classify(statement)

        # 2. Classificar tipo de lema
        if lemma_hint and lemma_hint in self.lemma_classifier.LEMMA_TYPES:
            lemma_type = lemma_hint
            lemma_confidence = 1.0
        else:
            lemma_type, lemma_confidence, _ = self.lemma_classifier.classify(statement)

        # 3. Obter perfil base de pesos
        base_weights = self.profiles.get_profile(domain_id)

        # 4. Aplicar ajustes de lema (boost/suppress)
        boost_list, suppress_list = self.lemma_classifier.get_boosts(lemma_type)
        adjusted_weights = dict(base_weights)

        for v_id in boost_list:
            if v_id in adjusted_weights:
                adjusted_weights[v_id] = min(adjusted_weights[v_id] * 1.5 + 0.15, 1.0)

        for v_id in suppress_list:
            if v_id in adjusted_weights:
                adjusted_weights[v_id] = max(adjusted_weights[v_id] * 0.3, 0.0)

        # 5. Determinar ativação
        active_verifiers = []
        disabled_verifiers = []
        for v_id, weight in adjusted_weights.items():
            if weight >= self.threshold_active:
                active_verifiers.append(v_id)
            else:
                disabled_verifiers.append(v_id)

        # 6. Construir raciocínio
        reasoning = (
            f"Domínio: {domain_id} (confiança: {domain_confidence:.2f}) | "
            f"Lema: {lemma_type} (confiança: {lemma_confidence:.2f}) | "
            f"Ativos: {len(active_verifiers)}/{len(adjusted_weights)} | "
            f"Desativados: {', '.join(disabled_verifiers) if disabled_verifiers else 'nenhum'} | "
            f"Boost: {', '.join(boost_list) if boost_list else 'nenhum'} | "
            f"Suppress: {', '.join(suppress_list) if suppress_list else 'nenhum'}"
        )

        return ContextResult(
            domain=DomainProfile(
                domain_id=domain_id,
                domain_name=domain_id.replace("_", " ").title(),
                description=self.profiles.get_description(domain_id),
                weights={},  # Preenchido via adjusted_weights
                total_active=len(active_verifiers),
                priority_verifiers=sorted(active_verifiers,
                    key=lambda v: adjusted_weights.get(v, 0), reverse=True),
            ),
            lemma_type=lemma_type,
            confidence=min(domain_confidence, lemma_confidence),
            activation_vector=adjusted_weights,
            active_verifiers=active_verifiers,
            disabled_verifiers=disabled_verifiers,
            reasoning=reasoning,
        )

    def compute_batch(self, statements: List[str],
                      domain_hint: Optional[str] = None) -> List[ContextResult]:
        """Calcula vetores de ativação para múltiplas afirmações."""
        return [self.compute(s, domain_hint=domain_hint) for s in statements]

    def get_domain_summary(self, domain_id: str) -> Dict[str, Any]:
        """Retorna resumo completo de um domínio."""
        weights = self.profiles.get_profile(domain_id)
        active = [v for v, w in weights.items() if w >= self.threshold_active]
        disabled = [v for v, w in weights.items() if w < self.threshold_active]
        return {
            "domain": domain_id,
            "description": self.profiles.get_description(domain_id),
            "weights": weights,
            "active_verifiers": active,
            "disabled_verifiers": disabled,
            "total_active": len(active),
            "total_disabled": len(disabled),
        }

# =====================================================================
# Integração com Q-Score UCB1
# =====================================================================

class ContextualQScore:
    """
    Extensão do Q-Score UCB1 com pesos contextuais.
    
    Q_i_contextual = Q_i_base * w_contextual + exploration_bonus
    onde w_contextual é o peso do verificador para este domínio/lema.
    """

    def __init__(self, engine: ContextWeightEngine):
        self.engine = engine
        self.q_scores: Dict[str, float] = {}  # Verificador → Q-Score acumulado
        self.n_selections: Dict[str, int] = {}  # Verificador → vezes selecionado
        self.total_selections = 0

    def select_verifier(self, statement: str, domain_hint: Optional[str] = None,
                        lemma_hint: Optional[str] = None,
                        exploration_weight: float = 2.0) -> Tuple[str, float, ContextResult]:
        """
        Seleciona o verificador ótimo usando UCB1 contextual.
        
        Returns: (verifier_id, q_score, context_result)
        """
        context = self.engine.compute(statement, domain_hint=domain_hint, lemma_hint=lemma_hint)
        weights = context.activation_vector

        best_v = None
        best_score = -float('inf')

        for v_id, w_ctx in weights.items():
            if w_ctx < self.engine.threshold_active:
                continue  # Verificador desativado para este contexto

            # Q-Score base (exploitation)
            q_base = self.q_scores.get(v_id, 0.5)

            # Bônus de exploração (UCB1)
            n_i = self.n_selections.get(v_id, 0)
            if n_i == 0:
                exploration_bonus = float('inf')  # Prioriza nunca usados
            else:
                exploration_bonus = math.sqrt(
                    exploration_weight * math.log(max(self.total_selections, 1)) / n_i
                )

            # Score contextual = base * peso_contextual + exploração
            contextual_score = q_base * w_ctx + exploration_bonus * 0.1

            if contextual_score > best_score:
                best_score = contextual_score
                best_v = v_id

        return best_v, best_score, context

    def update(self, verifier_id: str, reward: float):
        """Atualiza Q-Score após verificação."""
        self.total_selections += 1
        self.n_selections[verifier_id] = self.n_selections.get(verifier_id, 0) + 1
        n = self.n_selections[verifier_id]
        old_q = self.q_scores.get(verifier_id, 0.5)
        self.q_scores[verifier_id] = old_q + (reward - old_q) / n  # Média incremental

    def get_ranking(self) -> List[Tuple[str, float, int]]:
        """Retorna ranking de verificadores por Q-Score."""
        ranked = [(v, self.q_scores.get(v, 0.0), self.n_selections.get(v, 0))
                  for v in sorted(self.q_scores, key=lambda v: self.q_scores.get(v, 0), reverse=True)]
        return ranked

# =====================================================================
# Benchmark e Validação Exaustiva
# =====================================================================

class ContextBenchmark:
    """Benchmark para validação exaustiva do sistema de pesos contextuais."""

    TEST_CASES = [
        # (domain_hint, lemma_hint, statement, expected_top_verifier, expected_disabled)
        ("matematica", "demonstracao",
         "Prova: para todo n natural, n^2 + n é par. Demonstração por indução.",
         "V2", ["V7", "V8", "V9"]),
        ("fisica", None,
         "A força resultante F = m * a implica que a aceleração é proporcional à força aplicada.",
         "V1", ["V8", "V9"]),
        ("estatistica", "dado_estatistico",
         "A correlação entre horas de estudo e nota foi r=0.73, p<0.001, IC95% [0.65, 0.80].",
         "V4", ["V1", "V6"]),
        ("academico", "afirmacao_factual",
         "Estudos mostram que a IA melhora a produtividade acadêmica em 40%.",
         "V7", ["V1", "V2", "V3", "V6"]),
        ("juridico_lgpd", "norma",
         "O tratamento de dados pessoais deve ter consentimento explícito do titular, conforme Art. 7º da LGPD.",
         "V9", ["V1", "V2", "V3", "V4", "V5", "V6"]),
        ("etica_pesquisa", "norma",
         "Todo pesquisador deve declarar o uso de IA conforme Anexo IV do edital PPGTE/UFC.",
         "V9", ["V1", "V2", "V3", "V5", "V6"]),
        ("computacao", "demonstracao",
         "O algoritmo Quicksort tem complexidade média O(n log n) e pior caso O(n^2).",
         "V2", ["V1", "V7", "V8", "V9"]),  # demonstracao boost V6 de 0.1→0.3 mantendo ativo
        ("engenharia", "afirmacao_factual",
         "A tensão no resistor R1 é V = I * R = 0.002 * 1000 = 2.0V.",
         "V1", ["V8", "V9"]),
        # Sem hint: classificação automática (aceitar múltiplos domínios)
        (None, None,
         "Estudos mostram que a plataforma de IA multiagente melhora a produtividade científica.",
         "V7", ["V2", "V3", "V6"]),  # geral: V1=0.3 ativo, V2=0.3, V3=0.3 ativos
        (None, None,
         "Dados pessoais dos participantes serão processados localmente com consentimento via TCLE.",
         "V7", ["V1", "V2", "V3", "V4", "V5", "V6"]),  # juridico_lgpd + afirmacao_factual = V7 boosted
        (None, None,
         "A correlação de Pearson entre X e Y foi r=0.45 com bootstrap CI95% [0.30, 0.58].",
         "V4", ["V1", "V6"]),
    ]

    @classmethod
    def run(cls) -> Dict[str, Any]:
        """Executa benchmark completo."""
        engine = ContextWeightEngine()
        results = []
        passed = 0
        failed = 0

        for i, (domain_hint, lemma_hint, statement, expected_top, expected_disabled) in enumerate(cls.TEST_CASES):
            ctx = engine.compute(statement, domain_hint=domain_hint, lemma_hint=lemma_hint)

            # Verifica se o verificador top-1 está correto
            top_verifier = ctx.domain.priority_verifiers[0] if ctx.domain.priority_verifiers else None
            top_ok = top_verifier == expected_top

            # Verifica se os desativados esperados estão realmente desativados
            disabled_set = set(ctx.disabled_verifiers)
            expected_disabled_set = set(expected_disabled)
            disabled_ok = expected_disabled_set.issubset(disabled_set)

            test_ok = top_ok and disabled_ok
            if test_ok:
                passed += 1
            else:
                failed += 1

            results.append({
                "id": i + 1,
                "statement": statement[:100],
                "domain": ctx.domain.domain_id,
                "lemma": ctx.lemma_type,
                "top_verifier": top_verifier,
                "expected_top": expected_top,
                "top_ok": top_ok,
                "disabled": ctx.disabled_verifiers,
                "expected_disabled": expected_disabled,
                "disabled_ok": disabled_ok,
                "passed": test_ok,
                "confidence": ctx.confidence,
            })

        return {
            "total": len(results),
            "passed": passed,
            "failed": failed,
            "accuracy": passed / len(results) if results else 0,
            "results": results,
        }

# =====================================================================
# CLI Interativa
# =====================================================================

def interactive_demo():
    """Demonstração interativa do sistema de pesos contextuais."""
    print("=" * 70)
    print("CONTEXT WEIGHT ENGINE — Pesos Flexíveis Cora-Debate (EVO-8)")
    print("=" * 70)
    engine = ContextWeightEngine()

    # 1. Mostrar todos os perfis de domínio
    print("\n--- PERFIS DE DOMÍNIO DISPONÍVEIS ---")
    for domain in DomainProfiles.list_domains():
        summary = engine.get_domain_summary(domain["id"])
        print(f"\n  [{domain['id']}] {domain['description']}")
        print(f"  Ativos ({summary['total_active']}): {', '.join(summary['active_verifiers'])}")
        print(f"  Desativados ({summary['total_disabled']}): {', '.join(summary['disabled_verifiers'])}")
        weights_str = " | ".join(f"{v}={summary['weights'][v]:.1f}" for v in sorted(summary['weights']))
        print(f"  Pesos: {weights_str}")

    # 2. Executar benchmark
    print("\n--- BENCHMARK DE VALIDAÇÃO ---")
    bench = ContextBenchmark.run()
    print(f"  Total: {bench['total']} | Passou: {bench['passed']} | Falhou: {bench['failed']}")
    print(f"  Acurácia: {bench['accuracy']:.0%}")
    for r in bench["results"]:
        status = "✅" if r["passed"] else "❌"
        print(f"  {status} Teste {r['id']}: dom={r['domain']}, lema={r['lemma']}, "
              f"top={r['top_verifier']} (esperado={r['expected_top']}), "
              f"conf={r['confidence']:.2f}")

    # 3. Demonstração com Q-Score contextual
    print("\n--- Q-SCORE CONTEXTUAL (Simulação) ---")
    cq = ContextualQScore(engine)
    test_statements = [
        "A força F = m * a é a segunda lei de Newton.",
        "O teorema de Pitágoras estabelece que a^2 + b^2 = c^2.",
        "Estudos mostram que o OpenCode Ecosystem melhora a produtividade.",
        "Dados sensíveis devem ser anonimizados conforme LGPD Art. 11.",
    ]
    for stmt in test_statements:
        v_id, score, ctx = cq.select_verifier(stmt)
        cq.update(v_id, 0.8)  # Simula recompensa positiva
        print(f"  Afirmação: {stmt[:70]}...")
        print(f"  → Verificador: {v_id} | Score: {score:.3f} | Domínio: {ctx.domain.domain_id} | Lema: {ctx.lemma_type}")

    print(f"\n  Ranking Q-Score: {cq.get_ranking()}")

    print("\n" + "=" * 70)
    print("DEMONSTRAÇÃO CONCLUÍDA")
    print("=" * 70)

# =====================================================================
# Main
# =====================================================================

if __name__ == "__main__":
    import sys
    if "--demo" in sys.argv:
        interactive_demo()
    elif "--bench" in sys.argv:
        bench = ContextBenchmark.run()
        print(json.dumps(bench, indent=2, ensure_ascii=False))
    elif "--classify" in sys.argv and len(sys.argv) > 2:
        text = " ".join(sys.argv[2:])
        engine = ContextWeightEngine()
        ctx = engine.compute(text)
        print(f"Domínio: {ctx.domain.domain_id} ({ctx.domain.description})")
        print(f"Lema: {ctx.lemma_type}")
        print(f"Confiança: {ctx.confidence:.2f}")
        print(f"Ativos: {ctx.active_verifiers}")
        print(f"Desativados: {ctx.disabled_verifiers}")
        print(f"Pesos: {ctx.activation_vector}")
        print(f"Raciocínio: {ctx.reasoning}")
    elif "--profile" in sys.argv and len(sys.argv) > 2:
        domain = sys.argv[2]
        engine = ContextWeightEngine()
        summary = engine.get_domain_summary(domain)
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    else:
        print("Uso:")
        print("  python context_weight_engine.py --demo         # Demonstração completa")
        print("  python context_weight_engine.py --bench        # Benchmark de validação")
        print("  python context_weight_engine.py --classify ... # Classificar afirmação")
        print("  python context_weight_engine.py --profile X    # Ver perfil de domínio")
        interactive_demo()
