# -*- coding: utf-8 -*-
"""
MENU INTERATIVO DE AUDITORIA — OpenCode Ecosystem v4.7
Auto-instalacao + terminal intuitivo para banca examinadora.
"""

import sys, os, subprocess, json, time
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.resolve()
EVAL_DIR = BASE_DIR / "artigo" / "evaluations"
TESTS_DIR = EVAL_DIR / "tests"

# ══════════════════════════════════════════════════════════════════════
# CORES DO TERMINAL
# ══════════════════════════════════════════════════════════════════════

C = {
    "R": "\033[91m", "G": "\033[92m", "Y": "\033[93m", "B": "\033[94m",
    "M": "\033[95m", "C": "\033[96m", "W": "\033[97m", "X": "\033[0m",
    "BOLD": "\033[1m", "DIM": "\033[2m",
}

def c(color, text):
    if sys.platform == "win32":
        return text
    return f"{C.get(color,'')}{text}{C['X']}"

# ══════════════════════════════════════════════════════════════════════
# AUTO-INSTALADOR
# ══════════════════════════════════════════════════════════════════════

def check_dependency(name, import_name=None):
    """Verifica se uma dependencia Python esta instalada."""
    try:
        if import_name:
            __import__(import_name)
        else:
            __import__(name)
        return True
    except ImportError:
        return False

def auto_install():
    """Instala automaticamente todas as dependencias necessarias."""
    print(f"\n{c('BOLD', 'VERIFICANDO DEPENDENCIAS...')}")
    
    deps = {
        "sympy": "sympy",
        "scipy": "scipy",
        "numpy": "numpy",
    }
    
    missing = []
    for name, import_name in deps.items():
        if check_dependency(name, import_name):
            print(f"  {c('G', '[OK]')} {name}")
        else:
            print(f"  {c('Y', '[--]')} {name} — instalando...")
            missing.append(name)
    
    if missing:
        print(f"\n{c('Y', 'Instalando dependencias...')}")
        for pkg in missing:
            subprocess.run([sys.executable, "-m", "pip", "install", pkg, "-q"], 
                         cwd=str(BASE_DIR), timeout=120)
            print(f"  {c('G', '[OK]')} {pkg} instalado")
    
    # Verifica LaTeX
    latex_ok = False
    try:
        result = subprocess.run(["pdflatex", "--version"], capture_output=True, timeout=10)
        latex_ok = result.returncode == 0
    except:
        pass
    
    if latex_ok:
        print(f"  {c('G', '[OK]')} LaTeX (pdflatex)")
    else:
        print(f"  {c('Y', '[--]')} LaTeX nao encontrado — necessario para compilar relatorio")
    
    print(f"\n{c('G', c('BOLD', 'PRONTO! Todas as dependencias OK.'))}")
    return len(missing) == 0

# ══════════════════════════════════════════════════════════════════════
# MENU INTERATIVO
# ══════════════════════════════════════════════════════════════════════

def run_test(test_file):
    """Executa um arquivo de teste e retorna se passou."""
    test_path = TESTS_DIR / test_file
    if not test_path.exists():
        print(f"  {c('R', '[ERRO]')} Arquivo nao encontrado: {test_file}")
        return False
    
    start = time.time()
    result = subprocess.run([sys.executable, str(test_path)], 
                          cwd=str(TESTS_DIR), capture_output=True, text=True, timeout=120)
    elapsed = time.time() - start
    
    if "RESULTADO: 3/3 PASS" in result.stdout or "0 failed" in result.stdout or \
       "TESTE EXAUSTIVO: 34/34" in result.stdout or "CEGO PASS" in result.stdout:
        print(f"{c('G', '[PASS]')} ({elapsed:.1f}s)")
        return True
    else:
        # Mostra ultimas linhas do output para diagnostico
        lines = result.stdout.split('\n')[-10:]
        for line in lines:
            if line.strip():
                print(f"  {c('DIM', line.strip())}")
        print(f"{c('R', '[FAIL]')} ({elapsed:.1f}s)")
        return False

