#!/usr/bin/env python3
"""
DataCollector — Coleta dados reais (World Bank, IBGE) para calibrar simulações.
Gera DataFrames estruturados e cache local (SQLite).
Padrão Qualis A1 — fontes auditáveis e reprodutíveis.
"""

import json, sqlite3, time, os, sys
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Tuple
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from collections import defaultdict

BRAZIL_TZ = timezone(timedelta(hours=-3))
BRAZIL_TIME = lambda: datetime.now(BRAZIL_TZ)

# Indicadores reais do World Bank para o Brasil (2013-2023)
# Fonte: https://api.worldbank.org/v2/ — acesso público, sem autenticação
WORLD_BANK_INDICATORS = {
    # Macroeconomia
    "NY.GDP.PCAP.CD":    "PIB per capita (US$ corrente)",
    "NY.GDP.MKTP.KD.ZG": "Crescimento PIB (% anual)",
    "FP.CPI.TOTL.ZG":    "Inflação IPC (% anual)",
    "NE.EXP.GNFS.ZS":    "Exportações (% PIB)",
    "GC.DOD.TOTL.GD.ZS": "Dívida pública (% PIB)",
    "BX.KLT.DINV.WD.GD.ZS": "Investimento estrangeiro (% PIB)",
    "SL.UEM.TOTL.ZS":    "Desemprego total (% força trabalho)",

    # Social / Desigualdade
    "SI.POV.GINI":       "Índice de Gini",
    "SI.POV.NAHC":       "Pobreza (US$6.85/dia, % pop)",
    "SL.TLF.ACTI.ZS":    "Participação força trabalho (%)",

    # Educação
    "SE.PRM.ENRR":       "Matrícula ensino fundamental (%)",
    "SE.SEC.ENRR":       "Matrícula ensino médio (%)",
    "SE.TER.ENRR":       "Matrícula ensino superior (%)",
    "SE.XPD.TOTL.GD.ZS": "Gasto público educação (% PIB)",

    # Saúde
    "SP.DYN.LE00.IN":    "Expectativa de vida (anos)",
    "SH.XPD.CHEX.GD.ZS": "Gasto saúde (% PIB)",
    "SH.STA.MMRT":       "Mortalidade materna (por 100k)",
    "SH.DYN.MORT":       "Mortalidade infantil (por 1k)",

    # Ciência & Tecnologia
    "GB.XPD.RSDV.GD.ZS": "Gasto P&D (% PIB)",
    "IP.JRN.ARTC.SC":    "Artigos científicos publicados",
    "IT.NET.USER.ZS":    "Usuários internet (% pop)",
    "IT.CEL.SETS.P2":    "Assinaturas celular (por 100)",

    # Meio Ambiente
    "EN.ATM.CO2E.PC":    "Emissões CO2 per capita (ton)",
    "ER.FST.TOTL.ZS":    "Área florestal (% território)",
    "EG.USE.ELEC.KH.PC": "Consumo energia elétrica (kWh pc)",
}

# Dados do IBGE/PNAD (valores fixos atualizados anualmente)
IBGE_INDICATORS = {
    "populacao_milhoes":     {"valor": 212.6, "ano": 2024, "fonte": "IBGE/PNAD"},
    "populacao_urbana_pct":  {"valor": 87.4,  "ano": 2023, "fonte": "IBGE"},
    "analfabetismo_pct":     {"valor": 5.4,   "ano": 2023, "fonte": "IBGE/PNAD Continua"},
    "renda_domiciliar_media":{"valor": 1893,  "ano": 2023, "fonte": "IBGE/PNAD"},
    "desigualdade_racial_pct":{"valor": 74.6, "ano": 2023, "fonte": "IBGE (razão PcD/brancos)"},
}


# ═══════════════════════════════════════════════════════════════════
# DATA COLLECTOR ENGINE
# ═══════════════════════════════════════════════════════════════════

