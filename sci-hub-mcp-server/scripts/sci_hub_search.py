import sys
import os
# Adicionar o diretório atual ao path para importar scihub.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
 from scihub import SciHub
except ImportError:
 # Fallback se scihub.py não estiver no path
 class SciHub:
 def fetch(self, id): return {"success": False, "error": "SciHub module not found"}
 def download(self, url, path): return False

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
 """ SciHub """
 sh = SciHub()
 sh.timeout = 30 # 30 
 return sh

def search_paper_by_doi(doi):
 """ DOI Sci-Hub """
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
 'year': result.get('year', '')
 }
 except Exception as e:
 print(f": {str(e)}")
 return {
 'doi': doi,
 'status': 'not_found'
 }

def search_paper_by_title(title):
 """ Sci-Hub """
 # SciHub search ， DOI 
 # CrossRef DOI
 try:
 url = f"https://api.crossref.org/works?query.title={title}&rows=1"
 response = requests.get(url)
 if response.status_code == 200:
 data = response.json()
 if data['message']['items']:
 doi = data['message']['items'][0]['DOI']
 return search_paper_by_doi(doi)
 except Exception as e:
 print(f"CrossRef : {str(e)}")
 
 return {
 'title': title,
 'status': 'not_found'
 }

def search_papers_by_keyword(keyword, num_results=10):
 """，"""
 # CrossRef API 
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
 print(f": {str(e)}")
 
 return papers

def download_paper(pdf_url, output_path):
 """ PDF"""
 sh = SciHub()
 try:
 sh.download(pdf_url, output_path)
 return True
 except Exception as e:
 print(f": {str(e)}")
 return False


if __name__ == "__main__":
 print("Sci-Hub \n")

 # 1. DOI 
 print("1. DOI ")
 test_doi = "10.1002/jcad.12075" # 
 result = search_paper_by_doi(test_doi)
 
 if result['status'] == 'success':
 print(f": {result['title']}")
 print(f": {result['author']}")
 print(f": {result['year']}")
 print(f"PDF URL: {result['pdf_url']}")
 
 # 
 output_file = f"paper_{test_doi.replace('/', '_')}.pdf"
 if download_paper(result['pdf_url'], output_file):
 print(f": {output_file}")
 else:
 print("")
 else:
 print(f" DOI {test_doi} ")

 # 2. 
 print("\n2. ")
 test_title = "Choosing Assessment Instruments for Posttraumatic Stress Disorder Screening and Outcome Research"
 result = search_paper_by_title(test_title)
 
 if result['status'] == 'success':
 print(f"DOI: {result['doi']}")
 print(f": {result['author']}")
 print(f": {result['year']}")
 print(f"PDF URL: {result['pdf_url']}")
 else:
 print(f" '{test_title}' ")

 # 3. 
 print("\n3. ")
 test_keyword = "artificial intelligence medicine 2023"
 papers = search_papers_by_keyword(test_keyword, num_results=3)
 
 for i, paper in enumerate(papers, 1):
 print(f"\n {i}:")
 print(f": {paper['title']}")
 print(f"DOI: {paper['doi']}")
 print(f": {paper['author']}")
 print(f": {paper['year']}")
 if paper.get('pdf_url'):
 print(f"PDF URL: {paper['pdf_url']}")

