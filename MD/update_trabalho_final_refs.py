import os

md_path = r"C:\Users\marce\Documents\OpenCode_Ecosystem\MD\MD\01_Trabalho_Final.md"
refs_path = r"C:\Users\marce\Documents\OpenCode_Ecosystem\MD\generated_refs.md"

with open(md_path, "r", encoding="utf-8") as f:
    content = f.read()

with open(refs_path, "r", encoding="utf-8") as f:
    refs_content = f.read()

# Replace the title '# REFERÊNCIAS BIBLIOGRÁFICAS' in generated refs with '**6. REFERÊNCIAS BIBLIOGRÁFICAS**' or similar to match style
refs_content = refs_content.replace("# REFERÊNCIAS BIBLIOGRÁFICAS", "**6. REFERÊNCIAS BIBLIOGRÁFICAS**")

# We split the original content at character index 136424 (which we verified is the start of References)
body_content = content[:136424]

updated_content = body_content + refs_content

with open(md_path, "w", encoding="utf-8") as f:
    f.write(updated_content)

print("Updated 01_Trabalho_Final.md references successfully!")
