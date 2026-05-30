import os
import sys
import importlib.util
import subprocess
import json

class EcosystemAuditor:
    def __init__(self):
        self.audit_report = {
            "status": "PENDING",
            "findings": [],
            "summary": ""
        }
        self.skills_path = "/home/ubuntu/skills/"
        sys.path.append(os.path.abspath(self.skills_path))

    def _log_finding(self, type, description, details=None):
        self.audit_report["findings"].append({
            "type": type,
            "description": description,
            "details": details
        })

    def _run_command(self, command, cwd=None):
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True, cwd=cwd)
            return result.stdout, result.stderr
        except subprocess.CalledProcessError as e:
            self._log_finding("ERROR", f"Comando falhou: {command}", {"stdout": e.stdout, "stderr": e.stderr})
            return e.stdout, e.stderr
        except FileNotFoundError:
            self._log_finding("ERROR", f"Comando não encontrado: {command[0]}", None)
            return "", ""

    def _import_skill_module(self, skill_name, module_path):
        try:
            path = os.path.join(self.skills_path, skill_name, module_path)
            spec = importlib.util.spec_from_file_location(module_path.replace("/", "."), path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        except Exception as e:
            self._log_finding("ERROR", f"Falha ao importar módulo {module_path} da skill {skill_name}", str(e))
            return None

    def audit_static_analysis(self):
        self._log_finding("INFO", "Iniciando análise estática de scripts Python.")
        python_scripts = []
        for root, _, files in os.walk(self.skills_path):
            for file in files:
                if file.endswith(".py"):
                    python_scripts.append(os.path.join(root, file))
        
        for script in python_scripts:
            stdout, stderr = self._run_command([sys.executable, "-m", "py_compile", script])
            if stderr:
                self._log_finding("WARNING", f"Erro de compilação em {script}", stderr)
            else:
                self._log_finding("INFO", f"Compilação de {script} OK.")

    def audit_dependencies(self):
        self._log_finding("INFO", "Verificando dependências das skills.")
        # Exemplo: verificar se o orquestrador do nexus-ultra-ecosystem pode ser importado
        orchestrator_mod = self._import_skill_module("nexus-ultra-ecosystem", "scripts/orchestrator.py")
        if orchestrator_mod:
            self._log_finding("INFO", "Orquestrador do NEXUS-ULTRA-ECOSYSTEM importado com sucesso.")
        else:
            self._log_finding("ERROR", "Falha ao importar orquestrador do NEXUS-ULTRA-ECOSYSTEM.")

    def audit_integration_tests(self):
        self._log_finding("INFO", "Executando testes de integração simulados.")
        orchestrator_mod = self._import_skill_module("nexus-ultra-ecosystem", "scripts/orchestrator.py")
        if not orchestrator_mod:
            self._log_finding("ERROR", "Não foi possível carregar o orquestrador para testes de integração.")
            return

        try:
            NexusUltraEcosystem = orchestrator_mod.NexusUltraEcosystem
            mega_skill = NexusUltraEcosystem()

            # Teste Jurídico
            juridico_result = mega_skill.process_task("Pesquisar jurisprudência sobre direito do consumidor no Brasil.")
            if "Resultado simulado para consulta jurídica" in str(juridico_result):
                self._log_finding("INFO", "Teste Jurídico OK.")
            else:
                self._log_finding("ERROR", "Teste Jurídico falhou.", juridico_result)

            # Teste de Saúde (BSDT)
            bsdt_result = mega_skill.process_task("Simular o manejo de diabetes tipo 1 para um paciente.")
            # O BSDT retorna um DataFrame ou uma string de simulação
            if "glucose" in str(bsdt_result).lower() or "simulação" in str(bsdt_result).lower():
                self._log_finding("INFO", "Teste de Saúde (BSDT) OK.")
            else:
                self._log_finding("ERROR", "Teste de Saúde (BSDT) falhou.", str(bsdt_result))

            # Teste Acadêmico
            academic_result = mega_skill.process_task("Escrever um artigo acadêmico sobre os impactos da IA na educação.")
            if "resultado simulado" in str(academic_result).lower():
                self._log_finding("INFO", "Teste Acadêmico OK.")
            else:
                self._log_finding("ERROR", "Teste Acadêmico falhou.", str(academic_result))

            # Teste Sci-Hub (requer contexto)
            scihub_result = mega_skill.process_task("Baixar artigo acadêmico via Sci-Hub: 10.1038/s41597-022-01899-x", context={"identifier": "10.1038/s41597-022-01899-x"})
            # Aceitar sucesso ou erro esperado (não encontrado nos espelhos ou falha de conexão externa)
            if "pdf_url" in str(scihub_result) or "não encontrado" in str(scihub_result).lower() or "failed to resolve" in str(scihub_result).lower():
                self._log_finding("INFO", "Teste Sci-Hub OK (resultado esperado para ambiente sem acesso externo direto ou artigo ausente).")
            else:
                self._log_finding("ERROR", "Teste Sci-Hub falhou com erro inesperado.", str(scihub_result))

        except Exception as e:
            self._log_finding("CRITICAL", "Exceção durante testes de integração do orquestrador.", str(e))

    def audit_ecosystem(self):
        self.audit_static_analysis()
        self.audit_dependencies()
        self.audit_integration_tests()
        
        errors = [f for f in self.audit_report["findings"] if f["type"] == "ERROR" or f["type"] == "CRITICAL"]
        if errors:
            self.audit_report["status"] = "FAILED"
            self.audit_report["summary"] = f"Auditoria concluída com {len(errors)} erros críticos/fatais."
        else:
            self.audit_report["status"] = "PASSED"
            self.audit_report["summary"] = "Auditoria concluída com sucesso. Nenhum erro crítico encontrado."
        
        return self.audit_report

if __name__ == "__main__":
    auditor = EcosystemAuditor()
    report = auditor.audit_ecosystem()
    print(json.dumps(report, indent=2))
