import os
import re

md_dir = r"C:\Users\marce\Documents\OpenCode_Ecosystem\MD\MD"
files = ["01_Trabalho_Final.md", "02-Dissertação_EstagioAtual.md"]

# Let's collect all keys from referencias.bib
bib_path = r"C:\Users\marce\Documents\OpenCode_Ecosystem\MD\dissertacao-latex\referencias.bib"
bib_keys = []
with open(bib_path, "r", encoding="utf-8") as f:
    for line in f:
        m = re.match(r"^\s*@\w+\{(\w+),", line)
        if m:
            bib_keys.append(m.group(1))

print("Keys in BibTeX:", sorted(bib_keys))

for fname in files:
    fpath = os.path.join(md_dir, fname)
    if not os.path.exists(fpath):
        print(f"File not found: {fpath}")
        continue
    
    print(f"\n==================================================")
    print(f"Analyzing {fname}")
    print(f"==================================================")
    
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Find all Markdown headings
    headings = re.findall(r"^(#+ .*)$", content, re.MULTILINE)
    print("Headings found in markdown:")
    for h in headings:
        if "refer" in h.lower() or "bibli" in h.lower():
            print(f"  {h}")
            
    # Let's find any citations matching [A-Z]+[0-9]{4} or resembling LaTeX cite
    # or just any words that match keys
    found_keys = {}
    for key in bib_keys:
        count = len(re.findall(r"\b" + re.escape(key) + r"\b", content, re.IGNORECASE))
        if count > 0:
            found_keys[key] = count
            
    print("\nMatches for BibTeX keys in this file:")
    for k, v in sorted(found_keys.items()):
        print(f"  {k}: {v} matches")
        
    # Find potential citations/references in the file that are NOT in the bib keys
    # Let's search for patterns like [NAME2018] or similar uppercase keys
    all_caps_brackets = re.findall(r"\[([A-Z]+[0-9]{4}[a-z]?)\]", content)
    all_caps_parens = re.findall(r"\(([A-Z]+,?\s+[0-9]{4}[a-z]?)\)", content)
    
    print(f"\nPotential bracket citations ([KEY]): {set(all_caps_brackets)}")
    print(f"Number of distinct bracket citations: {len(set(all_caps_brackets))}")
