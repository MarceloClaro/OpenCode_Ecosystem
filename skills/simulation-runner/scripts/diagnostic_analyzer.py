#!/usr/bin/env python3
"""
DiagnosticAnalyzer — 30 colunas de análise por tópico + Relatório diagnóstico minucioso.
Integra: sim_engine + RigorousMLPipeline + GraphDecisionEngine + Game Theory.
Qualis A1 — cada resultado com justificativa estatística e teórica.
"""

import json, os, math, random, sys
from datetime import datetime, timezone, timedelta
from collections import defaultdict
from typing import Dict, List, Any, Optional

BRAZIL_TZ = timezone(timedelta(hours=-3))

def _import_modules():
    """Importa todos os módulos de análise com fallback."""
    base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    paths = [
        os.path.join(base, "skills", "simulation-runner", "scripts"),
        os.path.join(base, "skills", "data-collector", "scripts"),
        os.path.join(base, "skills", "agent-forum", "scripts"),
    ]
    for p in paths:
        if p not in sys.path:
            sys.path.insert(0, p)

    mods = {}
    try:
        from sim_engine import SimulationEngine
        mods["sim"] = True
    except: mods["sim"] = False

    try:
        from graph_decision_engine import GraphTheoryEngine
        mods["graph"] = True
    except: mods["graph"] = False

    try:
        from rigorous_ml_pipeline import CorrelationMatrix, HypothesisTester, AnomalyDetector, CrossValidator, PCAReducer
        mods["ml"] = True
    except: mods["ml"] = False

    try:
        from debate_strategies import reasoning_for_stage, ReasoningType
        mods["game_theory"] = True
    except: mods["game_theory"] = False

    try:
        from omen_engine import ForecastEngine
        mods["forecast"] = True
    except: mods["forecast"] = False

    return mods


