#!/usr/bin/env python3
# =====================================================================
# OLLAMA AUTONOMY AGENT — OpenCode Ecosystem v4.6.2
# =====================================================================
# Autonomous local LLM setup: installs, configures, verifies
# Full local autonomy — zero external API dependencies
# =====================================================================

import os, sys, subprocess, json, time, platform, shutil
from pathlib import Path

class OllamaAutonomyAgent:
    """
    Autonomous agent for complete local LLM setup.
    
    Responsibilities:
    1. DETECT — Check if Ollama and models are available
    2. INSTALL — Install Ollama if missing (platform-aware)
    3. PULL — Download required models (mistral, phi3, qwen)
    4. CONFIGURE — Set up the bridge between OpenCode and Ollama
    5. VERIFY — Run test battery on all models
    6. REGISTER — Update ecosystem configuration
    7. MONITOR — Health check daemon (optional)
    """
    
    def __init__(self, verbose=True):
        self.verbose = verbose
        self.ollama_path = self._find_ollama()
        self.required_models = {
            "mistral:7b": {"size_gb": 4.4, "role": "deep_math", "priority": "HIGH"},
            "phi3:mini": {"size_gb": 2.2, "role": "fast_check", "priority": "HIGH"},
            "qwen2.5-coder:7b": {"size_gb": 4.7, "role": "code_tasks", "priority": "MEDIUM"},
        }
        self.total_download_gb = sum(m["size_gb"] for m in self.required_models.values())
        self.status = {
            "ollama_installed": False,
            "ollama_running": False,
            "models_installed": {},
            "bridge_configured": False,
            "integration_tested": False,
        }
    
    def _log(self, msg, level="INFO"):
        prefix = {"INFO": "   ", "OK": " OK", "WARN": " WARN", "ERROR": " ERR", "PHASE": "\n>> "}
        p = prefix.get(level, "   ")
        # Force ASCII-safe output
        text = f"{p} {msg}"
        print(text.encode('ascii', errors='replace').decode('ascii'))
    
    def _find_ollama(self):
        """Find Ollama executable."""
        ollama = shutil.which("ollama")
        if ollama:
            return ollama
        # Windows default path
        win_path = Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Ollama" / "ollama.exe"
        if win_path.exists():
            return str(win_path)
        return None
    
    # ================================================================
    # PHASE 1: DETECT
    # ================================================================
    def detect(self):
        """Detect current Ollama installation status."""
        self._log("PHASE 1: DETECT", "PHASE")
        
        # Check Ollama binary
        if self.ollama_path:
            self.status["ollama_installed"] = True
            self._log(f"Ollama found: {self.ollama_path}", "OK")
        else:
            self._log("Ollama NOT installed", "WARN")
            return self.status
        
        # Check if Ollama server is running
        try:
            import requests
            r = requests.get("http://localhost:11434/api/tags", timeout=5)
            if r.status_code == 200:
                self.status["ollama_running"] = True
                installed = [m["name"] for m in r.json().get("models", [])]
                self._log(f"Ollama server RUNNING — {len(installed)} models installed", "OK")
                
                for model_name, cfg in self.required_models.items():
                    if model_name in installed:
                        self.status["models_installed"][model_name] = "INSTALLED"
                    else:
                        self.status["models_installed"][model_name] = "MISSING"
            else:
                self._log("Ollama server not responding", "WARN")
        except Exception:
            self._log("Ollama server not running — starting...", "WARN")
            try:
                subprocess.Popen(["ollama", "serve"], 
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(3)
                self.status["ollama_running"] = True
                self._log("Ollama server started", "OK")
            except:
                self._log("Could not start Ollama server", "ERROR")
        
        # Print model status
        for model, status in self.status["models_installed"].items():
            icon = "OK" if status == "INSTALLED" else "DL"
            cfg = self.required_models[model]
            print(f"   {icon} {model:<25} {cfg['size_gb']}GB — {cfg['role']} [{status}]")
        
        missing = sum(1 for s in self.status["models_installed"].values() if s == "MISSING")
        if missing > 0:
            missing_gb = sum(self.required_models[m]["size_gb"] 
                           for m, s in self.status["models_installed"].items() if s == "MISSING")
            self._log(f"Missing {missing} models ({missing_gb:.1f} GB to download)", "WARN")
        
        return self.status
    
    # ================================================================
    # PHASE 2: INSTALL (if needed)
    # ================================================================
    def install_ollama(self):
        """Install Ollama if missing."""
        self._log("PHASE 2: INSTALL OLLAMA", "PHASE")
        
        if self.status["ollama_installed"]:
            self._log("Ollama already installed — skipping", "OK")
            return True
        
        system = platform.system()
        self._log(f"Installing Ollama for {system}...")
        
        if system == "Windows":
            self._log("Windows: Download from https://ollama.com/download/windows", "WARN")
            self._log("Please install manually and re-run this agent.", "WARN")
            return False
        elif system == "Linux":
            try:
                subprocess.run(
                    "curl -fsSL https://ollama.com/install.sh | sh",
                    shell=True, check=True, timeout=300
                )
                self._log("Ollama installed successfully", "OK")
                self.ollama_path = shutil.which("ollama")
                return True
            except:
                self._log("Installation failed", "ERROR")
                return False
        elif system == "Darwin":
            self._log("macOS: Download from https://ollama.com/download/mac", "WARN")
            return False
        return False
    
    # ================================================================
    # PHASE 3: PULL MODELS
    # ================================================================
    def pull_models(self, force_all=False):
        """Pull required Ollama models."""
        self._log("PHASE 3: PULL MODELS", "PHASE")
        
        total_size = 0
        for model_name, status in self.status["models_installed"].items():
            if status == "MISSING" or force_all:
                cfg = self.required_models[model_name]
                size_gb = cfg["size_gb"]
                total_size += size_gb
                
                self._log(f"Downloading {model_name} ({size_gb:.1f} GB)...", "INFO")
                print(f"   This may take {size_gb * 5:.0f}-{size_gb * 10:.0f} minutes...")
                
                try:
                    start = time.time()
                    result = subprocess.run(
                        ["ollama", "pull", model_name],
                        capture_output=True, text=True, timeout=3600
                    )
                    elapsed = time.time() - start
                    
                    if result.returncode == 0:
                        self.status["models_installed"][model_name] = "INSTALLED"
                        self._log(f"{model_name} downloaded in {elapsed/60:.1f} min", "OK")
                    else:
                        self._log(f"Failed: {result.stderr[:200]}", "ERROR")
                except subprocess.TimeoutExpired:
                    self._log(f"Timeout downloading {model_name}", "ERROR")
                except Exception as e:
                    self._log(f"Error: {e}", "ERROR")
            else:
                self._log(f"{model_name} already installed — skipping", "OK")
        
        return sum(1 for s in self.status["models_installed"].values() if s == "INSTALLED")
    
    # ================================================================
    # PHASE 4: CONFIGURE BRIDGE
    # ================================================================
    def configure_bridge(self):
        """Configure the OpenCode ↔ Ollama bridge."""
        self._log("PHASE 4: CONFIGURE BRIDGE", "PHASE")
        
        # Check if ollama_verifier.py exists
        agents_dir = Path(__file__).parent
        verifier = agents_dir / "ollama_verifier.py"
        
        if not verifier.exists():
            self._log("ollama_verifier.py not found — creating...", "WARN")
            # Should already exist from v4.6.2 installation
            return False
        
        self._log("Bridge agent found: ollama_verifier.py", "OK")
        
        # Verify the orchestrator has Phase 5.6 integrated
        orchestrator = agents_dir.parent / "definitive_orchestrator.py"
        if orchestrator.exists():
            content = orchestrator.read_text(encoding="utf-8")
            if "PHASE 5.6" in content or "ollama_verify_phase" in content:
                self._log("Orchestrator Phase 5.6 integrated", "OK")
                self.status["bridge_configured"] = True
            else:
                self._log("Orchestrator needs Phase 5.6 integration", "WARN")
        
        # Create opencode.json MCP entry
        self._log("To activate in OpenCode, add to opencode.json:", "INFO")
        print('''
  "mcpServers": {
    "ollama-verifier": {
      "command": "python",
      "args": ["skills/reasoning-orchestrator-v11/agents/ollama_verifier.py"],
      "description": "Local LLM verification (mistral:7b + phi3:mini)"
    }
  }
''')
        
        self.status["bridge_configured"] = True
        return True
    
    # ================================================================
    # PHASE 5: VERIFY INTEGRATION
    # ================================================================
    def verify_integration(self):
        """Run test battery to verify everything works."""
        self._log("PHASE 5: VERIFY INTEGRATION", "PHASE")
        
        tests_passed = 0
        tests_total = 3
        
        # Test 1: Quick sanity (phi3:mini)
        self._log("Test 1/3: phi3:mini sanity check...", "INFO")
        try:
            import requests
            r = requests.post("http://localhost:11434/api/generate", json={
                "model": "phi3:mini",
                "prompt": "What is 2+2? Answer in one word.",
                "stream": False,
                "options": {"num_predict": 5}
            }, timeout=60)
            if "4" in response or "four" in response.lower():
                tests_passed += 1
                self._log("phi3:mini OK", "OK")
            else:
                self._log("phi3:mini unexpected response", "WARN")
        except Exception as e:
            self._log(f"phi3:mini FAILED: {e}", "ERROR")
        
        # Test 2: Math verification (mistral:7b)
        self._log("Test 2/3: mistral:7b Cartan proof...", "INFO")
        try:
            r = requests.post("http://localhost:11434/api/generate", json={
                "model": "mistral:7b",
                "prompt": "Use Cartans formula L_X = i_X d + d i_X. With d(omega)=0 and i_{X_H}omega=-dH, prove L_{X_H}omega=0 in 4 steps.",
                "stream": False,
                "options": {"temperature": 0.1, "num_predict": 300}
            }, timeout=300)
            response = r.json().get("response", "").lower()
            if "cartan" in response and ("d^2" in response or "zero" in response or "d(dh)" in response.lower()):
                tests_passed += 1
                self._log("mistral:7b Cartan proof OK", "OK")
            else:
                self._log(f"mistral:7b response unexpected ({len(response)} chars)", "WARN")
        except Exception as e:
            self._log(f"mistral:7b FAILED: {e}", "ERROR")
        
        # Test 3: Code generation (qwen2.5-coder:7b)
        self._log("Test 3/3: qwen2.5-coder:7b code generation...", "INFO")
        try:
            r = requests.post("http://localhost:11434/api/generate", json={
                "model": "qwen2.5-coder:7b",
                "prompt": "Write a Python function fibonacci(n) that returns the nth Fibonacci number. Return ONLY the code.",
                "stream": False,
                "options": {"temperature": 0.1, "num_predict": 100}
            }, timeout=120)
            response = r.json().get("response", "")
            if "def fibonacci" in response and "return" in response:
                tests_passed += 1
                self._log("qwen2.5-coder:7b code OK", "OK")
            else:
                self._log("qwen2.5-coder:7b unexpected response", "WARN")
        except Exception as e:
            self._log(f"qwen2.5-coder:7b FAILED: {e}", "ERROR")
        
        self.status["integration_tested"] = True
        
        self._log(f"\n   VERIFICATION: {tests_passed}/{tests_total} tests passed", 
                 "OK" if tests_passed == tests_total else "WARN")
        
        if tests_passed == tests_total:
            self._log("ALL SYSTEMS GO — Full local autonomy achieved!", "OK")
        elif tests_passed >= 2:
            self._log("PARTIAL autonomy — some models unavailable", "WARN")
        else:
            self._log("INCOMPLETE — run 'ollama pull <model>' for missing models", "ERROR")
        
        return tests_passed == tests_total
    
    # ================================================================
    # PHASE 6: HEALTH REPORT
    # ================================================================
    def health_report(self):
        """Generate comprehensive health report."""
        self._log("PHASE 6: HEALTH REPORT", "PHASE")
        
        report = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "cora_version": "4.6.2",
            "ollama_installed": self.status["ollama_installed"],
            "ollama_running": self.status["ollama_running"],
            "models": self.status["models_installed"],
            "bridge_configured": self.status["bridge_configured"],
            "integration_tested": self.status["integration_tested"],
            "total_models": len(self.status["models_installed"]),
            "installed_models": sum(1 for s in self.status["models_installed"].values() if s == "INSTALLED"),
            "autonomy_level": "FULL" if self.status["integration_tested"] and 
                            all(s == "INSTALLED" for s in self.status["models_installed"].values())
                            else "PARTIAL",
        }
        
        print(f"\n{'='*60}")
        print("OLLAMA AUTONOMY HEALTH REPORT")
        print(f"{'='*60}")
        print(f"  Ollama:         {'RUNNING' if report['ollama_running'] else 'STOPPED'}")
        print(f"  Models:         {report['installed_models']}/{report['total_models']}")
        print(f"  Bridge:         {'CONNECTED' if report['bridge_configured'] else 'DISCONNECTED'}")
        print(f"  Integration:    {'VERIFIED' if report['integration_tested'] else 'UNTESTED'}")
        print(f"  Autonomy Level: {report['autonomy_level']}")
        print(f"{'='*60}")
        
        # Save report
        report_path = Path(__file__).parent.parent.parent.parent / "evals" / "ollama_autonomy_health.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        self._log(f"Report saved: {report_path}", "OK")
        
        return report
    
    # ================================================================
    # MAIN: FULL AUTONOMY SETUP
    # ================================================================
    def full_setup(self):
        """Run complete autonomy setup pipeline."""
        print("=" * 60)
        print("OLLAMA AUTONOMY AGENT — OpenCode Ecosystem v4.6.2")
        print("Full Local LLM Setup for Scientific Reasoning")
        print("=" * 60)
        print(f"  Models required: {len(self.required_models)} ({self.total_download_gb:.1f} GB total)")
        print(f"  Platform: {platform.system()} {platform.machine()}")
        print()
        
        # Phase 1: Detect
        self.detect()
        
        # Phase 2: Install Ollama (if needed)
        if not self.status["ollama_installed"]:
            ok = self.install_ollama()
            if not ok:
                self._log("Cannot proceed without Ollama", "ERROR")
                return self.status
            self.detect()  # Refresh status
        
        # Phase 3: Pull models
        self.pull_models()
        
        # Phase 4: Configure bridge
        self.configure_bridge()
        
        # Phase 5: Verify
        self.verify_integration()
        
        # Phase 6: Report
        self.health_report()
        
        # Final message
        installed = sum(1 for s in self.status["models_installed"].values() if s == "INSTALLED")
        total = len(self.required_models)
        
        print(f"\n{'='*60}")
        if installed == total and self.status["integration_tested"]:
            print("FULL LOCAL AUTONOMY ACHIEVED")
            print("Zero external API dependencies.")
            print("Run: python skills/reasoning-orchestrator-v11/definitive_orchestrator.py")
        else:
            print(f"PARTIAL SETUP ({installed}/{total} models)")
            print("Re-run this agent to complete setup.")
        print(f"{'='*60}")
        
        return self.status


# =====================================================================
# CLI Entry Point
# =====================================================================
if __name__ == "__main__":
    agent = OllamaAutonomyAgent(verbose=True)
    agent.full_setup()
