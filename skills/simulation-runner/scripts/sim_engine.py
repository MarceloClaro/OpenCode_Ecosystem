"""
P20 — Simulation Runner: Motor de simulação multiagente local.
Supera o MiroFish original: milhares de agentes, multi-rodada,
Teoria dos Jogos, emergência coletiva, persistência SQLite.

Arquitetura:
  OASIS Agents → Simulation Engine → Round Loop → State → SQLite
       ↑                ↑                              ↓
  Config(BRAZIL_TZ)  Variable Injection ←── Emergent Analysis
"""
import sys, os, json, math, random, sqlite3, time, threading
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict, Counter

# ═══════════════════════════════════════════════════════════════════
# BRAZIL Timezone (local, sem dependência externa)
# ═══════════════════════════════════════════════════════════════════

BRAZIL_TZ = timezone(timedelta(hours=-3))
BRAZIL_TIME = lambda: datetime.now(BRAZIL_TZ)

# ═══════════════════════════════════════════════════════════════════
# Modelos de Dados
# ═══════════════════════════════════════════════════════════════════

class AgentState(Enum):
    IDLE = "idle"
    THINKING = "thinking"
    ACTING = "acting"
    INTERACTING = "interacting"
    DORMANT = "dormant"

class ActionType(Enum):
    POST = "post"           # Criar conteúdo
    COMMENT = "comment"     # Comentar em post existente
    SHARE = "share"         # Compartilhar
    LIKE = "like"           # Reagir
    FOLLOW = "follow"       # Seguir outro agente
    UNFOLLOW = "unfollow"   # Deixar de seguir
    REPLY = "reply"         # Responder comentário
    DO_NOTHING = "nothing"  # Inatividade

class Sentiment(Enum):
    VERY_NEGATIVE = -2
    NEGATIVE = -1
    NEUTRAL = 0
    POSITIVE = 1
    VERY_POSITIVE = 2

@dataclass
class AgentMemory:
    """Memória de curto e longo prazo do agente."""
    recent_posts: List[str] = field(default_factory=list)
    recent_interactions: List[Dict] = field(default_factory=list)
    key_memories: List[str] = field(default_factory=list)  # Memórias de longo prazo
    trust_scores: Dict[str, float] = field(default_factory=dict)  # Confiança em outros agentes
    opinion_vector: Dict[str, float] = field(default_factory=dict)  # Opiniões sobre tópicos
    emotional_state: float = 0.0  # -1.0 (negativo) a 1.0 (positivo)
    energy: float = 1.0  # 0.0 (exausto) a 1.0 (energético)

@dataclass
class SimAgent:
    """Agente de simulação completo."""
    id: str
    name: str
    profile: Dict[str, Any] = field(default_factory=dict)
    state: AgentState = AgentState.IDLE
    memory: AgentMemory = field(default_factory=AgentMemory)
    position: Dict[str, Any] = field(default_factory=dict)  # Posição no grafo social
    activity_level: float = 0.5
    influence: float = 1.0
    stance: str = "neutral"
    followers: List[str] = field(default_factory=list)
    following: List[str] = field(default_factory=list)
    posts_count: int = 0
    interactions_count: int = 0
    network_neighbors: List[str] = field(default_factory=list)  # Scale-free network edges
    emotional_state: float = 0.0  # Sentiment tracking
    created_at: str = field(default_factory=lambda: BRAZIL_TIME().isoformat())

