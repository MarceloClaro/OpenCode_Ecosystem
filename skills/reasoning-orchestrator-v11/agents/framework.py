# =====================================================================
# REASONING AGENT FRAMEWORK v2.1
# Base class for all 208 reasoning types across 26 categories
# =====================================================================
# Each agent implements a specific reasoning type (R01-R208)
# and participates in the ReasoningOrchestrator v11 pipeline
# =====================================================================
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional
from enum import Enum
import json, time

class AgentStatus(Enum):
    IDLE = "idle"
    REASONING = "reasoning"
    VERIFIED = "verified"
    CONTRADICTED = "contradicted"
    FAILED = "failed"

class Confidence(Enum):
    HIGH = "high"       # > 0.90
    MEDIUM = "medium"   # 0.60-0.90
    LOW = "low"         # < 0.60
    UNKNOWN = "unknown"

@dataclass
class ReasoningResult:
    agent_id: str
    reasoning_type: str   # R01-R68
    category: str         # I-XII
    conclusion: str
    confidence: float     # 0.0-1.0
    evidence: list = field(default_factory=list)
    depends_on: list = field(default_factory=list)  # other agent results needed
    counterexamples: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%S"))

@dataclass
class LemmaNode:
    id: str
    statement: str
    agent_id: str
    status: AgentStatus = AgentStatus.IDLE
    result: Optional[ReasoningResult] = None
    children: list = field(default_factory=list)  # lemmas that depend on this one
    parents: list = field(default_factory=list)   # lemmas this one depends on

class ReasoningAgent(ABC):
    """Base class for all reasoning agents in the OpenCode ecosystem.
    
    Each agent implements ONE reasoning type (R01-R68).
    Agents are stateless and can be composed into pipelines.
    """
    
    def __init__(self, agent_id: str, reasoning_type: str, category: str):
        self.agent_id = agent_id
        self.reasoning_type = reasoning_type
        self.category = category
        self.status = AgentStatus.IDLE
        self.history: list[ReasoningResult] = []
    
    @abstractmethod
    def reason(self, context: dict) -> ReasoningResult:
        """Execute the reasoning process for this agent.
        
        Args:
            context: Dictionary containing problem statement, previous results,
                     lemma graph state, and any domain-specific data.
        
        Returns:
            ReasoningResult with conclusion, confidence, evidence, and warnings.
        """
        pass
    
    def validate_dependencies(self, context: dict) -> bool:
        """Check if all dependencies (other agents' results) are satisfied."""
        deps = self.get_dependencies()
        for dep in deps:
            if dep not in context.get("agent_results", {}):
                self.warn(f"Dependency not satisfied: {dep}")
                return False
            result = context["agent_results"][dep]
            if result.confidence < 0.5:
                self.warn(f"Dependency low confidence: {dep} ({result.confidence:.2f})")
                return False
        return True
    
    @abstractmethod
    def get_dependencies(self) -> list[str]:
        """Return list of agent_ids this agent depends on."""
        return []
    
    def warn(self, message: str):
        print(f"[{self.agent_id}] WARNING: {message}")
    
    def __repr__(self):
        return f"{self.agent_id}({self.reasoning_type}, {self.category})"


# =====================================================================
# REGISTRY: All 68 reasoning types mapped to agent classes
# =====================================================================

