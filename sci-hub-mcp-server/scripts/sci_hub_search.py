import sys
import os
# Adicionar o diretorio atual ao path para importar scihub.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from scihub import SciHub
except ImportError:
    # Fallback se scihub.py nao estiver no path
    class SciHub:
        def fetch(self, id):
            return {"success": False, "error": "SciHub module not found"}
        def download(self, url, path):
            return False

import re
import urllib3
import requests

# HTTPS
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class SciHubWrapper:
    """Wrapper para a classe SciHub para compatibilidade com o orquestrador"""
    def __init__(self):
        self.sh = SciHub()

    def fetch_article(self, identifier):
        return search_paper_by_doi(identifier)


def create_scihub_instance():
    """Criar instancia do SciHub"""
    sh = SciHub()
    sh.timeout = 30
    return sh


def search_paper_by_doi(doi):
    """Buscar paper por DOI - CrossRef primario, Sci-Hub fallback"""
    # 1. Tentar CrossRef primeiro (sempre funciona)
    try:
        url = f"https://api.crossref.org/works/{doi}"
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            data = response.json()["message"]
            title = data.get("title", [""])[0] if data.get("title") else ""
            authors = ", ".join(
                f"{a.get('given', '')} {a.get('family', '')}"
                for a in data.get("author", [])
            )
            year = ""
            if data.get("published-print"):
                parts = data["published-print"].get("date-parts", [[]])[0]
                if parts:
                    year = str(parts[0])
            elif data.get("created"):
                year = str(data["created"].get("date-parts", [[]])[0][0])

            return {
                "doi": doi,
                "title": title,
                "author": authors,
                "year": year,
                "status": "success",
                "source": "crossref"
            }
    except Exception as e:
        print(f"CrossRef fallback: {str(e)}")

    # 2. Tentar Sci-Hub
    sh = create_scihub_instance()
    try:
        result = sh.fetch(doi)
        if result.get('success') is False:
            return {'doi': doi, 'status': 'not_found', 'error': result.get('error')}

        return {
            'doi': doi,
            'pdf_url': result.get('url', ''),
            'status': 'success',
            'title': result.get('title', ''),
            'author': result.get('author', ''),
            'year': result.get('year', ''),
            'source': 'scihub'
        }
    except Exception as e:
        return {
            'doi': doi,
            'status': 'not_found',
            'error': f"CrossRef e Sci-Hub falharam: {str(e)}"
        }


def search_paper_by_title(title):
    """Buscar paper no Sci-Hub por titulo"""
    # SciHub search nao tem busca por titulo, usar CrossRef para obter DOI
    try:
        url = f"https://api.crossref.org/works?query.title={title}&rows=1"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data['message']['items']:
                doi = data['message']['items'][0]['DOI']
                return search_paper_by_doi(doi)
    except Exception as e:
        print(f"CrossRef error: {str(e)}")

    return {
        'title': title,
        'status': 'not_found'
    }


def search_papers_by_keyword(keyword, num_results=10):
    """Buscar papers no Sci-Hub por palavra-chave"""
    # Usar CrossRef API para obter DOIs, depois buscar no Sci-Hub
    papers = []
    try:
        url = f"https://api.crossref.org/works?query={keyword}&rows={num_results}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            for item in data['message']['items']:
                doi = item.get('DOI')
                if doi:
                    result = search_paper_by_doi(doi)
                    if result['status'] == 'success':
                        papers.append(result)
    except Exception as e:
        print(f"Erro busca keyword: {str(e)}")

    return papers


def download_paper(pdf_url, output_path):
    """Baixar PDF do Sci-Hub"""
    sh = SciHub()
    try:
        sh.download(pdf_url, output_path)
        return True
    except Exception as e:
        print(f"Erro download: {str(e)}")
        return False


if __name__ == "__main__":
    print("Sci-Hub Teste\n")

    # 1. Busca por DOI
    print("1. Busca por DOI")
    test_doi = "10.1002/jcad.12075"
    result = search_paper_by_doi(test_doi)

    if result['status'] == 'success':
        print(f"Titulo: {result['title']}")
        print(f"Autor: {result['author']}")
        print(f"Ano: {result['year']}")
        print(f"PDF URL: {result['pdf_url']}")

        # Download
        output_file = f"paper_{test_doi.replace('/', '_')}.pdf"
        if download_paper(result['pdf_url'], output_file):
            print(f"Download OK: {output_file}")
        else:
            print("Falha no download")
    else:
        print(f"DOI {test_doi} nao encontrado")

    # 2. Busca por titulo
    print("\n2. Busca por titulo")
    test_title = "Choosing Assessment Instruments for Posttraumatic Stress Disorder Screening and Outcome Research"
    result = search_paper_by_title(test_title)

    if result['status'] == 'success':
        print(f"DOI: {result['doi']}")
        print(f"Autor: {result['author']}")
        print(f"Ano: {result['year']}")
        print(f"PDF URL: {result['pdf_url']}")
    else:
        print(f"Titulo '{test_title}' nao encontrado")

    # 3. Busca por keyword
    print("\n3. Busca por keyword")
    test_keyword = "artificial intelligence medicine 2023"
    papers = search_papers_by_keyword(test_keyword, num_results=3)

    for i, paper in enumerate(papers, 1):
        print(f"\nPaper {i}:")
        print(f"Titulo: {paper['title']}")
        print(f"DOI: {paper['doi']}")
        print(f"Autor: {paper['author']}")
        print(f"Ano: {paper['year']}")
        if paper.get('pdf_url'):
            print(f"PDF URL: {paper['pdf_url']}")
