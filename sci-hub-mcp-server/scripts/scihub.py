
import requests
import re
from bs4 import BeautifulSoup

class SciHub:
    def __init__(self):
        self.base_url = "https://sci-hub.se/"
        self.timeout = 30

    def fetch(self, identifier):
        """Fetch article from Sci-Hub by DOI, PMID or URL."""
        try:
            url = self.base_url + identifier
            response = requests.get(url, verify=False, timeout=self.timeout)
            if response.status_code != 200:
                return {"success": False, "error": "Artigo não encontrado."}
            
            soup = BeautifulSoup(response.content, 'html.parser')
            iframe = soup.find('iframe', id='pdf')
            if not iframe:
                # Try finding direct link
                embed = soup.find('embed', type='application/pdf')
                if embed:
                    pdf_url = embed.get('src')
                else:
                    return {"success": False, "error": "PDF não encontrado na página."}
            else:
                pdf_url = iframe.get('src')

            if pdf_url.startswith('//'):
                pdf_url = 'https:' + pdf_url
            
            return {
                "success": True,
                "url": pdf_url,
                "title": soup.title.string if soup.title else identifier
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def download(self, pdf_url, output_path):
        """Download PDF from URL."""
        try:
            response = requests.get(pdf_url, verify=False, timeout=self.timeout)
            with open(output_path, 'wb') as f:
                f.write(response.content)
            return True
        except Exception as e:
            print(f"Erro ao baixar: {e}")
            return False
