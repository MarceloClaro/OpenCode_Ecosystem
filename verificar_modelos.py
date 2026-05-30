import os
import sys
import json
import subprocess
import urllib.request
import urllib.error

def run_ps(cmd):
    """Executa um comando powershell e retorna a saída limpa."""
    try:
        res = subprocess.run(
            ["powershell", "-NoProfile", "-Command", cmd],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        return res.stdout.strip()
    except Exception as e:
        return f"Erro: {str(e)}"

def check_port(url):
    try:
        with urllib.request.urlopen(url, timeout=3) as response:
            return response.status == 200, response.read().decode('utf-8', errors='ignore')
    except urllib.error.URLError:
        return False, None
    except Exception as e:
        return False, str(e)

def print_section(title):
    print("\n" + "=" * 70)
    print(f" {title} ".center(70, "═"))
    print("=" * 70)

def main():
    print("=" * 70)
    print(" DETALHAMENTO COMPLETO DE HARDWARE E SERVIÇOS LLM ".center(70, "█"))
    print("=" * 70)

    # 1. SISTEMA OPERACIONAL
    print_section("SISTEMA OPERACIONAL")
    os_name = run_ps("(Get-CimInstance Win32_OperatingSystem).Caption")
    os_version = run_ps("(Get-CimInstance Win32_OperatingSystem).Version")
    os_build = run_ps("(Get-CimInstance Win32_OperatingSystem).BuildNumber")
    os_arch = run_ps("(Get-CimInstance Win32_OperatingSystem).OSArchitecture")
    print(f"OS: {os_name}")
    print(f"Versão: {os_version} (Build {os_build})")
    print(f"Arquitetura: {os_arch}")

    # 2. PROCESSADOR (CPU)
    print_section("PROCESSADOR (CPU)")
    cpu_name = run_ps("(Get-CimInstance Win32_Processor).Name")
    cpu_cores = run_ps("(Get-CimInstance Win32_Processor).NumberOfCores")
    cpu_threads = run_ps("(Get-CimInstance Win32_Processor).NumberOfLogicalProcessors")
    cpu_clock = run_ps("(Get-CimInstance Win32_Processor).MaxClockSpeed")
    print(f"Modelo: {cpu_name}")
    print(f"Núcleos Físicos: {cpu_cores}")
    print(f"Threads (Lógicos): {cpu_threads}")
    try:
        clock_ghz = int(cpu_clock) / 1000
        print(f"Clock Máximo: {clock_ghz:.2f} GHz")
    except:
        print(f"Clock Máximo: {cpu_clock} MHz")

    # 3. MEMÓRIA RAM
    print_section("MEMÓRIA RAM")
    ram_raw = run_ps("(Get-CimInstance Win32_PhysicalMemory | Measure-Object -Property Capacity -Sum).Sum")
    ram_speed = run_ps("(Get-CimInstance Win32_PhysicalMemory | Select-Object -First 1).Speed")
    ram_slots = run_ps("(Get-CimInstance Win32_PhysicalMemory).Count")
    try:
        ram_gb = int(ram_raw) / (1024**3)
        print(f"RAM Total: {ram_gb:.2f} GB")
    except:
        print(f"RAM Total: {ram_raw}")
    print(f"Velocidade dos Pentes: {ram_speed} MHz")
    print(f"Pentes Instalados: {ram_slots}")

    # 4. PLACA DE VÍDEO (GPU) E VRAM
    print_section("PLACA DE VÍDEO (GPU)")
    gpus_data = run_ps("Get-CimInstance Win32_VideoController | Select-Object Name, AdapterRAM, DriverVersion | ConvertTo-Json")
    
    if gpus_data and not gpus_data.startswith("Erro"):
        try:
            gpus = json.loads(gpus_data)
            if not isinstance(gpus, list):
                gpus = [gpus]
            for i, gpu in enumerate(gpus):
                name = gpu.get("Name", "Desconhecida")
                vram_raw = gpu.get("AdapterRAM", 0)
                driver = gpu.get("DriverVersion", "N/A")
                
                # Tratamento de VRAM negativa ou nula comum no Windows com GPUs modernas
                if vram_raw:
                    # Converte para valor positivo caso assinado incorretamente, e divide
                    vram_val = abs(int(vram_raw))
                    vram_gb = vram_val / (1024**3)
                    # Caso de reportar RAM do sistema compartilhada incorretamente
                    if vram_gb > 256: 
                        vram_gb = (vram_val % (2**32)) / (1024**3)
                    vram_str = f"{vram_gb:.2f} GB"
                else:
                    vram_str = "Memória Compartilhada / Dinâmica"

                print(f"GPU [{i}]: {name}")
                print(f"  VRAM Dedicada Estimada: {vram_str}")
                print(f"  Versão do Driver: {driver}")
        except Exception as e:
            # Fallback simples se JSON falhar
            gpu_names = run_ps("Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty Name")
            print("GPUs Detectadas:")
            print(gpu_names)
    else:
        print("Nenhuma GPU encontrada via WMI.")

    # Teste específico para NVIDIA CUDA
    nvidia_smi = run_ps("nvidia-smi")
    if nvidia_smi and not nvidia_smi.startswith("Erro") and "NVIDIA-SMI" in nvidia_smi:
        print("\n--- Informações NVIDIA SMI / CUDA ---")
        lines = nvidia_smi.split('\n')
        # Exibe as primeiras 10 linhas que trazem a GPU e a versão do CUDA
        for line in lines[:12]:
            print(f"  {line}")

    # 5. DISCOS E ARMAZENAMENTO
    print_section("DISCOS E ARMAZENAMENTO (C:)")
    disk_free = run_ps("(Get-CimInstance Win32_LogicalDisk -Filter \"DeviceID='C:'\").FreeSpace")
    disk_total = run_ps("(Get-CimInstance Win32_LogicalDisk -Filter \"DeviceID='C:'\").Size")
    try:
        free_gb = int(disk_free) / (1024**3)
        total_gb = int(disk_total) / (1024**3)
        pct_free = (free_gb / total_gb) * 100
        print(f"Disco C: - Total: {total_gb:.1f} GB | Livre: {free_gb:.1f} GB ({pct_free:.1f}% livre)")
    except:
        print("Não foi possível ler as partições de disco.")

    # 6. AMBIENTE DE DESENVOLVIMENTO
    print_section("AMBIENTE DE DESENVOLVIMENTO")
    print(f"Python Executável: {sys.executable}")
    print(f"Python Versão: {sys.version.split()[0]}")
    print(f"Node.js Versão: {run_ps('node --version')}")
    print(f"Bun Versão: {run_ps('bun --version')}")
    print(f"OpenCode CLI Versão: {run_ps('opencode --version')}")

    # 7. SERVIÇOS LLM E MODELOS
    print_section("SERVIÇOS DE MODELOS LOCAIS (LLM)")
    
    # Ollama
    ollama_ok, ollama_data = check_port("http://localhost:11434/api/tags")
    if ollama_ok:
        print("Ollama: ATIVO na porta 11434")
        try:
            models_json = json.loads(ollama_data)
            models = models_json.get("models", [])
            if models:
                print("Modelos disponíveis:")
                for m in models:
                    name = m.get("name", "N/A")
                    size_bytes = m.get("size", 0)
                    size_gb = size_bytes / (1024**3)
                    details = m.get("details", {})
                    family = details.get("family", "Desconhecida")
                    quant = details.get("quantization_level", "N/A")
                    print(f"  - {name:<25} | Tamanho: {size_gb:5.2f} GB | Família: {family:<10} | Quant: {quant}")
            else:
                print("  Nenhum modelo baixado no Ollama.")
        except Exception as e:
            print(f"  Erro ao listar modelos do Ollama: {e}")
        
        # Verificar se há modelo carregado na VRAM (Ollama /api/ps)
        ps_ok, ps_data = check_port("http://localhost:11434/api/ps")
        if ps_ok:
            try:
                ps_json = json.loads(ps_data)
                loaded_models = ps_json.get("models", [])
                if loaded_models:
                    print("\nModelos atualmente carregados em memória (VRAM/RAM):")
                    for lm in loaded_models:
                        print(f"  - {lm.get('name')} (Expira em: {lm.get('expires_at')})")
                else:
                    print("\nNenhum modelo atualmente carregado na VRAM (ocioso).")
            except:
                pass
    else:
        print("Ollama: INATIVO")

    # LM Studio
    lm_ok, lm_data = check_port("http://localhost:1234/v1/models")
    if lm_ok:
        print("\nLM Studio: ATIVO na porta 1234")
        try:
            models_json = json.loads(lm_data)
            models = models_json.get("data", [])
            if models:
                print("Modelos carregados no servidor local:")
                for m in models:
                    print(f"  - ID: {m.get('id')}")
            else:
                print("  Nenhum modelo ativo no LM Studio.")
        except Exception as e:
            print(f"  Erro ao listar modelos do LM Studio: {e}")
    else:
        print("\nLM Studio: INATIVO")

    print("\n" + "=" * 70)
    print(" Fim do Diagnóstico ".center(70, "═"))
    print("=" * 70)

if __name__ == "__main__":
    main()
