"""
Step-by-step LLM Config Generator — P13
Gera configuracoes complexas usando LLM em multiplas etapas com fallback heuristico.
Inspirado pelo SimulationConfigGenerator do MiroFish-Offline.
"""
import json
import math
import re
import time
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime

BRAZIL_TIMEZONE = {
    # Brasil (UTC-3, horário de Brasília)
    # Dados de uso de redes sociais: Twitter/Instagram peak 12h-14h (almoço) e 19h-22h (pós-trabalho)
    # WhatsApp: uso contínuo 6h-23h com picos comerciais 8h-18h
    "dead_hours": [0, 1, 2, 3, 4],
    "morning_hours": [5, 6, 7],
    "work_hours": [8, 9, 10, 11, 13, 14, 15, 16, 17],
    "lunch_hours": [12],
    "peak_hours": [18, 19, 20, 21, 22],
    "night_hours": [23],
    "activity_multipliers": {
        "dead": 0.03, "morning": 0.4, "work": 0.65,
        "lunch": 0.85, "peak": 1.5, "night": 0.45
    }
}

# Alias para compatibilidade retroativa
CHINA_TIMEZONE = BRAZIL_TIMEZONE

TYPE_ALIASES = {
    "official": "Official", "gov": "Official", "government": "Official",
    "media": "MediaOutlet", "news": "MediaOutlet", "press": "MediaOutlet",
    "broadcast": "MediaOutlet", "journalist": "MediaOutlet",
    "student": "Student", "undergrad": "Student", "graduate": "Student",
    "professor": "Professor", "prof": "Professor", "teacher": "Professor",
    "faculty": "Professor", "academic": "Professor",
    "alumni": "Alumni", "alum": "Alumni", "former": "Alumni",
    "person": "Person", "individual": "Person", "user": "Person",
    "citizen": "Person", "public": "Person",
    "university": "Official", "instituicao": "Official", "orgao": "Official",
}

TYPE_RULES = {
    "Official": {
        "post_frequency": (0.3, 0.5),
        "activity_hours": list(range(8, 19)),
        "writing_style": "formal",
        "credibility_score": (0.7, 0.95),
        "influence_score": (0.6, 0.9),
        "stance_weights": {"Apoio": 0.5, "Neutro": 0.4, "Oposicao": 0.1},
        "topics_focus": ["politicas", "regulamentacao", "comunicados"],
    },
    "MediaOutlet": {
        "post_frequency": (0.6, 1.0),
        "activity_hours": list(range(6, 23)),
        "writing_style": "formal",
        "credibility_score": (0.5, 0.85),
        "influence_score": (0.7, 0.95),
        "stance_weights": {"Apoio": 0.2, "Neutro": 0.6, "Oposicao": 0.2},
        "topics_focus": ["noticias", "reportagens", "cobertura"],
    },
    "Student": {
        "post_frequency": (0.4, 0.8),
        "activity_hours": list(range(14, 23)) + [12, 13],
        "writing_style": "casual",
        "credibility_score": (0.2, 0.5),
        "influence_score": (0.2, 0.5),
        "stance_weights": {"Apoio": 0.4, "Neutro": 0.2, "Oposicao": 0.4},
        "topics_focus": ["protestos", "debates", "redes sociais"],
    },
    "Professor": {
        "post_frequency": (0.2, 0.4),
        "activity_hours": list(range(8, 18)),
        "writing_style": "tecnico",
        "credibility_score": (0.7, 0.95),
        "influence_score": (0.5, 0.8),
        "stance_weights": {"Apoio": 0.3, "Neutro": 0.5, "Oposicao": 0.2},
        "topics_focus": ["pesquisa", "educacao", "analise"],
    },
    "Alumni": {
        "post_frequency": (0.1, 0.3),
        "activity_hours": list(range(18, 23)) + list(range(7, 10)),
        "writing_style": "variado",
        "credibility_score": (0.3, 0.6),
        "influence_score": (0.3, 0.6),
        "stance_weights": {"Apoio": 0.4, "Neutro": 0.4, "Oposicao": 0.2},
        "topics_focus": ["opiniao", "experiencia", "conexoes"],
    },
    "Person": {
        "post_frequency": (0.3, 0.6),
        "activity_hours": list(range(7, 23)),
        "writing_style": "casual",
        "credibility_score": (0.1, 0.4),
        "influence_score": (0.1, 0.4),
        "stance_weights": {"Apoio": 0.3, "Neutro": 0.4, "Oposicao": 0.3},
        "topics_focus": ["cotidiano", "opiniao", "reacoes"],
    },
}


