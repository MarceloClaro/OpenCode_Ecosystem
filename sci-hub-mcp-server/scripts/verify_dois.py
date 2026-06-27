import requests
import json
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# DOIs from referencias.bib
dois = {
    "ALMEIDA2024": "10.54033/cadpedv21n9-232",
    "BARBOSA2013": "10.26849/bts.v39i2.349",
    "BARRON1998": "10.1080/10508406.1998.9672056",
    "BARROWS1996": "10.1002/tl.37219966804",
    "BLACK1998": "10.1080/0969595980050102",
    "CALLEGARIO2025": "10.28998/lte.2024.n.2.17872",
    "CANTANHEDE2026": "10.47820/recima21.v7i4.7525",
    "GOMES2009": "10.1590/S0100-55022009000300014",
    "GUSMAO2022": "10.5902/1984644464040",
    "MACHADO2025": "10.34630/pel.v8i3.6360",
    "MACIEL2018": "10.17921/2447-8733.2018v19n2p195-201",
    "MENEZES2020": "10.5935/0034-7140.20200010",
    "MEZZARI2011": "10.1590/S0100-55022011000100015",
    "MIRANDA2022": "10.34117/bjdv8n4-353",
    "RIBEIRO2023": "10.54021/seesv4n1-027",
    "RIBEIRO2025": "10.58422/repesq.2025.e1751",
    "RIOS2026": "10.22481/praxisedu.v22i53.17193",
    "SANTOS2019": "10.18265/1517-03062015v1n44p113-121",
    "SANTOS2024": "10.17921/2447-8733.2024v25n1p51-59",
    "SCHMIDT2001": "10.1111/j.1365-2923.1983.tb01086.x",
    "SILVA2023": "10.5585/45.2023.24026",
    "SOARES2013": "10.1590/S0101-73302013000300013",
    "SOARES2021": "10.4025/actascieduc.v44i1.52168",
    "SOUSA2025": "10.36560/18320252057",
    "TEODORO2024": "10.14244/reveduc.v18i1.5376",
    "DAHAL2026": "10.3389/frma.2025.1669578",
    "PAULUS2023": "10.1177/15344843221138381",
    "KABIR2025": "10.1177/16094069251336810",
}

print("=== Verificacao de DOIs via CrossRef ===\n")
results = {}
for key, doi in dois.items():
    try:
        r = requests.get(f"https://api.crossref.org/works/{doi}", timeout=10)
        if r.status_code == 200:
            data = r.json()["message"]
            title = data.get("title", [""])[0][:80]
            year = ""
            if data.get("published-print"):
                parts = data["published-print"].get("date-parts", [[]])[0]
                if parts:
                    year = str(parts[0])
            results[key] = {"status": "OK", "doi": doi, "title": title, "year": year}
            print(f"  OK   {key:20s} {doi}")
        else:
            results[key] = {"status": "NOT_FOUND", "doi": doi}
            print(f"  FAIL {key:20s} {doi} -> HTTP {r.status_code}")
    except Exception as e:
        results[key] = {"status": "ERROR", "doi": doi, "error": str(e)}
        print(f"  ERR  {key:20s} {doi} -> {e}")

ok = sum(1 for r in results.values() if r["status"] == "OK")
fail = sum(1 for r in results.values() if r["status"] != "OK")
print(f"\n=== Resultado: {ok} OK, {fail} FAIL de {len(dois)} ===")
