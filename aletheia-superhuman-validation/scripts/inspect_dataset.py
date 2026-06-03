#!/usr/bin/env python3
"""Inspecionar estrutura do dataset enriquecido."""

import json
from pathlib import Path

dataset_path = Path("data/erdos_718_enriched_v1.1.json")

with open(dataset_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Normalizar estrutura
if isinstance(data, dict):
    problems = data.get('problems', [])
else:
    problems = data if isinstance(data, list) else []

print(f"Total de problemas: {len(problems)}\n")

if problems:
    p0 = problems[0]
    print("Chaves disponíveis em problema #0:")
    for key in sorted(p0.keys()):
        value = p0[key]
        value_type = type(value).__name__
        
        if isinstance(value, (str, int, float, bool)):
            value_preview = str(value)[:60]
        elif isinstance(value, (list, dict)):
            value_preview = f"<{value_type}> com {len(value)} items"
        else:
            value_preview = str(value)[:60]
        
        print(f"  {key}: {value_type} = {value_preview}")
    
    print("\n" + "="*70)
    print("AMOSTRA: Primeiros 3 problemas")
    print("="*70 + "\n")
    
    for i, problem in enumerate(problems[:3]):
        print(f"Problema #{i}:")
        print(f"  ID: {problem.get('id')}")
        print(f"  Domain: {problem.get('domain')}")
        print(f"  Statement: {problem.get('statement', '')[:100]}...")
        print(f"  Quality Score: {problem.get('quality_score')}")
        print(f"  Status: {problem.get('status')}")
        print(f"  Known Results: {len(problem.get('known_results', []))} items")
        print(f"  Papers: {len(problem.get('related_papers', []))} items")
        print()
