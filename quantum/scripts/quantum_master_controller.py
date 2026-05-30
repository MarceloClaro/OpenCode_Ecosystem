import argparse
import subprocess
import sys
import os

def run_script(script_name, args=None):
    script_path = os.path.join(os.path.dirname(__file__), script_name)
    cmd = [sys.executable, script_path]
    if args:
        cmd.extend(args)
    print(f"--- Executando: {script_name} ---")
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar {script_name}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Quantum Skill Master Controller")
    parser.add_argument("--mode", choices=["benchmark", "mitigate", "test", "rust-perf", "academic"], 
                        required=True, help="Modo de operação")
    parser.add_argument("--samples", type=int, default=100, help="Número de amostras para benchmark")
    
    args = parser.parse_args()

    if args.mode == "benchmark":
        run_script("qml_scientific_benchmarking.py", ["--samples", str(args.samples)])
    elif args.mode == "mitigate":
        run_script("quantum_error_mitigation.py")
    elif args.mode == "test":
        run_script("quantum_unit_tests.py")
    elif args.mode == "rust-perf":
        print("Compilando e executando processador Rust...")
        rust_script = os.path.join(os.path.dirname(__file__), "quantum_processor.rs")
        output_bin = os.path.join(os.path.dirname(__file__), "quantum_processor")
        subprocess.run(["rustc", rust_script, "-o", output_bin], check=True)
        subprocess.run([output_bin], check=True)
    elif args.mode == "academic":
        print("Iniciando pipeline acadêmico...")
        print("Consulte references/academic_quantum_research.md para o fluxo completo.")

if __name__ == "__main__":
    main()
