import os
import re

md_dir = r"C:\Users\marce\Documents\OpenCode_Ecosystem\MD\MD"
fname = "01_Trabalho_Final.md"
fpath = os.path.join(md_dir, fname)

with open(fpath, "r", encoding="utf-8") as f:
    content = f.read()

# Split at References
ref_match = re.search(r"\*\*6\.\s+REFER\?NCIAS\s+BIBLIOGRAFICAS\*\*", content, re.IGNORECASE)
if ref_match:
    body = content[:ref_match.start()]
    refs_part = content[ref_match.start():]
else:
    print("References section not found. Searching in whole file.")
    body = content
    refs_part = ""

# Look for bracketed numbers in body
bracket_nums = re.findall(r"\[\d+\]", body)
print(f"Bracket numbers in body: {len(bracket_nums)}")
for bn in set(bracket_nums):
    print(f"  bn: {bn}")
    # find where they are
    for m in re.finditer(re.escape(bn), body):
        idx = m.start()
        context = body[max(0, idx-60):min(len(body), idx+60)]
        print(f"    Context: {repr(context)}")
        
# Let's search for any words followed by a year, e.g. "Moran (2018)" or "Silva (2020)"
author_year = re.findall(r"\b([A-Z][a-zA-Z\s]+)\((\d{4})\)", body)
print(f"\nAuthor (Year) occurrences: {len(author_year)}")
for ay in set(author_year):
    print(f"  {ay}")
