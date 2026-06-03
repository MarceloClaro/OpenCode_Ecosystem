#!/usr/bin/env python3
import sys
sys.path.insert(0, 'scripts')

from proof_generator_v2 import ProofGeneratorV2
import json
from pathlib import Path

gen = ProofGeneratorV2()

problems = [
    {'id': 'A0004', 'stmt': 'Chains of triples', 'domain': 'combinatorics'},
    {'id': 'B0014', 'stmt': 'Series convergence', 'domain': 'analysis'}
]

print('Gerando provas...\n')
for p in problems:
    c = gen.generate(p['id'], p['stmt'], p['domain'])
    print(f"{p['id']}: {c.confidence:.0%}")

print('\nOK')
