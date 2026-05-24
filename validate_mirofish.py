import sys
import os
import time
import threading
import urllib.request
import py_compile
from urllib.error import URLError

FILE_PATH = r"c:\Users\marce\.config\opencode\skills\mirofish-server\scripts\mirofish_server.py"
PORT = 8788

def validate_syntax():
    try:
        py_compile.compile(FILE_PATH, doraise=True)
        print("✅ [Técnica] Validação Sintática: PASSOU (Sem erros de sintaxe)")
        return True
    except py_compile.PyCompileError as e:
        print(f"❌ [Técnica] Validação Sintática: FALHOU\n{e}")
        return False

def run_server():
    # Insert path to allow imports
    sys.path.insert(0, os.path.dirname(FILE_PATH))
    import mirofish_server  # type: ignore[import-not-found]
    import http.server
    
    server_address = ('', PORT)
    httpd = http.server.HTTPServer(server_address, mirofish_server.MiroFishHandler)
    httpd.serve_forever()

def validate_practical():
    # Start server in thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    time.sleep(2) # wait for server to start
    
    try:
        # Test 1: GET /api/status
        req = urllib.request.Request(f"http://localhost:{PORT}/api/status")
        with urllib.request.urlopen(req) as response:
            status_code = response.getcode()
            if status_code == 200:
                print("✅ [Prática] Requisição GET /api/status: PASSOU (Status 200 OK)")
            else:
                print(f"❌ [Prática] Requisição GET /api/status: FALHOU (Status {status_code})")
                
        # Test 2: OPTIONS request
        req_opt = urllib.request.Request(f"http://localhost:{PORT}/api/status", method="OPTIONS")
        with urllib.request.urlopen(req_opt) as response_opt:
            if response_opt.getcode() == 200:
                print("✅ [Prática] Requisição OPTIONS: PASSOU (Status 200 OK)")
            else:
                print(f"❌ [Prática] Requisição OPTIONS: FALHOU")
                
        # Test 3: POST /api/start
        req_post = urllib.request.Request(f"http://localhost:{PORT}/api/start", method="POST")
        req_post.add_header('Content-Type', 'application/json')
        with urllib.request.urlopen(req_post, data=b'{}') as response_post:
            if response_post.getcode() == 200:
                print("✅ [Prática] Requisição POST /api/start: PASSOU (Status 200 OK)")
            else:
                print(f"❌ [Prática] Requisição POST /api/start: FALHOU")
                
        # Test 4: POST /api/warroom
        req_warroom = urllib.request.Request(f"http://localhost:{PORT}/api/warroom", method="POST")
        req_warroom.add_header('Content-Type', 'application/json')
        with urllib.request.urlopen(req_warroom, data=b'{"problem":"Teste"}') as response_warroom:
            if response_warroom.getcode() == 200:
                print("✅ [Prática] Requisição POST /api/warroom: PASSOU (Status 200 OK)")
            else:
                print(f"❌ [Prática] Requisição POST /api/warroom: FALHOU")

        # Test 5: POST /api/omen/predict
        req_omen = urllib.request.Request(f"http://localhost:{PORT}/api/omen/predict", method="POST")
        req_omen.add_header('Content-Type', 'application/json')
        with urllib.request.urlopen(req_omen, data=b'{}') as response_omen:
            if response_omen.getcode() == 200:
                print("✅ [Prática] Requisição POST /api/omen/predict: PASSOU (Status 200 OK)")
            else:
                print(f"❌ [Prática] Requisição POST /api/omen/predict: FALHOU")

        # Test 6: POST /api/report (Pipeline Massivo)
        req_report = urllib.request.Request(f"http://localhost:{PORT}/api/report", method="POST")
        req_report.add_header('Content-Type', 'application/json')
        with urllib.request.urlopen(req_report, data=b'{}') as response_report:
            if response_report.getcode() == 200:
                print("✅ [Prática] Requisição POST /api/report: PASSOU (Status 200 OK)")
            else:
                print(f"❌ [Prática] Requisição POST /api/report: FALHOU")

        # Test 7: GET /api/health (Telemetria)
        req_health = urllib.request.Request(f"http://localhost:{PORT}/api/health")
        with urllib.request.urlopen(req_health) as response_health:
            if response_health.getcode() == 200:
                print("✅ [Prática] Requisição GET /api/health: PASSOU (Status 200 OK)")
            else:
                print(f"❌ [Prática] Requisição GET /api/health: FALHOU")

        # Test 8: GET /api/omen/audit (Comparador)
        req_audit = urllib.request.Request(f"http://localhost:{PORT}/api/omen/audit")
        with urllib.request.urlopen(req_audit) as response_audit:
            if response_audit.getcode() == 200:
                print("✅ [Prática] Requisição GET /api/omen/audit: PASSOU (Status 200 OK)")
            else:
                print(f"❌ [Prática] Requisição GET /api/omen/audit: FALHOU")

    except Exception as e:
        print(f"❌ [Prática] Erro de Conexão: {e}")

if __name__ == '__main__':
    print("Iniciando Validações Autônomas...")
    if validate_syntax():
        validate_practical()
    print("Validação Concluída.")
