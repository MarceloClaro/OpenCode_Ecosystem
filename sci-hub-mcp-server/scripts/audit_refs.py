import re
import os
import sys
import io
import requests
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = r"C:\Users\marce\Documents\OpenCode_Ecosystem\MD\dissertacao-latex"
# Include ALL tex files that are actually \input into dissertacao.tex
TEX_FILES = [
    "01_introducao.tex",
    "02_aspectos_estrategicos.tex",
    "03_organizacao_trabalho.tex",
    "04_resultados.tex",
    "04_projecao_estudo.tex",
    "05_conclusao.tex",
    "apx-qualitative-coder.tex",
    "12-introducao.tex",
    "13-revisao-literatura.tex",
    "14-metodologia.tex",
    "15-resultados.tex",
    "16-discussao.tex",
    "17-conclusao.tex",
    "18-referencias.tex",
    "19-apendice-a.tex",
    "20-apendice-b.tex",
    "21-apendice-c.tex",
]

print("=" * 70)
print("VARREDURA COMPLETA: CITAÇÕES × REFERÊNCIAS × LINKS")
print("=" * 70)

all_citations = set()
citation_map = {}

for texfile in TEX_FILES:
    path = os.path.join(BASE, texfile)
    if not os.path.exists(path):
        continue
    with open(path, encoding="utf-8") as f:
        content = f.read()
    cites = re.findall(r'\\cite[tp]?\{([^}]+)\}', content)
    for c in cites:
        keys = [k.strip() for k in c.split(",")]
        for key in keys:
            all_citations.add(key)
            if key not in citation_map:
                citation_map[key] = []
            citation_map[key].append(texfile)

print(f"\n[1] CITAÇÕES ENCONTRADAS NO TEXTO: {len(all_citations)}")
for key in sorted(all_citations):
    files = ", ".join(sorted(set(citation_map[key])))
    print(f"  {key:25s} -> {files}")

bib_path = os.path.join(BASE, "referencias.bib")
with open(bib_path, encoding="utf-8") as f:
    bib_content = f.read()

bib_entries = re.findall(r'@\w+\{(\w+),', bib_content)
print(f"\n[2] ENTRADAS EM referencias.bib: {len(bib_entries)}")

print(f"\n[3] CHAVES CITADAS QUE NÃO EXISTEM NO .BIB")
missing = [k for k in all_citations if k not in bib_entries]
if missing:
    for k in missing:
        print(f"  FALTA: {k}")
else:
    print("  Nenhuma")

print(f"\n[4] ENTRADAS NO .BIB QUE NÃO SÃO CITADAS")
uncited = [k for k in bib_entries if k not in all_citations]
if uncited:
    for k in uncited:
        print(f"  NÃO CITADO: {k}")
else:
    print("  Nenhuma")

# Parse bib for DOI/URL
entries = re.split(r'@\w+\{', bib_content)[1:]
ref_data = {}
for entry in entries:
    key_match = re.match(r'(\w+),', entry)
    if not key_match:
        continue
    key = key_match.group(1)
    doi_match = re.search(r'doi\s*=\s*\{([^}]+)\}', entry)
    url_match = re.search(r'url\s*=\s*\{([^}]+)\}', entry)
    doi = doi_match.group(1) if doi_match else None
    url = url_match.group(1) if url_match else None
    ref_data[key] = {"doi": doi, "url": url}

print(f"\n[5] REFERÊNCIAS CITADAS SEM DOI NEM URL")
no_link = []
for key in sorted(all_citations):
    if key in ref_data:
        d = ref_data[key]["doi"]
        u = ref_data[key]["url"]
        if not d and not u:
            no_link.append(key)
            print(f"  SEM LINK: {key}")
if not no_link:
    print("  Todas têm DOI ou URL")

print(f"\n[6] VERIFICAÇÃO DE DOIs VIA CROSSREF")
doi_ok = 0
doi_fail = 0
doi_fail_list = []
for key in sorted(all_citations):
    if key in ref_data and ref_data[key]["doi"]:
        doi = ref_data[key]["doi"]
        try:
            r = requests.get(f"https://api.crossref.org/works/{doi}", timeout=10)
            if r.status_code == 200:
                doi_ok += 1
                print(f"  OK   {key:25s} {doi}")
            else:
                doi_fail += 1
                doi_fail_list.append(key)
                print(f"  FAIL {key:25s} {doi} -> HTTP {r.status_code}")
        except Exception as e:
            doi_fail += 1
            doi_fail_list.append(key)
            print(f"  ERR  {key:25s} {doi} -> {e}")
    elif key in ref_data and not ref_data[key]["doi"]:
        print(f"  N/A  {key:25s} (livro/relatório, sem DOI)")

print(f"\n{'=' * 70}")
print(f"RESUMO DA VARREDURA")
print(f"{'=' * 70}")
print(f"  Citações no texto:          {len(all_citations)}")
print(f"  Entradas no .bib:           {len(bib_entries)}")
print(f"  Faltando no .bib:           {len(missing)}")
print(f"  Não citadas no texto:       {len(uncited)}")
print(f"  Sem DOI nem URL:            {len(no_link)}")
print(f"  DOIs verificados OK:        {doi_ok}")
print(f"  DOIs com falha:             {doi_fail}")
if doi_fail_list:
    print(f"  Falhas: {', '.join(doi_fail_list)}")
print(f"{'=' * 70}")
