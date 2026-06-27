import os
import re

md_dir = r"C:\Users\marce\Documents\OpenCode_Ecosystem\MD\MD"
fname = "01_Trabalho_Final.md"
fpath = os.path.join(md_dir, fname)

with open(fpath, "r", encoding="utf-8") as f:
    content = f.read()

# Let's find matches of [1], [2], etc in the text
# But wait, before the references section. Where does the references section start?
ref_match = re.search(r"\*\*6\.\s+REFER\?NCIAS\s+BIBLIOGRAFICAS\*\*", content, re.IGNORECASE)
if not ref_match:
    ref_match = re.search(r"REFER\?NCIAS\s+BIBLIOGRAFICAS", content, re.IGNORECASE)

if ref_match:
    body = content[:ref_match.start()]
    refs_part = content[ref_match.start():]
else:
    body = content
    refs_part = ""

citations = re.findall(r"\[\d+\]", body)
print(f"Total citations of type [N] in body: {len(citations)}")
print("Unique citations:", sorted(list(set(citations))))

# Let's list some context of where these [N] are used in body
for cite in sorted(list(set(citations)))[:20]:
    matches = [m.start() for m in re.finditer(re.escape(cite), body)]
    print(f"Citation {cite} appears {len(matches)} times:")
    for idx in matches[:2]:
        context = body[max(0, idx-50):min(len(body), idx+50)]
        print(f"  ... {repr(context)} ...")