class DataCollector:
    """Coleta dados reais de APIs públicas e gera DataFrames."""

    def __init__(self, cache_db: str = ".reversa/data_cache.db"):
        self.cache_db = cache_db
        self._init_cache()
        self.indicators: Dict[str, List[Dict]] = {}
        self.dataframe: Dict[str, Any] = {}

    def _init_cache(self):
        os.makedirs(os.path.dirname(self.cache_db), exist_ok=True)
        conn = sqlite3.connect(self.cache_db)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS wb_cache (
                indicator TEXT, country TEXT, year INTEGER,
                value REAL, fetched_at TEXT,
                PRIMARY KEY (indicator, country, year)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS fetch_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT, records INTEGER, success INTEGER,
                error TEXT, timestamp TEXT
            )
        """)
        conn.commit()
        conn.close()

    def fetch_world_bank(self, indicator: str, country: str = "BR",
                         years: str = "2013:2023") -> List[Dict]:
        """Busca indicador do World Bank API. Gratuito, sem auth."""
        # Check cache first
        conn = sqlite3.connect(self.cache_db)
        cached = conn.execute(
            "SELECT year, value FROM wb_cache WHERE indicator=? AND country=? ORDER BY year",
            (indicator, country)
        ).fetchall()
        if len(cached) >= 5:
            conn.close()
            return [{"year": r[0], "value": r[1]} for r in cached]

        # Fetch from API
        url = (f"https://api.worldbank.org/v2/country/{country}/indicator/{indicator}"
               f"?format=json&date={years}&per_page=100")
        try:
            req = Request(url, headers={"User-Agent": "OpenCode/4.2 MiroFish Research"})
            with urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode())

            records = []
            if data and len(data) > 1 and data[1]:
                for item in data[1]:
                    if item.get("value") is not None:
                        year = int(item["date"])
                        value = float(item["value"])
                        records.append({"year": year, "value": value})
                        conn.execute(
                            "INSERT OR REPLACE INTO wb_cache VALUES (?,?,?,?,?)",
                            (indicator, country, year, value, BRAZIL_TIME().isoformat())
                        )
            conn.execute(
                "INSERT INTO fetch_log (source, records, success, timestamp) VALUES (?,?,?,?)",
                (f"WB:{indicator}", len(records), 1, BRAZIL_TIME().isoformat())
            )
            conn.commit()
            conn.close()

            if not records:
                print(f"[WARN] No data for {indicator} — usando fallback sintético")
            return sorted(records, key=lambda r: r["year"])

        except (URLError, HTTPError, ConnectionError, TimeoutError, OSError) as e:
            conn.execute(
                "INSERT INTO fetch_log (source, records, success, error, timestamp) VALUES (?,?,?,?,?)",
                (f"WB:{indicator}", 0, 0, str(e)[:200], BRAZIL_TIME().isoformat())
            )
            conn.commit()
            conn.close()
            print(f"[WARN] API offline para {indicator}: {e}")
            return []

    def build_dataframe(self, indicators: List[str] = None,
                        country: str = "BR") -> Dict[str, Any]:
        """Constrói DataFrame sintético (dict) com dados reais + preenchimento."""
        if indicators is None:
            indicators = list(WORLD_BANK_INDICATORS.keys())

        years = list(range(2013, 2024))
        df = {"years": years}

        for ind in indicators:
            label = WORLD_BANK_INDICATORS.get(ind, ind)
            records = self.fetch_world_bank(ind, country)
            values_by_year = {r["year"]: r["value"] for r in records}

            series = []
            for y in years:
                if y in values_by_year:
                    series.append(round(values_by_year[y], 4))
                else:
                    # Interpolação linear ou último valor conhecido
                    known = [(k, v) for k, v in sorted(values_by_year.items())]
                    if known:
                        if y < known[0][0]:
                            series.append(round(known[0][1], 4))
                        elif y > known[-1][0]:
                            series.append(round(known[-1][1], 4))
                        else:
                            # Interpolar
                            for i in range(len(known) - 1):
                                if known[i][0] <= y <= known[i+1][0]:
                                    t = (y - known[i][0]) / (known[i+1][0] - known[i][0])
                                    v = known[i][1] + t * (known[i+1][1] - known[i][1])
                                    series.append(round(v, 4))
                                    break
                            else:
                                series.append(round(known[-1][1], 4))
                    else:
                        series.append(None)
            df[ind] = series
            df[f"{ind}_label"] = label

        # Add IBGE data
        for key, info in IBGE_INDICATORS.items():
            df[key] = info

        self.dataframe = df
        return df

    def get_brazil_summary(self) -> Dict[str, Any]:
        """Retorna resumo executivo dos indicadores Brasil."""
        if not self.dataframe:
            self.build_dataframe()

        df = self.dataframe
        summary = {
            "timestamp": BRAZIL_TIME().isoformat(),
            "country": "Brasil (BR)",
            "period": f"{df['years'][0]}-{df['years'][-1]}",
            "sources": ["World Bank API", "IBGE/PNAD"],
            "indicators": {},
        }

        for ind, label in WORLD_BANK_INDICATORS.items():
            if ind in df:
                values = [v for v in df[ind] if v is not None]
                if len(values) >= 2:
                    first = values[0]
                    last = values[-1]
                    trend = "up" if last > first * 1.02 else "down" if last < first * 0.98 else "stable"
                    summary["indicators"][ind] = {
                        "label": label,
                        "first": first,
                        "last": last,
                        "change_pct": round((last - first) / abs(first) * 100, 2) if first else 0,
                        "trend": trend,
                        "values": values,
                    }

        return summary

    def compute_correlations(self) -> List[Dict]:
        """Calcula correlações de Pearson entre indicadores."""
        if not self.dataframe:
            self.build_dataframe()

        df = self.dataframe
        years = df["years"]
        indicators = [k for k in WORLD_BANK_INDICATORS if k in df and any(v is not None for v in df[k])]
        correlations = []

        for i in range(len(indicators)):
            for j in range(i + 1, len(indicators)):
                a_vals = df[indicators[i]]
                b_vals = df[indicators[j]]
                pairs = [(a, b) for a, b in zip(a_vals, b_vals) if a is not None and b is not None]
                if len(pairs) < 4:
                    continue

                n = len(pairs)
                ma = sum(p[0] for p in pairs) / n
                mb = sum(p[1] for p in pairs) / n
                num = sum((p[0] - ma) * (p[1] - mb) for p in pairs)
                da = sum((p[0] - ma) ** 2 for p in pairs)
                db = sum((p[1] - mb) ** 2 for p in pairs)
                r = round(num / ((da * db) ** 0.5), 4) if da > 0 and db > 0 else 0

                if abs(r) > 0.25:
                    correlations.append({
                        "ind_a": indicators[i],
                        "label_a": WORLD_BANK_INDICATORS[indicators[i]],
                        "ind_b": indicators[j],
                        "label_b": WORLD_BANK_INDICATORS[indicators[j]],
                        "r": r,
                        "strength": "forte" if abs(r) > 0.6 else "moderada" if abs(r) > 0.3 else "fraca",
                        "n": n,
                    })

        return sorted(correlations, key=lambda c: abs(c["r"]), reverse=True)


# ═══════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("DataCollector — World Bank + IBGE")
    print("=" * 60)

    dc = DataCollector()
    df = dc.build_dataframe()

    # Resumo
    summary = dc.get_brazil_summary()
    print(f"\nBrasil {summary['period']}:")
    for ind, info in sorted(summary["indicators"].items(), key=lambda x: abs(x[1]["change_pct"]), reverse=True)[:5]:
        arrow = "↑" if info["trend"] == "up" else "↓" if info["trend"] == "down" else "→"
        print(f"  {arrow} {info['label']}: {info['first']:.1f} → {info['last']:.1f} ({info['change_pct']:+.1f}%)")

    # Correlações
    corrs = dc.compute_correlations()
    print(f"\nTop 5 correlações (|r| > 0.25):")
    for c in corrs[:5]:
        print(f"  {c['label_a'][:30]} × {c['label_b'][:30]}: r={c['r']:+.3f} ({c['strength']}, n={c['n']})")

    print(f"\nTotal: {len(df['years'])} anos, {len(summary['indicators'])} indicadores, {len(corrs)} correlações")
