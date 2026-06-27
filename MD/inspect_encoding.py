import os

md_dir = r"C:\Users\marce\Documents\OpenCode_Ecosystem\MD\MD"
files = ["01_Trabalho_Final.md", "02-Dissertação_EstagioAtual.md"]

for fname in files:
    fpath = os.path.join(md_dir, fname)
    if not os.path.exists(fpath):
        print(f"File not found: {fpath}")
        continue
    
    print(f"\n==================================================")
    print(f"File: {fname}")
    print(f"Size: {os.path.getsize(fpath)} bytes")
    
    # Try reading as binary first to inspect the first 100 bytes
    with open(fpath, "rb") as f:
        head = f.read(100)
        print(f"Binary header: {head}")
        
    # Read text using different encodings if needed
    for enc in ["utf-8", "latin-1", "utf-16", "utf-16-le", "cp1252"]:
        try:
            with open(fpath, "r", encoding=enc) as f:
                content = f.read()
                print(f"Successfully read with {enc}. Length: {len(content)} characters.")
                print(f"First 200 chars: {repr(content[:200])}")
                break
        except Exception as e:
            print(f"Failed with {enc}: {e}")
