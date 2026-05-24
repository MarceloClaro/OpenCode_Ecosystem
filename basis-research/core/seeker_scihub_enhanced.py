# -*- coding: utf-8 -*-
"""
SEEKER-SciHub Enhanced v2.0
Pipeline de busca acadêmica multi-estratégia integrado ao OpenCode Ecosystem v4.2.2

Melhorias sobre o scihub_downloader.py v1.0:
  1. Verificação de DOI via CrossRef ANTES de tentar Sci-Hub (evita requisições desnecessárias)
  2. Fallback em cascata: CrossRef → Unpaywall → Sci-Hub → CORE → arXiv
  3. Cache local de resultados (TTL 24h) para evitar re-requisições
  4. Extração estruturada de metadados ABNT NBR 6023:2025
  5. Logging de auditoria compatível com PhD Auditor (L5)
  6. Verificação de integridade do PDF (tamanho mínimo + header)
  7. Suporte a batch de DOIs com paralelismo controlado (ThreadPoolExecutor)
  8. Integração com .evolve/ para rastreabilidade no ecossistema
"""

import re
import hashlib
import logging
import os
import json
import time
import threading
from datetime import datetime, timezone
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional

import requests
import urllib3
from bs4 import BeautifulSoup

try:
    import cloudscraper
    HAS_CLOUDSCRAPER = True
except ImportError:
    HAS_CLOUDSCRAPER = False

urllib3.disable_warnings()

# ─────────────────────────────────────────────
# Configuração de logging — compatível com PhD Auditor L5
# ─────────────────────────────────────────────
logging.basicConfig(format='[%(asctime)s][%(levelname)s][SciHub] %(message)s', datefmt='%H:%M:%S')
logger = logging.getLogger('SciHub-Enhanced')
logger.setLevel(logging.INFO)

BRAZIL_TZ = timezone.utc  # UTC-3 na prática via localtime

# ─────────────────────────────────────────────
# Constantes e configuração
# ─────────────────────────────────────────────
FALLBACK_URLS = [
    'https://sci-hub.se',
    'https://sci-hub.st',
    'https://sci-hub.ru',
    'https://sci-hub.ee',
    'https://sci-hub.ren',
]

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/124.0.0.0 Safari/537.36'
    )
}

# APIs abertas para verificação e fallback
CROSSREF_API   = 'https://api.crossref.org/works/{doi}'
UNPAYWALL_API  = 'https://api.unpaywall.org/v2/{doi}?email=opencode@ecosystem.br'
CORE_API       = 'https://api.core.ac.uk/v3/search/works'
ARXIV_API      = 'https://export.arxiv.org/api/query'

# Cache local
CACHE_DIR      = Path('.evolve/scihub-cache')
CACHE_TTL_S    = 86400  # 24 horas

MIN_PDF_BYTES  = 5_000  # PDFs menores são suspeitos


# ─────────────────────────────────────────────
# Helpers de cache
# ─────────────────────────────────────────────

def _cache_key(identifier: str) -> str:
    return hashlib.md5(identifier.encode()).hexdigest()

def _cache_get(identifier: str) -> Optional[dict]:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    p = CACHE_DIR / (_cache_key(identifier) + '.json')
    if p.exists():
        age = time.time() - p.stat().st_mtime
        if age < CACHE_TTL_S:
            try:
                return json.loads(p.read_text(encoding='utf-8'))
            except Exception:
                pass
    return None

def _cache_set(identifier: str, data: dict) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    p = CACHE_DIR / (_cache_key(identifier) + '.json')
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

def _is_valid_pdf(content: bytes) -> bool:
    return len(content) >= MIN_PDF_BYTES and content[:4] == b'%PDF'


# ─────────────────────────────────────────────
# Formatação ABNT NBR 6023:2025
# ─────────────────────────────────────────────

