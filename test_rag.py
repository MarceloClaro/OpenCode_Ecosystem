import sys
import json
import sqlite3
import os
import importlib.util

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar rag_server com suporte a caminhos com hífens
spec = importlib.util.spec_from_file_location("rag_server", os.path.join(os.path.dirname(__file__), "skills", "maswos-v5-nexus", "servers", "rag_server.py"))
rag_server = importlib.util.module_from_spec(spec)
sys.modules["rag_server"] = rag_server
spec.loader.exec_module(rag_server)

consultar_rag = rag_server.consultar_rag
comparar_estrategias_rag = rag_server.comparar_estrategias_rag

def test_rags():
    print("========================================")
    print(" INICIANDO TESTE DO RAG NÃO-SIMULADO")
    print("========================================\n")
    
    pergunta = "Como funciona a orquestração do Nexus no OpenCode Ecosystem?"
    
    print(f"🔹 Pergunta de teste: '{pergunta}'\n")

    # Testando Vanilla RAG
    print("▶ Testando Estratégia VANILLA:")
    res_vanilla = json.loads(consultar_rag(pergunta, "vanilla", 3))
    print(f"  Encontrados: {res_vanilla['total_encontrados']}")
    if res_vanilla['resultados']:
        print(f"  Top Score: {res_vanilla['resultados'][0]['score']}")
        print(f"  Snippet: {res_vanilla['resultados'][0]['snippet'][:100]}...\n")
    
    # Testando Hybrid RAG
    print("▶ Testando Estratégia HYBRID:")
    res_hybrid = json.loads(consultar_rag(pergunta, "hybrid", 3))
    print(f"  Encontrados: {res_hybrid['total_encontrados']}")
    if res_hybrid['resultados']:
        print(f"  Top Score: {res_hybrid['resultados'][0]['score']}")
        print(f"  Snippet: {res_hybrid['resultados'][0]['snippet'][:100]}...\n")
        
    # Testando Agentic RAG
    print("▶ Testando Estratégia AGENTIC (Roteamento Dinâmico):")
    res_agentic = json.loads(consultar_rag(pergunta, "agentic", 3))
    print(f"  Estratégia Escolhida Pelo Roteador: {res_agentic.get('estrategia_executada', 'Desconhecido')}")
    print(f"  Encontrados: {res_agentic['total_encontrados']}\n")

    # Testando Comparador de Estratégias
    print("▶ Executando Comparação Completa (Todas as 9 Estratégias):")
    res_comp = json.loads(comparar_estrategias_rag(pergunta))
    print(f"  A melhor estratégia calculada foi: {res_comp['melhor_estrategia_nome']} ({res_comp['melhor_estrategia']})")
    
    print("\n✅ Testes concluídos!")

if __name__ == "__main__":
    test_rags()
