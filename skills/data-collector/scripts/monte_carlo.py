#!/usr/bin/env python3
"""
Monte Carlo Sensitivity Analyzer — Quantifica incerteza dos parâmetros da simulação.
Executa N rodadas com perturbações aleatórias, mede variância dos outputs,
calcula índices de sensibilidade e gera contraprovas (counterfactuals).

Integra com: sim_engine.py, report_generator.py
Padrão: Sobol-like sensitivity indices + bootstrap confidence intervals.
"""

import sys, os, json, math, time, random
from datetime import datetime, timezone, timedelta
from collections import defaultdict
from typing import Dict, List, Any, Tuple, Optional

BRAZIL_TZ = timezone(timedelta(hours=-3))
BRAZIL_TIME = lambda: datetime.now(BRAZIL_TZ)

# Parâmetros sujeitos a análise de sensibilidade
SENSITIVITY_PARAMS = {
    "sentiment_bias_range": {
        "label": "Viés de sentimento inicial",
        "baseline": 0.0,
        "range": [-0.5, 0.5],
        "unit": "(-1 a +1)",
    },
    "influence_decay": {
        "label": "Decaimento de influência",
        "baseline": 0.95,
        "range": [0.80, 1.0],
        "unit": "fator multiplicativo/rodada",
    },
    "event_impact_multiplier": {
        "label": "Multiplicador de impacto de eventos",
        "baseline": 1.0,
        "range": [0.5, 2.0],
        "unit": "fator",
    },
    "stance_mixing_rate": {
        "label": "Taxa de mistura entre stances",
        "baseline": 0.1,
        "range": [0.0, 0.3],
        "unit": "probabilidade/rodada",
    },
    "topic_resonance": {
        "label": "Ressonância temática",
        "baseline": 0.5,
        "range": [0.2, 0.8],
        "unit": "probabilidade de engajamento",
    },
    "polarization_threshold": {
        "label": "Limiar de polarização",
        "baseline": 0.3,
        "range": [0.1, 0.5],
        "unit": "desvio padrão sentimento",
    },
    "echo_chamber_strength": {
        "label": "Força da echo chamber",
        "baseline": 0.4,
        "range": [0.1, 0.7],
        "unit": "probabilidade interação homófila",
    },
    "viral_coefficient": {
        "label": "Coeficiente de viralidade",
        "baseline": 0.15,
        "range": [0.05, 0.30],
        "unit": "R0 informacional",
    },
}


