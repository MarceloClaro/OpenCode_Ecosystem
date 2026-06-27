import os
import re

md_dir = r"C:\Users\marce\Documents\OpenCode_Ecosystem\MD\MD"
fname = "01_Trabalho_Final.md"
fpath = os.path.join(md_dir, fname)

with open(fpath, "r", encoding="utf-8") as f:
    content = f.read()

# Split at index 136424
body = content[:136424]
refs_part = content[136424:]

print(f"Body length: {len(body)}")
print(f"Refs part length: {len(refs_part)}")

# Search for bracketed numbers in body
bracket_nums = re.findall(r"\[\d+\]", body)
print(f"Bracket numbers in body: {len(bracket_nums)}")
for bn in set(bracket_nums):
    print(f"  bn: {bn}")
    for m in re.finditer(re.escape(bn), body):
        idx = m.start()
        context = body[max(0, idx-60):min(len(body), idx+60)]
        safe = context.encode('cp1252', errors='replace').decode('cp1252')
        print(f"    Context: {repr(safe)}")
        
# Search for any Author (Year) or (Author, Year) or [Author, Year] patterns in body
parenthesized_citations = re.findall(r"\(([^)]+,\s*\d{4})\)", body)
print(f"Parenthesized citations in body: {len(parenthesized_citations)}")
for pc in sorted(list(set(parenthesized_citations))):
    print(f"  pc: {pc}")

bracketed_citations = re.findall(r"\[([^\]]+,\s*\d{4})\]", body)
print(f"Bracketed citations in body: {len(bracketed_citations)}")
for bc in sorted(list(set(bracketed_citations))):
    print(f"  bc: {bc}")

# Let's search for just any year 19XX or 20XX in the body and print its context
years = list(re.finditer(r"\b(19\d{2}|20\d{2})\b", body))
print(f"Years in body: {len(years)}")
for i, m in enumerate(years):
    idx = m.start()
    context = body[max(0, idx-40):min(len(body), idx+40)]
    safe = context.encode('cp1252', errors='replace').decode('cp1252')
    print(f"  Year {m.group(1)} context {i}: {repr(safe)}")
