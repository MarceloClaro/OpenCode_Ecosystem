import os

latex_dir = r"C:\Users\marce\Documents\OpenCode_Ecosystem\MD\dissertacao-latex"
fpath = os.path.join(latex_dir, "06_referencias.tex")

with open(fpath, "r", encoding="utf-8") as f:
    content = f.read()

print("Length of 06_referencias.tex:", len(content))
print("First 3000 characters of 06_referencias.tex:")
# Print replacing non-ASCII characters
print(content[:3000].encode('ascii', errors='replace').decode('ascii'))
