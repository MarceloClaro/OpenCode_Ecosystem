import sys
import argparse
from typing import List, Dict

# Mapeamento de perfis de agentes do ecossistema para tipos de raciocinio recomendados
AGENT_PROFILES = {
    "ws-coder": {
        "description": "Desenvolvedor focado em codigo limpo, robusto e de alto desempenho",
        "default_depth": "L2",
        "reasoning_types": ["Dedutivo", "Sistemico", "Analise de Custo/Beneficio"],
        "barrier": "Teste de stress sintatico"
    },
    "ws-reviewer": {
        "description": "Revisor focado em qualidade, seguranca e conformidade",
        "default_depth": "L3",
        "reasoning_types": ["Falsificacionista", "Indutivo", "Decomposicao de Problemas"],
        "barrier": "Verificacao de limites de confianca (>=80%)"
    },
    "scribe": {
        "description": "Redator e organizador academico (Qualis A1 / ABNT)",
        "default_depth": "L4",
        "reasoning_types": ["Dialetico", "Abdutivo", "Pensamento Critico"],
        "barrier": "Consistencia de citacoes e ABNT"
    },
    "gaper": {
        "description": "Detector de lacunas e inconsistencias logicas",
        "default_depth": "L3",
        "reasoning_types": ["Falsificacionista", "Sistemico", "Bayesiano"],
        "barrier": "Identificacao de premissas ocultas"
    },
    "rude": {
        "description": "Pessimista realista e validador de viabilidade pratica",
        "default_depth": "L2",
        "reasoning_types": ["Teoria dos Jogos", "Analise SWOT", "Falsificacionista"],
        "barrier": "Teste de viabilidade em pior caso"
    }
}

def gerar_checkpoint_nexus(agente: str, tarefa: str, profundidade: str = None) -> str:
    if agente not in AGENT_PROFILES:
        return f"Erro: Agente '{agente}' desconhecido. Escolha entre: {list(AGENT_PROFILES.keys())}"
    
    perfil = AGENT_PROFILES[agente]
    prof = profundidade or perfil["default_depth"]
    
    checkpoint = f"""> **Checkpoint Nexus (Auto-gerado)**:
> - **Agente**: {agente} ({perfil['description']})
> - **Nivel de Profundidade**: {prof}
> - **Modelos de Raciocinio**: {", ".join(perfil['reasoning_types'])}
> - **Tarefa Alvo**: {tarefa}
> - **Barreira Logica**: {perfil['barrier']}"""
    return checkpoint

def validar_resposta_barreira(barreira: str, texto_resposta: str) -> bool:
    texto_lower = texto_resposta.lower()
    
    # Validacoes heuristicas basicas de barreiras logicas
    if "falsificacionista" in barreira.lower() or "stress" in barreira.lower():
        # Deve questionar premissas ou procurar falhas
        indicadores = ["entretanto", "porem", "contudo", "limite", "falha", "risco", "excecao", "teste"]
        return any(ind in texto_lower for ind in indicadores)
        
    elif "bayesiano" in barreira.lower() or "confianca" in barreira.lower():
        # Deve estimar probabilidades ou graus de certeza
        indicadores = ["probabilidade", "chance", "peso", "estimativa", "%", "confianca", "certeza"]
        return any(ind in texto_lower for ind in indicadores)
        
    elif "sistemico" in barreira.lower() or "decomposicao" in barreira.lower():
        # Deve conter conexoes estruturadas ou listas numeradas de partes do sistema
        indicadores = ["componente", "fluxo", "arquitetura", "interacao", "1.", "2.", "modulo", "conexao"]
        return any(ind in texto_lower for ind in indicadores)
        
    # Barreira desconhecida ou generica
    return len(texto_resposta.strip()) > 50

def main():
    parser = argparse.ArgumentParser(description="Helper e Gerador de Raciocinio para o Reasoning Orchestrator Nexus")
    parser.add_argument("--agente", choices=list(AGENT_PROFILES.keys()), required=True, help="Agente que solicita o raciocinio")
    parser.add_argument("--tarefa", required=True, help="Tarefa analitica ou de desenvolvimento a ser realizada")
    parser.add_argument("--depth", choices=["L1", "L2", "L3", "L4", "L5", "L6"], help="Sobrescrever nivel de profundidade")
    parser.add_argument("--validar", help="Arquivo contendo a resposta gerada pelo agente para validar a barreira logica")
    
    args = parser.parse_args()
    
    checkpoint = gerar_checkpoint_nexus(args.agente, args.tarefa, args.depth)
    print("=== CHECKPOINT NEXUS RECOMENDADO ===\n")
    print(checkpoint)
    print("\n====================================")
    
    if args.validar:
        caminho = Path(args.validar)
        if caminho.is_file():
            resp = caminho.read_text(encoding="utf-8", errors="ignore")
            perfil = AGENT_PROFILES[args.agente]
            ok = validar_resposta_barreira(perfil["barrier"], resp)
            print(f"\nResultado da Barreira Logica ('{perfil['barrier']}'):")
            print(f"Status: {'[APROVADO]' if ok else '[REPROVADO - Resposta nao atende a barreira logica]'}")
            sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
