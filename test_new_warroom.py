import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "skills", "simulation-runner", "scripts"))
from multiagent_warroom import MultiAgentWarRoom

print("Instanciando a sala de guerra ampliada...")
wr = MultiAgentWarRoom()
print(f"Total de agentes carregados: {len(wr.agents)}")

problem = "Impacto da IA no mercado de trabalho brasileiro"
print(f"\nRodando deliberate para o tema: '{problem}'")
res = wr.deliberate(problem)

print("\n--- RESULTADO DA SÍNTESE ---")
print(f"Consenso: {res['synthesis']['consensus_level']}")
print(f"Recomendação Principal: {res['synthesis']['recommendation']}")
print("\nInsights das rodadas:")
for idx, insight in enumerate(res['synthesis']['key_insights']):
    print(f"{idx+1}. {insight}")

print("\n--- AGENTES ATIVADOS ---")
print(res["agents_activated"])
