import os
import re

md_path = r"C:\Users\marce\Documents\OpenCode_Ecosystem\MD\MD\01_Trabalho_Final.md"
latex_dir = r"C:\Users\marce\Documents\OpenCode_Ecosystem\MD\dissertacao-latex"

with open(md_path, "r", encoding="utf-8") as f:
    md_content = f.read()

# Let's clean the markdown content of markdown formatting, newlines, etc. for matching
def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    return text.lower()

md_clean = clean_text(md_content[:5000]) # First 5000 chars of MD

tex_files = [f for f in os.listdir(latex_dir) if f.endswith(".tex")]
for fname in sorted(tex_files):
    fpath = os.path.join(latex_dir, fname)
    with open(fpath, "r", encoding="utf-8") as f:
        tex_content = f.read()
    
    tex_clean = clean_text(tex_content)
    
    # Check if there is overlap of large chunks
    # Let's take a 100 character chunk from MD and see if it is in Tex
    overlap_found = False
    for i in range(0, len(md_content) - 200, 500):
        chunk = clean_text(md_content[i:i+150])
        if len(chunk) > 50 and chunk in tex_clean:
            print(f"Overlap found in {fname}!")
            print(f"  MD chunk: {repr(md_content[i:i+150])}")
            overlap_found = True
            break
