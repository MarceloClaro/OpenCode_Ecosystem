from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, InputGuardrail, GuardrailFunctionOutput
from pydantic import BaseModel
import asyncio
from typing import List, Dict, Any


# Configuração do modelo (ajuste conforme necessário)
model = OpenAIChatCompletionsModel(
    model="llama3.1:8b",
    openai_client=AsyncOpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
)

# Modelo de saída para identificar a urgência do pedido
class UrgencyCheckOutput(BaseModel):
    is_urgent: bool
    reasoning: str

# Modelo de saída para o agente de triagem
class TriageOutput(BaseModel):
    analysis: str
    recommended_agent: str

# Classe para armazenar contexto durante o processamento
class QueryContext:
    def __init__(self):
        self.is_urgent = False
        self.urgency_reasoning = ""

# Agente para verificar se a questão é urgente
urgency_guardrail_agent = Agent(
    name="Verificação de Urgência",
    instructions="Analise se o problema do cliente é urgente. Uma consulta é urgente quando envolve: serviços interrompidos, perdas financeiras imediatas, riscos à segurança, ou grande insatisfação do cliente.",
    model=model,
    output_type=UrgencyCheckOutput,
)

# Agentes especializados em diferentes áreas de suporte
technical_support_agent = Agent(
    name="Suporte Técnico",
    handoff_description="Especialista em resolver problemas técnicos.",
    instructions="Você ajuda com solução de problemas técnicos, mau funcionamento de produtos e questões de uso. Se o problema for identificado como urgente, priorize uma solução rápida e ofereça alternativas temporárias imediatas.",
    model=model,
)

billing_support_agent = Agent(
    name="Suporte de Faturamento",
    handoff_description="Trata de consultas financeiras e de faturamento.",
    instructions="Você ajuda clientes com problemas de faturamento, reembolsos e disputas de pagamento. Se o problema for identificado como urgente, mencione os prazos acelerados de resolução e forneça um número de protocolo para acompanhamento.",
    model=model,
)

general_support_agent = Agent(
    name="Suporte Geral",
    handoff_description="Trata de consultas gerais e solicitações de atendimento ao cliente.",
    instructions="Você fornece informações sobre políticas da empresa, detalhes de serviços e perguntas gerais de clientes. Se a consulta for marcada como urgente, forneça informações mais detalhadas e opções de contato direto quando necessário.",
    model=model,
)

complaint_support_agent = Agent(
    name="Tratamento de Reclamações",
    handoff_description="Trata reclamações de clientes e escalonamentos.",
    instructions="Você ajuda clientes com reclamações, insatisfação e estratégias de resolução de problemas. Se a reclamação for marcada como urgente, demonstre empatia reforçada, ofereça compensação quando apropriado e garanta um tempo de resolução acelerado.",
    model=model,
)

# Guarda as informações de urgência para cada consulta
query_contexts = {}

# Guardrail para verificar urgência
async def urgency_guardrail(ctx, agent, input_data):
    # Verificar a urgência
    result = await Runner.run(urgency_guardrail_agent, input_data, context=ctx.context)
    final_output = result.final_output_as(UrgencyCheckOutput)
    
    # Armazenar informações de urgência no dicionário global
    query_context = QueryContext()
    query_context.is_urgent = final_output.is_urgent
    query_context.urgency_reasoning = final_output.reasoning
    
    # Usar o input_data como chave para armazenar o contexto
    query_contexts[input_data] = query_context
    
    # Sempre permite a passagem da consulta
    return GuardrailFunctionOutput(
        output_info=final_output,
        tripwire_triggered=False,
    )

# Agente de triagem que direciona as perguntas para os agentes corretos
triage_agent = Agent(
    name="Agente de Triagem",
    instructions="""
    Você é o agente de triagem responsável por encaminhar as consultas dos clientes para o especialista mais adequado.
    
    Analise cuidadosamente o conteúdo da consulta e determine qual o agente especializado mais indicado:
    
    - Suporte Técnico: Problemas técnicos, mau funcionamento, configuração, conexão, equipamentos
    - Suporte de Faturamento: Cobranças, pagamentos, reembolsos, valores, faturas
    - Tratamento de Reclamações: Produtos errados, insatisfação, queixas, reclamações
    - Suporte Geral: Informações gerais, dúvidas sobre serviços, políticas
    
    Para reclamações sobre produtos errados ou qualquer expressão de insatisfação, encaminhe sempre para o Tratamento de Reclamações.

    Forneça uma breve análise e indique claramente para qual agente a consulta está sendo encaminhada.
    
    IMPORTANTE: Você deve sempre escolher um dos quatro especialistas acima. Qualquer consulta que mencione produto errado, recebimento de produto incorreto, ou insatisfação deve ser encaminhada para o Tratamento de Reclamações.
    """,
    model=model,
    output_type=TriageOutput,
    handoffs=[
        technical_support_agent,
        billing_support_agent,
        general_support_agent,
        complaint_support_agent,
    ],
    input_guardrails=[
        InputGuardrail(guardrail_function=urgency_guardrail),
    ],
)