@dataclass
class SimAction:
    """Ação registrada na simulação."""
    id: str
    agent_id: str
    action_type: ActionType
    content: str = ""
    target_id: Optional[str] = None
    sentiment: Sentiment = Sentiment.NEUTRAL
    round_number: int = 0
    platform: str = "twitter"
    timestamp: str = field(default_factory=lambda: BRAZIL_TIME().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SimEvent:
    """Evento externo injetado na simulação (God's-eye view)."""
    id: str
    title: str
    description: str
    impact_level: float  # 0.0 a 1.0
    affected_agents: List[str] = field(default_factory=list)
    sentiment_shift: float = 0.0  # -1.0 a 1.0
    round_injected: int = 0
    duration_rounds: int = 1
    timestamp: str = field(default_factory=lambda: BRAZIL_TIME().isoformat())


# ═══════════════════════════════════════════════════════════════════
# SIMULATION ENGINE
# ═══════════════════════════════════════════════════════════════════

class SimulationEngine:
    """Motor de simulação multiagente completo."""

    def __init__(self, name: str = "BrazilSim", db_path: str = ""):
        self.name = name
        self.agents: Dict[str, SimAgent] = {}
        self.actions: List[SimAction] = []
        self.events: List[SimEvent] = []
        self.current_round: int = 0
        self.max_rounds: int = 50
        self.platforms = ["twitter", "reddit"]
        self.stats: Dict[str, Any] = defaultdict(int)
        self._running = False
        self.real_data_calibration: Dict[str, float] = {}  # G1: F1→F2
        self.use_llm_discourse: bool = False  # G5: LLM integration
        self.llm_engine = None
        self.topic_weights: Dict[str, float] = {}  # G1: calibrated topic weights

        # DB local SQLite
        self.db_path = db_path or f".reversa/sim_{name}.db"
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=WAL;")
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS agents (
            id TEXT PRIMARY KEY, name TEXT, state TEXT, activity REAL,
            influence REAL, stance TEXT, followers_count INTEGER,
            posts_count INTEGER, interactions_count INTEGER,
            emotional_state REAL, profile_json TEXT, created_at TEXT
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS actions (
            id TEXT PRIMARY KEY, agent_id TEXT, type TEXT, content TEXT,
            target_id TEXT, sentiment TEXT, round INTEGER, platform TEXT,
            timestamp TEXT, metadata_json TEXT
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS events (
            id TEXT PRIMARY KEY, title TEXT, description TEXT,
            impact REAL, round INTEGER, duration INTEGER, timestamp TEXT
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS rounds (
            round_number INTEGER PRIMARY KEY, timestamp TEXT,
            total_actions INTEGER, active_agents INTEGER,
            avg_sentiment REAL, emergent_patterns TEXT
        )""")
        conn.commit()
        conn.close()

    # ── Agent Management ──────────────────────────────────────────

    def create_agent(self, name: str, profile: Dict[str, Any] = None) -> SimAgent:
        """Cria um agente a partir de um perfil OASIS."""
        agent_id = f"agent_{len(self.agents):04d}"
        profile = profile or {}

        activity_cfg = profile.get("activity_config", {})
        agent = SimAgent(
            id=agent_id,
            name=name,
            profile=profile,
            activity_level=activity_cfg.get("activity_level", random.uniform(0.3, 0.9)),
            influence=activity_cfg.get("influence_weight", random.uniform(0.5, 2.0)),
            stance=activity_cfg.get("stance", "neutral"),
            memory=AgentMemory(
                opinion_vector=self._random_opinion_vector(100),
            ),
        )
        self.agents[agent_id] = agent
        return agent

    def create_agents_from_profiles(self, profiles: List[Dict]) -> List[SimAgent]:
        """Cria múltiplos agentes a partir de perfis OASIS."""
        agents = []
        for profile in profiles:
            agent = self.create_agent(profile.get("name", "Agente"), profile)
            agents.append(agent)
        return agents

    def create_agents_batch(self, count: int, types: List[str] = None) -> List[SimAgent]:
        """Cria um lote de agentes com tipos variados."""
        types = types or ["Official", "Professor", "Student", "Person", "MediaOutlet", "Alumni"]
        agents = []
        for i in range(count):
            agent_type = random.choice(types)
            profile = {
                "name": f"{agent_type}_{i:04d}",
                "labels": [agent_type],
                "activity_config": {
                    "activity_level": random.uniform(0.2, 0.9),
                    "influence_weight": random.uniform(0.3, 2.5),
                    "stance": random.choice(["supportive", "critical", "neutral", "curious"]),
                    "sentiment_bias": random.uniform(-0.5, 0.5),
                },
            }
            agent = self.create_agent(profile["name"], profile)
            agents.append(agent)
        return agents

    def build_scale_free_network(self, m0: int = 3, m: int = 2):
        """
        Constrói rede scale-free (Barabási-Albert) entre agentes.
        
        - m0: tamanho do núcleo inicial totalmente conectado
        - m: arestas adicionadas por novo nó (preferential attachment)
        
        Cada agente ganha atributo `network_neighbors: List[str]` com IDs.
        Isso substitui conexões aleatórias por topologia realista de rede social.
        """
        agent_ids = list(self.agents.keys())
        n = len(agent_ids)

        if n < m0:
            return  # Insuficiente

        # Inicializar grafo
        neighbors = defaultdict(set)

        # Núcleo inicial: m0 nós totalmente conectados
        for i in range(m0):
            for j in range(i + 1, m0):
                neighbors[agent_ids[i]].add(agent_ids[j])
                neighbors[agent_ids[j]].add(agent_ids[i])

        # Crescimento com preferential attachment
        degrees = {aid: len(neighbors[aid]) for aid in agent_ids[:m0]}
        total_degree = sum(degrees.values())

        for i in range(m0, n):
            new_id = agent_ids[i]
            targets = set()

            while len(targets) < min(m, i):
                # Preferential attachment: probabilidade ∝ degree
                if total_degree == 0:
                    # Fallback: aleatório
                    candidates = [aid for aid in agent_ids[:i] if aid not in targets]
                    if candidates:
                        targets.add(random.choice(candidates))
                    else:
                        break
                else:
                    r = random.uniform(0, total_degree)
                    cumulative = 0.0
                    chosen = None
                    for aid in agent_ids[:i]:
                        if aid not in targets:
                            cumulative += degrees.get(aid, 1)  # +1 evita grau zero
                            if cumulative >= r:
                                chosen = aid
                                break
                    if chosen:
                        targets.add(chosen)
                        neighbors[new_id].add(chosen)
                        neighbors[chosen].add(new_id)
                        degrees[chosen] = degrees.get(chosen, 0) + 1
                        degrees[new_id] = degrees.get(new_id, 0) + 1
                        total_degree += 2

            # Atualizar total_degree para próximo nó
            total_degree = sum(degrees.values())

        # Atribuir vizinhos aos agentes
        for aid in agent_ids:
            self.agents[aid].network_neighbors = list(neighbors.get(aid, set()))

        # Métricas da rede
        all_degrees = [len(neighbors.get(aid, set())) for aid in agent_ids]
        self.network_stats = {
            "type": "scale_free",
            "nodes": n,
            "edges": sum(all_degrees) // 2,
            "avg_degree": round(sum(all_degrees) / n, 2) if n > 0 else 0,
            "max_degree": max(all_degrees) if all_degrees else 0,
            "m0": m0, "m": m,
            "power_law_alpha": self._estimate_power_law(all_degrees),
        }

        return self.network_stats

    def _estimate_power_law(self, degrees: List[int]) -> float:
        """Estima expoente α da power-law P(k) ∝ k^(-α) via MLE."""
        k_min = min(d for d in degrees if d > 0) if any(d > 0 for d in degrees) else 1
        valid = [d for d in degrees if d >= k_min]
        if len(valid) < 3:
            return 0.0
        n = len(valid)
        sum_log = sum(math.log(d / (k_min - 0.5)) for d in valid)
        alpha = 1 + n / sum_log if sum_log > 0 else 0.0
        return round(alpha, 3)

    # ── Simulation Loop ───────────────────────────────────────────

    def run_simulation(self, rounds: int = 50, agents: int = 100,
                       events: List[Dict] = None,
                       callback: Callable = None) -> Dict[str, Any]:
        """Executa simulação completa.

        Args:
            rounds: Número de rodadas
            agents: Número de agentes (se < existentes, usa existentes)
            events: Lista de eventos externos para injetar
            callback: Função chamada a cada rodada (round_num, stats)

        Returns:
            Dict com estatísticas completas da simulação
        """
        self.max_rounds = rounds

        # Criar agentes se necessário
        if len(self.agents) < agents:
            self.create_agents_batch(agents - len(self.agents))

        # Injetar eventos
        if events:
            for evt in events:
                self.inject_event(evt.get("title", ""),
                                  evt.get("description", ""),
                                  evt.get("impact", 0.5),
                                  evt.get("round", 1))

        print(f"\n{'=' * 60}")
        print(f"[SIM] {self.name}")
        print(f"     Agents: {len(self.agents)} | Rounds: {rounds} | Platforms: {self.platforms}")
        print(f"     Timezone: BRAZIL (UTC-3) | DB: {self.db_path}")
        print(f"{'=' * 60}")

        self._running = True
        start_time = time.time()

        for r in range(1, rounds + 1):
            self.current_round = r
            round_start = time.time()

            # Aplicar eventos da rodada
            self._apply_events(r)

            # Cada agente age
            round_actions = []
            active_agents = 0
            sentiments = []

            for agent in list(self.agents.values()):
                if random.random() > agent.activity_level * 0.5:
                    continue  # Agente inativo nesta rodada

                active_agents += 1
                actions = self._agent_act(agent, r)
                round_actions.extend(actions)

                for a in actions:
                    if hasattr(a, 'sentiment'):
                        sentiments.append(a.sentiment.value)

            self.actions.extend(round_actions)

            # Dinâmica social evolutiva (Edge Rewiring & Social Reinforcement Learning)
            self._run_social_dynamics()

            # Estatísticas da rodada
            avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
            self.stats[f"round_{r}_actions"] = len(round_actions)
            self.stats[f"round_{r}_active"] = active_agents

            # Salvar no banco
            self._save_round(r, len(round_actions), active_agents, avg_sentiment)

            # Callback
            if callback:
                callback(r, {
                    "actions": len(round_actions),
                    "active": active_agents,
                    "sentiment": avg_sentiment,
                    "total_agents": len(self.agents),
                })

            round_time = time.time() - round_start
            if r % 10 == 0 or r == 1:
                print(f"   Rodada {r:3d}/{rounds} | {len(round_actions):4d} ações | "
                      f"{active_agents:4d} ativos | sentimento: {avg_sentiment:+.2f} | "
                      f"{round_time:.2f}s")

        self._running = False
        total_time = time.time() - start_time

        # Estatísticas finais
        final_stats = self._compute_final_stats(total_time)
        self._save_agents()

        print(f"\n{'=' * 60}")
        print(f"[OK] SIMULATION DONE in {total_time:.1f}s")
        print(f"   Actions: {final_stats['total_actions']}")
        print(f"   Posts: {final_stats['total_posts']} | Interactions: {final_stats['total_interactions']}")
        print(f"   Avg Sentiment: {final_stats['avg_sentiment']:+.2f}")
        print(f"   Top influencer: {final_stats.get('most_influential', '?')}")
        print(f"{'=' * 60}")

        return final_stats

    def _run_social_dynamics(self):
        """
        Executa dinâmica de evolução social co-evolutiva da rede.
        1. Adaptação Topológica (Edge Rewiring): Agentes rompem laços com vizinhos de opinião oposta
           e conectam-se a novos agentes de opinião similar para simular Echo Chambers.
        2. Aprendizado Social (Stance Shifts): Agentes de baixo engajamento se adaptam ao stance de
           vizinhos influentes para maximizar sua reputação.
        """
        for agent in list(self.agents.values()):
            if not agent.network_neighbors:
                continue

            # 1. Reconfiguração Topológica (Edge Rewiring)
            new_neighbors = []
            rewire_count = 0
            for neighbor_id in agent.network_neighbors:
                neighbor = self.agents.get(neighbor_id)
                if not neighbor:
                    continue
                
                delta_sentiment = abs(agent.memory.emotional_state - neighbor.memory.emotional_state)
                # Se a discórdia de sentimento for muito alta (> 1.2), há chance proporcional de unfollow
                if delta_sentiment > 1.2 and random.random() < 0.25 * delta_sentiment:
                    rewire_count += 1
                    continue
                new_neighbors.append(neighbor_id)
            
            # Repor conexões cortadas conectando-se a quem tem afinidade (echo chambers)
            candidates = [
                aid for aid, a in self.agents.items()
                if aid != agent.id and aid not in new_neighbors
                and abs(agent.memory.emotional_state - a.memory.emotional_state) < 0.3
            ]
            if candidates and rewire_count > 0:
                chosen_candidates = random.sample(candidates, min(len(candidates), rewire_count))
                new_neighbors.extend(chosen_candidates)

            agent.network_neighbors = new_neighbors

            # 2. Aprendizado Social & Adaptação de Stance
            # Agentes de baixa influência tentam se alinhar aos líderes locais para mimetismo
            if agent.influence < 1.5:
                neighbors = [self.agents[nid] for nid in agent.network_neighbors if nid in self.agents]
                if neighbors:
                    best_neighbor = max(neighbors, key=lambda n: n.influence)
                    if best_neighbor.influence > agent.influence:
                        if agent.stance != best_neighbor.stance and random.random() < 0.08:
                            agent.stance = best_neighbor.stance

    def _agent_act(self, agent: SimAgent, round_num: int) -> List[SimAction]:
        """Um agente decide e executa ações em uma rodada."""
        actions = []

        # Decisão baseada em energia, atividade e contexto
        if agent.memory.energy < 0.2 and random.random() > 0.3:
            return actions  # Muito cansado

        # Postar?
        posts_per_hour = agent.profile.get("activity_config", {}).get("posts_per_hour", 0.5)
        if random.random() < posts_per_hour * agent.memory.energy:
            topic = self._select_topic(agent)
            sentiment = self._determine_sentiment(agent, topic)
            content = self._generate_content(agent, topic, sentiment)
            action = SimAction(
                id=f"act_{len(self.actions):08d}",
                agent_id=agent.id,
                action_type=ActionType.POST,
                content=content,
                sentiment=sentiment,
                round_number=round_num,
                platform=random.choice(self.platforms),
            )
            actions.append(action)
            agent.posts_count += 1
            agent.memory.energy -= 0.1

        # Interagir com outros agentes?
        if random.random() < agent.activity_level * 0.3 and agent.following:
            target = random.choice(agent.following)
            if target in self.agents:
                action = SimAction(
                    id=f"act_{len(self.actions):08d}",
                    agent_id=agent.id,
                    action_type=random.choice([ActionType.COMMENT, ActionType.LIKE, ActionType.SHARE]),
                    target_id=target,
                    sentiment=self._determine_sentiment(agent, "interaction"),
                    round_number=round_num,
                    platform=random.choice(self.platforms),
                )
                actions.append(action)
                agent.interactions_count += 1
                agent.memory.energy -= 0.05

        # Recuperar energia
        agent.memory.energy = min(1.0, agent.memory.energy + 0.15)

        return actions

    def _random_opinion_vector(self, n: int = 100) -> Dict[str, float]:
        """Gera vetor de opinião para todos os tópicos."""
        all_topics = [
            "ia_impacto","economia","inflacao","desemprego","crescimento_pib","juros_selic",
            "cambio_dolar","divida_publica","reforma_tributaria","balanca_comercial",
            "investimento_estrangeiro","credito","industria_nacional","agronegocio",
            "comercio_exterior","mercado_trabalho","desigualdade","pobreza","fome","moradia",
            "saneamento","transporte_publico","seguranca_publica","violencia","drogas",
            "genero","lgbtqia","racial","indigena","pcd","idosos","educacao","ensino_superior",
            "ciencia","tecnologia","inovacao","pesquisa_desenvolvimento","fuga_cerebros",
            "ensino_tecnico","educacao_infantil","alfabetizacao","saude","saude_mental",
            "pandemia","vacinas","dengue","cancer","obesidade","alcoolismo","tabagismo",
            "drogas_licitas","ia_etica","ia_regulacao","automacao","robotica","privacidade_dados",
            "ciberseguranca","blockchain","metaverso","computacao_quantica","meio_ambiente",
            "amazonia","mudancas_climaticas","energia_renovavel","carbono","reciclagem","agua",
            "biodiversidade","oceanos","desastres_naturais","guerra","paz","conflitos",
            "refugiados","imigracao","nacionalismo","globalizacao","blocos_economicos","otan",
            "onu","eleicoes","corrupcao","transparencia","reforma_politica","democracia",
            "autoritarismo","populismo","fake_news","liberdade_imprensa","participacao_popular",
            "cultura","religiao","esporte","entretenimento","redes_sociais","saude_mental_publica",
            "burnout","nomadismo_digital","minimalismo","consumismo",
        ]
        return {t: random.uniform(-1, 1) for t in all_topics[:n]}

    def _select_topic(self, agent: SimAgent) -> str:
        """Seleciona tópico baseado nas opiniões do agente."""
        if agent.memory.opinion_vector:
            # Tópico com opinião mais extrema (mais engajamento)
            return max(agent.memory.opinion_vector, key=lambda k: abs(agent.memory.opinion_vector[k]))
        return random.choice(list(agent.memory.opinion_vector.keys() or ["ia_impacto"]))

    def _determine_sentiment(self, agent: SimAgent, topic: str) -> Sentiment:
        """Determina sentimento baseado em opinião + viés."""
        opinion = agent.memory.opinion_vector.get(topic, 0)
        bias = agent.profile.get("activity_config", {}).get("sentiment_bias", 0)
        score = opinion + bias + random.uniform(-0.3, 0.3)
        score = max(-1.0, min(1.0, score))

        if score > 0.6: return Sentiment.VERY_POSITIVE
        if score > 0.2: return Sentiment.POSITIVE
        if score > -0.2: return Sentiment.NEUTRAL
        if score > -0.6: return Sentiment.NEGATIVE
        return Sentiment.VERY_NEGATIVE

    def _generate_content(self, agent: SimAgent, topic: str, sentiment: Sentiment) -> str:
        """Gera conteúdo textual com LLM (se disponível) ou templates enriquecidos."""
        # G5: Tentar LLM primeiro
        if self.use_llm_discourse and not self.llm_engine:
            try:
                from llm_discourse import LLMDiscourseEngine
                self.llm_engine = LLMDiscourseEngine()
            except ImportError:
                self.use_llm_discourse = False

        if self.use_llm_discourse and self.llm_engine:
            agent_data = {
                "name": agent.name, "stance": agent.stance,
                "sentiment_bias": agent.memory.opinion_vector.get(topic, 0),
                "category": agent.profile.get("labels", ["geral"])[0] if agent.profile.get("labels") else "geral",
            }
            post = self.llm_engine.generate_post(agent_data, topic, sentiment.value)
            if post and len(post) > 20:
                return post[:300]

        # Fallback: templates genéricos
        generic_templates = [
            "{topic}: precisamos de mais investimento e atenção!",
            "O debate sobre {topic} está cada vez mais polarizado.",
            "{topic} deve ser prioridade nacional urgente.",
            "Os dados sobre {topic} são alarmantes e exigem ação.",
            "Finalmente estão discutindo {topic} com a seriedade que merece.",
            "Não podemos mais ignorar os impactos de {topic} na sociedade.",
            "Estudos recentes mostram avanços significativos em {topic}.",
            "A situação de {topic} melhorou, mas ainda há muito a fazer.",
            "Especialistas alertam sobre os riscos de negligenciar {topic}.",
            "{topic} precisa de políticas públicas baseadas em evidências.",
        ]
        template = random.choice(generic_templates)
        return template.replace("{topic}", topic.replace("_", " "))

    # ── Variable Injection (God's-eye view) ──────────────────────

    def inject_event(self, title: str, description: str,
                     impact: float = 0.5, round_num: int = 1,
                     duration: int = 1,
                     target_stance: str = None) -> SimEvent:
        """Injeta evento externo na simulação."""
        event = SimEvent(
            id=f"evt_{len(self.events):04d}",
            title=title,
            description=description,
            impact_level=impact,
            round_injected=round_num,
            duration_rounds=duration,
        )

        # Afetar agentes com base no impacto e stance
        affected = []
        for agent in self.agents.values():
            if random.random() < abs(impact):
                affected.append(agent.id)
                # Shift de sentimento com Efeito Rebote (Backfire Effect)
                actual_impact = impact
                if "diretriz" in title.lower() or "war room" in title.lower():
                    if agent.stance == "critical":
                        actual_impact = -abs(impact) * 1.5  # Reage contra (sentimento cai)
                    elif agent.stance == "supportive":
                        actual_impact = abs(impact) * 1.2   # Reage a favor (sentimento sobe)
                    elif agent.stance == "curious":
                        actual_impact = abs(impact) * 0.4
                    else:  # neutral
                        actual_impact = abs(impact) * 0.1
                else:
                    # Direção heurística baseada no título para eventos gerais
                    is_negative = any(w in title.lower() or w in description.lower() for w in ["crise", "desastre", "queda", "recessao", "surto", "pandemia", "bolha", "perde"])
                    direction = -1.0 if is_negative else 1.0
                    actual_impact = abs(impact) * direction

                agent.memory.emotional_state += actual_impact * random.uniform(0.3, 0.8)
                agent.memory.emotional_state = max(-1.0, min(1.0, agent.memory.emotional_state))

        event.affected_agents = affected
        self.events.append(event)
        return event

    def _apply_events(self, round_num: int):
        """Aplica eventos ativos na rodada atual."""
        for event in self.events:
            if event.round_injected <= round_num < event.round_injected + event.duration_rounds:
                for agent_id in event.affected_agents:
                    if agent_id in self.agents:
                        agent = self.agents[agent_id]
                        agent.memory.energy += event.impact_level * 0.1  # Eventos dão energia
                        agent.memory.energy = min(1.0, agent.memory.energy)

    # ── Persistência ──────────────────────────────────────────────

    def _save_round(self, round_num: int, actions: int, active: int, sentiment: float):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            "INSERT OR REPLACE INTO rounds VALUES (?, ?, ?, ?, ?, ?)",
            (round_num, BRAZIL_TIME().isoformat(), actions, active, sentiment, "{}")
        )
        conn.commit()
        conn.close()

    def _clear_db(self):
        """Limpa dados de simulações anteriores."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        for table in ["rounds", "actions", "events"]:
            c.execute(f"DELETE FROM {table}")
        conn.commit()
        conn.close()

    def _save_agents(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        for agent in self.agents.values():
            c.execute("""INSERT OR REPLACE INTO agents VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                (agent.id, agent.name, agent.state.value, agent.activity_level,
                 agent.influence, agent.stance, len(agent.followers),
                 agent.posts_count, agent.interactions_count,
                 agent.memory.emotional_state,
                 json.dumps(agent.profile, ensure_ascii=False),
                 agent.created_at))
        conn.commit()
        conn.close()

    # ── Estatísticas e Análise ────────────────────────────────────

    def _compute_final_stats(self, total_time: float) -> Dict[str, Any]:
        """Computa estatísticas finais da simulação."""
        total_actions = len(self.actions)
        posts = sum(1 for a in self.actions if a.action_type == ActionType.POST)
        interactions = total_actions - posts
        sentiments = [a.sentiment.value for a in self.actions]
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0

        # Agente mais influente
        agent_influence = {a.id: a.influence * a.followers.__len__() * (1 + a.posts_count * 0.01)
                          for a in self.agents.values()}
        most_influential_id = max(agent_influence, key=agent_influence.get) if agent_influence else ""
        most_influential = self.agents.get(most_influential_id, SimAgent("", "?"))

        # ── Sentimento por tópico (enriquecido: média, std, volume, evolução, correlação) ──
        TOPICS = [
            # Economia (15)
            "economia", "inflacao", "desemprego", "crescimento_pib", "juros_selic",
            "cambio_dolar", "divida_publica", "reforma_tributaria", "balanca_comercial",
            "investimento_estrangeiro", "credito", "industria_nacional", "agronegocio",
            "comercio_exterior", "mercado_trabalho",

            # Social (15)
            "desigualdade", "pobreza", "fome", "moradia", "saneamento",
            "transporte_publico", "seguranca_publica", "violencia", "drogas",
            "genero", "lgbtqia", "racial", "indigena", "pcd", "idosos",

            # Educação & Ciência (10)
            "educacao", "ensino_superior", "ciencia", "tecnologia", "inovacao",
            "pesquisa_desenvolvimento", "fuga_cerebros", "ensino_tecnico",
            "educacao_infantil", "alfabetizacao",

            # Saúde (10)
            "saude", "saude_mental", "pandemia", "vacinas", "dengue",
            "cancer", "obesidade", "alcoolismo", "tabagismo", "drogas_licitas",

            # Tecnologia (10)
            "ia_impacto", "ia_etica", "ia_regulacao", "automacao", "robotica",
            "privacidade_dados", "ciberseguranca", "blockchain", "metaverso",
            "computacao_quantica",

            # Meio Ambiente (10)
            "meio_ambiente", "amazonia", "mudancas_climaticas", "energia_renovavel",
            "carbono", "reciclagem", "agua", "biodiversidade", "oceanos",
            "desastres_naturais",

            # Geopolítica (10)
            "guerra", "paz", "conflitos", "refugiados", "imigracao",
            "nacionalismo", "globalizacao", "blocos_economicos", "otan",
            "onu",

            # Política (10)
            "eleicoes", "corrupcao", "transparencia", "reforma_politica",
            "democracia", "autoritarismo", "populismo", "fake_news",
            "liberdade_imprensa", "participacao_popular",

            # Cultura & Comportamento (10)
            "cultura", "religiao", "esporte", "entretenimento", "redes_sociais",
            "saude_mental_publica", "burnout", "nomadismo_digital",
            "minimalismo", "consumismo",
        ]
        topic_sentiments = defaultdict(list)
        topic_volume = defaultdict(int)
        topic_by_round = defaultdict(lambda: defaultdict(list))  # topic -> round -> [sentiments]
        topic_by_stance = defaultdict(lambda: defaultdict(int))  # topic -> stance -> count

        for action in self.actions:
            if action.content:
                content_lower = action.content.lower()
                agent = self.agents.get(action.agent_id)
                stance = getattr(agent, 'stance', 'neutral') if agent else 'neutral'
                for topic in TOPICS:
                    if topic.replace("_", " ") in content_lower or topic.replace("_", "") in content_lower.replace(" ",""):
                        topic_sentiments[topic].append(action.sentiment.value)
                        topic_volume[topic] += 1
                        topic_by_round[topic][action.round_number].append(action.sentiment.value)
                        topic_by_stance[topic][stance] += 1

        def _stats(values):
            if not values: return {"mean": 0, "std": 0, "min": 0, "max": 0, "n": 0}
            m = sum(values)/len(values)
            return {"mean": round(m,4), "std": round((sum((v-m)**2 for v in values)/len(values))**0.5, 4),
                    "min": round(min(values),4), "max": round(max(values),4), "n": len(values)}

        # Evolução por rodada (série temporal)
        topic_evolution = {}
        for topic in TOPICS:
            evolution = []
            for rnd in sorted(topic_by_round[topic].keys()):
                vals = topic_by_round[topic][rnd]
                m = sum(vals)/len(vals)
                evolution.append({"round": rnd, "mean": round(m,4), "n": len(vals),
                                  "std": round((sum((v-m)**2 for v in vals)/len(vals))**0.5, 4) if len(vals)>1 else 0})
            topic_evolution[topic] = evolution

        # Correlação entre tópicos
        topic_vectors = {}
        for topic in TOPICS:
            if topic in topic_sentiments and len(topic_sentiments[topic]) >= 3:
                topic_vectors[topic] = topic_sentiments[topic]
        correlations = {}
        tkeys = list(topic_vectors.keys())
        for i in range(len(tkeys)):
            for j in range(i+1, len(tkeys)):
                a = topic_vectors[tkeys[i]]
                b = topic_vectors[tkeys[j]]
                n = min(len(a), len(b))
                ma = sum(a[:n])/n; mb = sum(b[:n])/n
                num = sum((a[k]-ma)*(b[k]-mb) for k in range(n))
                da = (sum((x-ma)**2 for x in a[:n])/n)**0.5
                db = (sum((x-mb)**2 for x in b[:n])/n)**0.5
                r = round(num/(n*da*db), 4) if da>0 and db>0 else 0
                correlations[f"{tkeys[i]}↔{tkeys[j]}"] = {"r": r, "strength": "forte" if abs(r)>0.6 else "moderada" if abs(r)>0.3 else "fraca"}

        topic_enriched = {}
        for topic in TOPICS:
            stats = _stats(topic_sentiments.get(topic, []))
            dominant_stance = max(topic_by_stance[topic].items(), key=lambda x: x[1])[0] if topic_by_stance[topic] else "n/a"
            topic_enriched[topic] = {
                **stats,
                "volume": topic_volume.get(topic, 0),
                "dominant_stance": dominant_stance,
                "stance_breakdown": dict(topic_by_stance[topic]),
                "evolution": topic_evolution.get(topic, []),
                "trend": round(topic_evolution[topic][-1]["mean"] - topic_evolution[topic][0]["mean"], 4)
                    if topic in topic_evolution and len(topic_evolution[topic]) >= 2 else 0
            }

        # Emergent patterns
        patterns = self._detect_emergent_patterns()

        return {
            "simulation_name": self.name,
            "total_rounds": self.current_round,
            "total_agents": len(self.agents),
            "total_actions": total_actions,
            "total_posts": posts,
            "total_interactions": interactions,
            "total_events": len(self.events),
            "avg_sentiment": round(avg_sentiment, 3),
            "most_influential": most_influential.name,
            "most_influential_id": most_influential_id,
            "topic_sentiments": {t: d["mean"] for t,d in topic_enriched.items()},
            "topic_analysis": topic_enriched,
            "topic_correlations": correlations,
            "emergent_patterns": patterns,
            "duration_seconds": round(total_time, 1),
            "actions_per_second": round(total_actions / total_time, 1) if total_time > 0 else 0,
            "db_path": self.db_path,
            "timestamp": BRAZIL_TIME().isoformat(),
        }

    def _detect_emergent_patterns(self) -> List[Dict[str, Any]]:
        """Detecta padrões emergentes na simulação."""
        patterns = []

        # 1. Polarização: desvio padrão do sentimento por rodada
        sentiments_by_round = defaultdict(list)
        for a in self.actions:
            sentiments_by_round[a.round_number].append(a.sentiment.value)

        polarization_score = 0
        for r, s_list in sentiments_by_round.items():
            if len(s_list) > 10:
                std = math.sqrt(sum((x - sum(s_list)/len(s_list))**2 for x in s_list) / len(s_list))
                polarization_score += std
        polarization_score /= max(len(sentiments_by_round), 1)

        patterns.append({
            "type": "polarization",
            "score": round(polarization_score, 3),
            "interpretation": "Alta polarização" if polarization_score > 1.0 else
                             "Polarização moderada" if polarization_score > 0.5 else
                             "Baixa polarização",
        })

        # 2. Echo chamber: similaridade de opinião entre agentes conectados
        echo_score = 0
        connected_pairs = 0
        for agent in self.agents.values():
            for follower_id in agent.followers:
                if follower_id in self.agents:
                    a1_vec = agent.memory.opinion_vector
                    a2_vec = self.agents[follower_id].memory.opinion_vector
                    common = set(a1_vec) & set(a2_vec)
                    if common:
                        similarity = sum(abs(a1_vec[k] - a2_vec[k]) for k in common) / len(common)
                        echo_score += (1 - similarity)
                        connected_pairs += 1

        if connected_pairs > 0:
            echo_score /= connected_pairs
            patterns.append({
                "type": "echo_chamber",
                "score": round(echo_score, 3),
                "interpretation": "Forte echo chamber" if echo_score > 0.7 else
                                 "Echo chamber moderada" if echo_score > 0.4 else
                                 "Diversidade de opinião",
            })

        # 3. Viral events: picos de atividade
        actions_per_round = Counter(a.round_number for a in self.actions)
        if actions_per_round:
            avg = sum(actions_per_round.values()) / len(actions_per_round)
            viral_rounds = [r for r, c in actions_per_round.items() if c > avg * 2]
            if viral_rounds:
                patterns.append({
                    "type": "viral_events",
                    "rounds": viral_rounds[:5],
                    "count": len(viral_rounds),
                    "interpretation": f"{len(viral_rounds)} rodadas com atividade viral (>2x média)",
                })

        return patterns


# ═══════════════════════════════════════════════════════════════════
# SIMULATION RUNNER (High-level API)
# ═══════════════════════════════════════════════════════════════════

def run_brazil_simulation(rounds: int = 50, agents: int = 200,
                          inject_events: bool = True) -> Dict[str, Any]:
    """Executa simulação completa do Brasil.

    Supera MiroFish original: 200+ agentes, 50 rodadas,
    persistência SQLite, análise de padrões emergentes,
    BRAZIL_TIMEZONE, Teoria dos Jogos integrada.
    """
    engine = SimulationEngine(name="Brazil_MiroFish", db_path=".reversa/sim_brazil.db")

    # Criar agentes de stakeholders brasileiros
    profiles = [
        {"name": "Ministro da Fazenda", "labels": ["Official"],
         "activity_config": {"activity_level": 0.3, "influence_weight": 3.0, "stance": "supportive", "sentiment_bias": 0.2}},
        {"name": "Presidente do BC", "labels": ["Official"],
         "activity_config": {"activity_level": 0.2, "influence_weight": 2.8, "stance": "neutral", "sentiment_bias": 0.0}},
        {"name": "CEO Startup IA", "labels": ["Person"],
         "activity_config": {"activity_level": 0.7, "influence_weight": 2.0, "stance": "supportive", "sentiment_bias": 0.5}},
        {"name": "Sindicalista", "labels": ["Person"],
         "activity_config": {"activity_level": 0.8, "influence_weight": 1.5, "stance": "critical", "sentiment_bias": -0.3}},
    ]
    engine.create_agents_from_profiles(profiles)
    engine.create_agents_batch(agents - len(profiles))

    # Eventos externos
    if inject_events:
        engine.inject_event(
            "Nova regulamentação de IA aprovada no Congresso",
            "Marco regulatório exige transparência e limites para IA generativa",
            impact=0.8, round_num=10, duration=3,
        )
        engine.inject_event(
            "Bolha das IAs: NVIDIA perde 30% em uma semana",
            "Investidores questionam valuations de empresas de IA",
            impact=0.9, round_num=25, duration=5,
        )
        engine.inject_event(
            "Brasil anuncia investimento recorde em P&D: R$ 50 bi",
            "Governo lança programa de inovação com foco em IA e biotecnologia",
            impact=0.7, round_num=40, duration=4,
        )

    return engine.run_simulation(rounds=rounds, agents=agents)


# ═══════════════════════════════════════════════════════════════════
# CLI / Test
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="P20 Simulation Runner")
    parser.add_argument("--rounds", type=int, default=50, help="Número de rodadas")
    parser.add_argument("--agents", type=int, default=200, help="Número de agentes")
    parser.add_argument("--no-events", action="store_true", help="Sem eventos externos")
    args = parser.parse_args()

    stats = run_brazil_simulation(
        rounds=args.rounds,
        agents=args.agents,
        inject_events=not args.no_events,
    )

    print(f"\n📊 ESTATÍSTICAS FINAIS:")
    for k, v in stats.items():
        if k != "emergent_patterns":
            print(f"   {k}: {v}")

    print(f"\n🔍 PADRÕES EMERGENTES:")
    for p in stats.get("emergent_patterns", []):
        print(f"   [{p['type']}] {p['interpretation']} (score: {p.get('score', '?')})")