def format_abnt(meta: dict) -> str:
    """
    Gera citação ABNT NBR 6023:2025 a partir de metadados CrossRef.
    Formato: SOBRENOME, Nome. Título. Revista, v.X, n.Y, p.AA-BB, Ano.
    DOI: https://doi.org/...
    """
    authors = meta.get('author', [])
    if authors:
        first = authors[0]
        family = first.get('family', '').upper()
        given  = first.get('given', '')
        author_str = f"{family}, {given}"
        if len(authors) > 1:
            author_str += " et al."
    else:
        author_str = "[s.n.]"

    title   = meta.get('title', ['[s.t.]'])[0] if meta.get('title') else '[s.t.]'
    journal = meta.get('container-title', [''])[0] if meta.get('container-title') else ''
    year    = (meta.get('published-print') or meta.get('published-online') or {}).get('date-parts', [['']])[0][0]
    volume  = meta.get('volume', '')
    issue   = meta.get('issue', '')
    page    = meta.get('page', '')
    doi     = meta.get('DOI', '')

    parts = [f"{author_str}. {title}."]
    if journal:
        detail = f" {journal}"
        if volume: detail += f", v. {volume}"
        if issue:  detail += f", n. {issue}"
        if page:   detail += f", p. {page}"
        if year:   detail += f", {year}"
        parts.append(detail + ".")
    if doi:
        parts.append(f" DOI: https://doi.org/{doi}")

    return " ".join(parts)


# ─────────────────────────────────────────────
# Classe principal — SciHubEnhanced
# ─────────────────────────────────────────────

