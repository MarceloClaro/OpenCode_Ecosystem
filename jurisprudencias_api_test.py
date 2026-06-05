import requests, json, re, sys
try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

requests.packages.urllib3.disable_warnings()
s = requests.Session()
s.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8'
})

errors = 0

def test(name, method, url, **kwargs):
    global errors
    try:
        fn = getattr(s, method.lower())
        r = fn(url, timeout=kwargs.pop('timeout', 20), verify=False, **kwargs)
        ok = r.status_code in (200, 202)
        print(f'  [{r.status_code}] {name}')
        if ok and BS4_AVAILABLE:
            soup = BeautifulSoup(r.text, 'lxml')
            text = soup.get_text(separator=' ', strip=True)[:300]
            if text:
                print(f'    Content: {text}')
        elif ok:
            print(f'    Size: {len(r.text)} bytes')
        else:
            print(f'    Response: {r.text[:200]}')
        if not ok:
            errors += 1
    except Exception as e:
        print(f'  [ERRO] {name}: {e}')
        errors += 1

print('=== STF Jurisprudencia Portal ===')
test('Landing page', 'get', 'https://portal.stf.jus.br/jurisprudencia/pesquisarInteiroTeor.asp')
test('POST search', 'post', 'https://portal.stf.jus.br/jurisprudencia/pesquisarInteiroTeor.asp',
     data={'pesquisaJurisprudencia': 'habeas corpus', 'tipo-pesquisa': 'pesquisaJurisprudencia'})

print('\n=== STF Legacy Portal ===')
test('Landing', 'get', 'https://jurisprudencia.stf.jus.br/')
test('Consulta', 'get', 'https://jurisprudencia.stf.jus.br/consulta/pesquisar?q=habeas&pag=1')

print('\n=== STJ Portal ===')
test('SCON', 'get', 'https://scon.stj.jus.br/SCON/')

print('\n=== TRF1 ===')
test('TRF1', 'get', 'https://www.trf1.jus.br/jurisprudencia/')

print(f'\n--- Resumo: {errors} erro(s) ---')
