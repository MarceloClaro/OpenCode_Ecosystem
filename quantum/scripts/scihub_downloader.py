# -*- coding: utf-8 -*-

"""
SciHub Downloader — busca e download de artigos cientificos
com bypass de Cloudflare via cloudscraper (sci-hub).
"""

import re, argparse, hashlib, logging, os
import requests, urllib3
from bs4 import BeautifulSoup
from retrying import retry

try:
    import cloudscraper
    HAS_CLOUDSCRAPER = True
except ImportError:
    HAS_CLOUDSCRAPER = False

logging.basicConfig()
logger = logging.getLogger('SciHub')
logger.setLevel(logging.WARNING)
urllib3.disable_warnings()

SCHOLARS_BASE_URL = 'https://scholar.google.com/scholar'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36'}

FALLBACK_URLS = ['https://sci-hub.se', 'https://sci-hub.st', 'https://sci-hub.ru', 'https://sci-hub.ee']

class SciHub(object):
    def __init__(self):
        self.sess = requests.Session()
        self.sess.headers = HEADERS
        if HAS_CLOUDSCRAPER:
            self.scraper = cloudscraper.create_scraper()
        else:
            self.scraper = self.sess
        self.available_base_url_list = self._get_available_scihub_urls()
        if not self.available_base_url_list:
            self.available_base_url_list = FALLBACK_URLS
        self.base_url = self.available_base_url_list[0]
        if not self.base_url.endswith('/'):
            self.base_url += '/'

    def _get_available_scihub_urls(self):
        urls = []
        try:
            res = requests.get('https://sci-hub.now.sh/', timeout=5)
            s = BeautifulSoup(res.content, 'html.parser')
            for a in s.find_all('a', href=True):
                href = a['href']
                if 'sci-hub.' in href and href.startswith('http'):
                    urls.append(href.rstrip('/'))
        except:
            pass
        return urls

    def _change_base_url(self):
        if len(self.available_base_url_list) <= 1:
            self.available_base_url_list = FALLBACK_URLS
            logger.info("Reset to fallback URLs")
        else:
            del self.available_base_url_list[0]
        self.base_url = self.available_base_url_list[0]
        if not self.base_url.endswith('/'):
            self.base_url += '/'
        logger.info(f"Switching to {self.base_url}")

    def set_proxy(self, proxy):
        if proxy:
            self.sess.proxies = {"http": proxy, "https": proxy}
            if HAS_CLOUDSCRAPER:
                self.scraper.proxies = {"http": proxy, "https": proxy}

    def search(self, query, limit=10):
        start = 0
        results = {'papers': []}
        while True:
            try:
                res = self.sess.get(SCHOLARS_BASE_URL, params={'q': query, 'start': start}, timeout=15)
            except requests.exceptions.RequestException as e:
                results['err'] = 'Connection error: ' + str(e)
                return results
            s = BeautifulSoup(res.content, 'html.parser')
            papers = s.find_all('div', class_="gs_r")
            if not papers:
                if 'CAPTCHA' in str(res.content):
                    results['err'] = 'Captcha blocked search'
                return results
            for paper in papers:
                if not paper.find('table'):
                    source = None
                    pdf = paper.find('div', class_='gs_ggs gs_fl')
                    link = paper.find('h3', class_='gs_rt')
                    if pdf:
                        source = pdf.find('a')['href']
                    elif link.find('a'):
                        source = link.find('a')['href']
                    else:
                        continue
                    results['papers'].append({'name': link.text.strip(), 'url': source})
                    if len(results['papers']) >= limit:
                        return results
            start += 10

    @retry(wait_random_min=100, wait_random_max=1000, stop_max_attempt_number=10)
    def download(self, identifier, destination='', path=None):
        data = self.fetch(identifier)
        if 'err' not in data:
            filepath = os.path.join(destination, path if path else data['name'])
            self._save(data['pdf'], filepath)
            data['saved_to'] = filepath
        return data

    def fetch(self, identifier):
        max_attempts = len(self.available_base_url_list) + len(FALLBACK_URLS)
        for attempt in range(max_attempts):
            try:
                url = self._get_direct_url(identifier)
                if not url:
                    self._change_base_url()
                    continue
                res = self.scraper.get(url, verify=False, timeout=30)
                ct = res.headers.get('Content-Type', '')
                if 'application/pdf' in ct:
                    return {'pdf': res.content, 'url': url, 'name': self._generate_name(res)}
                elif 'text/html' in ct and 'cloudflare' in res.text.lower():
                    self._change_base_url()
                    continue
                else:
                    self._change_base_url()
                    continue
            except requests.exceptions.ConnectionError:
                self._change_base_url()
            except requests.exceptions.RequestException:
                self._change_base_url()
            except Exception:
                self._change_base_url()
        return {'err': f'Failed after {max_attempts} attempts: all Sci-Hub domains blocked or unavailable'}

    def _get_direct_url(self, identifier):
        id_type = self._classify(identifier)
        if id_type == 'url-direct':
            return identifier
        try:
            res = self.scraper.get(self.base_url + identifier, verify=False, timeout=15)
            s = BeautifulSoup(res.content, 'html.parser')
            for tag in ['iframe', 'embed']:
                el = s.find(tag)
                if el and el.get('src'):
                    src = el['src']
                    if src.startswith('//'): src = 'https:' + src
                    if src.startswith('http'): return src
            for a in s.find_all('a'):
                href = a.get('href', '')
                if '.pdf' in href: return href
        except:
            pass

    def _classify(self, identifier):
        if identifier.startswith('http'):
            return 'url-direct' if identifier.endswith('pdf') else 'url-non-direct'
        return 'pmid' if identifier.isdigit() else 'doi'

    def _save(self, data, path):
        os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
        with open(path, 'wb') as f:
            f.write(data)

    def _generate_name(self, res):
        name = re.sub(r'#view=(.+)', '', res.url.split('/')[-1])
        pdf_hash = hashlib.md5(res.content).hexdigest()[:8]
        return f'{pdf_hash}-{name[-30:]}'

def main():
    sh = SciHub()
    parser = argparse.ArgumentParser(description='SciHub Downloader')
    parser.add_argument('-d', '--download', metavar='(DOI|PMID|URL)', type=str)
    parser.add_argument('-s', '--search', metavar='query', type=str)
    parser.add_argument('-sd', '--search_download', metavar='query', type=str)
    parser.add_argument('-l', '--limit', metavar='N', type=int, default=5)
    parser.add_argument('-o', '--output', metavar='path', type=str, default='')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()
    if args.verbose: logger.setLevel(logging.DEBUG)
    if args.download:
        r = sh.download(args.download, args.output)
        if 'err' in r: print(f"ERR: {r['err']}")
        else: print(f"OK: {r.get('saved_to', r['url'])}")
    elif args.search:
        r = sh.search(args.search, args.limit)
        if 'err' in r: print(f"ERR: {r['err']}")
        else:
            for i, p in enumerate(r['papers']):
                print(f"{i+1}. {p['name'][:120]}\n   {p['url']}\n")
    elif args.search_download:
        r = sh.search(args.search_download, args.limit)
        if 'err' in r: print(f"ERR: {r['err']}")
        else:
            for paper in r['papers']:
                print(f"Downloading: {paper['name'][:80]}")
                dr = sh.download(paper['url'], args.output)
                if 'err' in dr: print(f"  ERR: {dr['err']}")
                else: print(f"  OK: {dr.get('saved_to', dr['url'])}")

if __name__ == '__main__':
    main()

if __name__ == "__main__":
    main()
