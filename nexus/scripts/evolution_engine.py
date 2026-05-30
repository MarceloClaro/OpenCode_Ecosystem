"""evolution_engine.py - Motor de evolucao autonoma com aprendizado entre ciclos.

Aprende padroes de sucesso/falha de ciclos anteriores, gera recomendacoes
inteligentes, detecta regressoes e sugere proximos passos com prioridade.

Uso:
    python nexus/scripts/evolution_engine.py --analyze
    python nexus/scripts/evolution_engine.py --learn
    python nexus/scripts/evolution_engine.py --suggest
    python nexus/scripts/evolution_engine.py --report
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Any

WORKSPACE = Path(__file__).parent.parent.parent.resolve()
HISTORY_PATH = WORKSPACE / "cache" / "ecosystem_history.json"
CICLOS_PATH = WORKSPACE / "AGENTS.md"
KNOWLEDGE_PATH = WORKSPACE / "cache" / "evolution_knowledge.json"


def carregar_historico() -> list[dict]:
    if not HISTORY_PATH.exists():
        return []
    try:
        data = json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
        return data.get("snapshots", [])
    except:
        return []


def carregar_conhecimento() -> dict:
    if KNOWLEDGE_PATH.exists():
        try:
            return json.loads(KNOWLEDGE_PATH.read_text(encoding="utf-8"))
        except:
            pass
    return {
        "padroes_sucesso": [],
        "padroes_falha": [],
        "metricas_historicas": [],
        "recomendacoes_aplicadas": [],
        "ciclos_analisados": 0,
    }


def parse_ciclos_agents() -> list[dict]:
    """Extrai ciclos do AGENTS.md."""
    if not CICLOS_PATH.exists():
        return []
    content = CICLOS_PATH.read_text(encoding="utf-8", errors="ignore")
    ciclos = []
    # Procura padrao: | \d+ | ... | \d+ |
    matches = re.findall(r'\|\s*(\d+)\s*\|\s*([^|]+)\s*\|\s*(\d+)\s*\|', content)
    for m in matches:
        ciclos.append({
            "numero": int(m[0]),
            "foco": m[1].strip(),
            "score": int(m[2]),
        })
    return ciclos



def detectar_padroes(historico: list[dict]) -> dict:
    """Aprende padroes de melhoria e regressao entre snapshots."""
    padroes = {
        "melhorias_continuas": [],
        "regressoes": [],
        "metricas_tendencia": {},
        "ciclo_atual": None,
    }
    if len(historico) < 2:
        return padroes

    # Analisa metricas ao longo do tempo
    metricas_chave = ["skills_under_2500b", "frontmatter_ok", "cjk_leaks", "scripts_total"]
    for metrica in metricas_chave:
        valores = []
        for snap in historico:
            if "health" in snap and metrica in snap["health"]:
                valores.append((snap["timestamp"][:10], snap["health"][metrica]))
        if len(valores) >= 2:
            tendencia = "melhoria" if valores[-1][1] >= valores[0][1] else "regressao"
            padroes["metricas_tendencia"][metrica] = {
                "valores": valores,
                "tendencia": tendencia,
                "delta": valores[-1][1] - valores[0][1],
            }

    # Detecta anomalias que persistem
    for snap in historico:
        if snap.get("anomalies", 0) > 0:
            padroes["regressoes"].append({
                "data": snap["timestamp"][:10],
                "ciclo": snap.get("ciclo", "?"),
                "anomalias": snap["anomalies"],
            })

    padroes["ciclo_atual"] = historico[-1].get("ciclo") if historico else None
    return padroes


def gerar_sugestoes(padroes: dict, conhecimento: dict) -> list[dict]:
    """Gera sugestoes inteligentes baseadas em padroes e conhecimento."""
    sugestoes = []

    # Prioridade baseada em tendencias
    for metrica, dados in padroes.get("metricas_tendencia", {}).items():
        if dados["tendencia"] == "regressao":
            sugestoes.append({
                "prioridade": "alta",
                "categoria": "regressao",
                "acao": f"Reverter regressao em {metrica} (delta={dados['delta']})",
                "justificativa": f"Metrica piorou entre {dados['valores'][0][0]} e {dados['valores'][-1][0]}",
            })

    # Sugestoes de expansao baseadas em gaps conhecidos
    sugestoes_expansao = [
        ("Portal CNPq", "Scraping de chamadas CNPq (bloqueado atualmente)", "alta"),
        ("Portal CAPES", "Scraping de editais CAPES", "alta"),
        ("SEEKER integracao direta", "Conectar editais-br como tool nativa do SEEKER", "media"),
        ("Auto-feedback loop", "Coleta automatica de feedback baseada em cliques do usuario", "media"),
        ("Dashboard web", "Interface web para visualizacao de resultados editais", "baixa"),
        ("API publica", "Expor servidor editais-br via API publica", "baixa"),
    ]
    for nome, desc, prioridade in sugestoes_expansao:
        # So sugere se nao foi aplicado antes
        ja_aplicado = any(
            nome in r.get("acao", "") or nome in r.get("descricao", "")
            for r in conhecimento.get("recomendacoes_aplicadas", [])
        )
        if not ja_aplicado:
            sugestoes.append({
                "prioridade": prioridade,
                "categoria": "expansao",
                "acao": f"Adicionar {nome}",
                "justificativa": desc,
            })

    # Sugestoes de aprendizado
    if conhecimento.get("ciclos_analisados", 0) > 0:
        sugestoes.append({
            "prioridade": "media",
            "categoria": "aprendizado",
            "acao": "Revisar padroes de sucesso dos ciclos anteriores",
            "justificativa": f"{conhecimento['ciclos_analisados']} ciclos analisados, {len(conhecimento['padroes_sucesso'])} padroes de sucesso",
        })

    return sorted(sugestoes, key=lambda x: {"alta": 0, "media": 1, "baixa": 2}[x["prioridade"]])


def calcular_health_projetado(historico: list[dict]) -> dict:
    """Projeta health score futuro baseado em tendencias."""
    if len(historico) < 2:
        return {"projecao": "insuficiente_historico"}

    # Pega ultimos health scores
    healths = []
    for snap in historico:
        if "health" in snap:
            # Calcula score composto
            h = snap["health"]
            score = 0
            total_weight = 0
            for k, w in [("skills_under_2500b", 30), ("frontmatter_ok", 25), ("cjk_leaks", -20)]:
                if k in h:
                    score += h[k] * w
                    total_weight += abs(w)
            healths.append({"ciclo": snap.get("ciclo", "?"), "timestamp": snap["timestamp"][:10], "score": score / total_weight if total_weight > 0 else 0})

    if len(healths) >= 2:
        recentes = healths[-3:] if len(healths) >= 3 else healths
        media = sum(h["score"] for h in recentes) / len(recentes)
        return {
            "projecao": "estavel" if media >= 0.95 else "melhoria_possivel",
            "health_atual": healths[-1]["score"],
            "media_recente": media,
            "historico": healths,
        }
    return {"projecao": "insuficiente_historico"}


def analyze() -> dict:
    """Analisa estado atual e historico de evolucao."""
    historico = carregar_historico()
    conhecimento = carregar_conhecimento()
    ciclos = parse_ciclos_agents()

    padroes = detectar_padroes(historico)
    sugestoes = gerar_sugestoes(padroes, conhecimento)
    projecao = calcular_health_projetado(historico)

    analysis = {
        "timestamp": datetime.now().isoformat(),
        "ciclos_documentados": len(ciclos),
        "snapshots_disponiveis": len(historico),
        "padroes": padroes,
        "sugestoes": sugestoes,
        "projecao": projecao,
        "conhecimento_acumulado": conhecimento["ciclos_analisados"],
    }
    return analysis


def learn():
    """Aprende com o estado atual e atualiza base de conhecimento.
    Extrai learnings de outcomes e tendencias.
    """
    conhecimento = carregar_conhecimento()
    conhecimento["ciclos_analisados"] += 1
    conhecimento["ultima_analise"] = datetime.now().isoformat()

    # Tenta rodar scanner para pegar metricas atuais
    try:
        from ecosystem_scanner import scan
        manifest = scan()
        conhecimento["ultimo_manifesto"] = {
            "timestamp": manifest["timestamp"],
            "health": manifest["health"],
            "totals": manifest["totals"],
            "anomalies": len(manifest["anomalies"]),
        }
    except ImportError:
        conhecimento["ultimo_manifesto"] = {"error": "scanner_nao_disponivel"}

    # Extrai learnings de outcomes registrados
    learnings_path = WORKSPACE / ".evolve" / "learnings.json"
    novos_aprendizados = []
    
    # Carrega outcomes para extrair learnings
    outcomes_path = WORKSPACE / ".evolve" / "outcomes.json"
    if outcomes_path.exists():
        try:
            outcomes = json.loads(outcomes_path.read_text(encoding="utf-8"))
            total_outcomes = len(outcomes.get("outcomes", []))
            ciclos_executados = sum(1 for o in outcomes.get("outcomes", []) if o.get("component") == "evolution_loop" and o.get("success"))
            diagnosticos = sum(1 for o in outcomes.get("outcomes", []) if o.get("component") == "social_diagnosis" and o.get("success"))
            score_medio = sum(o.get("score", 0) for o in outcomes.get("outcomes", [])) / max(total_outcomes, 1)
            
            novos_aprendizados.append({
                "timestamp": datetime.now().isoformat(),
                "categoria": "ciclo_evolucao",
                "aprendizado": f"{ciclos_executados} ciclos de evolucao executados com sucesso, score medio {score_medio:.1f}",
                "fonte": "outcomes.json",
                "confianca": 0.9,
            })
            novos_aprendizados.append({
                "timestamp": datetime.now().isoformat(),
                "categoria": "diagnostico",
                "aprendizado": f"{diagnosticos} diagnostico(s) multi-perspectiva realizados",
                "fonte": "outcomes.json",
                "confianca": 0.9,
            })
        except Exception as e:
            print(f"[evolution] Erro ao ler outcomes: {e}")

    # Extrai learnings do ultimo manifesto
    ultimo = conhecimento.get("ultimo_manifesto", {})
    if ultimo.get("totals"):
        tots = ultimo["totals"]
        health = ultimo.get("health", {})
        novos_aprendizados.append({
            "timestamp": datetime.now().isoformat(),
            "categoria": "ecossistema",
            "aprendizado": f"Ecossistema possui {tots.get('skills',0)} skills, {tots.get('scripts',0)} scripts, {tots.get('agents',0)} agentes, {tots.get('plugins',0)} plugins",
            "fonte": "ecosystem_scanner",
            "confianca": 0.95,
        })
        if health.get("cjk_leaks", 0) == 0:
            novos_aprendizados.append({
                "timestamp": datetime.now().isoformat(),
                "categoria": "qualidade",
                "aprendizado": "Zero CJK leaks detectados - corretor linguistico operacional",
                "fonte": "ecosystem_scanner",
                "confianca": 0.95,
            })
        if health.get("scripts_needing_entrypoint", 0) > 0:
            novos_aprendizados.append({
                "timestamp": datetime.now().isoformat(),
                "categoria": "arquitetura",
                "aprendizado": f"{health['scripts_needing_entrypoint']} scripts sem entrypoint - maioria bibliotecas puras (decisao arquitetural)",
                "fonte": "ecosystem_scanner",
                "confianca": 0.8,
            })

    # Carrega historico para detectar tendencias
    try:
        historico = carregar_historico()
        if len(historico) >= 3:
            # Verifica tendencia de skills
            skills_vals = [s.get("totals", {}).get("skills", 0) for s in historico[-5:]]
            if skills_vals:
                delta_skills = skills_vals[-1] - skills_vals[0]
                if delta_skills > 0:
                    novos_aprendizados.append({
                        "timestamp": datetime.now().isoformat(),
                        "categoria": "tendencia",
                        "aprendizado": f"Crescimento de {delta_skills} skills nos ultimos snapshots",
                        "fonte": "ecosystem_history",
                        "confianca": 0.7,
                    })
                elif delta_skills < 0:
                    novos_aprendizados.append({
                        "timestamp": datetime.now().isoformat(),
                        "categoria": "tendencia",
                        "aprendizado": f"Reducao de {abs(delta_skills)} skills - possivel consolidacao",
                        "fonte": "ecosystem_history",
                        "confianca": 0.7,
                    })
    except Exception as e:
        print(f"[evolution] Erro ao analisar historico: {e}")

    # Atualiza learnings.json
    if novos_aprendizados:
        learnings_data = {"learnings": [], "total_records": 0, "last_updated": ""}
        if learnings_path.exists():
            try:
                learnings_data = json.loads(learnings_path.read_text(encoding="utf-8"))
            except:
                pass
        learnings_data["learnings"].extend(novos_aprendizados)
        learnings_data["total_records"] = len(learnings_data["learnings"])
        learnings_data["last_updated"] = datetime.now().isoformat()
        learnings_path.parent.mkdir(parents=True, exist_ok=True)
        learnings_path.write_text(json.dumps(learnings_data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[evolution] {len(novos_aprendizados)} aprendizado(s) extraido(s) e salvo(s)")

    KNOWLEDGE_PATH.parent.mkdir(parents=True, exist_ok=True)
    KNOWLEDGE_PATH.write_text(json.dumps(conhecimento, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[evolution] Conhecimento atualizado (ciclo {conhecimento['ciclos_analisados']})")


def gerar_relatorio_evolucao(analysis: dict) -> str:
    lines = []
    lines.append(f"# Relatorio de Evolucao Autonoma")
    lines.append(f"**Data**: {analysis['timestamp']}")
    lines.append(f"**Ciclos documentados**: {analysis['ciclos_documentados']}")
    lines.append(f"**Snapshots disponiveis**: {analysis['snapshots_disponiveis']}")
    lines.append("")
    lines.append("## Projecao de Health")
    proj = analysis.get("projecao", {})
    if "health_atual" in proj:
        lines.append(f"- Health atual: {proj['health_atual']:.2%}")
        lines.append(f"- Media recente: {proj['media_recente']:.2%}")
        lines.append(f"- Projecao: {proj['projecao']}")
    lines.append("")
    lines.append("## Sugestoes Prioritarias")
    for s in analysis.get("sugestoes", []):
        lines.append(f"- [{s['prioridade'].upper()}] **{s['acao']}**")
        lines.append(f"  _Categoria: {s['categoria']} | {s['justificativa']}_")
    lines.append("")
    lines.append("## Tendencias")
    for metrica, dados in analysis.get("padroes", {}).get("metricas_tendencia", {}).items():
        vals = " -> ".join(f"{v[1]}" for v in dados["valores"])
        lines.append(f"- {metrica}: {vals} (tendencia: {dados['tendencia']})")
    lines.append("")
    lines.append("_Gerado por evolution_engine.py_")
    return "\n".join(lines)


def main():
    import argparse
    p = argparse.ArgumentParser(description="Motor de evolucao autonoma")
    p.add_argument("--analyze", action="store_true", help="Analisa padroes de evolucao")
    p.add_argument("--learn", action="store_true", help="Aprende com estado atual")
    p.add_argument("--suggest", action="store_true", help="Gera sugestoes de melhoria")
    p.add_argument("--report", action="store_true", help="Relatorio completo")
    args = p.parse_args()

    if args.learn:
        learn()
        return

    analysis = analyze()

    if args.analyze or args.suggest or args.report or not any(vars(args).values()):
        if args.suggest:
            print("## Sugestoes de Melhoria")
            for s in analysis.get("sugestoes", []):
                print(f"[{s['prioridade'].upper()}] {s['acao']}")
                print(f"  -> {s['justificativa']}")
        elif args.report:
            report = gerar_relatorio_evolucao(analysis)
            report_path = WORKSPACE / "evals" / f"evolucao_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
            report_path.write_text(report, encoding="utf-8")
            print(f"[evolution] Relatorio salvo em {report_path}")
        else:
            import json
            print(json.dumps(analysis, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