# Função para formatar a saída com informações de urgência
def format_output_with_urgency_info(result, query_context):
    # Tentar extrair a análise da resposta estruturada
    if hasattr(result, 'output') and hasattr(result.output, 'analysis'):
        output = result.output.analysis
        if hasattr(result.output, 'recommended_agent'):
            recommended_agent = result.output.recommended_agent
            output += f"\n\nEncaminhado para: {recommended_agent}"
    # Se não tiver output estruturado, usar a saída final
    elif hasattr(result, 'final_output'):
        # Verificar se final_output é um objeto ou string
        if hasattr(result.final_output, '__str__'):
            output = str(result.final_output)
        else:
            output = result.final_output
    else:
        output = "Não foi possível obter a resposta do agente."
    
    if query_context and hasattr(query_context, 'is_urgent'):
        if query_context.is_urgent:
            urgency_tag = "\n[⚠️ CONSULTA URGENTE - Prioridade Alta]"
            urgency_explanation = f"\nMotivo da urgência: {query_context.urgency_reasoning}"
            return output + urgency_tag + urgency_explanation
        else:
            urgency_tag = "\n[Consulta Regular - Prioridade Normal]"
            return output + urgency_tag
    else:
        return output

# Função principal para testes
async def main():
    # Lista de consultas (ordenadas aleatoriamente inicialmente)
    test_queries = [
        "Minha conexão com a internet parou de funcionar, o que devo fazer?",
        "Fui cobrado duas vezes pelo mesmo pedido!",
        "Quais são os horários de atendimento ao cliente?",
        "Recebi o produto errado e estou muito chateado.",
        "Como posso cancelar minha assinatura?",
    ]
    
    # Dicionário para armazenar as respostas junto com as informações de urgência
    responses = []
    
    # Primeiro passo: processar todas as consultas e coletar urgência
    for query in test_queries:
        try:
            # Executar o agente de triagem
            result = await Runner.run(triage_agent, query)
            
            # Recuperar o contexto de urgência armazenado
            query_context = query_contexts.get(query, QueryContext())
            
            # Obter o agente recomendado
            recommended_agent = "Suporte Geral"
            if hasattr(result, 'output') and hasattr(result.output, 'recommended_agent'):
                recommended_agent = result.output.recommended_agent
                print(f"Agente recomendado para '{query}': {recommended_agent}")
            
            # Armazenar a resposta com informações de prioridade
            responses.append({
                'query': query,
                'result': result,
                'is_urgent': query_context.is_urgent,
                'urgency_reasoning': query_context.urgency_reasoning,
                'query_context': query_context,
                'recommended_agent': recommended_agent
            })
            
        except Exception as e:
            print(f"Erro ao processar a consulta: {query}")
            print(f"Erro: {str(e)}\n")
    
    # Segundo passo: ordenar as consultas com base na urgência (urgentes primeiro)
    responses.sort(key=lambda x: not x['is_urgent'])
    
    # Terceiro passo: exibir as respostas na ordem de prioridade
    print("\n===== RESPOSTAS ORDENADAS POR PRIORIDADE =====\n")
    
    for i, response_data in enumerate(responses):
        query = response_data['query']
        result = response_data['result']
        query_context = response_data['query_context']
        recommended_agent = response_data.get('recommended_agent', 'Não especificado')
        
        print(f"Consulta #{i+1}: {query}")
        print(f"Encaminhado para: {recommended_agent}")
        
        # Formatar a saída com informações de urgência
        formatted_output = format_output_with_urgency_info(result, query_context)
        print(f"Resposta: {formatted_output}\n")
        print("-------------------------------------------\n")

if __name__ == "__main__":
    asyncio.run(main())
