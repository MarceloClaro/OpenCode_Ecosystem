#!/usr/bin/env python3
# Chat Científico e Auditoria de Tokenização Local
# Criador: Prof. Marcelo Claro Laranjeira (https://github.com/MarceloClaro)
# ORCID: https://orcid.org/0000-0001-8996-2887

import os
import sys
import json
import urllib.request
import urllib.parse
import time
import subprocess
import re

# Configurações de Caminho
ECO_DIR = "/mnt/c/Users/marce/Documents/OpenCode_Ecosystem"
PROJECTS_DIR = os.path.join(ECO_DIR, "projects")
AUDIT_LOG_PATH = os.path.join(ECO_DIR, "docs/session_token_audit.log")
CMD_FILE = os.path.join(ECO_DIR, ".vocalizer_cmd")

# Estilos de Cores ANSI
RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
BLUE = "\033[0;34m"
CYAN = "\033[0;36m"
MAGENTA = "\033[0;35m"
BOLD = "\033[1m"
NC = "\033[0m"

def falar(msg):
    # Envia comando PLAY para o daemon de vocalização nativo
    try:
        msg_limpa = msg.replace('"', '').replace("'", "").replace("`", "").replace("\n", " ")
        msg_limpa = msg_limpa[:800] # Limite para não sobrecarregar
        # Espera se o arquivo anterior ainda não foi limpo pelo daemon (máximo 1 segundo)
        for _ in range(10):
            if not os.path.exists(CMD_FILE):
                break
            time.sleep(0.1)
        
        with open(CMD_FILE, "w", encoding="utf-8") as f:
            f.write(f"PLAY:{msg_limpa}")
    except Exception as e:
        print(f"Erro ao enviar comando de voz: {e}")

def realizar_busca_interna(termo):
    print(f"{YELLOW}>> Realizando busca semântica/textual local em /projects por: '{termo}'...{NC}")
    try:
        resultado = subprocess.check_output(
            ["grep", "-rni", "--exclude-dir=.git", termo, PROJECTS_DIR],
            stderr=subprocess.DEVNULL, text=True
        )
        linhas = resultado.strip().split("\n")[:10]
        if linhas and linhas[0]:
            print(f"{GREEN}[OK] {len(linhas)} ocorrências locais encontradas.{NC}")
            return "\n".join(linhas)
    except Exception:
        pass
    print("Nenhuma referência encontrada nos códigos locais.")
    return ""

def realizar_busca_externa(termo):
    print(f"{YELLOW}>> Consultando base de conhecimento externa (Wikipedia + DuckDuckGo) por: '{termo}'...{NC}")
    results = []
    
    # 1. Wikipedia Search
    try:
        encoded_term = urllib.parse.quote_plus(termo)
        url = f"https://pt.wikipedia.org/w/api.php?action=query&format=json&list=search&srsearch={encoded_term}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=4) as response:
            data = json.loads(response.read().decode("utf-8"))
            search_results = data.get("query", {}).get("search", [])
            for item in search_results[:2]:
                title = item["title"]
                snippet = item["snippet"].replace('<span class="searchmatch">', '').replace('</span>', '')
                results.append(f"- Wikipedia | {title}: {snippet}")
    except Exception as e:
        print(f"{RED}Aviso: Falha ao consultar Wikipedia: {e}{NC}")
        
    # 2. DuckDuckGo Search
    try:
        encoded_term = urllib.parse.quote_plus(termo)
        url = f"https://html.duckduckgo.com/html/?q={encoded_term}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
        with urllib.request.urlopen(req, timeout=4) as response:
            html = response.read().decode("utf-8")
            snippets = re.findall(r'<a class="result__snippet"[^>]*>(.*?)</a>', html, re.DOTALL)
            for s in snippets[:3]:
                clean_s = re.sub(r'<[^>]+>', '', s).strip()
                results.append(f"- Web | {clean_s}")
    except Exception as e:
        print(f"{RED}Aviso: Falha ao consultar DuckDuckGo: {e}{NC}")
        
    if results:
        print(f"{GREEN}[OK] {len(results)} referências externas recuperadas.{NC}")
        return "\n".join(results)
    
    print("Nenhuma informação externa encontrada.")
    return ""

