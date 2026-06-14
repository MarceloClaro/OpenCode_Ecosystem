import sys
import os

met_path = 'dissertacao-opencode/capitulos/14-metodologia.tex'
res_path = 'dissertacao-opencode/capitulos/15-resultados.tex'

with open(met_path, 'r', encoding='utf-8') as f:
    met = f.read()

met = met.replace('10 Suites, 274 CTs', '11 Suites, 278 CTs')
met = met.replace('10 suites de teste', '11 suites de teste')
met = met.replace('274 casos de teste', '278 casos de teste')

# Insert the SPEC-036 paragraph before \subsection
if r'\subsection{Infraestrutura e Avaliação Sistêmica}' in met:
    spec_text = r"""
Além disso, a validação estrutural do ecossistema expandiu-se com a especificação \textbf{SPEC-036}, introduzindo o MasterOrchestrator. Uma suite adicional com 4 Casos de Teste (CT-3601 a CT-3604) garante que a macro-orquestração ocorra de ponta a ponta com rigorosa conformidade SDD/TDD, resultando no controle unificado de agentes PhD e Polimata sob um único entrypoint altamente reprodutível.
"""
    met = met.replace(r'\subsection{Infraestrutura e Avaliação Sistêmica}', spec_text + '\n' + r'\subsection{Infraestrutura e Avaliação Sistêmica}')

with open(met_path, 'w', encoding='utf-8') as f:
    f.write(met)


with open(res_path, 'r', encoding='utf-8') as f:
    res = f.read()

res = res.replace('19 ciclos evolutivos (R1 a R19)', '20 ciclos evolutivos (R1 a R20)')
res = res.replace('Ecossistema OpenCode (R1-R19)', 'Ecossistema OpenCode (R1-R20)')

table_row_r19_1 = r"R19 & Adaptação Ollama Local & 100 & 5 modelos customizados, SPEC-034, discovery e scripts locais \\"
table_row_r20_1 = r"R20 & Master Orchestrator (SPEC-036) & 100 & Coordenação PhD/Polimata, Orquestração End-to-End, TDD rigoroso \\"
res = res.replace(table_row_r19_1, table_row_r19_1 + "\n" + table_row_r20_1)

table_row_r19_2 = r"R19 & Adaptação Ollama Local & 100 & Integração de 5 modelos locais LLM, SDD/TDD rigorosos, 100\% auditabilidade \\"
table_row_r20_2 = r"R20 & Master Orchestrator & 100 & Ponto de entrada unificado, integração PhD e Polimata (SPEC-036) \\"
res = res.replace(table_row_r19_2, table_row_r19_2 + "\n" + table_row_r20_2)

# Also update text where R19 is mentioned
res = res.replace(r'A \textbf{Fase 4} (R19, 99$\rightarrow$100, +1 ponto) consolida a arquitetura através da adaptação com a inteligência local via Ollama', 
                  r'A \textbf{Fase 4} (R19-R20, 99$\rightarrow$100, +1 ponto) consolida a arquitetura através da adaptação com a inteligência local via Ollama e centraliza o comando sistêmico via MasterOrchestrator')

res = res.replace(r'O ciclo R19 culminou com um score perfeito de 100/100', r'Os ciclos R19 e R20 culminaram com um score perfeito de 100/100')

with open(res_path, 'w', encoding='utf-8') as f:
    f.write(res)

print("Updated dissertation tex files successfully.")
