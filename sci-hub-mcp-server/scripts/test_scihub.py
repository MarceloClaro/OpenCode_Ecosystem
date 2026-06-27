import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from sci_hub_search import search_paper_by_doi

tests = [
    ("Schmidt 1983", "10.1111/j.1365-2923.1983.tb01086.x"),
    ("Nature 2010", "10.1038/nature09492"),
    ("Creswell 2018", "10.4324/9781315274218"),
]

for name, doi in tests:
    print(f"=== {name} ({doi}) ===")
    r = search_paper_by_doi(doi)
    print("Status:", r["status"])
    print("Titulo:", r.get("title", "")[:80])
    print("Fonte:", r.get("source", ""))
    if r.get("pdf_url"):
        print("PDF:", r["pdf_url"][:80])
    print()
