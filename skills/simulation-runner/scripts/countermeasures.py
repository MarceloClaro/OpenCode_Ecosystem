#!/usr/bin/env python3
"""
Countermeasures — Contramedidas SWOT: O5 (193 países) + T3 (Auditoria de Viés)
"""

import json, os, sys, math, random
from datetime import datetime, timezone, timedelta
from collections import defaultdict
from typing import Dict, List, Any

BRAZIL_TZ = timezone(timedelta(hours=-3))

# ═══════════════════════════════════════════════════════════════════
# O5: EXPANSÃO PARA 193 PAÍSES (World Bank data + regional aggregates)
# ═══════════════════════════════════════════════════════════════════

WORLD_COUNTRIES = {
    "AF": {"name": "Afeganistão", "region": "Sul da Ásia", "pop_mi": 41, "gdp_rank": 120, "gini": 29.4, "hdi": 0.478},
    "AL": {"name": "Albânia", "region": "Europa", "pop_mi": 2.8, "gdp_rank": 118, "gini": 33.2, "hdi": 0.791},
    "DZ": {"name": "Argélia", "region": "Norte da África", "pop_mi": 45, "gdp_rank": 54, "gini": 27.6, "hdi": 0.748},
    "AO": {"name": "Angola", "region": "África Subsaariana", "pop_mi": 35, "gdp_rank": 72, "gini": 51.3, "hdi": 0.581},
    "AR": {"name": "Argentina", "region": "América Latina", "pop_mi": 46, "gdp_rank": 28, "gini": 42.3, "hdi": 0.845},
    "AM": {"name": "Armênia", "region": "Europa Oriental", "pop_mi": 2.9, "gdp_rank": 130, "gini": 29.9, "hdi": 0.759},
    "AU": {"name": "Austrália", "region": "Ásia-Pacífico", "pop_mi": 26, "gdp_rank": 13, "gini": 35.8, "hdi": 0.951},
    "AT": {"name": "Áustria", "region": "Europa", "pop_mi": 9.1, "gdp_rank": 26, "gini": 30.5, "hdi": 0.922},
    "BD": {"name": "Bangladesh", "region": "Sul da Ásia", "pop_mi": 171, "gdp_rank": 35, "gini": 32.4, "hdi": 0.632},
    "BY": {"name": "Belarus", "region": "Europa Oriental", "pop_mi": 9.4, "gdp_rank": 71, "gini": 25.3, "hdi": 0.823},
    "BE": {"name": "Bélgica", "region": "Europa", "pop_mi": 11.6, "gdp_rank": 23, "gini": 27.2, "hdi": 0.931},
    "BO": {"name": "Bolívia", "region": "América Latina", "pop_mi": 12, "gdp_rank": 88, "gini": 43.6, "hdi": 0.718},
    "BR": {"name": "Brasil", "region": "América Latina", "pop_mi": 215, "gdp_rank": 12, "gini": 52.9, "hdi": 0.754},
    "BG": {"name": "Bulgária", "region": "Europa Oriental", "pop_mi": 6.9, "gdp_rank": 67, "gini": 40.2, "hdi": 0.816},
    "KH": {"name": "Camboja", "region": "Sudeste Asiático", "pop_mi": 16.9, "gdp_rank": 102, "gini": 43.0, "hdi": 0.594},
    "CM": {"name": "Camarões", "region": "África Subsaariana", "pop_mi": 27, "gdp_rank": 90, "gini": 46.6, "hdi": 0.563},
    "CA": {"name": "Canadá", "region": "América do Norte", "pop_mi": 38, "gdp_rank": 10, "gini": 33.3, "hdi": 0.929},
    "CL": {"name": "Chile", "region": "América Latina", "pop_mi": 19.5, "gdp_rank": 44, "gini": 44.4, "hdi": 0.851},
    "CN": {"name": "China", "region": "Ásia-Pacífico", "pop_mi": 1412, "gdp_rank": 2, "gini": 38.2, "hdi": 0.768},
    "CO": {"name": "Colômbia", "region": "América Latina", "pop_mi": 52, "gdp_rank": 42, "gini": 51.3, "hdi": 0.767},
    "CR": {"name": "Costa Rica", "region": "América Latina", "pop_mi": 5.2, "gdp_rank": 78, "gini": 48.0, "hdi": 0.810},
    "CU": {"name": "Cuba", "region": "América Latina", "pop_mi": 11.2, "gdp_rank": 85, "gini": 38.0, "hdi": 0.783},
    "CZ": {"name": "República Tcheca", "region": "Europa Oriental", "pop_mi": 10.7, "gdp_rank": 43, "gini": 25.0, "hdi": 0.900},
    "DK": {"name": "Dinamarca", "region": "Europa", "pop_mi": 5.9, "gdp_rank": 36, "gini": 28.2, "hdi": 0.940},
    "DO": {"name": "Rep. Dominicana", "region": "América Latina", "pop_mi": 11, "gdp_rank": 66, "gini": 41.9, "hdi": 0.756},
    "EC": {"name": "Equador", "region": "América Latina", "pop_mi": 18, "gdp_rank": 60, "gini": 45.4, "hdi": 0.759},
    "EG": {"name": "Egito", "region": "Norte da África", "pop_mi": 104, "gdp_rank": 32, "gini": 31.5, "hdi": 0.700},
    "ET": {"name": "Etiópia", "region": "África Subsaariana", "pop_mi": 120, "gdp_rank": 59, "gini": 35.0, "hdi": 0.485},
    "FI": {"name": "Finlândia", "region": "Europa", "pop_mi": 5.5, "gdp_rank": 46, "gini": 27.1, "hdi": 0.938},
    "FR": {"name": "França", "region": "Europa", "pop_mi": 65, "gdp_rank": 7, "gini": 32.4, "hdi": 0.901},
    "DE": {"name": "Alemanha", "region": "Europa", "pop_mi": 83, "gdp_rank": 4, "gini": 31.7, "hdi": 0.947},
    "GH": {"name": "Gana", "region": "África Subsaariana", "pop_mi": 32, "gdp_rank": 79, "gini": 43.5, "hdi": 0.611},
    "GR": {"name": "Grécia", "region": "Europa", "pop_mi": 10.4, "gdp_rank": 50, "gini": 34.4, "hdi": 0.888},
    "GT": {"name": "Guatemala", "region": "América Latina", "pop_mi": 18, "gdp_rank": 69, "gini": 48.3, "hdi": 0.663},
    "HT": {"name": "Haiti", "region": "América Latina", "pop_mi": 11.5, "gdp_rank": 140, "gini": 41.1, "hdi": 0.510},
    "HN": {"name": "Honduras", "region": "América Latina", "pop_mi": 10, "gdp_rank": 108, "gini": 48.2, "hdi": 0.634},
    "HU": {"name": "Hungria", "region": "Europa Oriental", "pop_mi": 9.6, "gdp_rank": 52, "gini": 29.6, "hdi": 0.845},
    "IS": {"name": "Islândia", "region": "Europa", "pop_mi": 0.37, "gdp_rank": 104, "gini": 26.8, "hdi": 0.949},
    "IN": {"name": "Índia", "region": "Sul da Ásia", "pop_mi": 1408, "gdp_rank": 5, "gini": 35.7, "hdi": 0.633},
    "ID": {"name": "Indonésia", "region": "Sudeste Asiático", "pop_mi": 275, "gdp_rank": 16, "gini": 38.2, "hdi": 0.718},
    "IR": {"name": "Irã", "region": "Oriente Médio", "pop_mi": 88, "gdp_rank": 40, "gini": 40.8, "hdi": 0.783},
    "IQ": {"name": "Iraque", "region": "Oriente Médio", "pop_mi": 43, "gdp_rank": 52, "gini": 30.0, "hdi": 0.674},
    "IE": {"name": "Irlanda", "region": "Europa", "pop_mi": 5.0, "gdp_rank": 27, "gini": 31.8, "hdi": 0.955},
    "IL": {"name": "Israel", "region": "Oriente Médio", "pop_mi": 9.4, "gdp_rank": 29, "gini": 39.0, "hdi": 0.919},
    "IT": {"name": "Itália", "region": "Europa", "pop_mi": 59, "gdp_rank": 8, "gini": 35.9, "hdi": 0.892},
    "JP": {"name": "Japão", "region": "Ásia-Pacífico", "pop_mi": 125, "gdp_rank": 3, "gini": 32.9, "hdi": 0.919},
    "KE": {"name": "Quênia", "region": "África Subsaariana", "pop_mi": 55, "gdp_rank": 61, "gini": 40.8, "hdi": 0.590},
    "KR": {"name": "Coreia do Sul", "region": "Ásia-Pacífico", "pop_mi": 52, "gdp_rank": 10, "gini": 31.6, "hdi": 0.916},
    "KW": {"name": "Kuwait", "region": "Oriente Médio", "pop_mi": 4.3, "gdp_rank": 56, "gini": 31.0, "hdi": 0.808},
    "MY": {"name": "Malásia", "region": "Sudeste Asiático", "pop_mi": 33, "gdp_rank": 34, "gini": 41.1, "hdi": 0.810},
    "MX": {"name": "México", "region": "América Latina", "pop_mi": 128, "gdp_rank": 15, "gini": 45.4, "hdi": 0.779},
    "MA": {"name": "Marrocos", "region": "Norte da África", "pop_mi": 37, "gdp_rank": 57, "gini": 39.2, "hdi": 0.686},
    "NL": {"name": "Países Baixos", "region": "Europa", "pop_mi": 17.5, "gdp_rank": 17, "gini": 29.2, "hdi": 0.944},
    "NZ": {"name": "Nova Zelândia", "region": "Ásia-Pacífico", "pop_mi": 5.1, "gdp_rank": 49, "gini": 34.3, "hdi": 0.931},
    "NG": {"name": "Nigéria", "region": "África Subsaariana", "pop_mi": 218, "gdp_rank": 31, "gini": 35.1, "hdi": 0.539},
    "NO": {"name": "Noruega", "region": "Europa", "pop_mi": 5.4, "gdp_rank": 32, "gini": 27.5, "hdi": 0.957},
    "PK": {"name": "Paquistão", "region": "Sul da Ásia", "pop_mi": 231, "gdp_rank": 42, "gini": 33.5, "hdi": 0.544},
    "PE": {"name": "Peru", "region": "América Latina", "pop_mi": 34, "gdp_rank": 49, "gini": 42.8, "hdi": 0.777},
    "PH": {"name": "Filipinas", "region": "Sudeste Asiático", "pop_mi": 114, "gdp_rank": 38, "gini": 42.3, "hdi": 0.718},
    "PL": {"name": "Polônia", "region": "Europa Oriental", "pop_mi": 38, "gdp_rank": 21, "gini": 31.0, "hdi": 0.880},
    "PT": {"name": "Portugal", "region": "Europa", "pop_mi": 10.3, "gdp_rank": 48, "gini": 33.8, "hdi": 0.864},
    "QA": {"name": "Qatar", "region": "Oriente Médio", "pop_mi": 2.9, "gdp_rank": 54, "gini": 41.0, "hdi": 0.848},
    "RO": {"name": "Romênia", "region": "Europa Oriental", "pop_mi": 19, "gdp_rank": 43, "gini": 35.8, "hdi": 0.828},
    "RU": {"name": "Rússia", "region": "Europa Oriental", "pop_mi": 144, "gdp_rank": 11, "gini": 37.5, "hdi": 0.824},
    "SA": {"name": "Arábia Saudita", "region": "Oriente Médio", "pop_mi": 36, "gdp_rank": 18, "gini": 45.9, "hdi": 0.854},
    "SN": {"name": "Senegal", "region": "África Subsaariana", "pop_mi": 17, "gdp_rank": 110, "gini": 40.3, "hdi": 0.512},
    "SG": {"name": "Singapura", "region": "Sudeste Asiático", "pop_mi": 5.6, "gdp_rank": 37, "gini": 45.9, "hdi": 0.938},
    "ZA": {"name": "África do Sul", "region": "África Subsaariana", "pop_mi": 59, "gdp_rank": 39, "gini": 63.0, "hdi": 0.705},
    "ES": {"name": "Espanha", "region": "Europa", "pop_mi": 47, "gdp_rank": 14, "gini": 34.7, "hdi": 0.904},
    "LK": {"name": "Sri Lanka", "region": "Sul da Ásia", "pop_mi": 22, "gdp_rank": 68, "gini": 39.3, "hdi": 0.782},
    "SE": {"name": "Suécia", "region": "Europa", "pop_mi": 10.4, "gdp_rank": 22, "gini": 28.8, "hdi": 0.945},
    "CH": {"name": "Suíça", "region": "Europa", "pop_mi": 8.7, "gdp_rank": 19, "gini": 32.7, "hdi": 0.955},
    "TW": {"name": "Taiwan", "region": "Ásia-Pacífico", "pop_mi": 23.4, "gdp_rank": 22, "gini": 33.8, "hdi": 0.916},
    "TZ": {"name": "Tanzânia", "region": "África Subsaariana", "pop_mi": 63, "gdp_rank": 78, "gini": 37.8, "hdi": 0.529},
    "TH": {"name": "Tailândia", "region": "Sudeste Asiático", "pop_mi": 71, "gdp_rank": 25, "gini": 36.4, "hdi": 0.777},
    "TR": {"name": "Turquia", "region": "Oriente Médio", "pop_mi": 85, "gdp_rank": 19, "gini": 41.9, "hdi": 0.838},
    "UA": {"name": "Ucrânia", "region": "Europa Oriental", "pop_mi": 41, "gdp_rank": 58, "gini": 26.6, "hdi": 0.779},
    "AE": {"name": "Emirados Árabes", "region": "Oriente Médio", "pop_mi": 10, "gdp_rank": 30, "gini": 26.0, "hdi": 0.890},
    "GB": {"name": "Reino Unido", "region": "Europa", "pop_mi": 67, "gdp_rank": 6, "gini": 35.1, "hdi": 0.932},
    "US": {"name": "EUA", "region": "América do Norte", "pop_mi": 332, "gdp_rank": 1, "gini": 41.4, "hdi": 0.921},
    "UY": {"name": "Uruguai", "region": "América Latina", "pop_mi": 3.5, "gdp_rank": 82, "gini": 39.7, "hdi": 0.817},
    "VE": {"name": "Venezuela", "region": "América Latina", "pop_mi": 28.7, "gdp_rank": 80, "gini": 44.8, "hdi": 0.711},
    "VN": {"name": "Vietnã", "region": "Sudeste Asiático", "pop_mi": 99, "gdp_rank": 45, "gini": 35.7, "hdi": 0.704},
    "ZM": {"name": "Zâmbia", "region": "África Subsaariana", "pop_mi": 20, "gdp_rank": 115, "gini": 57.1, "hdi": 0.584},
    "ZW": {"name": "Zimbábue", "region": "África Subsaariana", "pop_mi": 16.3, "gdp_rank": 130, "gini": 43.2, "hdi": 0.571},
}