def carregar_acumulado():
    total_prompt = 0
    total_eval = 0
    total_savings = 0.0
    if os.path.exists(AUDIT_LOG_PATH):
        try:
            with open(AUDIT_LOG_PATH, "r", encoding="utf-8") as f:
                for linha in f:
                    if "ACUMULADO_PROMPT_TOKENS=" in linha:
                        total_prompt = int(linha.split("=")[1].strip())
                    elif "ACUMULADO_EVAL_TOKENS=" in linha:
                        total_eval = int(linha.split("=")[1].strip())
                    elif "ACUMULADO_SAVINGS_USD=" in linha:
                        total_savings = float(linha.split("=")[1].strip())
        except Exception:
            pass
    return total_prompt, total_eval, total_savings

def salvar_acumulado(prompt_tokens, eval_tokens, savings):
    try:
        os.makedirs(os.path.dirname(AUDIT_LOG_PATH), exist_ok=True)
        with open(AUDIT_LOG_PATH, "w", encoding="utf-8") as f:
            f.write(f"ACUMULADO_PROMPT_TOKENS={prompt_tokens}\n")
            f.write(f"ACUMULADO_EVAL_TOKENS={eval_tokens}\n")
            f.write(f"ACUMULADO_SAVINGS_USD={savings:.8f}\n")
    except Exception as e:
        print(f"Erro ao salvar log de auditoria: {e}")

