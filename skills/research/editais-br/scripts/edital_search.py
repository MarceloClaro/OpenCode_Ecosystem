#!/usr/bin/env python3
# edital_search.py v7.1 — Ciclo 7: cache versionado + normalizacao score + fallback robusto

import argparse, asyncio, hashlib, json, os, re, sqlite3, subprocess, sys, time, urllib.parse
from dataclasses import dataclass, field, asdict
from pathlib import Path

CACHE_DIR = Path.home() / '.config/opencode/cache'
CACHE_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = CACHE_DIR / 'editais.db'
CACHE_TTL = 3600
CACHE_VERSION = 'v7.1'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0'

def init_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute('CREATE TABLE IF NOT EXISTS buscas (id INTEGER PRIMARY KEY AUTOINCREMENT, query TEXT, tipo TEXT, perfil TEXT, resultado TEXT, score_medio REAL, criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
    conn.execute('CREATE TABLE IF NOT EXISTS feedback (id INTEGER PRIMARY KEY AUTOINCREMENT, busca_id INTEGER, url TEXT, score REAL, gostou INTEGER, criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
    conn.execute('CREATE TABLE IF NOT EXISTS pesos (dimensao TEXT PRIMARY KEY, peso REAL DEFAULT 1.0, acertos INTEGER DEFAULT 0, erros INTEGER DEFAULT 0)')
    conn.commit()
    return conn

def _cache_key(query, tipo, perfil):
    return hashlib.md5(f'{CACHE_VERSION}|{query}|{tipo}|{perfil}'.encode()).hexdigest()

def _cache_get(key):
    p = CACHE_DIR / f'{key}.json'
    if p.exists():
        d = json.loads(p.read_text(encoding='utf-8'))
        if time.time() - d['ts'] < CACHE_TTL: return d['results']
    return None

def _cache_set(key, results):
    (CACHE_DIR / f'{key}.json').write_text(json.dumps({'ts': time.time(), 'results': results}, ensure_ascii=False), encoding='utf-8')

@dataclass
class Edital:
    titulo: str; url: str; portal: str = ''; score: float = 50.0
    fonte: str = 'web'; dimensoes: dict = field(default_factory=dict)

CURATED_JSON = Path(__file__).resolve().parent.parent / 'curated' / 'CURATED_EDITAIS_FULL.json'

def _carregar_curados():
    """Load curated editais from the unified JSON file (65 editais)."""
    try:
        with open(CURATED_JSON, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return [{
            'titulo': e['nome'],
            'url': _get_url(e['agencia']),
            'portal': e['agencia'].lower().replace('/', ''),
            'tipo': e['categoria'],
            'valor': e.get('valor_anual_estimado'),
            'score_pesquisa': e.get('scores', {}).get('pesquisa', 50),
        } for e in data.get('editais', [])]
    except Exception as ex:
        print(f'[editais-br] ERRO ao carregar curadoria: {ex}', file=sys.stderr)
        return []

def _get_url(agencia):
    m = {
        'CNPq': 'https://www.gov.br/cnpq', 'CAPES': 'https://www.gov.br/capes',
        'FINEP': 'https://finep.gov.br/chamadas-publicas',
        'FAPESP': 'https://fapesp.br', 'FAPERJ': 'https://www.faperj.br',
        'FAPEMIG': 'https://fapemig.br', 'FAPESB': 'https://fapesb.ba.gov.br',
        'FUNCAP': 'https://funcap.ce.gov.br', 'FACEPE': 'https://facepe.pe.gov.br',
        'FAPEMA': 'https://fapema.ma.gov.br', 'FAPESQ': 'https://fapesq.pb.gov.br',
        'FAPEPI': 'https://fapepi.pi.gov.br', 'FAPITEC': 'https://fapitec.se.gov.br',
        'FAPEAM': 'https://fapeam.am.gov.br', 'FAPAC': 'https://fapac.ac.gov.br',
        'FAPT': 'https://fapt.to.gov.br', 'FAPERO': 'https://fapero.ro.gov.br',
        'FAPDF': 'https://fapdf.df.gov.br', 'FUNDECT': 'https://fundect.ms.gov.br',
        'FAPEMAT': 'https://fapemat.mt.gov.br', 'FAPES': 'https://fapes.es.gov.br',
        'FAPERGS': 'https://fapergs.rs.gov.br', 'FAPESC': 'https://fapesc.sc.gov.br',
        'MCTI': 'https://www.gov.br/mcti', 'MCTI/SEBRAE': 'https://inovativabrasil.com.br',
        'BNDES': 'https://www.bndes.gov.br', 'EMBRAPII': 'https://embrapii.org.br',
        'SEBRAE': 'https://sebrae.com.br', 'Minc': 'https://rouanet.cultura.gov.br',
        'ANCINE': 'https://fsa.ancine.gov.br', 'Prosas': 'https://prosas.com.br',
        'FBB': 'https://www.fbb.org.br', 'Embrapa': 'https://www.embrapa.br',
        'Fiocruz': 'https://portal.fiocruz.br', 'Petrobras': 'https://petrobras.com.br',
        'Vale': 'https://vale.com', 'MS/Saúde': 'https://www.gov.br/saude',
    }
    return m.get(agencia, 'https://www.gov.br')

EDITAIS_CURADOS = _carregar_curados()

def _buscar_ddg(query, max_results=10):
    # Try DuckDuckGo via curl; if blocked, fall back to curated list
    try:
        q = urllib.parse.urlencode({'q': query})
        r = subprocess.run(['curl.exe', '-s', '-L', '-H', f'User-Agent: {USER_AGENT}', '-d', q, 'https://html.duckduckgo.com/html/'],
                           capture_output=True, text=True, errors='ignore', timeout=20)
        if r.returncode == 0 and 'challenge' not in r.stdout.lower()[:500] and len(r.stdout) > 15000:
            urls = re.findall(r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>([^<]+)</a>', r.stdout)
            ads = {'duckduckgo.com/y.js', 'bing.com/aclick', 'googleadservices'}
            seen, res = set(), []
            for u, t in urls:
                if any(a in u for a in ads): continue
                if u not in seen:
                    seen.add(u)
                    res.append({'titulo': t.strip(), 'url': u, 'portal': '', 'fonte': 'web'})
                if len(res) >= max_results: break
            return res
    except: pass
    # Fallback: curated + portal direct
    return _buscar_curados(query, max_results)

def _buscar_curados(query, max_results=10):
    q = query.lower()
    palavras = set(q.split())
    scored = []
    for e in EDITAIS_CURADOS:
        titulo_lower = e['titulo'].lower()
        match = sum(1 for p in palavras if p in titulo_lower or p in e['tipo'] or p in e['portal'])
        if match > 0:
            scored.append((match, e))
    scored.sort(key=lambda x: -x[0])
    return [{'titulo':e['titulo']+' (curadoria)','url':e['url'],'portal':e['portal'],'fonte':'curadoria'}
            for _,e in scored[:max_results]] or            [{'titulo':e['titulo']+' (curadoria)','url':e['url'],'portal':e['portal'],'fonte':'curadoria'}
            for e in EDITAIS_CURADOS[:max_results]]

def _buscar_portais(query, tipo, max_results=10):
    res = []
    try:
        import httpx
        c = httpx.Client(timeout=10, follow_redirects=True, headers={'User-Agent': USER_AGENT})
        r = c.get('https://finep.gov.br/chamadas-publicas')
        if r.status_code == 200:
            links = re.findall(r'<a[^>]+href="([^"]+chamada[^"]*)"[^>]*>([^<]+)</a>', r.text, re.I)
            seen = set()
            for u, t in links:
                u2 = u if u.startswith('http') else 'https://finep.gov.br' + u
                if u2 not in seen:
                    seen.add(u2)
                    res.append({'titulo': t.strip(), 'url': u2, 'portal': 'finep', 'fonte': 'portal'})
        c.close()
    except: pass
    return res[:max_results]

def _buscar_bndes(max_results=5):
    """Busca linhas de fomento do BNDES via portal de dados abertos."""
    res = []
    try:
        import urllib.request, json
        # CKAN API: package_search for financing datasets
        req = urllib.request.Request(
            'https://dadosabertos.bndes.gov.br/api/3/action/package_show?id=aprovacoes',
            headers={'User-Agent': USER_AGENT, 'Accept': 'application/json'}
        )
        r = urllib.request.urlopen(req, timeout=15)
        data = json.loads(r.read().decode())
        resources = data.get('result', {}).get('resources', [])
        for res_meta in resources[:max_results]:
            nome = res_meta.get('name', '').lower()
            if any(k in nome for k in ['financiamento','operacao','contrato','produto']):
                res.append({
                    'titulo': f"BNDES {res_meta.get('name', 'Aprovacao')}",
                    'url': res_meta.get('url', 'https://dadosabertos.bndes.gov.br'),
                    'portal': 'bndes',
                    'fonte': 'bndes_api'
                })
        if not res:
            # Fallback: datasets conhecidos
            urls_bndes = [
                ('BNDES Financiamento - Operacoes', 'https://dadosabertos.bndes.gov.br/dataset/aprovacoes'),
                ('BNDES Financiamento - Consultas', 'https://dadosabertos.bndes.gov.br/dataset/consultas'),
                ('BNDES Linhas de Financiamento', 'https://www.bndes.gov.br/wps/portal/site/home/financiamento'),
                ('BNDES Garagem - Startup', 'https://www.bndes.gov.br/wps/portal/site/home/onde-atuamos/inovacao/bndes-garagem'),
            ]
            for titulo, url in urls_bndes[:max_results]:
                res.append({'titulo': titulo, 'url': url, 'portal': 'bndes', 'fonte': 'bndes_api'})
    except Exception as e:
        print(f'[bndes] erro: {e}')
    return res

TERMOS_POR_TIPO = {
    'pesquisa': ['edital pesquisa','fomento pesquisa','chamada universal','INCT','jovem pesquisador'],
    'mestrado': ['bolsa mestrado','mestrado CAPES','Demanda Social','processo seletivo mestrado','pos-graduacao stricto'],
    'doutorado': ['bolsa doutorado','doutorado CAPES','PNPD','PROEX','pos-doutorado','bolsa produtividade'],
    'startup': ['edital startup','capital semente startup','aceleradora edital','InovAtiva Brasil','BNDES startup','FAPESP PIPE'],
    'inovacao': ['subvencao economica FINEP','Inovacred','RHAE CNPq','TECNOVA','embrapii','Lei do Bem'],
    'cultura': ['Lei Rouanet','edital cultura','salic','fomento cultura','premio cultural'],
    'social': ['edital OSC','termo fomento MROSC','impacto social','terceiro setor edital'],
}

async def buscar(query, tipo='', perfil='pesquisador', max_results=10, usar_cache=True):
    key = _cache_key(query, tipo, perfil)
    if usar_cache:
        cached = _cache_get(key)
        if cached: return cached
    # Build enriched query with type-specific terms
    extras = TERMOS_POR_TIPO.get(tipo, [])
    query_full = f'edital fomento {query} {" ".join(extras[:3])} 2026'
    loop = asyncio.get_event_loop()
    ddg = await loop.run_in_executor(None, _buscar_ddg, query_full, max_results)
    portais = await loop.run_in_executor(None, _buscar_portais, query_full, tipo, max_results)
    bndes = await loop.run_in_executor(None, _buscar_bndes, max_results // 2)
    seen, merged = set(), []
    for item in ddg + portais + bndes:
        u = item['url'].split('&')[0]
        if u not in seen:
            seen.add(u)
            e = Edital(**item)
            e.dimensoes = classificar(e.titulo, e.url)
            e.score = calcular_score(e.dimensoes, tipo, perfil)
            merged.append(e)
        if len(merged) >= max_results: break
    merged.sort(key=lambda e: e.score, reverse=True)
    resultado = [asdict(e) for e in merged]
    _cache_set(key, resultado)
    return resultado

# Match helper: word-boundary for short terms (<4 chars), substring for longer
_M = lambda ks, t: any((re.search(r'\b' + re.escape(k) + r'\b', t) if len(k) <= 3 else k in t) for k in ks)

AREAS = {
    'ia': ['inteligencia artificial','machine learning','deep learning','llm','gpt','neural','ia'],
    'saude': ['saude','medico','farmaceutico','clinico','doenca','hospital','sus','epidemio'],
    'biotec': ['biotecnologia','genetica','genomica','bioinfo','biologia molecular'],
    'energia': ['energia','fotovoltaico','eolica','renovavel','hidrogenio','solar','bioenergia'],
    'agro': ['agricultura','agropecuaria','agro','pecuaria','agronegocio'],
    'educacao': ['educacao','ensino','pedagogico','escolar','formacao docente','eja'],
    'social': ['social','direitos humanos','cidadania','inclusao','igualdade','quilombola','indigena'],
    'cultura': ['cultura','arte','musica','cinema','patrimonio','rouanet'],
    'tech': ['software','ti','computacao','digital','tecnologia','iot','blockchain','startup','inovacao','aceleradora','pipe','subvencao'],
    'engenharia': ['engenharia','materiais','automacao','robotica','manufatura'],
    'ambiente': ['ambiental','sustentabilidade','clima','florestal','biodiversidade','agua'],
    'ciencia_pura': ['pesquisa','cientifico','ciencia','academico','epistemologia','universal','produtividade','pos-graduacao','stricto','mestrado','doutorado','doutor','mestrando','doutorando'],
}
PERFIS = {
    'programa_pos': ['mestrado','doutor','pos-graduacao','stricto','mestrando','doutorando','pnpd','proex'],
    'microempresa': ['startup','mei','microempreendedor','pequena empresa'],
    'ict': ['ict','instituto pesquisa','laboratorio','centro pesquisa'],
    'osc': ['osc','ongs','terceiro setor','sociedade civil','associacao'],
}
MECANISMOS = {
    'bolsa': ['bolsa','taxa bancada','auxilio'],
    'subvencao': ['subvencao','subvencao economica'],
    'premio': ['premio','premiacao','concurso'],
    'credito': ['credito','financiamento','emprestimo'],
    'incentivo_fiscal': ['incentivo fiscal','lei do bem','renuncia fiscal'],
}

def classificar(titulo, url):
    t = f'{titulo} {url}'.lower()
    d = {}
    d['area'] = [n for n, ks in AREAS.items() if _M(ks, t)] or ['nao_classificado']
    for perfil_n, termos in PERFIS.items():
        if _M(termos, t): d['perfil'] = perfil_n; break
    else: d['perfil'] = 'universidade'
    for mec, termos in MECANISMOS.items():
        if _M(termos, t): d['mecanismo'] = mec; break
    else: d['mecanismo'] = 'nao_reembolsavel'
    d['abrangencia'] = 'internacional' if _M(['internacional','global'], t) else ('regional' if _M(['regional','nordeste','norte','sul','sudeste'], t) else 'nacional')
    d['status'] = 'encerrado' if _M(['encerrado','resultado final','homologado'], t) else 'aberto'
    for p, v in [(r'(\d+)\s*(?:milhao|M|mi)', 'acima_1M'), (r'(\d+)\s*(?:mil|k)', 'ate_200k')]:
        if re.search(p, t): d['faixa_valor'] = v; break
    else: d['faixa_valor'] = 'nao_informado'
    d['trl'] = 'trl_1_5' if _M(['trl_1','trl_2','trl_3','pesquisa basica'], t) else ('trl_6_9' if _M(['trl_6','trl_7','prototipo'], t) else 'nao_se_aplica')
    d['contrapartida'] = 'sem' if 'sem contrapartida' in t else ('exige' if 'contrapartida' in t else 'nao_informado')
    d['competitividade'] = 'alta' if _M(['alta concorrencia','limitado','poucas vagas'], t) else 'media'
    d['prazo'] = 'nao_informado'
    return d

def calcular_score(dims, tipo, perfil, query_match_ratio=0.0):
    s = 0.0
    # 1. Query relevance (0-30): how well search terms match
    s += query_match_ratio * 30
    # 2. Tipo alignment (0-30): query tipo matches classified area
    ta = {'pesquisa':['ciencia_pura'],'mestrado':['educacao','ciencia_pura'],'doutorado':['educacao','ciencia_pura'],'startup':['tech'],'inovacao':['tech'],'cultura':['cultura'],'social':['social']}
    ea = ta.get(tipo, [])
    if any(a in dims.get('area', []) for a in ea): s += 30
    # 3. Perfil alignment (0-20): user perfil matches edital perfil
    pp = {'mestrando':'programa_pos','doutorando':'programa_pos','pesquisador':'universidade','professor':'universidade','empreendedor':'microempresa','startup':'microempresa'}
    if pp.get(perfil, '') and dims.get('perfil') == pp[perfil]: s += 20
    # 4. Mechanism bonus (0-10): funding type adequacy
    s += {'bolsa':8,'subvencao':10,'premio':3,'credito':5,'nao_reembolsavel':8}.get(dims.get('mecanismo',''), 0)
    # 5. Completeness bonus (0-10): dimensions successfully classified
    known = sum(1 for v in dims.values() if not (isinstance(v, str) and v in ('nao_informado','nao_classificado','nao_se_aplica')) and not (isinstance(v, list) and v == ['nao_classificado']))
    s += min(known * 2, 12)
    # Penalties
    if dims.get('status') == 'encerrado': s -= 20
    if dims.get('contrapartida') == 'exige': s -= 10
    if dims.get('competitividade') == 'alta': s -= 5
    return max(0, min(100, s))

def iniciar_servidor(porta=8080):
    from http.server import HTTPServer, BaseHTTPRequestHandler
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/':
                self._respond(200, b'editais-br v7.0 OK')
            elif self.path.startswith('/buscar'):
                q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
                termo = q.get('q', [''])[0]
                if not termo: self._respond(400, b'{"erro":"parametro q obrigatorio"}'); return
                res = asyncio.run(buscar(termo, q.get('tipo',[''])[0], q.get('perfil',['pesquisador'])[0], 10))
                self._respond(200, json.dumps(res, ensure_ascii=False).encode())
            else: self._respond(404, b'{"erro":"not found"}')
        def _respond(self, code, body):
            self.send_response(code); self.send_header('Content-Type','application/json; charset=utf-8')
            self.end_headers(); self.wfile.write(body)
    HTTPServer(('', porta), Handler).serve_forever()

def main():
    conn = init_db()
    p = argparse.ArgumentParser(description='editais-br v7.0')
    p.add_argument('termo', nargs='?', help='Termo de busca')
    p.add_argument('--tipo', choices=['pesquisa','mestrado','doutorado','startup','inovacao','cultura','social'])
    p.add_argument('--perfil', choices=['mestrando','doutorando','pesquisador','professor','empreendedor','startup'], default='')
    p.add_argument('--max', type=int, default=10)
    p.add_argument('--json', action='store_true')
    p.add_argument('--servidor', action='store_true', help='Inicia servidor HTTP')
    p.add_argument('--porta', type=int, default=8080)
    p.add_argument('--no-cache', action='store_true')
    p.add_argument('--curadoria-only', action='store_true', help='Usar apenas curadoria (sem busca web)')
    p.add_argument('--feedback', nargs=3, metavar=('BUSCA_ID', 'URL', 'GOSTOU'),
                   help='Registrar feedback: busca_id url 1|0')
    p.add_argument('--treinar', action='store_true', help='Treinar pesos com base no feedback acumulado')
    args = p.parse_args()

    if args.feedback:
        busca_id, url_fb, gostou = args.feedback
        conn = init_db()
        cur = conn.execute('INSERT INTO feedback (busca_id, url, gostou) VALUES (?, ?, ?)',
                          (int(busca_id), url_fb, int(gostou)))
        conn.commit()
        print(f'[editais-br] Feedback registrado (id={cur.lastrowid})')
        conn.close()
        return

    if args.treinar:
        conn = init_db()
        # Pega feedback recente e atualiza pesos das dimensoes
        # Busca feedback com ou sem resultado vinculado
        fb = conn.execute('''
            SELECT f.url, f.gostou, b.resultado
            FROM feedback f
            LEFT JOIN buscas b ON f.busca_id = b.id
            WHERE f.gostou IS NOT NULL
        ''').fetchall()
        if not fb:
            print('[editais-br] Nenhum feedback para treinar')
            return
        acertos_total = 0
        for row in fb:
            url_fb, gostou, resultado = row
            try:
                resultados = json.loads(resultado)
                for r in resultados:
                    if r.get('url') == url_fb:
                        for dim in r.get('dimensoes', {}):
                            exists = conn.execute('SELECT peso, acertos, erros FROM pesos WHERE dimensao = ?', (dim,)).fetchone()
                            if exists:
                                novo_acertos = exists[1] + (1 if gostou else 0)
                                novo_erros = exists[2] + (0 if gostou else 1)
                                novo_peso = min(2.0, max(0.5, exists[0] + (0.1 if gostou else -0.1)))
                                conn.execute('UPDATE pesos SET peso=?, acertos=?, erros=? WHERE dimensao=?',
                                           (novo_peso, novo_acertos, novo_erros, dim))
                            else:
                                conn.execute('INSERT INTO pesos (dimensao, peso, acertos, erros) VALUES (?, ?, ?, ?)',
                                           (dim, 1.2 if gostou else 0.8, 1 if gostou else 0, 0 if gostou else 1))
                            acertos_total += gostou
            except: pass
        conn.commit()
        print(f'[editais-br] Pesos treinados com {len(fb)} feedbacks ({acertos_total} acertos)')
        conn.close()
        return

    if args.servidor:
        print(f'[editais-br] Servidor em http://localhost:{args.porta}')
        return iniciar_servidor(args.porta)
    if not args.termo: p.print_help(); return
    t0 = time.time()
    if args.curadoria_only:
        raw = _buscar_curados(args.termo, args.max)
        res = []
        palavras_query = set(args.termo.lower().split())
        for e in raw:
            ed = Edital(**e)
            ed.dimensoes = classificar(ed.titulo, ed.url)
            titulo_lower = ed.titulo.lower()
            matches = sum(1 for p in palavras_query if p in titulo_lower)
            qmr = matches / max(len(palavras_query), 1)
            perfil_efetivo = args.perfil or {'mestrado':'mestrando','doutorado':'doutorando','startup':'empreendedor','inovacao':'empreendedor'}.get(args.tipo, 'pesquisador')
            ed.score = calcular_score(ed.dimensoes, args.tipo or '', perfil_efetivo, qmr)
            res.append({'titulo':ed.titulo,'url':ed.url,'portal':ed.portal,'fonte':ed.fonte,'score':ed.score,'dimensoes':ed.dimensoes})
        res.sort(key=lambda x: -x.get('score', 50.0))
    else:
        perfil_efetivo = args.perfil or {'mestrado':'mestrando','doutorado':'doutorando','startup':'empreendedor','inovacao':'empreendedor'}.get(args.tipo, 'pesquisador')
        res = asyncio.run(buscar(args.termo, args.tipo or '', perfil_efetivo, args.max, not args.no_cache))
    # Normalize: ensure every result has 'score' (cache backwards compat)
    for e in res:
        e.setdefault('score', 50.0)
    res.sort(key=lambda x: -x['score'])
    print(f'[editais-br] {len(res)} resultados em {time.time()-t0:.1f}s')
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        for i, e in enumerate(res, 1):
            areas = ', '.join(e['dimensoes'].get('area', []))
            print(f'\n{i}. {e["titulo"][:75]}')
            print(f'   Score: {e["score"]:.0f}/100 | {e["fonte"]} | {areas}')
            print(f'   {e["url"][:90]}')

def buscar_sync(query: str, tipo: str = '', perfil: str = 'pesquisador', max_results: int = 10, usar_cache: bool = True) -> list[dict]:
    """Wrapper sincrono para busca de editais.

    Uso como tool nativa (sem HTTP/CLI):
        from edital_search import buscar_sync
        resultados = buscar_sync('ia saude', tipo='pesquisa', perfil='pesquisador')
    """
    import asyncio
    return asyncio.run(buscar(query, tipo, perfil, max_results, usar_cache))


if __name__ == '__main__':
    main()

if __name__ == "__main__":
    main()
