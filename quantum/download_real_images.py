#!/usr/bin/env python3
"""
Download real skin lesion images from ISIC dataset
These are authentic medical images, not synthetic
"""

import requests
import os
from PIL import Image
from io import BytesIO
import json

# ISIC dataset public API
ISIC_API = "https://isic-archive.com/api/v1"

# Mapping de tipos de lesão para ISIC diagnoses
DIAGNOSIS_MAPPING = {
    'MEL': 'melanoma',
    'NV': 'nevus',
    'BCC': 'basal cell carcinoma',
    'AKIEC': 'actinic keratosis',
    'BKL': 'seborrheic keratosis',
    'DF': 'dermatofibroma',
    'VASC': 'vascular lesion'
}

OUTPUT_DIR = "/home/ubuntu/HAM10000_real"

def download_images_by_diagnosis(diagnosis, class_code, limit=5):
    """Download real images for a specific diagnosis"""
    
    print(f"\n🔍 Buscando imagens reais de {diagnosis}...")
    
    try:
        # Query ISIC API
        search_url = f"{ISIC_API}/images"
        params = {
            'limit': limit * 2,  # Buscar mais para filtrar
            'offset': 0,
            'sort': ['-_id']
        }
        
        # Adicionar filtro de diagnóstico se disponível
        if diagnosis:
            params['diagnosis'] = diagnosis
        
        response = requests.get(search_url, params=params, timeout=10)
        
        if response.status_code != 200:
            print(f"⚠️  API retornou status {response.status_code}")
            return 0
        
        images = response.json()
        
        if not images:
            print(f"❌ Nenhuma imagem encontrada para {diagnosis}")
            return 0
        
        count = 0
        for idx, image_data in enumerate(images[:limit]):
            try:
                image_id = image_data.get('_id')
                
                # Download da imagem
                img_url = f"{ISIC_API}/images/{image_id}/download"
                img_response = requests.get(img_url, timeout=10)
                
                if img_response.status_code == 200:
                    # Salvar imagem
                    img = Image.open(BytesIO(img_response.content))
                    
                    # Redimensionar para 224x224 (padrão para VQC)
                    img = img.resize((224, 224), Image.Resampling.LANCZOS)
                    
                    # Salvar em classe específica
                    filename = f"{OUTPUT_DIR}/{class_code}/ISIC_{image_id}.jpg"
                    img.save(filename, quality=95)
                    
                    count += 1
                    print(f"✅ Salvo: {filename}")
                    
            except Exception as e:
                print(f"⚠️  Erro ao baixar imagem {idx}: {str(e)}")
                continue
        
        return count
        
    except Exception as e:
        print(f"❌ Erro na requisição: {str(e)}")
        return 0

def main():
    print("=" * 60)
    print("DOWNLOAD DE IMAGENS REAIS DO ISIC DATASET")
    print("=" * 60)
    
    total_downloaded = 0
    
    for class_code, diagnosis in DIAGNOSIS_MAPPING.items():
        count = download_images_by_diagnosis(diagnosis, class_code, limit=5)
        total_downloaded += count
    
    print("\n" + "=" * 60)
    print(f"✅ Total de imagens reais baixadas: {total_downloaded}")
    print(f"📁 Salvas em: {OUTPUT_DIR}")
    print("=" * 60)

if __name__ == "__main__":
    main()