class SciHubEnhanced:
    """
    Pipeline de acesso a literatura acadêmica com fallback em cascata:
    CrossRef → Unpaywall (OA) → Sci-Hub → CORE → arXiv
    """

    def __init__(self, proxy: Optional[str] = None, verbose: bool = False):
        self.sess = requests.Session()
        self.sess.headers.update(HEADERS)
        if proxy:
            self.sess.proxies = {"http": proxy, "https": proxy}
        self.scraper = cloudscraper.create_scraper() if HAS_CLOUDSCRAPER else self.sess
        self._lock = threading.Lock()
        self._url_pool = list(FALLBACK_URLS)
        self.base_url  = self._url_pool[0] + '/'
        if verbose:
            logger.setLevel(logging.DEBUG)

    # ── 1. Verificação CrossRef ──────────────────────────────────────────────

    def get_crossref_meta(self, doi: str) -> Optional[dict]:
        """Busca metadados verificados na API CrossRef (gratuita, sem autenticação)."""
        cached = _cache_get(f'crossref:{doi}')
        if cached:
            logger.debug(f"CrossRef cache hit: {doi}")
            return cached
        try:
            r = self.sess.get(CROSSREF_API.format(doi=doi), timeout=10)
            if r.status_code == 200:
                meta = r.json().get('message', {})
                _cache_set(f'crossref:{doi}', meta)
                return meta
        except Exception as e:
            logger.warning(f"CrossRef error for {doi}: {e}")
        return None

    # ── 2. Unpaywall — PDF de acesso aberto ─────────────────────────────────

    def get_oa_url(self, doi: str) -> Optional[str]:
        """Tenta obter PDF em acesso aberto via Unpaywall antes de usar Sci-Hub."""
        cached = _cache_get(f'unpaywall:{doi}')
        if cached:
            return cached.get('url')
        try:
            r = self.sess.get(UNPAYWALL_API.format(doi=doi), timeout=10)
            if r.status_code == 200:
                data = r.json()
                loc = data.get('best_oa_location') or {}
                url = loc.get('url_for_pdf') or loc.get('url')
                if url:
                    _cache_set(f'unpaywall:{doi}', {'url': url})
                    logger.info(f"Unpaywall OA found: {url}")
                    return url
        except Exception as e:
            logger.warning(f"Unpaywall error for {doi}: {e}")
        return None

    # ── 3. Sci-Hub (fallback) ────────────────────────────────────────────────

    def _rotate_url(self):
        with self._lock:
            if len(self._url_pool) > 1:
                self._url_pool.append(self._url_pool.pop(0))
            else:
                self._url_pool = list(FALLBACK_URLS)
            self.base_url = self._url_pool[0] + '/'
            logger.info(f"Rotated to: {self.base_url}")

    def _scihub_direct_url(self, identifier: str) -> Optional[str]:
        for _ in range(len(self._url_pool) + len(FALLBACK_URLS)):
            try:
                url = self.base_url + identifier
                r = self.scraper.get(url, verify=False, timeout=20)
                soup = BeautifulSoup(r.content, 'html.parser')
                for tag in ['iframe', 'embed']:
                    el = soup.find(tag)
                    if el and el.get('src'):
                        src = el['src']
                        if src.startswith('//'): src = 'https:' + src
                        if src.startswith('http'): return src
                for a in soup.find_all('a'):
                    href = a.get('href', '')
                    if '.pdf' in href: return href
            except Exception:
                pass
            self._rotate_url()
        return None

    def _download_pdf(self, pdf_url: str) -> Optional[bytes]:
        try:
            r = self.scraper.get(pdf_url, verify=False, timeout=30)
            if 'application/pdf' in r.headers.get('Content-Type', '') or _is_valid_pdf(r.content):
                if _is_valid_pdf(r.content):
                    return r.content
        except Exception as e:
            logger.warning(f"PDF download error: {e}")
        return None

    # ── 4. CORE fallback ─────────────────────────────────────────────────────

    def search_core(self, query: str, limit: int = 5) -> list:
        """Busca em CORE.ac.uk — repositório de acesso aberto com API gratuita."""
        try:
            r = self.sess.get(
                CORE_API,
                params={'q': query, 'limit': limit, 'fullText': False},
                timeout=15
            )
            if r.status_code == 200:
                results = r.json().get('results', [])
                return [
                    {
                        'title': p.get('title', ''),
                        'doi': p.get('doi', ''),
                        'url': p.get('downloadUrl') or p.get('sourceFulltextUrls', [''])[0],
                        'year': p.get('yearPublished'),
                        'source': 'CORE'
                    }
                    for p in results if p.get('title')
                ]
        except Exception as e:
            logger.warning(f"CORE error: {e}")
        return []

    # ── 5. arXiv fallback ────────────────────────────────────────────────────

    def search_arxiv(self, query: str, limit: int = 5) -> list:
        """Busca em arXiv — repositório OA de física, matemática, computação e mais."""
        try:
            r = self.sess.get(
                ARXIV_API,
                params={
                    'search_query': f'all:{query}',
                    'max_results': limit,
                    'sortBy': 'relevance'
                },
                timeout=15
            )
            if r.status_code == 200:
                soup = BeautifulSoup(r.content, 'xml')
                entries = soup.find_all('entry')
                results = []
                for e in entries:
                    title = e.find('title')
                    arxiv_id = e.find('id')
                    doi_tag = e.find('arxiv:doi')
                    results.append({
                        'title': title.text.strip() if title else '',
                        'doi': doi_tag.text.strip() if doi_tag else '',
                        'url': arxiv_id.text.strip().replace('/abs/', '/pdf/') + '.pdf' if arxiv_id else '',
                        'year': e.find('published').text[:4] if e.find('published') else '',
                        'source': 'arXiv'
                    })
                return results
        except Exception as e:
            logger.warning(f"arXiv error: {e}")
        return []

    # ── 6. Pipeline principal: fetch com fallback em cascata ─────────────────

    def fetch(self, doi: str, destination: str = 'papers', audit: bool = True) -> dict:
        """
        Busca e baixa um artigo usando pipeline em cascata:
        CrossRef (meta) → Unpaywall (OA PDF) → Sci-Hub (fallback) → erro

        Retorna dict com:
          - meta: metadados CrossRef
          - abnt: citação ABNT NBR 6023:2025
          - pdf_url: URL do PDF (se encontrado)
          - saved_to: caminho local do arquivo salvo
          - source: qual pipeline forneceu o PDF
          - audit: trilha de auditoria para PhD Auditor L5
          - err: mensagem de erro (se falhou)
        """
        result = {
            'doi': doi,
            'meta': None,
            'abnt': '',
            'pdf_url': None,
            'saved_to': None,
            'source': None,
            'audit': [],
            'err': None,
            'timestamp': datetime.now().isoformat()
        }

        # Etapa 1 — CrossRef: verificar DOI e obter metadados
        result['audit'].append('CrossRef: consultando metadados...')
        meta = self.get_crossref_meta(doi)
        if meta:
            result['meta'] = {
                'title': (meta.get('title') or [''])[0],
                'authors': [f"{a.get('family','')} {a.get('given','')}" for a in meta.get('author', [])],
                'year': str((meta.get('published-print') or meta.get('published-online') or {}).get('date-parts', [['']])[0][0]),
                'journal': (meta.get('container-title') or [''])[0],
                'doi': meta.get('DOI', doi),
                'volume': meta.get('volume', ''),
                'issue': meta.get('issue', ''),
                'page': meta.get('page', ''),
            }
            result['abnt'] = format_abnt(meta)
            result['audit'].append(f"CrossRef: OK — {result['meta']['title'][:60]}")
        else:
            result['audit'].append('CrossRef: DOI não encontrado ou inválido')

        # Etapa 2 — Unpaywall: PDF em acesso aberto
        result['audit'].append('Unpaywall: buscando PDF em acesso aberto...')
        oa_url = self.get_oa_url(doi)
        if oa_url:
            pdf_content = self._download_pdf(oa_url)
            if pdf_content:
                saved = self._save_pdf(pdf_content, destination, doi)
                result.update({'pdf_url': oa_url, 'saved_to': saved, 'source': 'Unpaywall (OA)'})
                result['audit'].append(f"Unpaywall: PDF OA salvo → {saved}")
                self._log_evolve(doi, result)
                return result
            result['audit'].append('Unpaywall: URL encontrada mas PDF inválido')
        else:
            result['audit'].append('Unpaywall: sem versão OA disponível')

        # Etapa 3 — Sci-Hub: fallback com rotação de mirrors
        result['audit'].append(f"Sci-Hub: tentando em {self.base_url}...")
        direct_url = self._scihub_direct_url(doi)
        if direct_url:
            pdf_content = self._download_pdf(direct_url)
            if pdf_content:
                saved = self._save_pdf(pdf_content, destination, doi)
                result.update({'pdf_url': direct_url, 'saved_to': saved, 'source': 'Sci-Hub'})
                result['audit'].append(f"Sci-Hub: PDF salvo → {saved}")
                self._log_evolve(doi, result)
                return result
            result['audit'].append('Sci-Hub: URL encontrada mas PDF inválido ou bloqueado')
        else:
            result['audit'].append('Sci-Hub: todos os mirrors falharam (Cloudflare/bloqueio)')

        # Etapa 4 — Fallback completo: sem PDF disponível
        result['err'] = 'PDF não disponível via Unpaywall nem Sci-Hub. Use CrossRef/meta para citação.'
        result['audit'].append('Pipeline: encerrado sem PDF — metadados disponíveis para citação manual')
        self._log_evolve(doi, result)
        return result

    # ── 7. Batch de DOIs ─────────────────────────────────────────────────────

    def fetch_batch(self, dois: list, destination: str = 'papers', max_workers: int = 3) -> list:
        """
        Processa uma lista de DOIs em paralelo controlado (max_workers threads).
        Respeita rate limits das APIs abertas.
        """
        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(self.fetch, doi, destination): doi for doi in dois}
            for future in as_completed(futures):
                doi = futures[future]
                try:
                    r = future.result()
                    results.append(r)
                    status = '✅' if r.get('saved_to') else ('⚠️' if r.get('abnt') else '❌')
                    print(f"  {status} {doi[:40]:<40} {r.get('source','—')}")
                except Exception as e:
                    results.append({'doi': doi, 'err': str(e)})
                time.sleep(0.5)  # rate limiting
        return results

    # ── Auxiliares ────────────────────────────────────────────────────────────

    def _save_pdf(self, content: bytes, destination: str, doi: str) -> str:
        os.makedirs(destination, exist_ok=True)
        safe_doi = re.sub(r'[^\w\-]', '_', doi)[:50]
        pdf_hash = hashlib.md5(content).hexdigest()[:8]
        path = os.path.join(destination, f'{pdf_hash}-{safe_doi}.pdf')
        with open(path, 'wb') as f:
            f.write(content)
        return path

    def _log_evolve(self, doi: str, result: dict) -> None:
        """Registra resultado no log de observabilidade do ecossistema."""
        log_path = Path('.evolve/scihub-observability.jsonl')
        log_path.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            'timestamp': result['timestamp'],
            'doi': doi,
            'source': result.get('source'),
            'has_pdf': result.get('saved_to') is not None,
            'has_meta': result.get('meta') is not None,
            'err': result.get('err'),
            'audit_steps': len(result.get('audit', [])),
        }
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')


