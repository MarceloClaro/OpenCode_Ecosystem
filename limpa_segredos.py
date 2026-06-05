import os

REPO    = r"C:\Users\marce\.config\opencode"
SECRET  = "GROQ_API_KEY_REMOVIDO_USE_VARIAVEL_DE_AMBIENTE"
SAFE    = "GROQ_API_KEY_REMOVIDO_USE_VARIAVEL_DE_AMBIENTE"
EXTS    = {".md", ".txt", ".json", ".py", ".ts", ".js", ".yaml", ".yml", ".toml", ".rst"}

count = 0
for root, dirs, files in os.walk(REPO):
    dirs[:] = [d for d in dirs if d != ".git"]
    for fname in files:
        if os.path.splitext(fname)[1] in EXTS:
            path = os.path.join(root, fname)
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                if SECRET in content:
                    content = content.replace(SECRET, SAFE)
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"[OK] {path.replace(REPO, '')}")
                    count += 1
            except Exception as e:
                print(f"[ERRO] {path}: {e}")

print(f"\n{'='*50}")
print(f"Total limpo: {count} arquivo(s)")
print(f"{'='*50}")

# Verificacao final
restantes = 0
for root, dirs, files in os.walk(REPO):
    dirs[:] = [d for d in dirs if d != ".git"]
    for fname in files:
        if os.path.splitext(fname)[1] in EXTS:
            path = os.path.join(root, fname)
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    if SECRET in f.read():
                        restantes += 1
                        print(f"[AINDA CONTEM] {path}")
            except:
                pass

if restantes == 0:
    print("VERIFICACAO OK: nenhum segredo restante nos arquivos.")
else:
    print(f"ATENCAO: {restantes} arquivo(s) ainda contem o segredo!")
