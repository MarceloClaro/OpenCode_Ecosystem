"""Debug regex pattern for theorem extraction."""
import re

with open('raw_data/formal-conjectures/ErdosProblems/1.lean', encoding='utf-8') as f:
    content = f.read()

print(f'File length: {len(content)} chars')
print(f'Doc comments: {content.count("/--")}')
print(f'theorem count: {content.count("theorem ")}')
print(f'lemma count: {content.count("lemma ")}')
print(f'def count: {content.count("def ")}')
print(f'abbrev count: {content.count("abbrev ")}')

# Test regex
pattern = re.compile(
    r'/\-\-[ \t]*\n?(.*?)\n?\-/\s*'
    r'(?:@\[category\s+([^\]]+)\]\s*)?'
    r'(theorem|lemma|def|abbrev|instance)\s+(\w+(?:\.\w+)*)',
    re.DOTALL
)
matches = list(pattern.finditer(content))
print(f'\nRegex matches: {len(matches)}')
for i, m in enumerate(matches):
    doc = m.group(1)[:80]
    cat = m.group(2) or '(none)'
    typ = m.group(3)
    name = m.group(4)
    print(f'  [{i}] {typ} {name} | cat: {cat} | doc: {doc}...')

# Also try a simpler pattern
print('\n--- Simpler pattern ---')
pattern2 = re.compile(
    r'/\-\-(.*?)\-/\s*'
    r'(?:@\[category\s+([^\]]+)\]\s*)?'
    r'(theorem|lemma|def|abbrev|instance)\s+(\S+)',
    re.DOTALL
)
matches2 = list(pattern2.finditer(content))
print(f'Matches: {len(matches2)}')
for i, m in enumerate(matches2):
    doc = m.group(1)[:80].replace('\n', ' ')
    cat = m.group(2) or '(none)'
    typ = m.group(3)
    name = m.group(4)
    print(f'  [{i}] {typ} {name} | cat: {cat} | doc: {doc}...')
