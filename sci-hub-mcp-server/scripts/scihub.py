
import requests
import re
from bs4 import BeautifulSoup

class SciHub:
    def __init__(self):
        self.mirrors = [
            "https://sci-hub.mksa.top/",
            "https://sci-hub.gupiaoq.com/",
            "https://sci-hub.hkvisa.net/",
            "https://sci-hub.ru/",
            "https://sci-hub.wf/",
            "https://sci-hub.shop/",
        ]
        self.base_url = self.mirrors[0]
        self.timeout = 30
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

    def fetch(self, identifier):
        """Fetch article from Sci-Hub by DOI, PMID or URL."""
        last_error = None
        for mirror in self.mirrors:
            try:
                url = mirror + identifier
                response = requests.get(url, headers=self.headers, verify=False, timeout=self.timeout)
                if response.status_code != 200:
                    last_error = f"HTTP {response.status_code}"
                    continue

                soup = BeautifulSoup(response.content, 'html.parser')
                iframe = soup.find('iframe', id='pdf')
                if not iframe:
                    # Try finding direct link
                    embed = soup.find('embed', type='application/pdf')
                    if embed:
                        pdf_url = embed.get('src')
                    else:
                        last_error = "PDF nao encontrado na pagina"
                        continue
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
                last_error = str(e)
                continue

        return {"success": False, "error": f"Todos os espelhos falharam: {last_error}"}

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