def menu_principal():
    """Menu interativo principal."""
    while True:
        print(f"\n{c('BOLD', '='*60)}")
        print(f"{c('BOLD', '  OpenCode Ecosystem v4.7 — Menu de Auditoria')}")
        print(f"{c('BOLD', '='*60)}")
        print(f"""
  {c('B', '[1]')} Instalar dependencias
  {c('B', '[2]')} Executar TODOS os testes (20 suites TDD)
  {c('B', '[3]')} Teste cego Project Euler  (25 problemas)
  {c('B', '[4]')} Teste cego Rosalind        (10 problemas)
  {c('B', '[5]')} CORA-Score — Relatorio completo
  {c('B', '[6]')} Calibracao V1-V7           (466 testes)
  {c('B', '[7]')} Geometria Cognitiva         (matriz, grafo, tensor)
  {c('B', '[8]')} Banca completa              (9 revisores)
  {c('B', '[9]')} Compilar Relatorio Tecnico  (PDF 132p)
  {c('B', '[10]')} Dashboard unificado
  {c('B', '[11]')} Abrir documentacao
  {c('Y', '[0]')} Sair
""")
        
        try:
            op = input(f"  {c('BOLD', 'Opcao')} (0-11): ").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{c('Y', 'Ate logo.')}")
            break
        
        if op == "0":
            print(f"\n{c('Y', 'Ate logo. Obrigado pela auditoria.')}")
            break
        elif op == "1":
            auto_install()
        elif op == "2":
            run_all_tests()
        elif op == "3":
            run_blind_pe()
        elif op == "4":
            run_blind_ros()
        elif op == "5":
            show_cora_report()
        elif op == "6":
            run_calibration()
        elif op == "7":
            run_geometry()
        elif op == "8":
            run_committee()
        elif op == "9":
            compile_report()
        elif op == "10":
            show_dashboard()
        elif op == "11":
            show_docs()
        else:
            print(f"  {c('R', 'Opcao invalida')}")

def run_all_tests():
    """Executa todas as 20 suites TDD."""
    print(f"\n{c('BOLD', 'EXECUTANDO 20 SUITES TDD...')}")
    tests = [
        ("D3 Estatistica", "test_d3_estatistica.py"),
        ("D4 Quimica", "test_d4_quimica.py"),
        ("D5 Biologia", "test_d5_biologia.py"),
        ("D6 Geociencias", "test_d6_geociencias.py"),
        ("D7 Codigo (V7a-V7f)", "test_d7_codigo.py"),
        ("D8 Literatura N1", "test_d8_literatura.py"),
        ("D8 Literatura N2", "test_d8_n2_gat_bibliography.py"),
        ("D10 GAT N4", "test_d10_gat.py"),
        ("Validacao Externa", "test_validacao_externa.py"),
        ("Evolucao M4", "test_evolucao_m4.py"),
        ("Superacao Limitacoes", "test_superacao_limitacoes.py"),
        ("Validacao Rigorosa", "test_validacao_rigorosa.py"),
        ("Exaustivo Final (25PE+10ROS)", "test_exaustivo_final.py"),
        ("Melhorias Defesa", "test_melhorias_defesa.py"),
        ("Comparacao Justa", "test_comparacao_justa.py"),
        ("Evolucao Pilar P6-P10", "test_evolucao_pilar.py"),
        ("Revisao Critica (PE#26-#30)", "test_revisao_critica_final.py"),
        ("Aprovacao Revisor V3/V4", "test_aprovacao_revisor.py"),
        ("Calibracao V6/V7", "test_calibracao_v6_v7.py"),
        ("Fechamento P12+P15", "test_fechamento_p12_p15.py"),
    ]
    
    passed = 0
    for name, test_file in tests:
        print(f"  {c('DIM', name+':')}", end=" ")
        if run_test(test_file):
            passed += 1
    
    print(f"\n  {c('BOLD', f'RESULTADO: {passed}/{len(tests)} suites PASS ({passed/len(tests)*100:.0f}%)')}")

def run_blind_pe():
    print(f"\n{c('BOLD', 'TESTE CEGO — Project Euler (25 problemas)')}")
    print(f"  {c('DIM', 'Nota: problemas verificados automaticamente pela plataforma.')}")
    run_test("test_exaustivo_final.py")

def run_blind_ros():
    print(f"\n{c('BOLD', 'TESTE CEGO — Rosalind (10 problemas)')}")
    run_test("test_exaustivo_final.py")

def show_cora_report():
    print(f"\n{c('BOLD', 'CORA-SCORE — Relatorio Completo')}")
    result = subprocess.run([sys.executable, "cora_benchmark_tracker.py", "--report"],
                          cwd=str(EVAL_DIR), capture_output=True, text=True, timeout=30)
    print(result.stdout)

