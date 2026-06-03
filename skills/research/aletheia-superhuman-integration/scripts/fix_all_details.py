#!/usr/bin/env python3
import re

with open('test_spec_014.py', 'r') as f:
    content = f.read()

# Remove all existing duplicate details
lines = content.split('\n')
output = []
skip_next = False

for i, line in enumerate(lines):
    if skip_next:
        skip_next = False
        continue
    
    # Check if this line is a duplicate details
    if 'details=' in line and i > 0:
        prev_line = lines[i-1] if i > 0 else ""
        if 'details=' in prev_line or 'details=' in lines[i-2] if i > 1 else False:
            continue
    
    # Check if line has CoraCheckResult that needs details
    if 'CoraCheckResult(' in line:
        # Find the closing paren
        block = [line]
        j = i + 1
        while j < len(lines):
            block.append(lines[j])
            if '),' in lines[j] or ')' in lines[j]:
                break
            j += 1
        
        block_str = '\n'.join(block)
        if 'details=' not in block_str and 'severity=' in block_str:
            # Need to add details
            block_str = block_str.replace('severity=', 'details="Test check",\n            severity=')
        
        block_lines = block_str.split('\n')
        output.extend(block_lines)
        
        # Skip processed lines
        for _ in range(j - i):
            i = j
    else:
        output.append(line)

with open('test_spec_014.py', 'w') as f:
    f.write('\n'.join(output))

print("Fixed all CoraCheckResult blocks properly")
