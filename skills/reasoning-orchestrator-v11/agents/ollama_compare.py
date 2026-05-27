#!/usr/bin/env python3
"""OLLAMA LLM COMPARISON — 3 models, 3 tests, real data"""
import requests, json, time, sys

OLLAMA = "http://localhost:11434/api/generate"

TESTS = [
    ("T1: Calculo", "What is the derivative of sin(x)cos(x)? Show steps. Answer in 100 words."),
    ("T2: IMO Geometry", "Acute triangle ABC with circumcenter O. Points P,Q,R on BC,CA,AB such that OP,OQ,OR perpendicular to BC,CA,AB. Prove AP,BQ,CR are concurrent. Show reasoning."),
    ("T3: Cartan", "Use Cartans formula to prove L_{X_H} omega = 0 for Hamiltonian field i_{X_H} omega = -dH. Show: 1)Cartan, 2)d(omega)=0, 3)i_XH omega=-dH, 4)d^2=0. Conclude."),
]

MODELS = ["phi3:mini", "qwen2.5-coder:7b", "mistral:7b"]

def test_model(model, test_name, prompt):
    start = time.time()
    try:
        r = requests.post(OLLAMA, json={
            "model": model, "prompt": prompt, "stream": False,
            "options": {"temperature": 0.1, "num_predict": 400}
        }, timeout=300)
        elapsed = time.time() - start
        resp = r.json().get("response", "")
        # Score by keyword matching
        if "derivative" in test_name.lower() or "sin" in prompt.lower():
            keywords = ["product", "rule", "derivative", "cos", "sin", "2x", "cos(2x)"]
        elif "triangle" in prompt.lower() or "circumcenter" in prompt.lower():
            keywords = ["concurrent", "perpendicular", "orthocenter", "ceva", "trig", "angle"]
        else:
            keywords = ["cartan", "lie", "derivative", "d^2", "closed", "omega", "exact", "zero"]
        score = sum(1 for k in keywords if k.lower() in resp.lower())
        return {"model": model, "test": test_name, "time_s": round(elapsed, 1),
                "score": score, "max": len(keywords), "response_preview": resp[:200]}
    except Exception as e:
        return {"model": model, "test": test_name, "time_s": 0, "score": 0, "max": 1, "error": str(e)[:100]}

results = []
for model in MODELS:
    print(f"\n{'='*50}")
    print(f"TESTING: {model}")
    print(f"{'='*50}")
    for tname, prompt in TESTS:
        print(f"  {tname}...", end=" ", flush=True)
        r = test_model(model, tname, prompt)
        results.append(r)
        if "error" in r:
            print(f"ERROR: {r['error'][:60]}")
        else:
            print(f"{r['time_s']}s | score={r['score']}/{r['max']}")
        time.sleep(0.5)

# Print comparison table
print(f"\n{'='*70}")
print("COMPARISON TABLE — 3 Ollama Models")
print(f"{'='*70}")
print(f"{'Test':<25} {'phi3:mini':>15} {'qwen2.5-coder:7b':>20} {'mistral:7b':>15}")
print("-" * 75)
for i, tname in enumerate(["T1: Calculo", "T2: IMO Geom", "T3: Cartan"]):
    row = [tname]
    for j, model in enumerate(MODELS):
        idx = i * 3 + j
        r = results[idx]
        if "error" in r:
            row.append(f"ERR")
        else:
            row.append(f"{r['score']}/{r['max']} ({r['time_s']}s)")
    print(f"{row[0]:<25} {row[1]:>15} {row[2]:>20} {row[3]:>15}")

print(f"\n{'='*70}")
print("SUMMARY")
print(f"{'='*70}")
for model in MODELS:
    model_results = [r for r in results if r["model"] == model]
    total_score = sum(r.get("score", 0) for r in model_results)
    total_max = sum(r.get("max", 1) for r in model_results)
    avg_time = sum(r.get("time_s", 0) for r in model_results) / max(len(model_results), 1)
    errors = sum(1 for r in model_results if "error" in r)
    print(f"  {model:<25} score={total_score}/{total_max} | avg={avg_time:.0f}s | errors={errors}")

# Save
with open(r"C:\Users\marce\.config\opencode\evals\ollama_comparison.json", "w") as f:
    json.dump(results, f, indent=2)
print("\nSaved: ollama_comparison.json")
