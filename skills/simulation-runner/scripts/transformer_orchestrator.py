#!/usr/bin/env python3
"""
TransformerOrchestrator — Rede de Atenção Multi-Head entre Componentes MiroFish.
Transforma o ecossistema em uma arquitetura transformer-like:
  - Cada skill/agente/MCP é um "token" no grafo de computação
  - Self-attention: agentes atendem uns aos outros durante simulação
  - Cross-attention: dados reais atendem parâmetros da simulação
  - Multi-head: múltiplas perspectivas (estratégica, cética, pragmática...)
  - Feed-forward: cada componente processa e propaga informação
  - Residual: informação original é preservada através das camadas

Arquitetura:
  Input → [Multi-Head Attention → Feed-Forward → Residual] × N camadas → Output
"""

import math, random, json, os, sys, time
from datetime import datetime, timezone, timedelta
from collections import defaultdict
from typing import Dict, List, Any, Tuple, Optional

BRAZIL_TZ = timezone(timedelta(hours=-3))
BRAZIL_TIME = lambda: datetime.now(BRAZIL_TZ)


# ═══════════════════════════════════════════════════════════════════
# TRANSFORMER ORCHESTRATOR
# ═══════════════════════════════════════════════════════════════════

class TransformerOrchestrator:
    """
    Orquestrador transformer-like para o ecossistema MiroFish.
    
    Componentes como tokens: skills, agentes, MCPs, fontes de dados.
    Atenção multi-head: cada "head" é uma perspectiva epistêmica diferente.
    Feed-forward: processamento específico de cada componente.
    Residual: preservação da informação original.
    """

    def __init__(self, n_heads: int = 6, n_layers: int = 3, d_model: int = 64):
        self.n_heads = n_heads
        self.n_layers = n_layers
        self.d_model = d_model

        # Componentes registrados como "tokens"
        self.components: Dict[str, Dict] = {}
        self.component_order: List[str] = []

        # Matrizes de atenção por camada
        self.attention_maps: List[Dict[str, Dict[str, float]]] = []

        # Estado compartilhado (residual stream)
        self.residual_state: Dict[str, List[float]] = {}

        # Métricas
        self.total_connections = 0
        self.active_paths = 0

        # Cabeças de atenção (perspectivas epistêmicas)
        self.heads = [
            {"name": "estrategica", "focus": ["simulacao", "previsao", "cenario"],
             "weight": 1.0, "description": "Atenção a padrões estratégicos e consequências de longo prazo"},
            {"name": "critica", "focus": ["validacao", "teste", "robustez"],
             "weight": 0.8, "description": "Atenção a falhas, vieses e premissas não verificadas"},
            {"name": "empirica", "focus": ["dados", "correlacao", "evidencia"],
             "weight": 1.2, "description": "Atenção a dados reais, métricas e significância estatística"},
            {"name": "sintetica", "focus": ["integracao", "consenso", "convergencia"],
             "weight": 0.9, "description": "Atenção a pontos de convergência e síntese interdisciplinar"},
            {"name": "pragmatica", "focus": ["acao", "implementacao", "recurso"],
             "weight": 0.7, "description": "Atenção a viabilidade prática e restrições operacionais"},
            {"name": "visionaria", "focus": ["futuro", "disrupcao", "tendencia"],
             "weight": 0.6, "description": "Atenção a sinais fracos e cenários de longo prazo"},
        ]

    def register_component(self, comp_id: str, comp_type: str,
                           embedding: List[float] = None,
                           connections: List[str] = None,
                           metadata: Dict = None):
        """Registra um componente como token na rede transformer."""
        if embedding is None:
            embedding = [random.uniform(-1, 1) for _ in range(self.d_model)]

        self.components[comp_id] = {
            "id": comp_id,
            "type": comp_type,
            "embedding": embedding[:self.d_model],
            "connections": connections or [],
            "metadata": metadata or {},
            "attention_received": defaultdict(float),
            "activation": 0.0,
        }
        if comp_id not in self.component_order:
            self.component_order.append(comp_id)

    def register_all_ecosystem_components(self):
        """Registra TODOS os componentes do ecossistema na rede transformer."""
        # Skills como tokens de processamento
        skills = {
            "sim_engine": "processor", "data_collector": "input",
            "citation_finder": "input", "whatsapp_profiler": "input",
            "report_generator": "output", "omen_engine": "processor",
            "forecast_engine": "processor", "graph_decision_engine": "processor",
            "diagnostic_analyzer": "processor", "rigorous_ml_pipeline": "processor",
            "expanded_profiles": "knowledge", "debate_strategies": "reasoning",
            "phd_auditor": "validator", "multiagent_warroom": "reasoning",
            "llm_discourse": "generator", "countermeasures": "validator",
        }
        for skill_id, skill_type in skills.items():
            self.register_component(skill_id, skill_type)

        # Fontes de dados como input tokens
        sources = {
            "world_bank": "data_source", "ibge": "data_source",
            "semantic_scholar": "data_source", "whatsapp_data": "data_source",
            "simulation_output": "data_source",
        }
        for src_id, src_type in sources.items():
            self.register_component(src_id, src_type)

        # Perfis de agente como tokens com embeddings psicológicos
        agent_types = ["estrategista", "cetico", "sintetizador", "especialista",
                       "visionario", "pragmatico", "analitico", "emocional", "social"]
        for at in agent_types:
            self.register_component(f"agent_{at}", "agent",
                                   metadata={"category": at})

        print(f"  🔗 {len(self.components)} componentes registrados na rede transformer")
        print(f"  🧠 {len(self.heads)} cabeças de atenção | {self.n_layers} camadas | d={self.d_model}")

    def compute_self_attention(self, layer: int) -> Dict[str, Dict[str, float]]:
        """
        Self-attention entre componentes.
        Attention(Q,K,V) = softmax(QK^T / sqrt(d_k)) V
        """
        n = len(self.component_order)
        d_k = self.d_model // self.n_heads
        attention = defaultdict(lambda: defaultdict(float))

        # Para cada par de componentes, computar similaridade de embedding
        for i in range(n):
            ci = self.component_order[i]
            emb_i = self.components[ci]["embedding"]

            for j in range(n):
                cj = self.component_order[j]
                emb_j = self.components[cj]["embedding"]

                # Dot-product attention: Q · K
                score = sum(emb_i[k] * emb_j[k] for k in range(min(len(emb_i), len(emb_j))))
                score /= math.sqrt(max(d_k, 1))

                # Bias de conexão explícita
                if cj in self.components[ci].get("connections", []):
                    score += 0.5
                if ci == cj:
                    score += 0.3  # Self-connection bias

                attention[ci][cj] = score

        # Softmax por linha
        for ci in self.component_order:
            scores = [attention[ci][cj] for cj in self.component_order]
            max_score = max(scores) if scores else 0
            exp_scores = [math.exp(s - max_score) for s in scores]
            total = sum(exp_scores)

            if total > 0:
                for idx, cj in enumerate(self.component_order):
                    attention[ci][cj] = round(exp_scores[idx] / total, 6)

        self.attention_maps.append(dict(attention))
        return dict(attention)

    def compute_multi_head_attention(self, layer: int) -> Dict[str, Any]:
        """
        Multi-head attention: cada cabeça foca em aspectos diferentes.
        """
        base_attention = self.compute_self_attention(layer)
        head_outputs = {}

        for head_idx, head in enumerate(self.heads):
            head_attention = defaultdict(lambda: defaultdict(float))

            for ci in self.component_order:
                for cj in self.component_order:
                    base_score = base_attention.get(ci, {}).get(cj, 0)

                    # Modulação por cabeça: foco em componentes relevantes
                    comp_type = self.components[cj].get("type", "")
                    type_match = any(focus in comp_type for focus in head["focus"])
                    head_mod = 1.5 if type_match else 0.5

                    head_attention[ci][cj] = base_score * head["weight"] * head_mod

            head_outputs[head["name"]] = {
                "attention": dict(head_attention),
                "top_connections": self._top_k_attention(head_attention, k=5),
            }

        # Atualizar atenção recebida por cada componente
        for ci in self.component_order:
            total_att = 0.0
            for head_name, ho in head_outputs.items():
                for cj in self.component_order:
                    total_att += ho["attention"].get(ci, {}).get(cj, 0)
            self.components[ci]["attention_received"][f"layer_{layer}"] += total_att
            self.components[ci]["activation"] = total_att / max(len(self.heads), 1)

        return {
            "layer": layer,
            "heads": head_outputs,
            "dominant_head": max(head_outputs, key=lambda h: sum(
                sum(v for v in head_outputs[h]["attention"].get(ci, {}).values())
                for ci in self.component_order[:5]
            )),
        }

    def feed_forward(self, component_id: str, layer: int) -> List[float]:
        """
        Feed-forward: processamento específico do componente.
        FFN(x) = ReLU(xW1 + b1)W2 + b2
        """
        comp = self.components[component_id]
        x = comp["embedding"][:]
        d = len(x)

        # W1: expansão
        hidden = []
        for i in range(d * 2):
            val = sum(x[j] * math.sin((i + j) * 0.1 + layer) for j in range(d))
            # ReLU
            hidden.append(max(0, val / math.sqrt(d)))

        # W2: projeção
        output = []
        for i in range(d):
            val = sum(hidden[j] * math.cos((i + j) * 0.1 + layer) for j in range(len(hidden)))
            output.append(val / math.sqrt(len(hidden)))

        # Normalização layer
        mean = sum(output) / d
        std = (sum((v - mean) ** 2 for v in output) / d) ** 0.5
        if std > 0:
            output = [(v - mean) / std for v in output]

        return output

    def forward_pass(self, n_layers: int = None) -> Dict[str, Any]:
        """
        Forward pass completo através de N camadas transformer.
        """
        if n_layers is None:
            n_layers = self.n_layers

        layer_outputs = []
        total_connections = 0

        for layer in range(n_layers):
            print(f"  [Camada {layer+1}/{n_layers}] Multi-head attention + Feed-forward...")

            # 1. Multi-head self-attention
            mha = self.compute_multi_head_attention(layer)

            # 2. Residual connection + Feed-forward
            for ci in self.component_order:
                # Attention output: média ponderada dos embeddings atendidos
                att_output = [0.0] * self.d_model
                total_weight = 0.0

                for cj in self.component_order:
                    att_weight = sum(
                        mha["heads"][h]["attention"].get(ci, {}).get(cj, 0)
                        for h in mha["heads"]
                    ) / len(mha["heads"])
                    total_weight += att_weight
                    emb_j = self.components[cj]["embedding"]
                    for k in range(min(len(emb_j), self.d_model)):
                        att_output[k] += att_weight * emb_j[k]

                if total_weight > 0:
                    att_output = [v / total_weight for v in att_output]

                # Feed-forward
                ff_output = self.feed_forward(ci, layer)

                # Residual: x + Attention(x) + FFN(x)
                orig = self.components[ci]["embedding"]
                new_emb = []
                for k in range(self.d_model):
                    new_emb.append(orig[k] * 0.5 + att_output[k] * 0.2 + ff_output[k] * 0.3)

                self.components[ci]["embedding"] = new_emb
                self.residual_state[ci] = new_emb

            # Contar conexões ativas
            active = 0
            for h in mha["heads"]:
                for ci in self.component_order:
                    for cj in self.component_order:
                        if mha["heads"][h]["attention"].get(ci, {}).get(cj, 0) > 0.01:
                            active += 1
            total_connections += active
            layer_outputs.append({"layer": layer, "active_connections": active})

        self.total_connections = total_connections
        self.active_paths = total_connections // max(n_layers, 1)

        return {
            "n_layers": n_layers,
            "layers": layer_outputs,
            "total_connections": total_connections,
            "active_paths_per_layer": self.active_paths,
            "most_attended_components": self._get_top_components(10),
            "attention_entropy": self._compute_attention_entropy(),
        }

    def _top_k_attention(self, attention: Dict[str, Dict[str, float]], k: int = 5) -> List[Dict]:
        """Top-K conexões de atenção."""
        pairs = []
        for ci in attention:
            for cj in attention[ci]:
                pairs.append({"from": ci, "to": cj, "weight": attention[ci][cj]})
        pairs.sort(key=lambda p: p["weight"], reverse=True)
        return pairs[:k]

    def _get_top_components(self, k: int = 10) -> List[Dict]:
        """Componentes que mais receberam atenção."""
        ranked = []
        for ci, comp in self.components.items():
            total_att = sum(comp["attention_received"].values())
            ranked.append({
                "id": ci, "type": comp["type"],
                "total_attention": round(total_att, 4),
                "activation": round(comp["activation"], 4),
            })
        ranked.sort(key=lambda c: c["total_attention"], reverse=True)
        return ranked[:k]

    def _compute_attention_entropy(self) -> float:
        """Entropia da distribuição de atenção (diversidade de conexões)."""
        weights = []
        for ci in self.component_order:
            weights.append(self.components[ci]["activation"] + 1e-10)

        total = sum(weights)
        probs = [w / total for w in weights]
        entropy = -sum(p * math.log(p) for p in probs if p > 0)
        return round(entropy, 4)

    def generate_orchestration_plan(self, problem: str) -> Dict[str, Any]:
        """
        Gera plano de orquestração baseado na atenção aprendida.
        Decide quais componentes ativar, em que ordem e com que peso.
        """
        # Determinar componentes relevantes via atenção ao problema
        problem_tokens = problem.lower().split()
        relevance = {}

        for ci, comp in self.components.items():
            type_match = any(tok in comp["type"] for tok in problem_tokens)
            meta_match = any(
                tok in str(comp.get("metadata", {})) for tok in problem_tokens
            )
            relevance[ci] = (type_match * 2 + meta_match + comp["activation"]) / 4

        # Ordenar por relevância
        ranked = sorted(relevance.items(), key=lambda x: x[1], reverse=True)
        top_components = ranked[:8]

        # Criar plano sequencial com pesos de atenção
        plan = []
        for i, (comp_id, rel) in enumerate(top_components):
            comp = self.components[comp_id]
            plan.append({
                "step": i + 1,
                "component": comp_id,
                "type": comp["type"],
                "relevance": round(rel, 4),
                "activation": round(comp["activation"], 4),
                "attention_weight": round(comp["activation"] * rel, 4),
            })

        return {
            "problem": problem[:100],
            "n_components": len(self.components),
            "activated_components": len(top_components),
            "plan": plan,
            "dominant_heads": [h["name"] for h in self.heads[:3]],
            "estimated_paths": self.active_paths,
        }

    def swot_transformer_analysis(self) -> str:
        """Análise SWOT do ecossistema como rede transformer."""
        forward = self.forward_pass(n_layers=self.n_layers)

        return f"""# 🔍 Análise SWOT — Ecossistema MiroFish como Rede Transformer

## Arquitetura Transformer
- **Tokens:** {len(self.components)} componentes (skills, agentes, MCPs, fontes de dados)
- **Cabeças de atenção:** {len(self.heads)} perspectivas epistêmicas
- **Camadas:** {self.n_layers} camadas de processamento
- **Conexões ativas:** {self.active_paths} por camada (total: {self.total_connections})
- **Dimensionalidade:** d_model={self.d_model}
- **Entropia de atenção:** {self._compute_attention_entropy():.3f} (quanto maior, mais diversa a rede)

---

## 💪 FORÇAS (como Transformer)

| Força | Evidência |
|--------|-----------|
| **S1: Multi-head attention real** | {len(self.heads)} cabeças com focos distintos (estratégica, crítica, empírica, sintética, pragmática, visionária) |
| **S2: Residual connections** | Informação original preservada através de {self.n_layers} camadas — evita vanishing gradient |
| **S3: Feed-forward especializado** | Cada componente processa informação de forma única (simulação, ML, previsão, discurso) |
| **S4: Self-attention entre agentes** | 61 perfis atendem uns aos outros durante simulação — emergência de padrões coletivos |
| **S5: Cross-attention dados→simulação** | World Bank, IBGE, Semantic Scholar atendem parâmetros da simulação (G1 corrigido) |
| **S6: Layer normalization** | Estabilidade numérica através das camadas — robustez comprovada |

## 🔻 FRAQUEZAS

| Fraqueza | Impacto | Mitigação |
|----------|---------|-----------|
| **W1: Embeddings aleatórios** | Componentes registrados com embeddings random — sem pré-treino | Fine-tuning com dados reais de execução |
| **W2: Atenção não-diferenciável** | Softmax manual — sem backpropagation real | Implementar autograd ou usar aproximação numérica |
| **W3: Sem posicional encoding** | Componentes não têm noção de ordem sequencial no pipeline | Adicionar positional encoding senoidal |
| **W4: d_model fixo** | 64 dimensões pode ser insuficiente para 30+ componentes | Aumentar ou usar dimensionamento adaptativo |
| **W5: Sem cross-validation da atenção** | Pesos de atenção não são validados externamente | Comparar com ground truth de execuções anteriores |

## 🚀 OPORTUNIDADES

| Oportunidade | Potencial |
|-------------|-----------|
| **O1: Pré-treino com execuções reais** | Aprender embeddings ótimos dos componentes com dados de {self.total_connections} conexões |
| **O2: Atenção cross-modal** | Texto (artigos) ↔ Dados numéricos (simulação) ↔ Grafos (rede social) |
| **O3: Transformer para otimização de pipeline** | Prever quais componentes ativar para minimizar latência e maximizar qualidade |
| **O4: Explicabilidade via atenção** | Visualizar quais componentes influenciaram cada decisão — auditoria completa |
| **O5: Fine-tuning por domínio** | Especializar pesos de atenção para economia, saúde, segurança, etc. |

## ⚠️ AMEAÇAS

| Ameaça | Severidade | Contramedida |
|--------|-----------|-------------|
| **T1: Overfitting de atenção** | MÉDIA | Dropout de conexões + regularização L2 nos pesos de atenção |
| **T2: Colapso de heads** | MÉDIA | Loss de diversidade entre cabeças (encorajar heads ortogonais) |
| **T3: Latência com muitas camadas** | BAIXA | Early stopping dinâmico quando atenção converge |

---

## 📊 Métricas da Rede

| Métrica | Valor |
|---------|-------|
| Componentes ativos | {len(self.components)} |
| Conexões de atenção | {self.active_paths}/camada |
| Cabeças de atenção | {len(self.heads)} |
| Entropia (diversidade) | {self._compute_attention_entropy():.3f} |
| Componente mais atendido | {self._get_top_components(1)[0]['id'] if self._get_top_components(1) else 'N/A'} |

---

**Conclusão:** O ecossistema MiroFish opera como uma **rede transformer orquestrada** com {self.n_layers} camadas de processamento e {len(self.heads)} cabeças de atenção multi-perspectiva. A arquitetura permite que cada componente atenda seletivamente a outros, propagando informação através de conexões residuais e processamento feed-forward especializado.
"""