@dataclass
class TimeSimulationConfig:
    total_rounds: int = 100
    round_interval_minutes: int = 15
    activity_timezone: str = "Asia/Shanghai"
    timezone_dead_hours: List[int] = field(default_factory=lambda: [0, 1, 2, 3, 4, 5])
    timezone_peak_hours: List[int] = field(default_factory=lambda: [19, 20, 21, 22])
    peak_activity_probability: float = 0.85
    base_activity_probability: float = 0.35
    scheduled_posts_per_peak_hour: int = 8
    scheduled_posts_per_regular_hour: int = 3
    random_activity_ratio: float = 0.3
    dead_hour_noise: float = 0.02

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class EventConfig:
    initial_posts: List[Dict] = field(default_factory=list)
    trending_topic: str = ""
    narrative_tags: List[str] = field(default_factory=list)
    event_intensity: str = "Media"
    controversy_level: float = 0.5
    polarization_expected: float = 0.5
    ai_influence_expected: float = 0.5
    external_factors: List[str] = field(default_factory=list)
    simulation_objective: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class AgentActivityConfig:
    entity_type: str = "Person"
    name: str = ""
    summary: str = ""
    post_frequency: float = 0.3
    activity_hours: List[int] = field(default_factory=lambda: list(range(8, 22)))
    topics: List[str] = field(default_factory=list)
    writing_style: str = "casual"
    credibility_score: float = 0.3
    influence_score: float = 0.3
    stance: str = "Neutro"
    interaction_targets: List[str] = field(default_factory=list)
    ai_usage_probability: float = 0.3
    platform_weights: Dict[str, float] = field(default_factory=lambda: {"twitter": 0.5, "reddit": 0.5})

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class PlatformConfig:
    algorithm_weights: Dict[str, float] = field(default_factory=lambda: {
        "recency": 0.3, "engagement": 0.3, "relevance": 0.2, "credibility": 0.1, "diversity": 0.1
    })
    content_moderation_threshold: float = 0.7
    virality_threshold: float = 0.8
    echo_chamber_factor: float = 0.4
    cross_platform_boost: float = 0.2
    trending_noise: float = 0.1
    recommendation_sensitivity: float = 0.6

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class SimulationParameters:
    simulation_id: str = ""
    requirement: str = ""
    timestamp: str = ""
    time_config: Optional[TimeSimulationConfig] = None
    event_config: Optional[EventConfig] = None
    agent_configs: List[AgentActivityConfig] = field(default_factory=list)
    platform_config: Optional[PlatformConfig] = None
    confidence_score: float = 0.0
    generation_steps: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        d = asdict(self)
        d["timestamp"] = self.timestamp or datetime.now().isoformat()
        return d

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


