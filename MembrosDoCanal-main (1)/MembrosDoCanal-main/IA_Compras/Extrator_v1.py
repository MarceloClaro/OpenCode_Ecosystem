import spacy
import csv
import os
import pytesseract
import re

# Carregar o modelo treinado de NER do spaCy
nlp = spacy.load("pt_core_news_md")

# Definir o idioma como português para o Tesseract
custom_config = r'--oem 3 --psm 3 -l por'

# Especificar o nome do arquivo de saída CSV
output_csv = 'entidades_empresas.csv'

# Funções para extrair informações específicas
def extract_cnpj(text):
    cnpj_pattern = r'\b\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}\b'
    return re.findall(cnpj_pattern, text)

def extract_valores(text):
    valor_pattern = r'\b\d+,\d{2}\b'
    return re.findall(valor_pattern, text)

def extract_dates(text):
    date_pattern = r'\b\d{2}/\d{2}/\d{4}\b'
    return re.findall(date_pattern, text)

# Criar ou abrir o arquivo CSV para escrita
with open(output_csv, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    # Escrever o cabeçalho do CSV
    writer.writerow(['Nome do Arquivo', 'CNPJ', 'Valor Total', 'Data', 'Texto Completo'])
    
    # Iterar sobre todos os arquivos no diretório de imagens
    for filename in os.listdir("./nota_fiscal"):
        if filename.endswith('.jpg'):
            # Obter o caminho completo do arquivo jpg
            jpg_path = os.path.join("./nota_fiscal", filename)
           
            # Extrair texto da imagem com o idioma configurado
            extracted_text = pytesseract.image_to_string(jpg_path, config=custom_config)

            print(f"----------------Texto extraído do arquivo {filename}--------------------")
            print(extracted_text)

            # Extrair entidades específicas
            cnpj = extract_cnpj(extracted_text)
            valores = extract_valores(extracted_text)
            datas = extract_dates(extracted_text)
            
            # Processar o texto extraído usando o modelo NER do spaCy
            doc = nlp(extracted_text)

            # Escrever dados no CSV
            writer.writerow([filename, cnpj, valores, datas, extracted_text])




         