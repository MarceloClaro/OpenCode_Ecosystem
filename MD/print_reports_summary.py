import os

md_dir = r"C:\Users\marce\Documents\OpenCode_Ecosystem\MD\MD"
files = [
    "REPORT_ANTIAI_01_Trabalho_Final.txt",
    "REPORT_ANTIPLAGIARISM_01_Trabalho_Final.txt",
    "REPORT_ANTIAI_02-Dissertação_EstagioAtual.txt",
    "REPORT_ANTIPLAGIARISM_02-Dissertação_EstagioAtual.txt"
]

for fname in files:
    fpath = os.path.join(md_dir, fname)
    if os.path.exists(fpath):
        print(f"\n==================================================")
        print(f"File: {fname}")
        print(f"==================================================")
        with open(fpath, "r", encoding="utf-8") as f:
            lines = f.readlines()
        # Print the first 15 lines or search for score
        for line in lines[:15]:
            print(line.strip().encode('cp1252', errors='replace').decode('cp1252'))
    else:
        print(f"File not found: {fname}")