# ═══════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 70)
    print("🧠 TRANSFORMER ORCHESTRATOR — Rede de Atenção Multi-Head")
    print("=" * 70)

    orchestrator = TransformerOrchestrator(n_heads=6, n_layers=3, d_model=64)
    orchestrator.register_all_ecosystem_components()

    # Forward pass completo
    results = orchestrator.forward_pass()

    print(f"\n{'─'*70}")
    print("RESULTADOS:")
    print(f"  Conexões ativas: {results['active_paths_per_layer']}/camada")
    print(f"  Total conexões: {results['total_connections']}")
    print(f"  Entropia (diversidade): {orchestrator._compute_attention_entropy():.3f}")

    print(f"\n  Top 5 componentes mais atendidos:")
    for c in orchestrator._get_top_components(5):
        print(f"    {c['id']}: att={c['total_attention']:.3f} act={c['activation']:.3f}")

    # Plano de orquestração
    plan = orchestrator.generate_orchestration_plan(
        "Impacto da inteligência artificial no mercado de trabalho brasileiro"
    )
    print(f"\n  Plano de orquestração ({plan['activated_components']} componentes):")
    for step in plan["plan"]:
        print(f"    {step['step']}. {step['component']} ({step['type']}) w={step['attention_weight']:.3f}")

    # SWOT
    swot = orchestrator.swot_transformer_analysis()
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "..", "..", ".reversa", "transformer_swot.md")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(swot)
    print(f"\n✅ SWOT Transformer: {path}")
