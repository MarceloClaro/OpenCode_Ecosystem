from extractor_text_docs import load_pdfs_from_folder, extract_text_from_pdf, clean_text

def chunk_text_into_paragraphs(text):
    paragraphs = []
    current_paragraph = []

    for line in text.splitlines():
        line = line.strip()
        if line:
            current_paragraph.append(line)
        else:
            if current_paragraph:
                paragraphs.append(" ".join(current_paragraph))
                current_paragraph = []
    if current_paragraph:
        paragraphs.append(" ".join(current_paragraph))
    
    return paragraphs

def process_pdfs_in_folder(folder_path):
    pdf_files = load_pdfs_from_folder(folder_path)
    all_paragraphs = []

    for pdf_file in pdf_files:
        text = clean_text(extract_text_from_pdf(pdf_file))
        paragraphs = chunk_text_into_paragraphs(text)
        
        for i, paragraph in enumerate(paragraphs):
            all_paragraphs.append({
                'paragraph': i + 1,
                'content': paragraph,
                'source': pdf_file
            })
    
    return all_paragraphs

folder_path = "documentos"
chunked_pdfs = process_pdfs_in_folder(folder_path)
#print(chunked_pdfs)