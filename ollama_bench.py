#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OLLAMA INTEGRATION — OpenCode Ecosystem com modelos locais
Executa o CORA-Eval usando modelos Ollama disponiveis localmente.
"""

import sys, subprocess, json, time, re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

BASE_DIR = Path(__file__).parent.resolve()

# ══════════════════════════════════════════════════════════════════════
# DETECTOR DE OLLAMA
# ══════════════════════════════════════════════════════════════════════

def detect_ollama() -> Optional[Dict]:
    """Detecta se Ollama esta instalado e quais modelos disponiveis."""
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            return None
        
        models = []
        for line in result.stdout.strip().split('\n')[1:]:  # pula header
            parts = line.split()
            if len(parts) >= 3:
                models.append({
                    "name": parts[0],
                    "id": parts[1],
                    "size": ' '.join(parts[2:-1]) if len(parts) > 3 else parts[2],
                })
        
        return {
            "installed": True,
            "models": models,
            "count": len(models),
        }
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None

def run_ollama_query(model: str, prompt: str, timeout: int = 60) -> Dict:
    """Executa uma consulta no Ollama e retorna resultado."""
    try:
        start = time.time()
        result = subprocess.run(
            ["ollama", "run", model, prompt],
            capture_output=True, text=True, timeout=timeout
        )
        elapsed = time.time() - start
        
        return {
            "success": result.returncode == 0,
            "response": result.stdout.strip(),
            "error": result.stderr.strip() if result.returncode != 0 else None,
            "time_seconds": round(elapsed, 1),
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "response": "", "error": f"Timeout ({timeout}s)", "time_seconds": timeout}
    except FileNotFoundError:
        return {"success": False, "response": "", "error": "Ollama nao encontrado", "time_seconds": 0}

# ══════════════════════════════════════════════════════════════════════
# BENCHMARK CORA-EVAL VIA OLLAMA
# ══════════════════════════════════════════════════════════════════════

# Problemas de teste simplificados que qualquer modelo pode responder
OLLAMA_BENCHMARK = [
    # Matematica (D1)
    {"id": "D1-N1-01", "dim": "D1", "nivel": "N1",
     "prompt": "Resolva: Qual a soma de 1+2+3+4+5? Responda apenas com o numero.",
     "answer": "15", "type": "exact"},
    {"id": "D1-N1-02", "dim": "D1", "nivel": "N1",
     "prompt": "Calcule: Qual a raiz quadrada de 144? Responda apenas com o numero.",
     "answer": "12", "type": "exact"},
    {"id": "D1-N1-03", "dim": "D1", "nivel": "N1",
     "prompt": "Qual o valor de 2 elevado a 10? Responda apenas com o numero.",
     "answer": "1024", "type": "exact"},
    
    # Fisica (D2)
    {"id": "D2-N1-01", "dim": "D2", "nivel": "N1",
     "prompt": "Calcule a energia cinetica: E=mv^2/2, m=2kg, v=3m/s. Responda so com o numero em Joules.",
     "answer": "9", "type": "exact"},
    {"id": "D2-N1-02", "dim": "D2", "nivel": "N1",
     "prompt": "Qual a forca resultante? F=ma, m=10kg, a=2m/s^2. Responda so com o numero em Newtons.",
     "answer": "20", "type": "exact"},
    
    # Biologia (D5)
    {"id": "D5-N1-01", "dim": "D5", "nivel": "N1",
     "prompt": "Transcreva DNA para RNA: ATGCGT. Responda apenas com a sequencia em letras maiusculas.",
     "answer": "AUGCGU", "type": "exact"},
    {"id": "D5-N1-02", "dim": "D5", "nivel": "N1",
     "prompt": "Qual aminoacido o codon AUG codifica? Responda apenas com o nome.",
     "answer": "Metionina", "type": "contains"},
    
    # Quimica (D4)
    {"id": "D4-N1-01", "dim": "D4", "nivel": "N1",
     "prompt": "Qual a massa molar da agua (H2O)? H=1, O=16. Responda so com o numero em g/mol.",
     "answer": "18", "type": "exact"},
    {"id": "D4-N1-02", "dim": "D4", "nivel": "N1",
     "prompt": "Balanceie: Quantas moleculas de H2O sao produzidas de 2H2 + O2? Responda so com o numero.",
     "answer": "2", "type": "exact"},
    
    # Geociencias (D6)
    {"id": "D6-N1-01", "dim": "D6", "nivel": "N1",
     "prompt": "Qual o ponto de ebulicao da agua em graus Celsius ao nivel do mar? Responda so com o numero.",
     "answer": "100", "type": "exact"},
    {"id": "D6-N1-02", "dim": "D6", "nivel": "N1",
     "prompt": "Qual a camada da atmosfera onde vivemos? Responda apenas com o nome.",
     "answer": "Troposfera", "type": "contains"},
]

def run_ollama_benchmark(model: str) -> Dict:
    """Executa o benchmark CORA-Eval simplificado via Ollama."""
    results = []
    passed = 0
    total = len(OLLAMA_BENCHMARK)
    
    print(f"\n  Executando benchmark com {model}...")
    print(f"  {total} questoes em 5 dimensoes (D1,D2,D4,D5,D6)")
    
    for i, test in enumerate(OLLAMA_BENCHMARK):
        print(f"  [{i+1}/{total}] {test['id']}...", end=" ", flush=True)
        
        result = run_ollama_query(model, test["prompt"], timeout=30)
        
        if result["success"]:
            response = result["response"].strip()
            answer = test["answer"]
            
            if test["type"] == "exact":
                # Extrai numeros da resposta
                numbers = re.findall(r'-?\d+\.?\d*', response)
                match = any(abs(float(n) - float(answer)) < 0.01 for n in numbers if n.replace('.','').replace('-','').isdigit())
            elif test["type"] == "contains":
                match = answer.lower() in response.lower()
            else:
                match = response == answer
            
            if match:
                passed += 1
                print("OK")
            else:
                print(f"X (esperado: {answer}, obtido: {response[:50]})")
            
            results.append({
                "id": test["id"],
                "dim": test["dim"],
                "nivel": test["nivel"],
                "expected": answer,
                "response": response[:100],
                "match": match,
                "time": result["time_seconds"],
            })
        else:
            print(f"ERRO: {result['error']}")
            results.append({"id": test["id"], "error": result["error"]})
    
    return {
        "model": model,
        "total": total,
        "passed": passed,
        "accuracy": round(passed/total*100, 1) if total > 0 else 0,
        "results": results,
    }

# ══════════════════════════════════════════════════════════════════════
# MENU OLLAMA
# ══════════════════════════════════════════════════════════════════════

def ollama_menu():
    """Menu interativo para testes com Ollama."""
    ollama = detect_ollama()
    
    if not ollama or not ollama["installed"]:
        print("\n  [--] Ollama nao detectado.")
        print("  Instale: https://ollama.com")
        print("  Depois: ollama pull <modelo>")
        return
    
    print(f"\n  Ollama detectado: {ollama['count']} modelos")
    for i, m in enumerate(ollama["models"]):
        print(f"    [{i+1}] {m['name']:<25s} ({m['size']})")
    
    try:
        choice = input(f"\n  Escolha o modelo (1-{ollama['count']}): ").strip()
        idx = int(choice) - 1
        if 0 <= idx < ollama["count"]:
            model = ollama["models"][idx]["name"]
            result = run_ollama_benchmark(model)
            print(f"\n  RESULTADO: {result['passed']}/{result['total']} ({result['accuracy']}%)")
            
            # Salva resultado
            out = BASE_DIR / f"ollama_benchmark_{model.replace(':','_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(out, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"  Salvo: {out}")
    except (ValueError, IndexError):
        print("  Opcao invalida")
    except (EOFError, KeyboardInterrupt):
        pass

# ══════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print(f"\n  OpenCode + Ollama — Benchmark Local")
    ollama = detect_ollama()
    if ollama:
        print(f"  Modelos disponiveis: {', '.join(m['name'] for m in ollama['models'])}")
        ollama_menu()
    else:
        print("  Ollama nao detectado. Instale em https://ollama.com")
