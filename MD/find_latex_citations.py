import os
import re

latex_dir = r"C:\Users\marce\Documents\OpenCode_Ecosystem\MD\dissertacao-latex"
tex_files = [f for f in os.listdir(latex_dir) if f.endswith(".tex")]

print("TeX Files:", tex_files)

# Let's search for \cite{...} in all tex files and print the context
for fname in sorted(tex_files):
    fpath = os.path.join(latex_dir, fname)
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Regex to find any \cite{...} or \cite[...]{...} or similar commands
    cites = re.finditer(r"\\cite(?:\[[^\]]*\])?\{([^\}]+)\}", content)
    cite_list = list(cites)
    if cite_list:
        print(f"\n==================================================")
        print(f"File: {fname}")
        print(f"==================================================")
        for m in cite_list:
            keys = m.group(1).split(",")
            keys = [k.strip() for k in keys]
            idx = m.start()
            context = content[max(0, idx-80):min(len(content), idx+80)]
            # Clean context from LaTeX comments/newlines for compact printing
            context_clean = " ".join(context.split())
            print(f"  Keys: {keys} -> Context: ... {repr(context_clean)} ...")
