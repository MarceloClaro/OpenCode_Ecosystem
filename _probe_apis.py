import requests, sys, json
requests.packages.urllib3.disable_warnings()

print('=== STF APIs ===')
stf_urls = [
    ('GET', 'https://portal.stf.jus.br/jurisprudencia/listarJurisprudencia.asp?s1=HC&pagina=1&tamanho=2'),
    ('GET', 'https://portal.stf.jus.br/jurisprudencia/pesquisarInteiroTeor.asp'),
    ('GET', 'https://jurisprudencia.stf.jus.br/consulta/pesquisar?q=habeas&pag=1'),
    ('GET', 'https://jurisprudencia.stf.jus.br/'),
]
for method, url in stf_urls:
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'}, timeout=15, verify=False)
        print(f'URL: {url}')
        print(f'Status: {r.status_code}')
        print(f'Content-Type: {r.headers.get("content-type","?")}')
        if r.status_code == 200:
            ct = r.headers.get('content-type','')
            if 'json' in ct:
                print(json.dumps(r.json(), indent=2, ensure_ascii=False)[:1500])
            else:
                print(r.text[:1000])
        else:
            print(r.text[:500])
        print()
    except Exception as e:
        print(f'URL: {url}')
        print(f'ERRO: {e}')
        print()

print('=== STJ APIs ===')
stj_urls = [
    ('GET', 'https://scon.stj.jus.br/SCON/pesquisar?b=ACOR&p=habeas&l=2&O=JT'),
    ('GET', 'https://scon.stj.jus.br/SCON/'),
]
for method, url in stj_urls:
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15, verify=False)
        print(f'URL: {url}')
        print(f'Status: {r.status_code}')
        print(f'Content-Type: {r.headers.get("content-type","?")}')
        print(r.text[:1000])
        print()
    except Exception as e:
        print(f'URL: {url}')
        print(f'ERRO: {e}')
        print()

print('=== DataJud CNJ ===')
cnj_urls = [
    ('GET', 'https://datajud.cnj.jus.br/api/v1/'),
    ('GET', 'https://datajud.cnj.jus.br/swagger-ui.html'),
]
for method, url in cnj_urls:
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'}, timeout=15, verify=False)
        print(f'URL: {url}')
        print(f'Status: {r.status_code}')
        print(f'Content-Type: {r.headers.get("content-type","?")}')
        if r.status_code == 200:
            print(r.text[:1000])
        else:
            print(r.text[:500])
        print()
    except Exception as e:
        print(f'URL: {url}')
        print(f'ERRO: {e}')
        print()
