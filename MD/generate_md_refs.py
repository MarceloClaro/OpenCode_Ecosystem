import os
import re

tex_path = r"C:\Users\marce\Documents\OpenCode_Ecosystem\MD\dissertacao-latex\06_referencias.tex"
out_path = r"C:\Users\marce\Documents\OpenCode_Ecosystem\MD\generated_refs.md"

with open(tex_path, "r", encoding="utf-8") as f:
    content = f.read()

# Let's extract everything inside \begin{thebibliography} ... \end{thebibliography}
start_match = re.search(r"\\begin\{thebibliography\}\{\d+\}", content)
end_match = re.search(r"\\end\{thebibliography\}", content)

if not start_match or not end_match:
    print("Could not find thebibliography environment!")
    exit(1)

bib_content = content[start_match.end():end_match.start()].strip()

# Split entries by \bibitem
# Note: some entries are separated by comments, newlines, etc.
raw_entries = re.split(r"\\bibitem(?:\[[^\]]*\])?\{([^\}]+)\}", bib_content)

# raw_entries has [text_before, key1, entry1, key2, entry2, ...]
entries = []
for i in range(1, len(raw_entries), 2):
    key = raw_entries[i].strip()
    entry_text = raw_entries[i+1].strip()
    entries.append((key, entry_text))

print(f"Parsed {len(entries)} bibliography entries.")

# Let's clean the entry_text from LaTeX commands
def clean_latex(text):
    # Remove LaTeX comments
    text = re.sub(r"%.*$", "", text, flags=re.MULTILINE)
    # Replace newlines with spaces, remove multiple spaces
    text = re.sub(r"\s+", " ", text)
    # Replace \textit{...} with *...*
    text = re.sub(r"\\textit\{([^\}]+)\}", r"*\1*", text)
    # Replace \url{...} with <...>
    text = re.sub(r"\\url\{([^\}]+)\}", r"<\1>", text)
    # Replace \href{url}{label} with [label](url) or just url
    text = re.sub(r"\\href\{([^\}]+)\}\{([^\}]+)\}", r"[\2](\1)", text)
    # Replace LaTeX escaped characters like \&, \_, \%
    text = text.replace(r"\&", "&").replace(r"\_", "_").replace(r"\%", "%")
    # Replace LaTeX special ligatures
    text = text.replace("``", '"').replace("''", '"').replace("`", "'").replace("'", "'")
    text = text.replace("---", "—").replace("--", "-").replace("~", " ")
    # Replace specific accents if any manual ones remain
    text = text.replace(r"{\'a}", "á").replace(r"{\`a}", "à").replace(r"{\~a}", "ã").replace(r"{\^a}", "â")
    text = text.replace(r"{\'e}", "é").replace(r"{\`e}", "è").replace(r"{\^e}", "ê")
    text = text.replace(r"{\'i}", "í").replace(r"{\`i}", "ì").replace(r"{\^i}", "î")
    text = text.replace(r"{\'o}", "ó").replace(r"{\`o}", "ò").replace(r"{\~o}", "õ").replace(r"{\^o}", "ô")
    text = text.replace(r"{\'u}", "u").replace(r"{\`u}", "ù").replace(r"{\^u}", "û")
    text = text.replace(r"{\c{c}}", "ç").replace(r"{\c{C}}", "Ç")
    text = text.replace(r"{\~n}", "ñ").replace(r"{\~N}", "Ñ")
    text = text.replace(r"{\'A}", "Á").replace(r"{\`A}", "À").replace(r"{\~A}", "Ã").replace(r"{\^A}", "Â")
    text = text.replace(r"{\'E}", "É").replace(r"{\`E}", "È").replace(r"{\^E}", "Ê")
    text = text.replace(r"{\'I}", "Í").replace(r"{\`I}", "Ì").replace(r"{\^I}", "Î")
    text = text.replace(r"{\'O}", "Ó").replace(r"{\`O}", "Ò").replace(r"{\~O}", "Õ").replace(r"{\^O}", "Ô")
    text = text.replace(r"{\'U}", "Ú").replace(r"{\`U}", "Ù").replace(r"{\^U}", "Û")
    # Remove any other trailing latex braces or commands
    text = text.strip()
    return text

cleaned_entries = []
for key, entry in entries:
    cleaned = clean_latex(entry)
    cleaned_entries.append(cleaned)

# Let's write to file
with open(out_path, "w", encoding="utf-8") as f:
    f.write("# REFERÊNCIAS BIBLIOGRÁFICAS\n\n")
    # Let's sort alphabetically by author name
    # We will sort using case-insensitive comparison of the cleaned entry text
    for entry in sorted(cleaned_entries, key=lambda x: x.lower()):
        f.write(entry + "\n\n")

print(f"Generated Markdown references list in: {out_path}")
