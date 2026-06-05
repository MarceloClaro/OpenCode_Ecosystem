"""
Academic Paper Search — arXiv + Semantic Scholar
100% funcional, gratuito, sem API key.
"""
import requests, json, time, argparse, urllib.parse, os
import xml.etree.ElementTree as ET

ARXIV_API = "http://export.arxiv.org/api/query"
SEMANTIC_API = "https://api.semanticscholar.org/graph/v1/paper/search"
NS = {'atom': 'http://www.w3.org/2005/Atom', 'arxiv': 'http://arxiv.org/schemas/atom'}

def get_arxiv_pdf(url):
    """Convert arXiv abstract URL to PDF URL."""
    return url.replace('/abs/', '/pdf/') + '.pdf' if '/abs/' in url else url

def download_arxiv_pdf(url, destination='.'):
    """Download PDF directly from arXiv (no Sci-Hub needed)."""
    pdf_url = get_arxiv_pdf(url)
    r = requests.get(pdf_url, timeout=60)
    if r.status_code == 200 and 'application/pdf' in r.headers.get('Content-Type', ''):
        filename = pdf_url.split('/')[-1]
        filepath = os.path.join(destination, filename)
        with open(filepath, 'wb') as f:
            f.write(r.content)
        return {'saved': filepath, 'size': len(r.content)}
    return {'err': f'PDF download failed: {r.status_code}'}

def search_arxiv(query, max_results=10):
    """Search arXiv and return structured paper list."""
    params = {'search_query': f'all:{query}', 'start': 0, 'max_results': max_results, 'sortBy': 'relevance'}
    r = requests.get(ARXIV_API, params=params, timeout=30)
    if r.status_code != 200:
        return {'err': f'arXiv returned {r.status_code}'}
    root = ET.fromstring(r.text)
    papers = []
    for entry in root.findall('atom:entry', NS):
        papers.append({
            'title': entry.find('atom:title', NS).text.strip().replace('\n', ' '),
            'url': entry.find('atom:id', NS).text,
            'authors': [a.find('atom:name', NS).text for a in entry.findall('atom:author', NS)],
            'summary': (entry.find('atom:summary', NS).text or '')[:300],
            'published': entry.find('atom:published', NS).text[:10],
            'source': 'arxiv'
        })
    return {'papers': papers[:max_results], 'total': len(papers)}

def search_semantic(query, max_results=10):
    """Search Semantic Scholar (may be rate-limited)."""
    params = {'query': query, 'limit': max_results, 'fields': 'title,year,authors,url,externalIds,abstract'}
    r = requests.get(SEMANTIC_API, params=params, timeout=20)
    if r.status_code != 200:
        return {'err': f'SemanticScholar: {r.status_code}', 'papers': []}
    papers = []
    for p in r.json().get('data', []):
        authors = [a.get('name', '') for a in (p.get('authors') or [])]
        papers.append({
            'title': p.get('title', ''),
            'url': p.get('url', ''),
            'authors': authors,
            'year': p.get('year'),
            'summary': (p.get('abstract') or '')[:300],
            'doi': (p.get('externalIds') or {}).get('DOI', ''),
            'source': 'semantic_scholar'
        })
    return {'papers': papers}

def search_all(query, max_results=10):
    """Search both arXiv and Semantic Scholar."""
    results = {'papers': [], 'sources': []}
    arxiv = search_arxiv(query, max_results)
    if 'err' not in arxiv:
        results['papers'].extend(arxiv['papers'])
        results['sources'].append('arxiv')
    else:
        results['sources'].append(f"arxiv_failed:{arxiv['err']}")
    sem = search_semantic(query, max_results)
    if 'err' not in sem:
        results['papers'].extend(sem['papers'])
        results['sources'].append('semantic_scholar')
    else:
        results['sources'].append(f"semantic_failed:{sem['err']}")
    return results

def main():
    parser = argparse.ArgumentParser(description='Academic Paper Search')
    parser.add_argument('query', nargs='?', default='', help='Search query')
    parser.add_argument('-n', '--num', type=int, default=10, help='Max results')
    parser.add_argument('-s', '--source', default='all', choices=['all','arxiv','semantic','as'], help='Source')
    parser.add_argument('-j', '--json', action='store_true', help='JSON output')
    parser.add_argument('--doi', type=str, help='Search by DOI')
    parser.add_argument('--download', type=int, default=0, help='Download N first PDFs from arXiv')
    args = parser.parse_args()
    if args.doi:
        query = args.doi
        args.source = 'arxiv'
    elif args.query:
        query = args.query
    else:
        print("Usage: academic-search.py 'quantum machine learning' -n 5")
        return
    if args.source == 'arxiv':
        results = search_arxiv(query, args.num)
    elif args.source in ('semantic', 'as'):
        results = search_semantic(query, args.num)
    else:
        results = search_all(query, args.num)
    if args.json:
        if args.download > 0:
            for p in papers[:args.download]:
                dl = download_arxiv_pdf(p['url'])
                p['download'] = dl
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        papers = results.get('papers', [])
        if args.download > 0:
            print(f"Downloading {min(args.download, len(papers))} papers from arXiv...")
            for p in papers[:args.download]:
                dl = download_arxiv_pdf(p['url'])
                if 'saved' in dl:
                    print(f"  OK: {dl['saved']} ({dl['size']} bytes)")
                else:
                    print(f"  FAIL: {dl.get('err')}")
            print()
        print(f"Found {len(papers)} papers from {results.get('sources',[])}")
        print()
        for i, p in enumerate(papers):
            print(f"{i+1}. {p['title'][:120]}")
            print(f"   {p['url']}")
            print(f"   Authors: {', '.join(p.get('authors', [])[:4])}")
            if p.get('doi'): print(f"   DOI: {p['doi']}")
            if p.get('summary'): print(f"   {p['summary'][:150]}...")
            print()

if __name__ == '__main__':
    main()

if __name__ == "__main__":
    main()