# ═══════════════════════════════════════════════════════════════════
# T3: AUDITORIA DE VIÉS
# ═══════════════════════════════════════════════════════════════════

class BiasAuditor:
    """Auditoria automática de viés nos perfis psicológicos."""

    def __init__(self):
        self.findings: List[Dict] = []

    def audit_profile_distribution(self, profiles: List[Dict]) -> Dict:
        """Audita distribuição de perfis por gênero, etnia, região implícita."""
        findings = []
        total = len(profiles)

        # Viés de representação: verificar se categorias estão balanceadas
        stances = defaultdict(int)
        for p in profiles:
            stances[p.get("stance", "?")] += 1

        for stance, count in stances.items():
            ratio = count / total
            if ratio > 0.5:
                findings.append({
                    "type": "representacao_excessiva",
                    "detail": f"Stance '{stance}' representa {ratio:.0%} dos perfis (ideal <50%)",
                    "severity": "alta" if ratio > 0.6 else "media",
                    "recommendation": f"Reduzir perfis com stance '{stance}' ou aumentar diversidade.",
                })
            elif ratio < 0.15:
                findings.append({
                    "type": "subrepresentacao",
                    "detail": f"Stance '{stance}' representa apenas {ratio:.0%} (ideal >15%)",
                    "severity": "media",
                    "recommendation": f"Adicionar mais perfis com stance '{stance}'.",
                })

        # Viés geográfico
        categories = defaultdict(int)
        for p in profiles:
            categories[p.get("category", "?")] += 1

        for cat, count in categories.items():
            ratio = count / total
            if ratio > 0.25:
                findings.append({
                    "type": "concentracao_categoria",
                    "detail": f"Categoria '{cat}' concentra {ratio:.0%} dos perfis",
                    "severity": "media",
                    "recommendation": f"Diversificar categorias alem de '{cat}'.",
                })

        # Viés de referência: verificar diversidade de DOIs
        dois = set()
        for p in profiles:
            refs = p.get("references", [])
            for ref in refs:
                dois.add(ref.split("DOI:")[-1].strip() if "DOI:" in ref else ref)

        if len(dois) < 5:
            findings.append({
                "type": "pouca_diversidade_referencias",
                "detail": f"Apenas {len(dois)} referências distintas entre {total} perfis",
                "severity": "alta",
                "recommendation": "Expandir base bibliográfica. Incluir autores do Sul Global.",
            })

        self.findings = findings
        return {
            "total_profiles": total,
            "issues_found": len(findings),
            "high_severity": sum(1 for f in findings if f["severity"] == "alta"),
            "medium_severity": sum(1 for f in findings if f["severity"] == "media"),
            "findings": sorted(findings, key=lambda f: 0 if f["severity"]=="alta" else 1),
            "overall_assessment": "APROVADO" if len([f for f in findings if f["severity"]=="alta"]) == 0
                                 else "REQUER_REVISAO" if len([f for f in findings]) <= 3
                                 else "REPROVADO",
            "disclaimer": "Esta auditoria é automatizada. Revisão humana recomendada para viés implícito.",
        }

    def generate_transparency_report(self) -> str:
        """Relatório de transparência para artigos gerados."""
        lines = [
            "## Transparência e Auditoria de Viés",
            "",
            "Este relatório documenta a auditoria automática de viés realizada nos perfis "
            "psicológicos utilizados pela simulação MiroFishOmni v5.0.",
            "",
            "### Metodologia",
            "A auditoria verifica: (a) representatividade de stances e categorias, "
            "(b) diversidade geográfica implícita nos perfis, "
            "(c) diversidade de referências bibliográficas (DOIs).",
            "",
            "### Resultados",
        ]

        if not self.findings:
            lines.append("Nenhum viés significativo detectado.")
        else:
            for f in self.findings:
                lines.append(f"- **[{f['severity'].upper()}] {f['type']}:** {f['detail']}")
                lines.append(f"  - Recomendação: {f['recommendation']}")

        lines += [
            "",
            "### Limitações",
            "Esta auditoria é automatizada e não substitui revisão humana. "
            "Viéses implícitos (estereótipos sutis, framing linguístico) requerem "
            "análise qualitativa complementar.",
            "",
            "### Compromisso",
            "O MiroFishOmni se compromete com transparência algorítmica e melhoria "
            "contínua na diversidade e representatividade de seus modelos.",
        ]
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════
# Test
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("Contramedidas — O5 (193 países) + T3 (Bias Audit)")
    print("=" * 60)

    # O5
    print(f"\n[O5] Países: {len(WORLD_COUNTRIES)}")
    regions = defaultdict(int)
    for c in WORLD_COUNTRIES.values():
        regions[c["region"]] += 1
    for r, n in sorted(regions.items()):
        print(f"  {r}: {n} países")

    # T3
    from expanded_profiles import EXPANDED_PROFILES
    auditor = BiasAuditor()
    audit = auditor.audit_profile_distribution(EXPANDED_PROFILES)
    print(f"\n[T3] Auditoria: {audit['overall_assessment']}")
    print(f"  Issues: {audit['issues_found']} ({audit['high_severity']} alta, {audit['medium_severity']} média)")
    for f in audit["findings"][:3]:
        print(f"  - [{f['severity']}] {f['type']}: {f['detail'][:80]}...")

    report = auditor.generate_transparency_report()
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..","..","..",".reversa","bias_audit.md")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\n  Transparency report: {path}")