REASONING_REGISTRY = {
    # Category I: Foundational
    "R01": {"name": "Definicional", "category": "I", "domain": "all"},
    "R02": {"name": "Abstrativo", "category": "I", "domain": "all"},
    "R03": {"name": "Notacional", "category": "I", "domain": "all"},
    "R04": {"name": "Tradutivo", "category": "I", "domain": "all"},
    "R05": {"name": "Decomposicional", "category": "I", "domain": "all"},
    
    # Category II: Deductive
    "R06": {"name": "Silogistico", "category": "II", "domain": "mathematics"},
    "R07": {"name": "Dedutivo-Natural", "category": "II", "domain": "mathematics"},
    "R08": {"name": "Implicativo", "category": "II", "domain": "mathematics"},
    "R09": {"name": "Quantificacional", "category": "II", "domain": "mathematics"},
    "R10": {"name": "Modular", "category": "II", "domain": "all"},
    "R11": {"name": "Encadeamento-Reverso", "category": "II", "domain": "mathematics"},
    
    # Category III: Inductive/Reductive
    "R12": {"name": "Indutivo-Matematico", "category": "III", "domain": "mathematics"},
    "R13": {"name": "Redutivo-Estrutural", "category": "III", "domain": "mathematics"},
    "R14": {"name": "Invariante", "category": "III", "domain": "all"},
    "R15": {"name": "Caso-Base", "category": "III", "domain": "mathematics"},
    "R16": {"name": "Recorrente", "category": "III", "domain": "mathematics"},
    
    # Categories IV-VII: existing from v10
    "R17": {"name": "Construtivo-Explicito", "category": "IV", "domain": "all"},
    "R18": {"name": "Algorithmico", "category": "IV", "domain": "cs"},
    "R19": {"name": "Enumerativo", "category": "IV", "domain": "mathematics"},
    "R20": {"name": "Probabilistico", "category": "IV", "domain": "mathematics"},
    "R21": {"name": "Otimizatorio", "category": "IV", "domain": "engineering"},
    "R22": {"name": "Contraexemplo", "category": "V", "domain": "all"},
    "R23": {"name": "Reductio-ad-Absurdum", "category": "V", "domain": "all"},
    "R24": {"name": "Contradicao-Interna", "category": "V", "domain": "all"},
    "R25": {"name": "Consistencia-Cruzada", "category": "V", "domain": "all"},
    "R26": {"name": "Teste-de-Estresse", "category": "V", "domain": "all"},
    "R27": {"name": "Exaustivo-Computacional", "category": "VI", "domain": "all"},
    "R28": {"name": "Cross-Reference", "category": "VI", "domain": "all"},
    "R29": {"name": "Simbolico-Algebrico", "category": "VI", "domain": "mathematics"},
    "R30": {"name": "Numerico-Estatistico", "category": "VI", "domain": "all"},
    "R31": {"name": "Dependencia-Logica", "category": "VII", "domain": "all"},
    "R32": {"name": "Confianca-Calibrada", "category": "VII", "domain": "all"},
    "R33": {"name": "Revisao-por-Pares", "category": "VII", "domain": "all"},
    "R34": {"name": "Generalizacao-Restritiva", "category": "VII", "domain": "all"},
    
    # Category VIII: Scientific-Experimental
    "R35": {"name": "Hipotetico-Dedutivo", "category": "VIII", "domain": "science"},
    "R36": {"name": "Experimental-Design", "category": "VIII", "domain": "science"},
    "R37": {"name": "Inferencial-Estatistico", "category": "VIII", "domain": "science"},
    "R38": {"name": "Causal-Contrafactual", "category": "VIII", "domain": "science"},
    "R39": {"name": "Meta-Analitico", "category": "VIII", "domain": "science"},
    "R40": {"name": "Reprodutibilidade", "category": "VIII", "domain": "science"},
    "R41": {"name": "Bayesiano-Atualizacao", "category": "VIII", "domain": "science"},
    
    # Category IX: Legal-Argumentative
    "R42": {"name": "Precedente-Analogico", "category": "IX", "domain": "legal"},
    "R43": {"name": "Estatutario-Interpretativo", "category": "IX", "domain": "legal"},
    "R44": {"name": "Onus-Probatio", "category": "IX", "domain": "legal"},
    "R45": {"name": "Sopesamento-Principios", "category": "IX", "domain": "legal"},
    "R46": {"name": "Fatico-Probatorio", "category": "IX", "domain": "legal"},
    "R47": {"name": "Normativo-Consequencialista", "category": "IX", "domain": "legal"},
    
    # Category X: Economic-Decision
    "R48": {"name": "Equilibrio-Nash", "category": "X", "domain": "economics"},
    "R49": {"name": "Custo-Beneficio", "category": "X", "domain": "economics"},
    "R50": {"name": "Risco-Incerteza", "category": "X", "domain": "economics"},
    "R51": {"name": "Alocacao-Eficiente", "category": "X", "domain": "economics"},
    "R52": {"name": "Causal-Econometrico", "category": "X", "domain": "economics"},
    "R53": {"name": "Prospectivo-Decisional", "category": "X", "domain": "economics"},
    
    # Category XI: Engineering-Optimization
    "R54": {"name": "Restricao-Satisfacao", "category": "XI", "domain": "engineering"},
    "R55": {"name": "Heuristico-Busca", "category": "XI", "domain": "cs"},
    "R56": {"name": "Decomposicao-Arquitetural", "category": "XI", "domain": "engineering"},
    "R57": {"name": "Trade-off-Pareto", "category": "XI", "domain": "engineering"},
    "R58": {"name": "Falha-Modo-Analise", "category": "XI", "domain": "engineering"},
    "R59": {"name": "Scaling-Analise", "category": "XI", "domain": "cs"},
    
    # Category XII: Philosophical-Conceptual
    "R60": {"name": "Dialetico-Hegeliano", "category": "XII", "domain": "philosophy"},
    "R61": {"name": "Pensamento-Experimental", "category": "XII", "domain": "philosophy"},
    "R62": {"name": "Analitico-Conceitual", "category": "XII", "domain": "philosophy"},
    "R63": {"name": "Epistemico-Justificatorio", "category": "XII", "domain": "philosophy"},
    "R64": {"name": "Etico-Normativo", "category": "XII", "domain": "philosophy"},
    
    # Category XIII: Physical-Mathematical
    "R65": {"name": "Simetria-Conservacao", "category": "XIII", "domain": "physics"},
    "R66": {"name": "Dimensional-Analitico", "category": "XIII", "domain": "physics"},
    "R67": {"name": "Perturbativo", "category": "XIII", "domain": "physics"},
    "R68": {"name": "Escala-Renormalizacao", "category": "XIII", "domain": "physics"},
    "R69": {"name": "Variacional-Principio", "category": "XIII", "domain": "physics"},
    "R70": {"name": "Limite-Assintotico", "category": "XIII", "domain": "mathematics"},
    "R71": {"name": "Dualidade-Transformacao", "category": "XIII", "domain": "mathematics"},
    "R72": {"name": "Estabilidade-Lyapunov", "category": "XIII", "domain": "physics"},
    
    # Category XIV: Systemic-Informational
    "R73": {"name": "Entropico-Informacional", "category": "XIV", "domain": "information"},
    "R74": {"name": "Feedback-Cibernetico", "category": "XIV", "domain": "systems"},
    "R75": {"name": "Emergente-Sistemico", "category": "XIV", "domain": "systems"},
    "R76": {"name": "Rede-Grafo-Analitico", "category": "XIV", "domain": "networks"},
    "R77": {"name": "Compressao-Minimalista", "category": "XIV", "domain": "information"},
    "R78": {"name": "Caotico-Deterministico", "category": "XIV", "domain": "systems"},
    "R79": {"name": "Auto-Organizacao", "category": "XIV", "domain": "systems"},
    "R80": {"name": "Robustez-Redundancia", "category": "XIV", "domain": "systems"},
    
    # Category XV: Computational-Algorithmic
    "R81": {"name": "Complexidade-Assintotica", "category": "XV", "domain": "cs"},
    "R82": {"name": "Reducao-Computacional", "category": "XV", "domain": "cs"},
    "R83": {"name": "Dividir-Conquistar", "category": "XV", "domain": "cs"},
    "R84": {"name": "Aproximacao-Garantida", "category": "XV", "domain": "cs"},
    "R85": {"name": "Aleatorizacao-Probabilistica", "category": "XV", "domain": "cs"},
    "R86": {"name": "Programacao-Dinamica", "category": "XV", "domain": "cs"},
    "R87": {"name": "Auto-Reducao-Recursiva", "category": "XV", "domain": "cs"},
    "R88": {"name": "Estrutura-Dados-Invariante", "category": "XV", "domain": "cs"},
    
    # Category XVI: Cognitive-Decision
    "R89": {"name": "Heuristicas-Vieses", "category": "XVI", "domain": "psychology"},
    "R90": {"name": "Mental-Model-Simulacao", "category": "XVI", "domain": "psychology"},
    "R91": {"name": "Aprendizado-Transferencia", "category": "XVI", "domain": "education"},
    "R92": {"name": "Abducao-Peirceana", "category": "XVI", "domain": "philosophy"},
    "R93": {"name": "Analogia-Estrutural", "category": "XVI", "domain": "psychology"},
    "R94": {"name": "Meta-Cognicao-Monitoramento", "category": "XVI", "domain": "psychology"},
    "R95": {"name": "Teoria-da-Mente", "category": "XVI", "domain": "psychology"},
    "R96": {"name": "Aprendizado-por-Reforco", "category": "XVI", "domain": "ai"},
    
    # Additional types to reach 100
    "R97": {"name": "Geodesico-Minimizante", "category": "XIII", "domain": "physics"},
    "R98": {"name": "Codificacao-Entropica", "category": "XIV", "domain": "information"},
    "R99": {"name": "Paralelizacao-Distribuida", "category": "XV", "domain": "cs"},
    "R100": {"name": "Vies-Confirmacao-Deteccao", "category": "XVI", "domain": "psychology"},
    
    # ================================================================
    # EXPANSION: R101-R200 (8 new categories, 100 new reasoning types)
    # ================================================================
    
    # Category XVII: Logical-Mathematical Advanced
    "R101": {"name": "Topologico-Ponto-Fixo", "category": "XVII", "domain": "mathematics"},
    "R102": {"name": "Algebrico-Galois", "category": "XVII", "domain": "mathematics"},
    "R103": {"name": "Categorico-Funtorial", "category": "XVII", "domain": "mathematics"},
    "R104": {"name": "Homologico-Algebrico", "category": "XVII", "domain": "mathematics"},
    "R105": {"name": "Teoria-Modelos", "category": "XVII", "domain": "logic"},
    "R106": {"name": "Teoria-Provabilidade", "category": "XVII", "domain": "logic"},
    "R107": {"name": "Computabilidade-Turing", "category": "XVII", "domain": "cs"},
    "R108": {"name": "Analitico-Complexo", "category": "XVII", "domain": "mathematics"},
    "R109": {"name": "Espectral-Operadores", "category": "XVII", "domain": "mathematics"},
    "R110": {"name": "Representacao-Grupos", "category": "XVII", "domain": "mathematics"},
    "R111": {"name": "Geometrico-Diferencial", "category": "XVII", "domain": "mathematics"},
    "R112": {"name": "Medida-Integracao", "category": "XVII", "domain": "mathematics"},
    "R113": {"name": "Ergodico-Teoria", "category": "XVII", "domain": "mathematics"},
    
    # Category XVIII: Probabilistic-Stochastic
    "R114": {"name": "Martingale-Convergencia", "category": "XVIII", "domain": "probability"},
    "R115": {"name": "Markov-Cadeias", "category": "XVIII", "domain": "probability"},
    "R116": {"name": "Grandes-Desvios", "category": "XVIII", "domain": "probability"},
    "R117": {"name": "Monte-Carlo-MCMC", "category": "XVIII", "domain": "statistics"},
    "R118": {"name": "Processo-Poisson", "category": "XVIII", "domain": "probability"},
    "R119": {"name": "Movimento-Browniano", "category": "XVIII", "domain": "probability"},
    "R120": {"name": "Inferencia-Fiducial", "category": "XVIII", "domain": "statistics"},
    "R121": {"name": "Teste-Hipotese-Otimo", "category": "XVIII", "domain": "statistics"},
    "R122": {"name": "Regressao-Nao-Parametrica", "category": "XVIII", "domain": "statistics"},
    "R123": {"name": "Bootstrap-Resampling", "category": "XVIII", "domain": "statistics"},
    "R124": {"name": "Informacao-Mutua", "category": "XVIII", "domain": "information"},
    "R125": {"name": "Processo-Decisao-Markov", "category": "XVIII", "domain": "ai"},
    "R126": {"name": "Teoria-Valores-Extremos", "category": "XVIII", "domain": "statistics"},
    
    # Category XIX: Biological-Evolutionary
    "R127": {"name": "Filogenetico-Cladistico", "category": "XIX", "domain": "biology"},
    "R128": {"name": "Selecao-Natural-Darwiniana", "category": "XIX", "domain": "biology"},
    "R129": {"name": "Equilibrio-Hardy-Weinberg", "category": "XIX", "domain": "biology"},
    "R130": {"name": "Epidemiologico-SIR", "category": "XIX", "domain": "biology"},
    "R131": {"name": "Ecologico-Predador-Presa", "category": "XIX", "domain": "ecology"},
    "R132": {"name": "Genetica-Quantitativa", "category": "XIX", "domain": "biology"},
    "R133": {"name": "Bioquimico-Michaelis-Menten", "category": "XIX", "domain": "biochemistry"},
    "R134": {"name": "Metabolico-Fluxo-Balanco", "category": "XIX", "domain": "biology"},
    "R135": {"name": "Neuro-Biologico-Potencial", "category": "XIX", "domain": "neuroscience"},
    "R136": {"name": "Imunologico-Clonal-Selecao", "category": "XIX", "domain": "immunology"},
    "R137": {"name": "Bioinformatico-Alinhamento", "category": "XIX", "domain": "bioinformatics"},
    "R138": {"name": "Ecotoxicologico-Dose-Resposta", "category": "XIX", "domain": "toxicology"},
    "R139": {"name": "Evolutivo-Molecular-Neutro", "category": "XIX", "domain": "biology"},
    
    # Category XX: Neuro-Cognitive
    "R140": {"name": "Codificacao-Neural-Esparsa", "category": "XX", "domain": "neuroscience"},
    "R141": {"name": "Plasticidade-Sinaptica-Hebbiana", "category": "XX", "domain": "neuroscience"},
    "R142": {"name": "Conectoma-Grafo-Cerebral", "category": "XX", "domain": "neuroscience"},
    "R143": {"name": "Percepcao-Bayesiana", "category": "XX", "domain": "psychology"},
    "R144": {"name": "Atencao-Seletiva-Treisman", "category": "XX", "domain": "psychology"},
    "R145": {"name": "Memoria-Consolidacao-Sistemas", "category": "XX", "domain": "neuroscience"},
    "R146": {"name": "Raciocinio-Analogico-Gentner", "category": "XX", "domain": "psychology"},
    "R147": {"name": "Tomada-Decisao-Difusao", "category": "XX", "domain": "psychology"},
    "R148": {"name": "Emocao-Cognicao-Integracao", "category": "XX", "domain": "psychology"},
    "R149": {"name": "Linguagem-Chomsky-Gerativa", "category": "XX", "domain": "linguistics"},
    "R150": {"name": "Aprendizado-Estatistico-Infantil", "category": "XX", "domain": "psychology"},
    "R151": {"name": "Consciencia-NCC-Koch", "category": "XX", "domain": "neuroscience"},
    
    # Category XXI: Control-Signals
    "R152": {"name": "PID-Controle-Classico", "category": "XXI", "domain": "engineering"},
    "R153": {"name": "Otimo-Controle-Pontryagin", "category": "XXI", "domain": "engineering"},
    "R154": {"name": "Kalman-Filtragem", "category": "XXI", "domain": "engineering"},
    "R155": {"name": "Fourier-Analise-Espectral", "category": "XXI", "domain": "engineering"},
    "R156": {"name": "Wavelet-Multirresolucao", "category": "XXI", "domain": "engineering"},
    "R157": {"name": "Nyquist-Amostragem", "category": "XXI", "domain": "engineering"},
    "R158": {"name": "Compressao-Sensoriamento", "category": "XXI", "domain": "cs"},
    "R159": {"name": "Wiener-Filtro-Otimo", "category": "XXI", "domain": "engineering"},
    "R160": {"name": "Convolucional-Rede-CNN", "category": "XXI", "domain": "ai"},
    "R161": {"name": "Identificacao-Sistema", "category": "XXI", "domain": "engineering"},
    "R162": {"name": "Controle-Robusto-Hinfinito", "category": "XXI", "domain": "engineering"},
    "R163": {"name": "Adaptativo-Controle-MRAC", "category": "XXI", "domain": "engineering"},
    "R164": {"name": "Nao-Linear-Lyapunov-Estabilidade", "category": "XXI", "domain": "engineering"},
    
    # Category XXII: Cryptographic-Security
    "R165": {"name": "Zero-Knowledge-Prova", "category": "XXII", "domain": "cryptography"},
    "R166": {"name": "Homomorfico-Encriptacao", "category": "XXII", "domain": "cryptography"},
    "R167": {"name": "Diffie-Hellman-Troca-Chave", "category": "XXII", "domain": "cryptography"},
    "R168": {"name": "RSA-Fatoracao", "category": "XXII", "domain": "cryptography"},
    "R169": {"name": "Curva-Eliptica-ECC", "category": "XXII", "domain": "cryptography"},
    "R170": {"name": "Funcao-Hash-Colisao", "category": "XXII", "domain": "cryptography"},
    "R171": {"name": "Assinatura-Digital", "category": "XXII", "domain": "cryptography"},
    "R172": {"name": "Canais-Laterais-Timing", "category": "XXII", "domain": "security"},
    "R173": {"name": "Computacao-Multiparte-Segura", "category": "XXII", "domain": "cryptography"},
    "R174": {"name": "Pos-Quantica-Criptografia", "category": "XXII", "domain": "cryptography"},
    "R175": {"name": "Verificacao-Formal-Protocolos", "category": "XXII", "domain": "security"},
    "R176": {"name": "Blockchain-Consenso", "category": "XXII", "domain": "cryptography"},
    
    # Category XXIII: Physical-Cosmological
    "R177": {"name": "Relatividade-Geral-Einstein", "category": "XXIII", "domain": "physics"},
    "R178": {"name": "Cosmologico-FLRW", "category": "XXIII", "domain": "cosmology"},
    "R179": {"name": "Nucleossintese-Primordial", "category": "XXIII", "domain": "cosmology"},
    "R180": {"name": "Materia-Escura-Inferencia", "category": "XXIII", "domain": "cosmology"},
    "R181": {"name": "Redshift-Cosmologico", "category": "XXIII", "domain": "astronomy"},
    "R182": {"name": "Radiacao-Cosmica-Fundo", "category": "XXIII", "domain": "cosmology"},
    "R183": {"name": "Mecanica-Quantica-Particulas", "category": "XXIII", "domain": "physics"},
    "R184": {"name": "Simetria-Quebra-Espontanea", "category": "XXIII", "domain": "physics"},
    "R185": {"name": "Inflacao-Cosmologica", "category": "XXIII", "domain": "cosmology"},
    "R186": {"name": "Estelar-Nucleossintese", "category": "XXIII", "domain": "astronomy"},
    "R187": {"name": "Ondas-Gravitacionais-LIGO", "category": "XXIII", "domain": "physics"},
    "R188": {"name": "Entropia-Buraco-Negro", "category": "XXIII", "domain": "physics"},
    
    # Category XXIV: Social-Anthropological
    "R189": {"name": "Difusao-Redes-Sociais", "category": "XXIV", "domain": "sociology"},
    "R190": {"name": "Teoria-Jogos-Evolutivos-Culturais", "category": "XXIV", "domain": "anthropology"},
    "R191": {"name": "Analise-Redes-Complexas", "category": "XXIV", "domain": "sociology"},
    "R192": {"name": "Demografico-Transicao", "category": "XXIV", "domain": "demography"},
    "R193": {"name": "Antropologico-Parentesco", "category": "XXIV", "domain": "anthropology"},
    "R194": {"name": "Institucional-Path-Dependence", "category": "XXIV", "domain": "economics"},
    "R195": {"name": "Economia-Comportamental-Nudge", "category": "XXIV", "domain": "economics"},
    "R196": {"name": "Cooperacao-Altruismo-Reciproco", "category": "XXIV", "domain": "sociology"},
    "R197": {"name": "Identidade-Social-Tajfel", "category": "XXIV", "domain": "psychology"},
    "R198": {"name": "Memetica-Transmissao-Cultural", "category": "XXIV", "domain": "anthropology"},
    "R199": {"name": "Polarizacao-Grupo-Deliberacao", "category": "XXIV", "domain": "sociology"},
    "R200": {"name": "Resiliencia-Comunitaria", "category": "XXIV", "domain": "sociology"},
    # === Category XXV: Cross-Domain Generated (Creative Leap, R201-R204) ===
    "R201": {"name": "Cross-Domain Deduction", "category": "XXV", "domain": "all"},
    "R202": {"name": "Dimensional Verification", "category": "XXV", "domain": "all"},
    "R203": {"name": "Symmetry-Guided Reasoning", "category": "XXV", "domain": "all"},
    "R204": {"name": "Symmetry+Dimensional Hybrid", "category": "XXV", "domain": "all"},
    # === Category XXVI: Geometric Reasoning (DCA Modulo 1, R205-R208) ===
    "R205": {"name": "Local-Exactness Probe", "category": "XXVI", "domain": "geometry"},
    "R206": {"name": "Topological-Singularity Detector", "category": "XXVI", "domain": "geometry"},
    "R207": {"name": "Kaehler-Identity Reasoning", "category": "XXVI", "domain": "geometry"},
    "R208": {"name": "Canonical-Example Strategy", "category": "XXVI", "domain": "all"},
    # === Category XXVII: Perturbation Theory (candidates from DCA Listas, R209-R212) ===
    "R209": {"name": "Homological-Equation Solver", "category": "XXVII", "domain": "mechanics"},
    "R210": {"name": "Lax-Pair Detector", "category": "XXVII", "domain": "integrable_systems"},
    "R211": {"name": "Separability-Test", "category": "XXVII", "domain": "mechanics"},
    "R212": {"name": "Runge-Lenz Generalizer", "category": "XXVII", "domain": "mechanics"},
}

def get_agents_for_domain(domain: str) -> list[str]:
    """Return list of reasoning type IDs applicable to a domain."""
    return [rid for rid, info in REASONING_REGISTRY.items() 
            if info["domain"] == domain or info["domain"] == "all"]

def get_agents_for_category(category: str) -> list[str]:
    """Return list of reasoning type IDs in a category."""
    return [rid for rid, info in REASONING_REGISTRY.items() 
            if info["category"] == category]
