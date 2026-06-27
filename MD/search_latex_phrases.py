import os
import re

latex_dir = r"C:\Users\marce\Documents\OpenCode_Ecosystem\MD\dissertacao-latex"
tex_files = [f for f in os.listdir(latex_dir) if f.endswith(".tex")]

phrases = ["motivacao", "aplica", "conceitos disciplinares", "impacto positivo"]

for fname in sorted(tex_files):
    fpath = os.path.join(latex_dir, fname)
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Remove accents for search
    content_no_acc = content.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
    content_no_acc = content_no_acc.replace("ã", "a").replace("õ", "o").replace("ç", "c").replace("ê", "e")
    
    for p in phrases:
        matches = list(re.finditer(re.escape(p), content_no_acc, re.IGNORECASE))
        if matches:
            print(f"\n==================================================")
            print(f"File: {fname} | Phrase: '{p}' matches: {len(matches)}")
            print(f"==================================================")
            for m in matches[:3]:
                idx = m.start()
                context = content[max(0, idx-60):min(len(content), idx+60)]
                print(f"  Context: {repr(' '.join(context.split()))}")