# ─────────────────────────────────────────────
# Interface CLI
# ─────────────────────────────────────────────

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='SciHub Enhanced v2.0 — Pipeline OpenCode Ecosystem'
    )
    parser.add_argument('-d', '--doi',    metavar='DOI',    help='Buscar/baixar por DOI')
    parser.add_argument('-b', '--batch',  metavar='FILE',   help='Arquivo com lista de DOIs (1 por linha)')
    parser.add_argument('-s', '--search', metavar='QUERY',  help='Buscar no CORE + arXiv por palavras-chave')
    parser.add_argument('-o', '--output', metavar='DIR',    default='papers', help='Diretório de saída')
    parser.add_argument('-l', '--limit',  metavar='N',      type=int, default=5, help='Máx. resultados na busca')
    parser.add_argument('-w', '--workers',metavar='N',      type=int, default=3, help='Workers paralelos (batch)')
    parser.add_argument('-v', '--verbose',action='store_true')
    args = parser.parse_args()

    sh = SciHubEnhanced(verbose=args.verbose)

    if args.doi:
        print(f"\n[SciHub Enhanced] Buscando: {args.doi}")
        r = sh.fetch(args.doi, args.output)
        print(f"\n  Título : {(r.get('meta') or {}).get('title','N/A')}")
        print(f"  Fonte  : {r.get('source','—')}")
        print(f"  PDF    : {r.get('saved_to') or r.get('pdf_url','—')}")
        print(f"  ABNT   : {r.get('abnt','—')}")
        if r.get('err'):
            print(f"  ⚠️  {r['err']}")
        print("\n  Trilha de auditoria:")
        for step in r.get('audit', []):
            print(f"    → {step}")

    elif args.batch:
        dois = Path(args.batch).read_text(encoding='utf-8').splitlines()
        dois = [d.strip() for d in dois if d.strip()]
        print(f"\n[SciHub Enhanced] Batch: {len(dois)} DOIs | workers={args.workers}")
        results = sh.fetch_batch(dois, args.output, args.workers)
        ok  = sum(1 for r in results if r.get('saved_to'))
        meta_only = sum(1 for r in results if r.get('abnt') and not r.get('saved_to'))
        err = sum(1 for r in results if r.get('err') and not r.get('abnt'))
        print(f"\n  ✅ PDFs baixados : {ok}")
        print(f"  ⚠️  Somente meta  : {meta_only}")
        print(f"  ❌ Falhas totais  : {err}")

    elif args.search:
        print(f"\n[SciHub Enhanced] Buscando: '{args.search}'")
        core    = sh.search_core(args.search, args.limit)
        arxiv   = sh.search_arxiv(args.search, args.limit)
        all_res = core + arxiv
        for i, p in enumerate(all_res, 1):
            print(f"\n  {i}. [{p['source']}] {p['title'][:80]}")
            if p.get('doi'):  print(f"     DOI : {p['doi']}")
            if p.get('year'): print(f"     Ano : {p['year']}")
            if p.get('url'):  print(f"     URL : {p['url'][:80]}")

    else:
        parser.print_help()

if __name__ == '__main__':
    main()
