import requests, json, re
requests.packages.urllib3.disable_warnings()
s = requests.Session()
s.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8'
})

# Step 1: Get the search landing page to get cookies
r1 = s.get('https://portal.stf.jus.br/jurisprudencia/pesquisarInteiroTeor.asp', timeout=20, verify=False)
print('Step 1 - Landing page:', r1.status_code, len(r1.text))
print('Cookies:', dict(s.cookies))

# Step 2: Try POST search
data = {
    'pesquisaJurisprudencia': 'habeas corpus',
    'tipo-pesquisa': 'pesquisaJurisprudencia'
}
r2 = s.post('https://portal.stf.jus.br/jurisprudencia/pesquisarInteiroTeor.asp', data=data, timeout=20, verify=False)
print('\nStep 2 - POST search:', r2.status_code, len(r2.text))

# Step 3: Try the internal API endpoint
from bs4 import BeautifulSoup
soup = BeautifulSoup(r1.text, 'lxml')
scripts = soup.find_all('script')
for sc in scripts:
    if sc.string:
        # Look for API URLs
        urls = re.findall(r'https?://[^\s"\'<>]+', sc.string)
        for u in urls:
            if 'jurisprudencia' in u.lower() or 'api' in u.lower():
                print(f'  Found URL in JS: {u}')

# Also look for fetch/XHR calls in scripts
for sc in scripts:
    if sc.string and ('fetch' in sc.string.lower() or 'xmlhttprequest' in sc.string.lower() or 'ajax' in sc.string.lower() or 'jurisprudencia' in sc.string.lower()):
        print(f'\nScript with API calls (len={len(sc.string)}):')
        print(sc.string[:2000])
        break
