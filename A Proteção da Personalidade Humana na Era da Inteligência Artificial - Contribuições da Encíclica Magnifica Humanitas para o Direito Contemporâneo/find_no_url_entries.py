import re

bib_path = r"C:\Users\marce\OneDrive\Documentos\Antiprojeto UFC\A Proteção da Personalidade Humana na Era da Inteligência Artificial - Contribuições da Encíclica Magnifica Humanitas para o Direito Contemporâneo\manuscrito\refs.bib"

with open(bib_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find entries without URLs
entries = re.findall(r'@(\w+)\{(\w+),\s*(.*?)\n\}', content, re.DOTALL)

print("=== ENTRIES WITH URL ===")
with_url = [k for t, k, f in entries if re.search(r'^\s*url\s*=', f, re.MULTILINE)]
for k in with_url:
    print(f"  {k}")

print("\n=== ENTRIES WITHOUT URL ===")
no_url = [k for t, k, f in not re.search(r'^\s*url\s*=', f, re.MULTILINE) for t, k, f in entries if not re.search(r'^\s*url\s*=', f, re.MULTILINE)]