class ConfigGenerator:
    MAX_CONTEXT_LENGTH = 50000
    AGENTS_PER_BATCH = 15

    def __init__(self, api_key: str = None, base_url: str = None, model: str = None):
        self.llm_available = bool(api_key)
        self.model = model or "gpt-4o"
        self.base_url = base_url
        self.client = None
        if self.llm_available:
            try:
                from openai import OpenAI
                kwargs = {"api_key": api_key}
                if base_url:
                    kwargs["base_url"] = base_url
                self.client = OpenAI(**kwargs)
            except ImportError:
                self.llm_available = False

    def generate(
        self,
        simulation_id: str,
        requirement: str,
        entities: List[Dict],
        enable_twitter: bool = True,
        enable_reddit: bool = True,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> SimulationParameters:
        params = SimulationParameters(
            simulation_id=simulation_id,
            requirement=requirement,
            timestamp=datetime.now().isoformat()
        )
        steps_completed = []
        steps_fallback = []

        def progress(msg: str):
            params.generation_steps.append(msg)
            if progress_callback:
                progress_callback(msg)

        context = self._build_context(requirement, entities)

        progress("Step 1/4: Generating time config...")
        try:
            time_result = self._generate_time_config(context, len(entities))
            params.time_config = self._parse_time_config(time_result, len(entities))
            steps_completed.append("time_llm")
        except Exception as e:
            progress(f"  Time LLM failed: {e}, using fallback")
            params.time_config = self._get_default_time_config(len(entities))
            steps_fallback.append("time")
        progress(f"  Rounds: {params.time_config.total_rounds}, Peak: {params.time_config.timezone_peak_hours}")

        progress("Step 2/4: Generating event config...")
        try:
            event_result = self._generate_event_config(context, requirement, entities)
            params.event_config = self._parse_event_config(event_result)
            steps_completed.append("event_llm")
        except Exception as e:
            progress(f"  Event LLM failed: {e}, using fallback")
            params.event_config = EventConfig(
                trending_topic=requirement[:80],
                narrative_tags=[requirement.split()[0]] if requirement.split() else ["geral"],
                event_intensity="Media",
                controversy_level=0.5,
                simulation_objective=requirement
            )
            steps_fallback.append("event")
        progress(f"  Topic: {params.event_config.trending_topic[:50]}...")

        progress("Step 3/4: Generating agent configs...")
        all_agent_configs = []
        total_agents = len(entities)
        for start_idx in range(0, total_agents, self.AGENTS_PER_BATCH):
            batch_num = start_idx // self.AGENTS_PER_BATCH + 1
            end_idx = min(start_idx + self.AGENTS_PER_BATCH, total_agents)
            progress(f"  Agent batch {batch_num}/{(total_agents-1)//self.AGENTS_PER_BATCH+1} ({start_idx}-{end_idx})...")
            try:
                batch_configs = self._generate_agent_configs_batch(
                    context, entities, start_idx, requirement
                )
                all_agent_configs.extend(batch_configs)
                steps_completed.append(f"agent_batch_{batch_num}_llm")
            except Exception as e:
                progress(f"  Agent batch {batch_num} LLM failed: {e}, using rule fallback")
                for i in range(start_idx, end_idx):
                    entity = entities[i] if i < len(entities) else {}
                    rule_config = self._generate_agent_config_by_rule(entity)
                    agent = AgentActivityConfig(
                        entity_type=rule_config.get("entity_type", "Person"),
                        name=entity.get("name", f"entity_{i}"),
                        summary=entity.get("summary", ""),
                        post_frequency=rule_config["post_frequency"],
                        activity_hours=rule_config["activity_hours"],
                        topics=rule_config["topics"],
                        writing_style=rule_config["writing_style"],
                        credibility_score=rule_config["credibility_score"],
                        influence_score=rule_config["influence_score"],
                        stance=rule_config["stance"],
                        platform_weights={"twitter": 0.6 if enable_twitter else 0.0,
                                          "reddit": 0.4 if enable_reddit else 0.0}
                    )
                    all_agent_configs.append(agent)
                steps_fallback.append(f"agent_batch_{batch_num}")
        params.agent_configs = all_agent_configs
        progress(f"  Generated {len(all_agent_configs)} agent configs")

        progress("Assigning initial post agents...")
        params.event_config = self._assign_initial_post_agents(params.event_config, params.agent_configs)

        progress("Step 4/4: Generating platform config...")
        try:
            platform_result = self._generate_platform_config(
                context, requirement, params.time_config, params.event_config, len(entities)
            )
            params.platform_config = self._parse_platform_config(platform_result)
            steps_completed.append("platform_llm")
        except Exception as e:
            progress(f"  Platform LLM failed: {e}, using fallback")
            params.platform_config = self._get_default_platform_config(params.event_config.event_intensity)
            steps_fallback.append("platform")

        params.confidence_score = self._compute_confidence(steps_completed, steps_fallback)
        progress(f"Confidence score: {params.confidence_score:.2f}")
        progress("Generation complete.")
        return params

    def _compute_confidence(self, steps_completed: List[str], steps_fallback: List[str]) -> float:
        total_steps = max(len(steps_completed) + len(steps_fallback), 1)
        fallback_ratio = len(steps_fallback) / total_steps
        if not self.llm_available:
            return max(0.0, 0.29 - fallback_ratio * 0.1)
        return max(0.0, 1.0 - fallback_ratio * 0.35)

    def _build_context(self, requirement: str, entities: List[Dict], document_text: Optional[str] = None) -> str:
        ctx = f"Requisito: {requirement}\n\nEntidades ({len(entities)}):\n"
        for i, e in enumerate(entities):
            name = e.get("name", f"Entidade {i}")
            etype = e.get("type", e.get("entity_type", "Person"))
            summary = e.get("summary", "")[:200]
            ctx += f"  [{i}] {name} ({etype}): {summary}\n"
        if document_text:
            remaining = self.MAX_CONTEXT_LENGTH - len(ctx)
            if remaining > 500:
                ctx += f"\nDocumento:\n{document_text[:remaining]}..."
        return ctx

    def _call_llm_with_retry(self, prompt: str, system_prompt: str, max_attempts: int = 3) -> Dict:
        temperatures = [0.7, 0.5, 0.3]
        last_error = None
        for attempt in range(max_attempts):
            try:
                temp = temperatures[attempt] if attempt < len(temperatures) else 0.2
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temp,
                    response_format={"type": "json_object"}
                )
                content = response.choices[0].message.content
                result = self._try_fix_config_json(content)
                if result is not None:
                    return result
                last_error = ValueError("JSON validation failed")
            except Exception as e:
                last_error = e
                if attempt < max_attempts - 1:
                    time.sleep(1)
        raise last_error or RuntimeError("LLM call failed after retries")

    def _fix_truncated_json(self, content: str) -> str:
        content = content.strip()
        if not content:
            return "{}"
        stack_open = 0
        in_string = False
        escape = False
        last_valid = 0
        for i, ch in enumerate(content):
            if escape:
                escape = False
                continue
            if ch == '\\' and in_string:
                escape = True
                continue
            if ch == '"' and not escape:
                in_string = not in_string
                continue
            if in_string:
                if ch == '\n':
                    content = content[:i] + '\\n' + content[i+1:]
                    continue
                continue
            if ch == '{':
                stack_open += 1
            elif ch == '}':
                stack_open -= 1
                if stack_open == 0:
                    last_valid = i + 1
            elif ch == '[':
                stack_open += 1
            elif ch == ']':
                stack_open -= 1
                if stack_open == 0:
                    last_valid = i + 1
        content = content[:last_valid]
        content = content.rstrip(',')
        content = re.sub(r',\s*([}\]])', r'\1', content)
        while stack_open > 0:
            content += '}'
            stack_open -= 1
        if not content.endswith('}') and not content.endswith(']'):
            content += '}'
        return content

    def _try_fix_config_json(self, content: str) -> Optional[Dict]:
        if not content:
            return None
        try:
            return json.loads(content.strip())
        except json.JSONDecodeError:
            pass
        try:
            fixed = self._fix_truncated_json(content)
            return json.loads(fixed)
        except (json.JSONDecodeError, ValueError):
            pass
        json_pattern = r'(\{.*\}|\[.*\])'
        match = re.search(json_pattern, content, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
        return None

    def _resolve_type_alias(self, type_str: str) -> str:
        if not type_str:
            return "Person"
        cleaned = type_str.strip().lower()
        if cleaned in TYPE_ALIASES:
            return TYPE_ALIASES[cleaned]
        if "student" in cleaned or "aluno" in cleaned:
            return "Student"
        if "professor" in cleaned or "teacher" in cleaned:
            return "Professor"
        if "media" in cleaned or "news" in cleaned or "jornal" in cleaned:
            return "MediaOutlet"
        if "official" in cleaned or "gov" in cleaned or "orgao" in cleaned:
            return "Official"
        if "alumni" in cleaned or "ex-" in cleaned:
            return "Alumni"
        return "Person"

    def _generate_time_config(self, context: str, num_entities: int) -> Dict:
        if not self.llm_available:
            raise RuntimeError("LLM not available")
        prompt = (
            f"Com base no contexto abaixo, gere uma configuracao de tempo para simulacao "
            f"com {num_entities} entidades.\n\n{context}\n\n"
            f"Retorne JSON com: total_rounds (80-200), round_interval_minutes (5-30), "
            f"activity_timezone (string), peak_activity_probability (0.5-1.0), "
            f"base_activity_probability (0.2-0.6), scheduled_posts_per_peak_hour (5-15), "
            f"scheduled_posts_per_regular_hour (1-5), random_activity_ratio (0.2-0.5), "
            f"dead_hour_noise (0.01-0.05)."
        )
        system = "Voce e um gerador de configuracoes de simulacao. Retorne APENAS JSON valido."
        result = self._call_llm_with_retry(prompt, system)
        result.setdefault("timezone_dead_hours", CHINA_TIMEZONE["dead_hours"])
        result.setdefault("timezone_peak_hours", CHINA_TIMEZONE["peak_hours"])
        return result

    def _get_default_time_config(self, num_entities: int) -> TimeSimulationConfig:
        rounds = min(200, max(80, num_entities * 2))
        return TimeSimulationConfig(
            total_rounds=rounds,
            round_interval_minutes=15,
            activity_timezone="Asia/Shanghai",
            timezone_dead_hours=CHINA_TIMEZONE["dead_hours"],
            timezone_peak_hours=CHINA_TIMEZONE["peak_hours"],
            peak_activity_probability=0.85,
            base_activity_probability=0.35,
            scheduled_posts_per_peak_hour=min(15, max(5, num_entities // 10)),
            scheduled_posts_per_regular_hour=min(5, max(1, num_entities // 30)),
            random_activity_ratio=0.3,
            dead_hour_noise=0.02,
        )

    def _parse_time_config(self, result: Dict, num_entities: int) -> TimeSimulationConfig:
        return TimeSimulationConfig(
            total_rounds=max(10, min(500, int(result.get("total_rounds", 100)))),
            round_interval_minutes=max(1, min(120, int(result.get("round_interval_minutes", 15)))),
            activity_timezone=str(result.get("activity_timezone", "Asia/Shanghai")),
            timezone_dead_hours=result.get("timezone_dead_hours", CHINA_TIMEZONE["dead_hours"]),
            timezone_peak_hours=result.get("timezone_peak_hours", CHINA_TIMEZONE["peak_hours"]),
            peak_activity_probability=max(0.0, min(1.0, float(result.get("peak_activity_probability", 0.85)))),
            base_activity_probability=max(0.0, min(1.0, float(result.get("base_activity_probability", 0.35)))),
            scheduled_posts_per_peak_hour=max(0, int(result.get("scheduled_posts_per_peak_hour", 8))),
            scheduled_posts_per_regular_hour=max(0, int(result.get("scheduled_posts_per_regular_hour", 3))),
            random_activity_ratio=max(0.0, min(1.0, float(result.get("random_activity_ratio", 0.3)))),
            dead_hour_noise=max(0.0, min(1.0, float(result.get("dead_hour_noise", 0.02)))),
        )

    def _generate_event_config(self, context: str, requirement: str, entities: List) -> Dict:
        if not self.llm_available:
            raise RuntimeError("LLM not available")
        entity_summaries = "\n".join(
            f"- {e.get('name', '?')} ({e.get('type', '?')})" for e in entities[:10]
        )
        prompt = (
            f"Gere configuracao de evento para simulacao.\n"
            f"Requisito: {requirement}\n"
            f"Entidades principais:\n{entity_summaries}\n\n"
            f"Retorne JSON com: initial_posts (array de ate 5 objetos com content, author_type), "
            f"trending_topic (string), narrative_tags (array), "
            f"event_intensity ('Baixa'|'Media'|'Alta'), "
            f"controversy_level (0.0-1.0), polarization_expected (0.0-1.0), "
            f"ai_influence_expected (0.0-1.0), simulation_objective (string)."
        )
        system = "Voce e um gerador de eventos de simulacao. Retorne APENAS JSON valido."
        return self._call_llm_with_retry(prompt, system)

    def _parse_event_config(self, result: Dict) -> EventConfig:
        intensity = result.get("event_intensity", "Media")
        if intensity not in ("Baixa", "Media", "Alta"):
            intensity = "Media"
        initial_posts = result.get("initial_posts", [])
        if not isinstance(initial_posts, list):
            initial_posts = []
        return EventConfig(
            initial_posts=initial_posts[:25],
            trending_topic=str(result.get("trending_topic", "")),
            narrative_tags=[str(t) for t in (result.get("narrative_tags") or [])],
            event_intensity=intensity,
            controversy_level=max(0.0, min(1.0, float(result.get("controversy_level", 0.5)))),
            polarization_expected=max(0.0, min(1.0, float(result.get("polarization_expected", 0.5)))),
            ai_influence_expected=max(0.0, min(1.0, float(result.get("ai_influence_expected", 0.5)))),
            external_factors=[str(f) for f in (result.get("external_factors") or [])],
            simulation_objective=str(result.get("simulation_objective", "")),
        )

    def _generate_agent_configs_batch(self, context: str, entities: List, start_idx: int, requirement: str) -> List[AgentActivityConfig]:
        if not self.llm_available:
            raise RuntimeError("LLM not available")
        end_idx = min(start_idx + self.AGENTS_PER_BATCH, len(entities))
        batch_entities = entities[start_idx:end_idx]
        entity_block = "\n".join(
            f"[{i}] {e.get('name', '?')} | type: {e.get('type', e.get('entity_type', 'Person'))} | {e.get('summary', '')[:100]}"
            for i, e in enumerate(batch_entities)
        )
        prompt = (
            f"Gere configuracoes de agente para as seguintes entidades (lote {start_idx}-{end_idx-1}).\n"
            f"Requisito: {requirement}\n\n"
            f"Entidades:\n{entity_block}\n\n"
            f"Retorne JSON com chave 'agents' contendo array de objetos. Cada objeto: "
            f"entity_type (Official|MediaOutlet|Student|Professor|Alumni|Person), "
            f"post_frequency (0.0-1.0), activity_hours (lista de horas 0-23), "
            f"topics (lista), writing_style (formal|casual|tecnico|emocional), "
            f"credibility_score (0.0-1.0), influence_score (0.0-1.0), "
            f"stance (Apoio|Neutro|Oposicao), ai_usage_probability (0.0-1.0)."
        )
        system = "Voce e um gerador de configuracoes de agentes. Retorne APENAS JSON valido."
        result = self._call_llm_with_retry(prompt, system)
        agents_data = result.get("agents", result.get("agent_configs", []))
        if not isinstance(agents_data, list):
            agents_data = [result]
        configs = []
        for i, ad in enumerate(agents_data):
            entity = batch_entities[i] if i < len(batch_entities) else {}
            etype = self._resolve_type_alias(ad.get("entity_type", entity.get("type", "Person")))
            configs.append(AgentActivityConfig(
                entity_type=etype,
                name=str(ad.get("name", entity.get("name", f"agent_{start_idx+i}"))),
                summary=str(ad.get("summary", entity.get("summary", ""))),
                post_frequency=max(0.0, min(1.0, float(ad.get("post_frequency", 0.3)))),
                activity_hours=[int(h) for h in (ad.get("activity_hours") or [])] or list(range(8, 22)),
                topics=[str(t) for t in (ad.get("topics") or [])],
                writing_style=str(ad.get("writing_style", "casual")),
                credibility_score=max(0.0, min(1.0, float(ad.get("credibility_score", 0.5)))),
                influence_score=max(0.0, min(1.0, float(ad.get("influence_score", 0.5)))),
                stance=str(ad.get("stance", "Neutro")),
                ai_usage_probability=max(0.0, min(1.0, float(ad.get("ai_usage_probability", 0.3)))),
            ))
        return configs

    def _generate_agent_config_by_rule(self, entity: Dict) -> Dict:
        raw_type = entity.get("type", entity.get("entity_type", "Person"))
        etype = self._resolve_type_alias(raw_type)
        rules = TYPE_RULES.get(etype, TYPE_RULES["Person"])
        import random
        freq_min, freq_max = rules["post_frequency"]
        cred_min, cred_max = rules["credibility_score"]
        inf_min, inf_max = rules["influence_score"]
        stance_weights = rules["stance_weights"]
        stance = random.choices(
            list(stance_weights.keys()),
            weights=list(stance_weights.values())
        )[0]
        return {
            "entity_type": etype,
            "post_frequency": round(random.uniform(freq_min, freq_max), 2),
            "activity_hours": rules["activity_hours"],
            "topics": rules["topics_focus"][:],
            "writing_style": rules["writing_style"],
            "credibility_score": round(random.uniform(cred_min, cred_max), 2),
            "influence_score": round(random.uniform(inf_min, inf_max), 2),
            "stance": stance,
        }

    def _assign_initial_post_agents(self, event_config: EventConfig, agent_configs: List[AgentActivityConfig]) -> EventConfig:
        assigned_posts = []
        for post in event_config.initial_posts:
            author_type = post.get("author_type", "")
            if author_type:
                matched = [a for a in agent_configs if a.entity_type == self._resolve_type_alias(author_type)]
                if matched:
                    import random
                    agent = random.choice(matched)
                    post["assigned_agent"] = agent.name
            assigned_posts.append(post)
        event_config.initial_posts = assigned_posts
        return event_config

    def _generate_platform_config(self, context: str, requirement: str, time_config: TimeSimulationConfig, event_config: EventConfig, num_agents: int) -> Dict:
        if not self.llm_available:
            raise RuntimeError("LLM not available")
        prompt = (
            f"Gere configuracao de plataforma para simulacao.\n"
            f"Requisito: {requirement}\n"
            f"Intensidade do evento: {event_config.event_intensity}\n"
            f"Numero de agentes: {num_agents}\n"
            f"Rounds: {time_config.total_rounds}\n\n"
            f"Retorne JSON com: algorithm_weights (objeto com keys recency/engagement/relevance/credibility/diversity, "
            f"soma=1.0), content_moderation_threshold (0.5-0.9), "
            f"virality_threshold (0.6-0.95), echo_chamber_factor (0.2-0.7), "
            f"cross_platform_boost (0.1-0.5), trending_noise (0.05-0.3), "
            f"recommendation_sensitivity (0.3-0.9)."
        )
        system = "Voce e um gerador de configuracoes de plataforma. Retorne APENAS JSON valido."
        return self._call_llm_with_retry(prompt, system)

    def _parse_platform_config(self, result: Dict) -> PlatformConfig:
        aw = result.get("algorithm_weights", {})
        total = sum(float(v) for v in aw.values()) or 1.0
        return PlatformConfig(
            algorithm_weights={k: float(v) / total for k, v in aw.items()},
            content_moderation_threshold=max(0.0, min(1.0, float(result.get("content_moderation_threshold", 0.7)))),
            virality_threshold=max(0.0, min(1.0, float(result.get("virality_threshold", 0.8)))),
            echo_chamber_factor=max(0.0, min(1.0, float(result.get("echo_chamber_factor", 0.4)))),
            cross_platform_boost=max(0.0, min(1.0, float(result.get("cross_platform_boost", 0.2)))),
            trending_noise=max(0.0, min(1.0, float(result.get("trending_noise", 0.1)))),
            recommendation_sensitivity=max(0.0, min(1.0, float(result.get("recommendation_sensitivity", 0.6)))),
        )

    def _get_default_platform_config(self, event_intensity: str) -> PlatformConfig:
        intensity_mult = {"Baixa": 0.7, "Media": 1.0, "Alta": 1.3}.get(event_intensity, 1.0)
        return PlatformConfig(
            algorithm_weights={"recency": 0.3, "engagement": 0.3, "relevance": 0.2, "credibility": 0.1, "diversity": 0.1},
            content_moderation_threshold=max(0.5, min(0.9, 0.7 * intensity_mult)),
            virality_threshold=max(0.6, min(0.95, 0.8 * intensity_mult)),
            echo_chamber_factor=max(0.2, min(0.7, 0.4 * intensity_mult)),
            cross_platform_boost=min(0.5, 0.2 * intensity_mult),
            trending_noise=min(0.3, 0.1 * intensity_mult),
            recommendation_sensitivity=max(0.3, min(0.9, 0.6 * intensity_mult)),
        )

    @classmethod
    def demo(cls):
        print("=" * 50)
        print("P13 Config Generator Demo")
        print("Step-by-step LLM Config Generator")
        print("=" * 50)
        gen = cls(api_key="")
        entities = [
            {"name": "Universidade Federal", "type": "Official", "summary": "Instituicao de ensino superior publica federal"},
            {"name": "Joao Aluno", "type": "Student", "summary": "Estudante de ciencias sociais, ativo em politica estudantil"},
            {"name": "Maria Professora", "type": "Professor", "summary": "Professora de direito constitucional, 15 anos de carreira"},
            {"name": "Portal de Noticias", "type": "MediaOutlet", "summary": "Portal independente de noticias universitarias"},
            {"name": "Carlos Alumni", "type": "Alumni", "summary": "Ex-aluno, atual empresario do setor de tecnologia"},
            {"name": "Ana Cidada", "type": "Person", "summary": "Moradora da regiao, acompanha noticias locais"},
        ]
        params = gen.generate("demo-001", "Debate sobre reforma universitaria", entities)
        print("\n" + params.to_json())
        print("\n" + "=" * 50)
        print(f"Confidence: {params.confidence_score:.2f}")
        print(f"Steps: {params.generation_steps}")
        print("=" * 50)

    # ── P18 Integration: Sensitivity Analyzer ──────────────────────────
    def analyze_sensitivity(self, event_intensity: str = "Media",
                           num_agents_range: list = None) -> dict:
        """Análise de sensibilidade dos parâmetros de simulação.

        Integra SensitivityAnalyzer + StatisticalRigor do nexus-phd-strategist.
        Varia parâmetros-chave e mede impacto nas projeções.
        """
        try:
            import sys
            sys.path.insert(0, r"C:\Users\marce\.config\opencode\skills\agent-forum\scripts")
            from phd_auditor import SensitivityAnalyzer, StatisticalRigor
        except ImportError:
            return {"error": "phd_auditor module not available"}

        if num_agents_range is None:
            num_agents_range = [3, 5, 8, 12, 20]

        # Baseline
        baseline_config = self._get_default_platform_config(event_intensity)

        def config_impact_fn(params: dict) -> float:
            """Mede impacto agregado da configuração (0-100)."""
            score = 0
            score += params.get("virality_threshold", 0.8) * 30
            score += (1 - params.get("echo_chamber_factor", 0.4)) * 25
            score += params.get("cross_platform_boost", 0.2) * 20
            score += params.get("recommendation_sensitivity", 0.6) * 15
            score += params.get("content_moderation_threshold", 0.7) * 10
            return score

        sa = SensitivityAnalyzer.analyze(
            base_conclusion={
                "parameters": {
                    "virality_threshold": baseline_config.virality_threshold,
                    "echo_chamber_factor": baseline_config.echo_chamber_factor,
                    "cross_platform_boost": baseline_config.cross_platform_boost,
                    "recommendation_sensitivity": baseline_config.recommendation_sensitivity,
                    "content_moderation_threshold": baseline_config.content_moderation_threshold,
                }
            },
            parameters={
                "virality_threshold": [0.5, baseline_config.virality_threshold, 0.95],
                "echo_chamber_factor": [0.2, baseline_config.echo_chamber_factor, 0.7],
                "num_agents": num_agents_range,
            },
            compute_fn=config_impact_fn,
        )

        # Adicionar rigor estatístico
        sa["bonferroni"] = StatisticalRigor.bonferroni_correction(
            [0.01, 0.02, 0.04, 0.08, 0.15]
        )
        sa["power_analysis"] = StatisticalRigor.statistical_power(
            effect_size=0.6, n=len(num_agents_range), alpha=0.05
        )

        return sa
        print("Demo concluida. Use o modo com LLM (api_key) para geracao completa.")