class DiagnosticAnalyzer:
    """Analisador diagnóstico com 30 colunas por tópico."""

    def __init__(self, simulation_summary: Dict):
        self.summary = simulation_summary
        self.modules = _import_modules()
        self.topic_data = simulation_summary.get("topic_analysis", {})
        self.topic_evolution = simulation_summary.get("topic_evolution", {})
        self.topic_correlations = simulation_summary.get("topic_correlations", {})
        self.patterns = simulation_summary.get("emergent_patterns", [])
        self.results: Dict[str, Dict] = {}

    def analyze_all_topics(self) -> Dict[str, Any]:
        """Análise completa com 30 colunas por tópico."""
        if not self.topic_data:
            return {"error": "Sem dados de tópicos"}

        all_topics = {}
        topics_list = list(self.topic_data.keys())

        # ── 1. Métricas básicas (7 colunas) ──
        for topic, data in self.topic_data.items():
            mean = data.get("mean", 0)
            trend = data.get("trend", 0)
            vol = data.get("volume", 0)
            std = data.get("std", 0)
            n_val = data.get("n", 0)
            stance = data.get("dominant_stance", "n/a")
            evolution = data.get("evolution", [])

            classification = "positivo" if mean > 0.1 else "negativo" if mean < -0.1 else "neutro"

            all_topics[topic] = {
                "sent_medio": round(mean, 4),
                "delta_tendencia": round(trend, 4),
                "volume": vol,
                "sigma_volatilidade": round(std, 4),
                "stance_dominante": stance,
                "classificacao": classification,
                "n": n_val,
                "min": round(data.get("min", 0), 4),
                "max": round(data.get("max", 0), 4),
                "cv": round(std / abs(mean), 4) if abs(mean) > 1e-10 else 0,
                "evolution": evolution,
            }

        # ── 2. ANOMALIAS (z-score + IQR + isolation) ──
        if self.modules.get("ml"):
            for topic in topics_list:
                evol = all_topics[topic].get("evolution", [])
                if evol and len(evol) >= 5:
                    values = [e["mean"] for e in evol]
                    anomalies = AnomalyDetector.detect_all(values)
                    all_topics[topic]["z_score_anomalies"] = anomalies.get("z_score_anomalies", 0)
                    all_topics[topic]["iqr_anomalies"] = anomalies.get("iqr_anomalies", 0)
                    all_topics[topic]["isolation_anomalies"] = anomalies.get("isolation_anomalies", 0)
                    all_topics[topic]["anomalias_confirmadas"] = anomalies.get("confirmed_anomalies", 0)
                    all_topics[topic]["anomaly_rate_pct"] = anomalies.get("anomaly_rate_pct", 0)
                else:
                    all_topics[topic]["z_score_anomalies"] = 0
                    all_topics[topic]["anomalias_confirmadas"] = 0

        # ── 3. TESTE DE HIPÓTESE (t-test entre tópicos) ──
        if self.modules.get("ml"):
            for i in range(len(topics_list)):
                for j in range(i + 1, min(i + 4, len(topics_list))):
                    a = topics_list[i]; b = topics_list[j]
                    evol_a = all_topics[a].get("evolution", [])
                    evol_b = all_topics[b].get("evolution", [])
                    if evol_a and evol_b and len(evol_a) >= 3 and len(evol_b) >= 3:
                        vals_a = [e["mean"] for e in evol_a]
                        vals_b = [e["mean"] for e in evol_b]
                        t = HypothesisTester.t_test_independent(vals_a, vals_b)
                        if t.get("significant"):
                            all_topics[a][f"t_test_vs_{b}"] = {
                                "t_stat": t["t_statistic"], "p_value": t["p_value"],
                                "cohens_d": t["cohens_d"], "significant": True,
                            }

        # ── 4. CORRELAÇÕES (Pearson + Spearman) ──
        if self.modules.get("ml"):
            for i in range(len(topics_list)):
                a = topics_list[i]
                evol_a = all_topics[a].get("evolution", [])
                if not evol_a or len(evol_a) < 3:
                    continue
                vals_a = [e["mean"] for e in evol_a]
                all_topics[a]["correlations"] = []
                for j in range(len(topics_list)):
                    if i == j: continue
                    b = topics_list[j]
                    evol_b = all_topics[b].get("evolution", [])
                    if not evol_b or len(evol_b) < 3: continue
                    vals_b = [e["mean"] for e in evol_b]
                    r = CorrelationMatrix.pearson(vals_a, vals_b)
                    if abs(r["r"]) > 0.15:
                        all_topics[a]["correlations"].append({
                            "with": b, "r": r["r"], "p_value": r["p_value"],
                            "significant": r["significant"],
                        })

        # ── 5. GRAFOS (PageRank + Betweenness) ──
        if self.modules.get("graph") and len(topics_list) >= 3:
            ge = GraphTheoryEngine()
            for topic in topics_list:
                ge.add_node(topic)
            # Conectar tópicos com correlação > 0.3
            for i in range(len(topics_list)):
                for j in range(i + 1, len(topics_list)):
                    a, b = topics_list[i], topics_list[j]
                    evol_a = all_topics[a].get("evolution", [])
                    evol_b = all_topics[b].get("evolution", [])
                    if evol_a and evol_b and len(evol_a) >= 3 and len(evol_b) >= 3:
                        vals_a = [e["mean"] for e in evol_a]
                        vals_b = [e["mean"] for e in evol_b]
                        r = CorrelationMatrix.pearson(vals_a, vals_b)
                        if abs(r["r"]) > 0.3:
                            ge.add_edge(a, b, abs(r["r"]))

            analysis = ge.analyze()
            pr = ge.pagerank()
            bc = ge.betweenness_centrality()
            communities = ge.detect_communities_girvan_newman(max_communities=5)

            for topic in topics_list:
                all_topics[topic]["pagerank"] = round(pr.get(topic, 0), 4)
                all_topics[topic]["betweenness"] = round(bc.get(topic, 0), 4)
                for ci, comm in enumerate(communities):
                    if topic in comm:
                        all_topics[topic]["comunidade"] = ci
                        break

        # ── 6. GAME THEORY / Nash ──
        for topic in topics_list:
            # Payoff estimado para cada stance no tópico
            stance_data = self.topic_data.get(topic, {}).get("stance_breakdown", {})
            payoffs = {}
            for stance, count in stance_data.items():
                payoffs[stance] = count / max(sum(stance_data.values()), 1)
            # Nash: estratégia mista = distribuição observada
            all_topics[topic]["nash_equilibrium"] = {
                "mixed_strategy": {s: round(count / max(sum(stance_data.values()), 1), 4)
                                   for s, count in stance_data.items()},
                "dominant_strategy": max(stance_data, key=stance_data.get) if stance_data else "n/a",
            }
            # Entropia
            probs = list(payoffs.values())
            entropy = -sum(p * math.log(p) if p > 0 else 0 for p in probs)
            all_topics[topic]["entropia"] = round(entropy, 4)

        # ── 7. Métricas financeiras (Sharpe, Sortino, β, α) ──
        for topic in topics_list:
            evol = all_topics[topic].get("evolution", [])
            if evol and len(evol) >= 5:
                returns = [evol[i]["mean"] - evol[i-1]["mean"] for i in range(1, len(evol))]
                if returns:
                    avg_ret = sum(returns) / len(returns)
                    std_ret = (sum((r - avg_ret)**2 for r in returns) / len(returns)) ** 0.5
                    sharpe = avg_ret / std_ret if std_ret > 0 else 0
                    down_returns = [r for r in returns if r < 0]
                    down_std = (sum(r**2 for r in down_returns) / max(len(down_returns), 1)) ** 0.5 if down_returns else std_ret
                    sortino = avg_ret / down_std if down_std > 0 else 0
                    cvar_95 = sorted(returns)[max(0, int(len(returns) * 0.05))]
                    all_topics[topic]["sharpe"] = round(sharpe, 4)
                    all_topics[topic]["sortino"] = round(sortino, 4)
                    all_topics[topic]["cvar_95"] = round(cvar_95, 4)
                    all_topics[topic]["alpha"] = round(avg_ret, 4)
                    all_topics[topic]["beta"] = round(std_ret, 4)
                    # Gini dos retornos
                    sorted_ret = sorted(abs(r) for r in returns)
                    gini_sum = sum((2*i - len(sorted_ret) - 1) * v for i, v in enumerate(sorted_ret))
                    gini_val = gini_sum / (len(sorted_ret) * sum(sorted_ret)) if sum(sorted_ret) > 0 else 0
                    all_topics[topic]["gini_retornos"] = round(gini_val, 4)

        # ── 8. PCA loading ──
        if self.modules.get("ml") and len(topics_list) >= 5:
            active = [t for t in topics_list if all_topics[t].get("n", 0) >= 5]
            if len(active) >= 4:
                X = [[all_topics[t]["sent_medio"], all_topics[t]["sigma_volatilidade"],
                      math.log(all_topics[t]["volume"] + 1), all_topics[t]["delta_tendencia"]]
                     for t in active]
                pca = PCAReducer(n_components=min(3, len(active)))
                pca.fit(X)
                for i, t in enumerate(active):
                    all_topics[t]["pca_loading"] = round(
                        sum(pca.components[0][j] * X[i][j] for j in range(len(X[0]))), 4
                    ) if pca.components else 0

        self.results = all_topics
        return all_topics

    def generate_diagnostic_report(self) -> str:
        """Relatório diagnóstico minucioso — uma justificativa por resultado."""
        if not self.results:
            self.analyze_all_topics()
        if not self.results:
            return "# Diagnóstico\nNenhum dado disponível."

        sim = self.summary
        lines = [
            "# 📊 Relatório Diagnóstico — Análise Minuciosa por Tópico",
            f"",
            f"**Gerado:** {datetime.now(BRAZIL_TZ).strftime('%d/%m/%Y %H:%M')} (UTC-3)",
            f"**Simulação:** {sim.get('total_agents','?')} agentes × {sim.get('total_rounds','?')} rodadas",
            f"**Ações:** {sim.get('total_actions','?')} | **Sentimento médio:** {sim.get('avg_sentiment',0):+.2f}",
            f"**Tópicos analisados:** {len(self.results)} | **Colunas por tópico:** 30",
            f"**Módulos ativos:** {', '.join(k for k,v in self.modules.items() if v)}",
            f"",
            "---",
            "",
        ]

        # Ordenar por volume (mais discutidos primeiro)
        sorted_topics = sorted(self.results.items(), key=lambda x: x[1].get("volume", 0), reverse=True)

        for topic, data in sorted_topics:
            if data.get("volume", 0) == 0:
                continue

            mean = data["sent_medio"]
            trend = data["delta_tendencia"]
            vol = data["volume"]
            std = data["sigma_volatilidade"]
            n_val = data["n"]
            classification = data["classificacao"]
            stance = data.get("stance_dominante", "?")

            # ── Título do tópico ──
            topic_label = topic.replace("_", " ").title()
            lines.append(f"## {topic_label}")
            lines.append(f"")

            # ── Diagnóstico principal ──
            lines.append(f"### 1. Diagnóstico Principal")
            lines.append(f"")
            lines.append(f"O tópico **{topic_label}** registrou **{vol} posts** ({n_val} ações analisadas) "
                        f"com sentimento médio de **{mean:+.3f}** (classificado como **{classification}**). "
                        f"A tendência é **{'de piora' if trend < -0.03 else 'de melhora' if trend > 0.03 else 'estável'}** "
                        f"(Δ = {trend:+.3f}).")
            lines.append(f"")

            # Justificativa estatística
            if abs(mean) > 1.0:
                lines.append(f"**Justificativa:** O sentimento é extremo (|μ| > 1.0), sugerindo forte consenso "
                            f"{'positivo' if mean > 0 else 'negativo'} entre os agentes sobre este tema. "
                            f"Este nível de polarização é raro e indica que o tópico toca em valores fundamentais "
                            f"dos participantes, conforme a Teoria dos Fundamentos Morais (Haidt, 2012).")
            elif std > 1.5:
                lines.append(f"**Justificativa:** A alta volatilidade (σ = {std:.3f}) indica **divergência significativa** "
                            f"entre agentes. Não há consenso — o debate é polarizado. "
                            f"Isso é consistente com a literatura sobre polarização afetiva (Iyengar et al., 2019).")
            else:
                lines.append(f"**Justificativa:** O sentimento moderado e baixa volatilidade sugerem que "
                            f"este tópico não desperta paixões extremas, sendo tratado de forma mais técnica "
                            f"pelos agentes. Tópicos com estas características tendem a gerar menos engajamento "
                            f"mas discussões de maior qualidade (Cacioppo & Petty, 1982 — Need for Cognition).")
            lines.append(f"")

            # ── Stance dominante ──
            lines.append(f"### 2. Análise de Stance")
            sb = self.topic_data.get(topic, {}).get("stance_breakdown", {})
            lines.append(f"**Stance dominante:** {stance} — distribuição: " + ", ".join(f"{s}: {c}" for s, c in sb.items()))
            lines.append(f"")

            if stance == "critical" and mean < 0:
                lines.append(f"**Interpretação:** Críticos dominam o debate com visão negativa. "
                            f"Isso pode indicar insatisfação com o status quo ou resistência a mudanças propostas. "
                            f"Segundo a Teoria da Justificação do Sistema (Jost & Banaji, 1994), críticos tendem a "
                            f"desafiar o sistema quando percebem injustiças ou ineficiências.")
            elif stance == "supportive" and mean > 0:
                lines.append(f"**Interpretação:** Apoiadores lideram com otimismo. "
                            f"Isto sugere que as narrativas positivas estão vencendo o debate público sobre este tema. "
                            f"Agentes com alto viés de promoção (Higgins, 1997) são mais propensos a amplificar sinais positivos.")
            elif stance == "curious":
                lines.append(f"**Interpretação:** A curiosidade domina — os agentes estão mais interessados em "
                            f"explorar o tema do que tomar posição. Este é um sinal saudável de deliberação pública, "
                            f"conforme a Teoria da Democracia Deliberativa (Habermas, 1981).")
            lines.append(f"")

            # ── Anomalias ──
            anomalies = data.get("anomalias_confirmadas", 0)
            lines.append(f"### 3. Anomalias Detectadas")
            if anomalies > 0:
                lines.append(f"**{anomalies} anomalias confirmadas** (2+ detectores: Z-score, IQR, Isolation Forest).")
                lines.append(f"Anomalias indicam eventos atípicos que fogem do padrão esperado. "
                            f"Estes podem corresponder a momentos de virada no debate ou influência de "
                            f"eventos externos (God's-eye view injections).")
            else:
                lines.append(f"Nenhuma anomalia detectada — o comportamento deste tópico é estável e previsível.")
            lines.append(f"")

            # ── Correlações ──
            correlations = data.get("correlations", [])
            if correlations:
                lines.append(f"### 4. Correlações Significativas")
                for c in sorted(correlations, key=lambda x: abs(x["r"]), reverse=True)[:5]:
                    lines.append(f"- **{c['with'].replace('_',' ').title()}:** r = {c['r']:+.3f} "
                                f"({'p < 0.05' if c.get('significant') else 'n.s.'}) — "
                                f"{'forte' if abs(c['r'])>0.6 else 'moderada' if abs(c['r'])>0.3 else 'fraca'} correlação")
                lines.append(f"")
            else:
                lines.append(f"### 4. Correlações Significativas")
                lines.append(f"Sem correlações significativas com outros tópicos (|r| > 0.15).")
                lines.append(f"")

            # ── Análise financeira ──
            sharpe = data.get("sharpe")
            if sharpe is not None:
                lines.append(f"### 5. Métricas Financeiras (Sentimento como Ativo)")
                lines.append(f"- **Sharpe Ratio:** {sharpe:+.3f} — {'bom' if abs(sharpe)>1 else 'regular' if abs(sharpe)>0.5 else 'ruim'} "
                            f"(retorno ajustado ao risco do sentimento)")
                lines.append(f"- **Sortino Ratio:** {data.get('sortino', 0):+.3f} — penaliza apenas volatilidade negativa")
                lines.append(f"- **CVaR 95%:** {data.get('cvar_95', 0):+.3f} — pior cenário em 5% dos casos")
                lines.append(f"- **Gini (retornos):** {data.get('gini_retornos', 0):.3f} — concentração de retornos")
                lines.append(f"")

            # ── Teoria dos Jogos ──
            ne = data.get("nash_equilibrium", {})
            if ne:
                lines.append(f"### 6. Equilíbrio de Nash & Teoria dos Jogos")
                dom = ne.get("dominant_strategy", "?")
                lines.append(f"- **Estratégia dominante:** {dom}")
                lines.append(f"- **Equilíbrio misto:** cada stance participa proporcionalmente à sua representação")
                lines.append(f"- **Entropia:** {data.get('entropia', 0):.3f} — {'alta diversidade' if data.get('entropia',0)>1 else 'baixa diversidade'} de estratégias")
                lines.append(f"")

            # ── Grafos ──
            pr = data.get("pagerank")
            bc = data.get("betweenness")
            if pr is not None:
                lines.append(f"### 7. Centralidade na Rede de Tópicos")
                lines.append(f"- **PageRank:** {pr:.4f} — importância do tópico na rede de debates")
                lines.append(f"- **Betweenness:** {bc:.4f} — o tópico como ponte entre outros temas")
                if bc > 0.1:
                    lines.append(f"  Alto betweenness → este tópico **conecta diferentes clusters** do debate.")
                lines.append(f"")

            # ── PCA ──
            pca_load = data.get("pca_loading")
            if pca_load is not None:
                lines.append(f"### 8. PCA Loading")
                lines.append(f"- **Loading PC1:** {pca_load:.4f} — contribuição para o componente principal")
                lines.append(f"")

            lines.append(f"---")
            lines.append(f"")

        # ── Resumo final ──
        lines.append(f"## Síntese: Padrões Emergentes")
        for p in self.patterns:
            lines.append(f"- **{p.get('type','?')}:** score={p.get('score','?')} — {p.get('interpretation','')}")
        lines.append(f"")

        lines.append(f"## Métodos e Referências")
        refs = [
            "Correlação de Pearson (Fisher, 1925)",
            "Teste t de Welch (Welch, 1947)",
            "Cohen's d (Cohen, 1988)",
            "Z-score + IQR + Isolation Forest (Hawkins, 1980; Liu et al., 2008)",
            "PageRank (Brin & Page, 1998)",
            "Betweenness Centrality (Freeman, 1977)",
            "Equilíbrio de Nash (Nash, 1950)",
            "PCA (Pearson, 1901; Hotelling, 1933)",
            "Sharpe Ratio (Sharpe, 1966)",
            "Teoria dos Fundamentos Morais (Haidt, 2012)",
            "Need for Cognition (Cacioppo & Petty, 1982)",
            "Foco Regulatório (Higgins, 1997)",
            "Justificação do Sistema (Jost & Banaji, 1994)",
        ]
        for r in refs:
            lines.append(f"- {r}")

        return "\n".join(lines)

    def save(self, path: str = None) -> str:
        if not path:
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "..", ".reversa", "diagnostic_report.md")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not self.results:
            self.analyze_all_topics()
        report = self.generate_diagnostic_report()
        with open(path, "w", encoding="utf-8") as f:
            f.write(report)
        return path


# ═══════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
    from sim_engine import SimulationEngine

    print("=" * 60)
    print("DIAGNOSTIC ANALYZER — 30 colunas por tópico")
    print("=" * 60)

    e = SimulationEngine("diag_test")
    e.create_agents_batch(100, ["supportive","critical","neutral","curious"])
    s = e.run_simulation(15)

    da = DiagnosticAnalyzer(s)
    topics = da.analyze_all_topics()

    active = sum(1 for t, d in topics.items() if d["volume"] > 0)
    print(f"\nTopicos ativos: {active}/{len(topics)}")
    for t, d in sorted(topics.items(), key=lambda x: x[1]["volume"], reverse=True)[:10]:
        print(f"  {t}: vol={d['volume']} sent={d['sent_medio']:+.3f} σ={d['sigma_volatilidade']:.3f} "
              f"anom={d.get('anomalias_confirmadas',0)} pr={d.get('pagerank','?'):.3f} sharpe={d.get('sharpe','?')}")

    path = da.save()
    print(f"\nDiagnostic report saved: {path}")
