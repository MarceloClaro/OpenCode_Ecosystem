import requests, json
requests.packages.urllib3.disable_warnings()
s = requests.Session()
s.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
r = s.get('https://portal.stf.jus.br/jurisprudencia/listarJurisprudencia.asp?s1=HC&pagina=1&tamanho=3', timeout=20, verify=False)
print('Status:', r.status_code, 'Size:', len(r.text))
from bs4 import BeautifulSoup
soup = BeautifulSoup(r.text, 'lxml')
forms = soup.find_all('form')
print('Forms:', len(forms))
for i,f in enumerate(forms):
    a = f.get('action','')
    m = f.get('method','')
    print(f'Form {i}: action=[{a}] method=[{m}]')
    for inp in f.find_all(['input','select','textarea']):
        n = inp.get('name','')
        if n:
            v = inp.get('value','')
            t = inp.get('type','')
            print(f'  {inp.name}: name=[{n}] value=[{str(v)[:80]}] type=[{t}]')
iframes = soup.find_all('iframe')
print('Iframes:', len(iframes))
for i, ifr in enumerate(iframes):
    print(f'Iframe {i}: src=[{ifr.get("src","")}]')
content = soup.find('main') or soup.find(id='conteudo') or soup.find(id='main')
if content:
    print(f'Content size: {len(str(content))}')
    print(content.text[:800])
else:
    body = soup.find('body')
    if body:
        text = body.get_text(strip=True)
        print(f'Body text length: {len(text)}')
        print(text[:800])