class MonteCarloAnalyzer:
    """Análise de sensibilidade via Monte Carlo com índices Sobol-like."""

    def __init__(self, n_iterations: int = 50):
        self.n_iterations = n_iterations
        self.params = SENSITIVITY_PARAMS
        self.results: List[Dict] = []
        self.sensitivity_indices: Dict[str, float] = {}
        self.confidence_intervals: Dict[str, Tuple[float, float]] = {}
        self.counterfactuals: List[Dict] = []

    def _perturb_params(self) -> Dict[str, float]:
        """Gera conjunto de parâmetros com perturbação aleatória uniforme."""
        perturbed = {}
        for key, config in self.params.items():
            lo, hi = config["range"]
            perturbed[key] = random.uniform(lo, hi)
        return perturbed

    def _run_single(self, params: Dict[str, float], agent_count: int = 100,
                    rounds: int = 15) -> Dict[str, Any]:
        """Executa uma simulação com parâmetros perturbados."""
        try:
            from sim_engine import SimulationEngine

            engine = SimulationEngine(f"mc_{random.randint(1000,9999)}")
            engine.create_agents_batch(agent_count,
                                       types=["supportive", "critical", "neutral", "curious"])

            # Aplica parâmetros perturbados ao engine
            engine.sentiment_bias_range = params.get("sentiment_bias_range", 0.0)
            engine.influence_decay = params.get("influence_decay", 0.95)
            engine.event_impact_multiplier = params.get("event_impact_multiplier", 1.0)

            summary = engine.run_simulation(rounds)

            return {
                "params": params,
                "avg_sentiment": summary.get("avg_sentiment", 0.0),
                "total_actions": summary.get("total_actions", 0),
                "polarization": (summary.get("emergent_patterns", [{}])[0].get("score", 0)
                                 if summary.get("emergent_patterns") else 0),
                "topic_variance": self._compute_topic_variance(summary.get("topic_analysis", {})),
                "duration": summary.get("duration_seconds", 0),
            }
        except ImportError:
            return {"params": params, "error": "sim_engine unavailable"}

    def _compute_topic_variance(self, topic_analysis: Dict) -> float:
        """Variância entre médias de sentimento dos tópicos."""
        if not topic_analysis:
            return 0.0
        means = [d.get("mean", 0) for d in topic_analysis.values()]
        if len(means) < 2:
            return 0.0
        avg = sum(means) / len(means)
        return sum((m - avg) ** 2 for m in means) / len(means)

    def run(self, agent_count: int = 100, rounds: int = 15) -> Dict[str, Any]:
        """Executa análise completa de Monte Carlo."""
        print(f"\n{'='*60}")
        print(f"🎲 MONTE CARLO SENSITIVITY ANALYSIS")
        print(f"   Iterações: {self.n_iterations} | Agentes: {agent_count} | Rodadas: {rounds}")
        print(f"{'='*60}")

        self.results = []
        start = time.time()

        for i in range(self.n_iterations):
            params = self._perturb_params()
            result = self._run_single(params, agent_count, rounds)
            self.results.append(result)

            if (i + 1) % 10 == 0 or i == 0:
                elapsed = time.time() - start
                eta = (elapsed / (i + 1)) * (self.n_iterations - i - 1)
                print(f"   Iter {i+1:3d}/{self.n_iterations} | "
                      f"sent={result.get('avg_sentiment', 0):+.2f} | "
                      f"pol={result.get('polarization', 0):.2f} | "
                      f"ETA {eta:.0f}s")

        total_time = time.time() - start
        self._compute_sensitivity()
        self._compute_confidence_intervals()
        self._generate_counterfactuals()

        return self.summary()

    def _compute_sensitivity(self):
        """Calcula índices de sensibilidade Sobol-like (first-order)."""
        if len(self.results) < 10:
            return

        # Para cada parâmetro, correlaciona com outputs
        param_names = list(self.params.keys())
        for pname in param_names:
            pvalues = [r["params"].get(pname, 0) for r in self.results]
            outputs = [r.get("avg_sentiment", 0) for r in self.results]

            # Correlação de Pearson param → output
            n = len(pvalues)
            mp = sum(pvalues) / n
            mo = sum(outputs) / n
            num = sum((pvalues[i] - mp) * (outputs[i] - mo) for i in range(n))
            dp = (sum((v - mp) ** 2 for v in pvalues) / n) ** 0.5
            do = (sum((v - mo) ** 2 for v in outputs) / n) ** 0.5

            r = num / (n * dp * do) if dp > 0 and do > 0 else 0
            self.sensitivity_indices[pname] = round(r, 4)

    def _compute_confidence_intervals(self):
        """Bootstrap 95% CI para sentimento médio."""
        sentiments = [r.get("avg_sentiment", 0) for r in self.results if "error" not in r]
        if len(sentiments) < 10:
            return

        # Bootstrap
        boot_means = []
        for _ in range(1000):
            sample = random.choices(sentiments, k=len(sentiments))
            boot_means.append(sum(sample) / len(sample))

        boot_means.sort()
        ci_lo = boot_means[25]   # 2.5th percentile
        ci_hi = boot_means[974]  # 97.5th percentile
        mean = sum(sentiments) / len(sentiments)

        self.confidence_intervals = {
            "avg_sentiment": (round(ci_lo, 4), round(ci_hi, 4)),
            "mean": round(mean, 4),
            "std": round((sum((s - mean) ** 2 for s in sentiments) / len(sentiments)) ** 0.5, 4),
        }

    def _generate_counterfactuals(self):
        """Gera cenários contrafactuais extremos."""
        if len(self.results) < 20:
            return

        sentiments = [(r.get("avg_sentiment", 0), r["params"]) for r in self.results if "error" not in r]
        sentiments.sort(key=lambda x: x[0])

        # Cenário mais pessimista (5% inferiores)
        n_low = max(1, len(sentiments) // 20)
        low_params = [s[1] for s in sentiments[:n_low]]
        low_avg = sum(s[0] for s in sentiments[:n_low]) / n_low

        # Cenário mais otimista (5% superiores)
        high_params = [s[1] for s in sentiments[-n_low:]]
        high_avg = sum(s[0] for s in sentiments[-n_low:]) / n_low

        # Cenário mediano
        mid_params = sentiments[len(sentiments)//2][1]

        self.counterfactuals = [
            {
                "scenario": "Pessimista extremo",
                "avg_sentiment": round(low_avg, 4),
                "typical_params": {k: round(sum(p.get(k, 0) for p in low_params)/n_low, 3)
                                   for k in self.params},
                "interpretation": "Configuração que maximiza sentimento negativo e polarização",
            },
            {
                "scenario": "Mediano (baseline)",
                "avg_sentiment": round(sentiments[len(sentiments)//2][0], 4),
                "typical_params": {k: round(v, 3) for k, v in mid_params.items()},
                "interpretation": "Cenário mais provável, parâmetros medianos",
            },
            {
                "scenario": "Otimista extremo",
                "avg_sentiment": round(high_avg, 4),
                "typical_params": {k: round(sum(p.get(k, 0) for p in high_params)/n_low, 3)
                                   for k in self.params},
                "interpretation": "Configuração que maximiza sentimento positivo e consenso",
            },
        ]

    def summary(self) -> Dict[str, Any]:
        """Retorna resumo executivo da análise."""
        ci = self.confidence_intervals
        return {
            "timestamp": BRAZIL_TIME().isoformat(),
            "n_iterations": self.n_iterations,
            "n_valid_results": len([r for r in self.results if "error" not in r]),
            "sensitivity_ranking": sorted(
                [(k, v) for k, v in self.sensitivity_indices.items()],
                key=lambda x: abs(x[1]), reverse=True
            ),
            "confidence_interval_95": {
                "avg_sentiment": f"[{ci.get('avg_sentiment', (0,0))[0]:.4f}, {ci.get('avg_sentiment', (0,0))[1]:.4f}]",
                "mean": ci.get("mean", 0),
                "std": ci.get("std", 0),
            },
            "counterfactuals": self.counterfactuals,
            "robustness": self._assess_robustness(),
        }

    def _assess_robustness(self) -> Dict[str, str]:
        """Avalia robustez dos resultados da simulação."""
        ci = self.confidence_intervals
        if not ci:
            return {"overall": "Indeterminado — amostra insuficiente"}

        mean = ci.get("mean", 0)
        std = ci.get("std", 0)
        ci_width = ci.get("avg_sentiment", (0, 0))

        assessments = {}

        # Robustez do sentimento
        if mean > 0 and ci_width[0] > 0:
            assessments["sentiment"] = "Robusto — sentimento consistentemente positivo (IC 95% todo > 0)"
        elif mean < 0 and ci_width[1] < 0:
            assessments["sentiment"] = "Robusto — sentimento consistentemente negativo (IC 95% todo < 0)"
        elif ci_width[0] < 0 < ci_width[1]:
            assessments["sentiment"] = "INCERTO — IC 95% cruza o zero. Sentimento não é estatisticamente significativo."
        else:
            assessments["sentiment"] = "Moderadamente robusto"

        # Variabilidade
        cv = std / abs(mean) if mean != 0 else float('inf')
        if cv < 0.5:
            assessments["variability"] = f"Baixa variabilidade (CV={cv:.2f}) — outputs consistentes entre iterações"
        elif cv < 1.0:
            assessments["variability"] = f"Variabilidade moderada (CV={cv:.2f}) — alguma sensibilidade a parâmetros"
        else:
            assessments["variability"] = f"ALTA variabilidade (CV={cv:.2f}) — outputs muito sensíveis. Usar com cautela."

        return assessments

    def to_markdown(self) -> str:
        """Gera relatório Markdown da análise Monte Carlo."""
        s = self.summary()
        ci = s["confidence_interval_95"]

        lines = [
            f"## 🎲 Análise de Sensibilidade Monte Carlo",
            f"",
            f"**Iterações:** {s['n_iterations']} | **Resultados válidos:** {s['n_valid_results']}",
            f"**Confiança:** Bootstrap 95% CI com 1000 reamostragens",
            f"",
            f"### Sensibilidade dos Parâmetros (Sobol-like first-order)",
            f"",
            f"| Parâmetro | ρ (Pearson) | Interpretação |",
            f"|-----------|-------------|---------------|",
        ]

        for pname, r in s["sensitivity_ranking"]:
            interp = ("🔴 Muito sensível" if abs(r) > 0.5 else
                      "🟡 Moderadamente sensível" if abs(r) > 0.2 else
                      "🟢 Pouco sensível")
            lines.append(f"| {pname} | {r:+.4f} | {interp} |")

        lines += [
            f"",
            f"### Intervalo de Confiança (95%)",
            f"",
            f"- **Sentimento médio:** μ = {ci['mean']:.4f}, σ = {ci['std']:.4f}",
            f"- **IC 95%:** {ci['avg_sentiment']}",
            f"",
            f"### Robustez",
        ]
        for key, val in s["robustness"].items():
            lines.append(f"- **{key}:** {val}")

        lines.append(f"\n### Cenários Contrafactuais")
        for cf in s["counterfactuals"]:
            lines.append(f"\n#### {cf['scenario']} (sentimento: {cf['avg_sentiment']:+.4f})")
            lines.append(f"*{cf['interpretation']}*")
            lines.append(f"")
            for k, v in sorted(cf["typical_params"].items()):
                baseline = self.params.get(k, {}).get("baseline", "?")
                delta = v - baseline if isinstance(baseline, (int, float)) else 0
                arrow = "↑" if delta > 0.05 else "↓" if delta < -0.05 else "→"
                lines.append(f"- {k}: {v:.3f} {arrow} (baseline: {baseline})")

        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════
# Quick test
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("═" * 60)
    print("🎲 Monte Carlo Sensitivity Analyzer")
    print("═" * 60)

    mca = MonteCarloAnalyzer(n_iterations=20)
    result = mca.run(agent_count=50, rounds=10)

    print(f"\n{mca.to_markdown()}")

    # Save
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "..", "..", "..", ".reversa", "monte_carlo_analysis.md")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(mca.to_markdown())
    print(f"\n✅ Relatório salvo: {out_path}")
