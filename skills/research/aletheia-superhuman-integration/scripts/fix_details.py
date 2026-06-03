#!/usr/bin/env python3
import re

with open('test_spec_014.py', 'r') as f:
    content = f.read()

# Simple regex-based approach: find CoraCheckResult blocks missing 'details'
# Pattern: CoraCheckResult( ... severity=... ) without details=

pattern = r'(CoraCheckResult\(\s*check_id=CoraCheckId\.[^,]+,\s*passed=[^,]+,\s*confidence=[^,]+,)'
replacement = r'\1\n                details="Test check",'

content = re.sub(pattern, replacement, content)

# Also handle severity cases
pattern2 = r'(severity="[^"]+",)\s*\)'
replacement2 = r'details="Test check",\n                \1\n            )'

content = re.sub(pattern2, replacement2, content)

with open('test_spec_014.py', 'w') as f:
    f.write(content)

print("Fixed")
