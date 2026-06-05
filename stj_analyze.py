import requests, json
requests.packages.urllib3.disable_warnings()
s = requests.Session()
s.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
r = s.get('https://processo.stj.jus.br/processo/pesquisa?tipo=acordaos&termo=habeas+corpus', timeout=20, verify=False)
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
tables = soup.find_all('table')
print('Tables:', len(tables))
for i, t in enumerate(tables[:5]):
    rows = t.find_all('tr')
    print(f'Table {i}: class={t.get("class","")} id={t.get("id","")} rows={len(rows)}')
links = soup.find_all('a', href=lambda x: x and 'acordao' in x.lower())
print('Acordao links:', len(links))
for l in links[:5]:
    print(f'  [{l.get("href","")}] text=[{l.text.strip()[:100]}]')
# Find the search results section
divs = soup.find_all('div', id=lambda x: x and ('result' in x.lower() or 'list' in x.lower()))
print('Result divs:', len(divs))
for d in divs:
    print(f'  id={d.get("id","")} class={d.get("class","")} size={len(str(d))}')
