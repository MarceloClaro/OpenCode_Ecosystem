import os
import fitz  # PyMuPDF
import re

def load_pdfs_from_folder(folder_path):
    pdf_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.pdf')]
    return pdf_files

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        blocks = page.get_text("blocks")  # Extrai o texto em blocos
        for block in blocks:
            text += block[4] + "\n"  # block[4] contém o conteúdo do texto
    return text


def clean_text(text):
    # Substituir combinações comuns de caracteres que geram problemas
    text = re.sub(r'c[̧~]', 'ç', text)
    text = re.sub(r'¸c', 'ç', text)
    text = re.sub(r'¸c', 'ç', text)  
    text = re.sub(r'˜a', 'ã', text)
    text = re.sub(r'´a', 'á', text)
    text = re.sub(r'`a', 'à', text)
    text = re.sub(r'˜A', 'Ã', text)
    text = re.sub(r'˜o', 'õ', text)
    text = re.sub(r'´o', 'ó', text)
    text = re.sub(r'ˆo', 'ô', text)
    text = re.sub(r'´ı', 'í', text)
    text = re.sub(r'´e', 'é', text)
    text = re.sub(r'´E', 'É', text)
    text = re.sub(r'ˆe', 'ê', text)
    text = re.sub(r'´u', 'ú', text)
       
    # Continue para outras substituições que identificar
    return text





