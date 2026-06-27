import requests
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

MIRRORS = [
    "https://sci-hub.se/",
    "https://sci-hub.st/",
    "https://sci-hub.ru/",
    "https://sci-hub.ren/",
    "https://sci-hub.wf/",
    "https://sci-hub.mksa.top/",
    "https://sci-hub.shop/",
    "https://sci-hub.gupiaoq.com/",
    "https://e-hentai.org/",
    "https://sci-hub.ee/",
    "https://sci-hub.hkvisa.net/",
    "https://s.v2.dood.am/",
    "https://tessy.fr/",
    "https://scipedia.com/",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

TEST_DOI = "10.1038/nature09492"

print("=== Scanner de Espelhos Sci-Hub ===")
print(f"DOI de teste: {TEST_DOI}\n")

working = []
for mirror in MIRRORS:
    try:
        url = mirror + TEST_DOI
        r = requests.get(url, headers=HEADERS, verify=False, timeout=10, allow_redirects=True)
        has_pdf = "iframe" in r.text.lower() or "embed" in r.text.lower()
        status = "FUNCIONA (PDF)" if has_pdf and r.status_code == 200 else f"HTTP {r.status_code}"
        print(f"  {mirror:45s} -> {status}")
        if r.status_code == 200:
            working.append(mirror)
    except Exception as e:
        print(f"  {mirror:45s} -> FALHOU ({type(e).__name__})")

print(f"\n=== {len(working)} espelhos funcionais ===")
for m in working:
    print(f"  {m}")