def main():
    print(f"{CYAN}================================================================={NC}")
    print(f"{CYAN}   INTERFACE DE AUDITORIA CIENTÍFICA (CAIXA BRANCA - QUALIS A1)  {NC}")
    print(f"{CYAN}   Orquestrador Local: Ollama Engine + RAG + TTS                 {NC}")
    print(f"{CYAN}   Autor: Prof. Marcelo Claro Laranjeira                         {NC}")
    print(f"{CYAN}   ORCID: 0000-0001-8996-2887                                    {NC}")
    print(f"{CYAN}================================================================={NC}")
    print("")

    falar("Painel de inferência local carregado. Pronto para receber consultas.")

    # Carrega dados acumulados de auditoria anterior
    acc_prompt, acc_eval, acc_savings = carregar_acumulado()

    pergunta = input(f"{BOLD}Digite a sua pergunta científica/código:{NC} ").strip()
    if not pergunta:
        print("Entrada vazia. Abortando.")
        return

    print("\nEscolha a estratégia de recuperação (RAG):")
    print(f" [1] {GREEN}Busca Local/Interna{NC} (Códigos em /projects)")
    print(f" [2] {YELLOW}Busca Externa{NC} (Wikipedia + DuckDuckGo)")
    print(f" [3] {CYAN}Busca Híbrida{NC} (Local + Web)")
    print(f" [4] {NC}Zero-Shot{NC} (Sem contexto adicional)")
    try:
        op = int(input("Opção: ").strip())
    except ValueError:
        op = 4

    contexto = ""
    if op == 1:
        contexto = realizar_busca_interna(pergunta)
    elif op == 2:
        contexto = realizar_busca_externa(pergunta)
    elif op == 3:
        c_int = realizar_busca_interna(pergunta)
        c_ext = realizar_busca_externa(pergunta)
        contexto = f"[Contexto Local]:\n{c_int}\n\n[Contexto Wikipedia]:\n{c_ext}"

    # Construção do prompt do RAG
    prompt_final = "Você é o assistente científico do Prof. Marcelo Claro Laranjeira. Responda à pergunta do usuário de forma clara e objetiva em português do Brasil."
    if contexto:
        prompt_final += f"\n\nContexto de suporte:\n{contexto}"
    prompt_final += f"\n\nPergunta do usuário: {pergunta}"

    print(f"\n{YELLOW}>> Conectando ao modelo local (qwen2.5-coder:1.5b)...{NC}")
    print(f"{MAGENTA}[AUDITORIA] Raciocínio em tempo real (White-Box Streaming):{NC}")
    print("-" * 65)

    # Inicia chamada de stream à API do Ollama
    payload = {
        "model": "qwen2.5-coder:1.5b",
        "prompt": prompt_final,
        "stream": True
    }
    
    url_ollama = "http://127.0.0.1:11434/api/generate"
    req_api = urllib.request.Request(
        url_ollama,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    t_start = time.time()
    resp_text = ""
    meta = {}

    try:
        with urllib.request.urlopen(req_api) as response:
            for line in response:
                if line:
                    chunk = json.loads(line.decode("utf-8"))
                    token = chunk.get("response", "")
                    resp_text += token
                    print(token, end="", flush=True)
                    
                    if chunk.get("done", False):
                        meta = chunk
    except Exception as e:
        print(f"\n{RED}Erro de conexão com o serviço Ollama local: {e}{NC}")
        falar("Erro de conexão com o modelo local.")
        return

    print("\n" + "-" * 65)
    t_end = time.time()
    duration = t_end - t_start

    # Leitura e cálculo dos metadados de tokenização
    prompt_tokens = meta.get("prompt_eval_count", 0)
    eval_tokens = meta.get("eval_count", 0)
    total_tokens = prompt_tokens + eval_tokens
    
    eval_dur_ns = meta.get("eval_duration", 0)
    eval_dur_sec = eval_dur_ns / 1_000_000_000.0 if eval_dur_ns else duration
    tokens_sec = eval_tokens / eval_dur_sec if eval_dur_sec > 0 else 0

    # Estimativa de Custos Economizados (Comparado com taxas de nuvem padrão: $0.15/1M Input, $0.60/1M Output)
    cost_saved_input = (prompt_tokens / 1_000_000.0) * 0.15
    cost_saved_output = (eval_tokens / 1_000_000.0) * 0.60
    cost_saved_total = cost_saved_input + cost_saved_output

    # Atualiza acumulado histórico
    new_acc_prompt = acc_prompt + prompt_tokens
    new_acc_eval = acc_eval + eval_tokens
    new_acc_savings = acc_savings + cost_saved_total
    salvar_acumulado(new_acc_prompt, new_acc_eval, new_acc_savings)

    # Renderização da Tabela de Auditoria
    print(f"\n{GREEN}================================================================={NC}")
    print(f"{GREEN}   RELATÓRIO DE AUDITORIA DE INFERÊNCIA E TOKENIZAÇÃO (A1)       {NC}")
    print(f"{GREEN}================================================================={NC}")
    print(f" Tempo de Geração (Geral):    {duration:.2f} segundos")
    print(f" Velocidade de Inferência:    {tokens_sec:.2f} tokens/segundo")
    print(f" Tokens de Entrada (Input):   {prompt_tokens} tokens")
    print(f" Tokens de Saída (Output):    {eval_tokens} tokens")
    print(f" Total de Tokens Processados: {total_tokens} tokens")
    print(f"-----------------------------------------------------------------")
    print(f" Custos Cloud Economizados:   $ {cost_saved_total:.8f} USD")
    print(f"-----------------------------------------------------------------")
    print(f" {BOLD}Histórico Acumulado desta Estação de Pesquisa:{NC}")
    print(f"   Total Input Tokens:        {new_acc_prompt} tokens")
    print(f"   Total Output Tokens:       {new_acc_eval} tokens")
    print(f"   Economia Total Acumulada:  $ {new_acc_savings:.8f} USD")
    print(f"{GREEN}================================================================={NC}\n")

    # Vocaliza a resposta e o relatório auditável em background
    relatorio_falado = f"Relatório de tokenização. Tempo de geração: {duration:.1f} segundos. Velocidade de {tokens_sec:.1f} tokens por segundo. Entrada de {prompt_tokens} tokens. Saída de {eval_tokens} tokens. Economia total de {cost_saved_total:.6f} dólares."
    falar(f"{resp_text} {relatorio_falado}")

    input("Pressione [Enter] para continuar...")

if __name__ == "__main__":
    main()