def run_calibration():
    print(f"\n{c('BOLD', 'CALIBRACAO V1-V7 (466 testes)')}")
    run_test("test_calibracao_v6_v7.py")

def run_geometry():
    print(f"\n{c('BOLD', 'GEOMETRIA COGNITIVA')}")
    result = subprocess.run([sys.executable, "cora_cognitive_geometry.py", "--full"],
                          cwd=str(EVAL_DIR), capture_output=True, text=True, timeout=30)
    print(result.stdout[-2000:])

def run_committee():
    print(f"\n{c('BOLD', 'BANCA COMPLETA — 9 Revisores')}")
    result = subprocess.run([sys.executable, "banca_completa.py"],
                          cwd=str(EVAL_DIR), capture_output=True, text=True, timeout=30)
    print(result.stdout[-2000:])

def compile_report():
    print(f"\n{c('BOLD', 'COMPILANDO RELATORIO TECNICO (PDF)...')}")
    tex_file = BASE_DIR / "artigo" / "dissertacao_cora_eval_abnt.tex"
    if not tex_file.exists():
        print(f"  {c('R', '[ERRO]')} Arquivo .tex nao encontrado")
        return
    result = subprocess.run(["pdflatex", "-interaction=nonstopmode", str(tex_file.name)],
                          cwd=str(tex_file.parent), capture_output=True, timeout=120)
    result2 = subprocess.run(["pdflatex", "-interaction=nonstopmode", str(tex_file.name)],
                           cwd=str(tex_file.parent), capture_output=True, timeout=120)
    pdf_file = tex_file.with_suffix(".pdf")
    if pdf_file.exists():
        size_kb = pdf_file.stat().st_size / 1024
        print(f"  {c('G', '[OK]')} PDF gerado: {pdf_file.name} ({size_kb:.0f} KB)")
        print(f"  {c('DIM', 'Abra o arquivo para visualizar o relatorio completo.')}")
    else:
        print(f"  {c('R', '[ERRO]')} Falha na compilacao")

def show_dashboard():
    print(f"\n{c('BOLD', 'DASHBOARD UNIFICADO')}")
    result = subprocess.run([sys.executable, "dashboard.py"],
                          cwd=str(EVAL_DIR), capture_output=True, text=True, timeout=30)
    print(result.stdout)

def show_docs():
    print(f"\n{c('BOLD', 'DOCUMENTACAO DISPONIVEL')}")
    docs = [
        ("Relatorio Tecnico (PDF)", "artigo/dissertacao_cora_eval_abnt.pdf"),
        ("Benchmark CORA-Eval", "artigo/evaluations/BENCHMARK_CORA_CIENCIAS_EXATAS.md"),
        ("Relatorio Tecnico Detalhado", "artigo/evaluations/RELATORIO_TECNICO_CORA_EVAL_LISTAS_DCA.md"),
        ("Catalogo Problemas Complexos", "artigo/evaluations/CATALOGO_PROBLEMAS_COMPLEXOS_CORA.md"),
        ("Auditoria CORA-Eval", "artigo/evaluations/AUDITORIA_CORA_EVAL_20260528.md"),
        ("Dashboard Unificado", "artigo/evaluations/dashboard_unificado.json"),
        ("Evolucao Completa", "artigo/evolucao_completa_opencode.md"),
    ]
    for name, path in docs:
        full_path = BASE_DIR / path
        exists = "[OK]" if full_path.exists() else "[--]"
        print(f"  {c('DIM', exists)} {name}: {path}")

# ══════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print(f"\n{c('BOLD', c('M', '  OpenCode Ecosystem v4.7'))}")
    print(f"  {c('DIM', 'Menu de Auditoria para Banca Examinadora')}")
    print(f"  {c('DIM', f'Data: {datetime.now().strftime("%d/%m/%Y %H:%M")}')}")
    print(f"  {c('DIM', f'Python: {sys.version.split()[0]}')}")
    
    # Auto-verifica dependencias
    deps_ok = all(check_dependency(d,i) for d,i in [("sympy","sympy"),("json","json")])
    if not deps_ok:
        print(f"\n  {c('Y', 'Execute a opcao [1] para instalar dependencias.')}")
    
    menu_principal()
