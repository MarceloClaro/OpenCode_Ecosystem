from google.adk.agents import Agent
import pandas as pd
import io


def analyze_statement(file_content: str) -> str:
    df = pd.read_csv(io.StringIO(file_content))  # <-- Lê string, não bytes
    resumo = df.groupby('Categoria')['Valor'].sum().sort_values(ascending=False)
    output = "Resumo de gastos por categoria:\n"
    for categoria, valor in resumo.items():
        output += f"- {categoria}: R$ {valor:.2f}\n"
    return output

root_agent = Agent(
    name="finance_agent",
    model="gemini-2.0-flash-exp",
    description="Um agente que analisa extratos bancários e dá dicas financeiras.",
    instruction="Seja claro, organizado e forneça insights financeiros baseados nos extratos. Para isso use o analyze_statement. Caso seja solicitado busque na internet informações sobre finanças.",
    tools=[analyze_statement]
)
