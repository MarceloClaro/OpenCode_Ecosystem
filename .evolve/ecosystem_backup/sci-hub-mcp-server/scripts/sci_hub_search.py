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

# 禁用 HTTPS 证书验证警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class SciHubWrapper:
    """Wrapper para a classe SciHub para compatibilidade com o orquestrador"""
    def __init__(self):
        self.sh = SciHub()
    
    def fetch_article(self, identifier):
        return search_paper_by_doi(identifier)

def create_scihub_instance():
    """创建 SciHub 实例并配置"""
    sh = SciHub()
    sh.timeout = 30  # 增加超时时间到 30 秒
    return sh

def search_paper_by_doi(doi):
    """通过 DOI 在 Sci-Hub 上搜索论文"""
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
        print(f"搜索出错: {str(e)}")
        return {
            'doi': doi,
            'status': 'not_found'
        }

def search_paper_by_title(title):
    """通过标题在 Sci-Hub 上搜索论文"""
    # 由于 SciHub 包不支持 search 方法，我们改用 DOI 搜索
    # 首先尝试从 CrossRef 获取 DOI
    try:
        url = f"https://api.crossref.org/works?query.title={title}&rows=1"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data['message']['items']:
                doi = data['message']['items'][0]['DOI']
                return search_paper_by_doi(doi)
    except Exception as e:
        print(f"CrossRef 搜索出错: {str(e)}")
    
    return {
        'title': title,
        'status': 'not_found'
    }

def search_papers_by_keyword(keyword, num_results=10):
    """通过关键词搜索论文，返回元数据列表"""
    # 使用 CrossRef API 进行搜索
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
        print(f"搜索出错: {str(e)}")
    
    return papers

def download_paper(pdf_url, output_path):
    """下载论文 PDF"""
    sh = SciHub()
    try:
        sh.download(pdf_url, output_path)
        return True
    except Exception as e:
        print(f"下载出错: {str(e)}")
        return False


if __name__ == "__main__":
    print("Sci-Hub 论文搜索测试\n")

    # 1. DOI 搜索测试
    print("1. 通过 DOI 搜索论文")
    test_doi = "10.1002/jcad.12075"  # 一篇神经科学相关的论文
    result = search_paper_by_doi(test_doi)
    
    if result['status'] == 'success':
        print(f"标题: {result['title']}")
        print(f"作者: {result['author']}")
        print(f"年份: {result['year']}")
        print(f"PDF URL: {result['pdf_url']}")
        
        # 尝试下载论文
        output_file = f"paper_{test_doi.replace('/', '_')}.pdf"
        if download_paper(result['pdf_url'], output_file):
            print(f"论文已下载到: {output_file}")
        else:
            print("论文下载失败")
    else:
        print(f"未找到 DOI 为 {test_doi} 的论文")

    # 2. 标题搜索测试
    print("\n2. 通过标题搜索论文")
    test_title = "Choosing Assessment Instruments for Posttraumatic Stress Disorder Screening and Outcome Research"
    result = search_paper_by_title(test_title)
    
    if result['status'] == 'success':
        print(f"DOI: {result['doi']}")
        print(f"作者: {result['author']}")
        print(f"年份: {result['year']}")
        print(f"PDF URL: {result['pdf_url']}")
    else:
        print(f"未找到标题为 '{test_title}' 的论文")

    # 3. 关键词搜索测试
    print("\n3. 通过关键词搜索论文")
    test_keyword = "artificial intelligence medicine 2023"
    papers = search_papers_by_keyword(test_keyword, num_results=3)
    
    for i, paper in enumerate(papers, 1):
        print(f"\n论文 {i}:")
        print(f"标题: {paper['title']}")
        print(f"DOI: {paper['doi']}")
        print(f"作者: {paper['author']}")
        print(f"年份: {paper['year']}")
        if paper.get('pdf_url'):
            print(f"PDF URL: {paper['pdf_url']}")

