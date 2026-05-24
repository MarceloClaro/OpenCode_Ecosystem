import streamlit as st
import asyncio
import os
import sys
from datetime import datetime
import pandas as pd

# Garantir que possamos importar do arquivo app.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar as classes e funções necessárias do arquivo principal
from backend_suporte import (
    Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, InputGuardrail, GuardrailFunctionOutput,
    triage_agent, technical_support_agent, billing_support_agent, general_support_agent, complaint_support_agent,
    QueryContext, query_contexts, TriageOutput
)

# Configurar o modelo - reutilizando o já definido em app.py
from backend_suporte import model

# Configurar página do Streamlit
st.set_page_config(
    page_title="Sistema de Suporte ao Cliente",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título e descrição do aplicativo
st.title("💬 Sistema de Suporte ao Cliente")
st.markdown("""
Este sistema ajuda a direcionar suas perguntas para os especialistas mais adequados.
Dependendo da urgência da sua questão, sua solicitação pode ser priorizada.
""")

# Inicializar o estado da sessão se necessário
if 'queries' not in st.session_state:
    st.session_state.queries = []  # Lista para armazenar consultas dos clientes

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = {}  # Histórico de chat para cada consulta

if 'current_query' not in st.session_state:
    st.session_state.current_query = None

if 'is_sent' not in st.session_state:
    st.session_state.is_sent = False

# Função para limpar o formulário
def clear_form():
    st.session_state.user_query = ""
    st.session_state.is_sent = False
    st.session_state.current_query = None

# Função para obter o agente especialista com base na consulta
def get_specialist_agent(specialist_name):
    if "Técnico" in specialist_name or "Suporte Técnico" in specialist_name:
        return technical_support_agent
    elif "Faturamento" in specialist_name or "Financeiro" in specialist_name:
        return billing_support_agent
    elif "Reclamações" in specialist_name or "Insatisfação" in specialist_name:
        return complaint_support_agent
    else:
        return general_support_agent

# Função para extrair o especialista a partir do texto da resposta
def extract_specialist_from_text(text):
    text = text.lower()
    
    # Lista de palavras-chave e seus especialistas correspondentes - Melhorada para reclamações
    keyword_mapping = [
        (["técnico", "suporte técnico", "problema técnico", "configuração", "conexão", "internet", 
          "máquina", "equipamento", "funcionamento", "não funciona", "parou de funcionar"], "Suporte Técnico"),
        
        (["fatura", "faturamento", "cobrança", "financeiro", "pagamento", "reembolso", "conta", 
          "valor", "preço", "cobrado", "dinheiro", "duas vezes", "duplicado", "boleto"], "Suporte de Faturamento"),
        
        (["reclamação", "insatisfação", "queixa", "reclamar", "insatisfeito", "irritado", 
          "decepcionado", "mal atendimento", "produto errado", "errado", "chateado", "erro na entrega", 
          "não recebi", "problema com produto", "defeituoso", "danificado", "devolver", "devolução"], "Tratamento de Reclamações")
    ]
    
    # Verificar cada conjunto de palavras-chave com pontuação
    scores = {"Suporte Técnico": 0, "Suporte de Faturamento": 0, "Tratamento de Reclamações": 0}
    
    for keywords, specialist in keyword_mapping:
        for keyword in keywords:
            if keyword in text:
                # Palavras mais específicas têm mais peso
                weight = 2 if len(keyword) > 8 else 1
                scores[specialist] += weight
    
    # Verificações adicionais para casos específicos
    if "errado" in text and "produto" in text:
        scores["Tratamento de Reclamações"] += 5  # Forte indicação de reclamação
    
    if "chateado" in text or "insatisfeito" in text:
        scores["Tratamento de Reclamações"] += 3  # Indicação de sentimento negativo
    
    # Verificar qual especialista teve a maior pontuação
    max_score = 0
    selected_specialist = "Suporte Geral"
    
    for specialist, score in scores.items():
        if score > max_score:
            max_score = score
            selected_specialist = specialist
    
    # Logar a decisão para depuração
    print(f"Pontuações: {scores}")
    print(f"Especialista selecionado: {selected_specialist}")
    
    return selected_specialist

# Função assíncrona para processar a consulta
async def process_query(query_text):
    try:
        # Analisar primeiro a consulta original para ter uma ideia inicial do especialista
        initial_specialist = extract_specialist_from_text(query_text)
        print(f"Especialista sugerido pela análise da consulta original: {initial_specialist}")
        
        # Executar o agente de triagem
        result = await Runner.run(triage_agent, query_text)
        
        # Para debug: imprimir informações sobre o resultado
        print(f"Tipo do objeto de resultado: {type(result)}")
        
        # Obter o contexto de urgência
        query_context = query_contexts.get(query_text, QueryContext())
        
        # Determinar o especialista a partir da resposta estruturada
        specialist_name = initial_specialist  # Valor padrão é a análise inicial
        
        try:
            # Verificar se temos uma resposta estruturada do TriageOutput
            if hasattr(result, 'output') and hasattr(result.output, 'recommended_agent'):
                recommended_agent = result.output.recommended_agent
                print(f"Agente recomendado pela resposta estruturada: {recommended_agent}")
                
                # Mapear o nome recomendado para um dos nossos agentes especialistas
                if "técnico" in recommended_agent.lower():
                    specialist_name = "Suporte Técnico"
                elif "faturamento" in recommended_agent.lower() or "financeiro" in recommended_agent.lower():
                    specialist_name = "Suporte de Faturamento"
                elif "reclamações" in recommended_agent.lower():
                    specialist_name = "Tratamento de Reclamações"
                elif "geral" in recommended_agent.lower():
                    specialist_name = "Suporte Geral"
                else:
                    # Se o nome não corresponde exatamente, usar o nome como está
                    specialist_name = recommended_agent
            
            # Se não temos uma resposta estruturada, tentar outros métodos
            elif hasattr(result, 'handoff_agent') and result.handoff_agent:
                if hasattr(result.handoff_agent, 'name'):
                    specialist_name = result.handoff_agent.name
                    print(f"Especialista determinado pelo handoff_agent: {specialist_name}")
            
            # Caso especial: produto errado + chateado -> Tratamento de Reclamações
            # Esta regra sempre tem precedência para garantir que reclamações sejam tratadas corretamente
            if "produto errado" in query_text.lower() or ("produto" in query_text.lower() and "errado" in query_text.lower()):
                if "chateado" in query_text.lower() or "insatisfeito" in query_text.lower():
                    specialist_name = "Tratamento de Reclamações"
                    print("Caso especial detectado: produto errado + insatisfação → Tratamento de Reclamações")
        
        except Exception as e:
            print(f"Erro ao determinar especialista: {str(e)}, usando especialista da análise inicial")
        
        # Retornar o resultado da triagem
        return {
            'query': query_text,
            'triagem_result': result,
            'is_urgent': query_context.is_urgent,
            'urgency_reasoning': query_context.urgency_reasoning,
            'specialist_name': specialist_name,
            'timestamp': datetime.now().strftime("%H:%M:%S - %d/%m/%Y"),
            'query_context': query_context
        }
    except Exception as e:
        print(f"Erro geral ao processar consulta: {str(e)}")
        return {
            'query': query_text,
            'error': str(e),
            'specialist_name': "Suporte Geral",  # Fallback para Suporte Geral em caso de erro
            'timestamp': datetime.now().strftime("%H:%M:%S - %d/%m/%Y")
        }

# Função assíncrona para chat com especialista
async def chat_with_specialist(query_data, message):
    try:
        specialist_name = query_data.get('specialist_name', 'Suporte Geral')
        original_query = query_data.get('query', '')
        is_urgent = query_data.get('is_urgent', False)
        
        # Selecionar o agente especialista correto
        specialist = get_specialist_agent(specialist_name)
        
        if not specialist:
            return "Não foi possível encontrar um especialista para sua consulta."
        
        # Criar um contexto para o chat que inclui a consulta original e o status de urgência
        context = f"CONSULTA ORIGINAL: {original_query}\n"
        if is_urgent:
            context += "ESTA É UMA CONSULTA URGENTE. Priorize uma resposta rápida e eficiente.\n"
        context += f"\nMENSAGEM ATUAL DO CLIENTE: {message}"
        
        # Executar o especialista com a mensagem
        result = await Runner.run(specialist, context)
        
        return result.final_output if result else "Sem resposta do especialista."
    except Exception as e:
        return f"Erro ao comunicar com especialista: {str(e)}"

# Função para executar código assíncrono no Streamlit
def run_async(coroutine):
    loop = asyncio.new_event_loop()
    return loop.run_until_complete(coroutine)

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
        output = result.final_output
    else:
        output = "Não foi possível obter a resposta do agente."
    
    # Adicionar informações de urgência
    if query_context and hasattr(query_context, 'is_urgent'):
        if query_context.is_urgent:
            urgency_tag = "\n\n[⚠️ CONSULTA URGENTE - Prioridade Alta]"
            urgency_explanation = f"\nMotivo da urgência: {query_context.urgency_reasoning}"
            return output + urgency_tag + urgency_explanation
        else:
            urgency_tag = "\n\n[Consulta Regular - Prioridade Normal]"
            return output + urgency_tag
    else:
        return output 

# Layout do sidebar para lista de consultas
with st.sidebar:
    st.header("Suas Consultas")
    
    # Ordenar consultas por urgência
    sorted_queries = sorted(
        st.session_state.queries,
        key=lambda x: not x.get('is_urgent', False)
    )
    
    # Mostrar consultas na lista
    for i, query_data in enumerate(sorted_queries):
        # Definir o ícone com base na urgência
        urgency_icon = "⚠️" if query_data.get('is_urgent', False) else "📝"
        specialist = query_data.get('specialist_name', 'Não classificado')
        
        # Extrair uma versão resumida da consulta
        query_text = query_data['query']
        short_query = query_text[:40] + "..." if len(query_text) > 40 else query_text
        
        # Botão para selecionar consulta
        if st.button(f"{urgency_icon} {short_query}", key=f"btn_{i}"):
            st.session_state.current_query = query_data
            st.session_state.is_sent = True
    
    if st.button("🆕 Nova Consulta"):
        clear_form()

# Layout principal - Formulário ou Chat dependendo do estado
if not st.session_state.is_sent:
    # Formulário para nova consulta
    with st.form("query_form"):
        st.subheader("Como podemos ajudar você hoje?")
        
        # Campo para a consulta do usuário
        st.text_area("Descreva sua questão ou problema:", height=150, key="user_query")
        
        submit_col1, submit_col2 = st.columns([1, 5])
        with submit_col1:
            submitted = st.form_submit_button("Enviar")
        with submit_col2:
            clear = st.form_submit_button("Limpar", on_click=clear_form)
        
        if submitted and st.session_state.user_query:
            # Obter o texto da consulta
            query_text = st.session_state.user_query
            
            # Mostrar indicador de progresso
            with st.spinner('Processando sua consulta...'):
                # Processar a consulta
                query_result = run_async(process_query(query_text))
                
                if 'error' not in query_result:
                    # Adicionar à lista de consultas
                    st.session_state.queries.append(query_result)
                    
                    # Definir como consulta atual
                    st.session_state.current_query = query_result
                    st.session_state.is_sent = True
                    
                    # Iniciar histórico de chat vazio para esta consulta
                    if query_text not in st.session_state.chat_history:
                        st.session_state.chat_history[query_text] = []
                    
                    # Recarregar a página para mostrar o resultado
                    st.rerun()
                else:
                    st.error(f"Erro ao processar a consulta: {query_result['error']}")
        elif submitted:
            st.warning("Por favor, escreva sua consulta antes de enviar.")

else:
    # Tela de chat com o especialista
    query_data = st.session_state.current_query
    
    if query_data:
        # Extrair informações relevantes
        query_text = query_data['query']
        specialist_name = query_data.get('specialist_name', 'Suporte Geral')
        is_urgent = query_data.get('is_urgent', False)
        urgency_reasoning = query_data.get('urgency_reasoning', '')
        timestamp = query_data.get('timestamp', datetime.now().strftime("%H:%M:%S - %d/%m/%Y"))
        
        # Definir a exibição baseada na urgência
        if is_urgent:
            st.error("⚠️ Consulta classificada como URGENTE")
        
        # Layout com duas colunas: detalhes da consulta e chat
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Detalhes da Consulta")
            st.write(f"**Consulta:** {query_text}")
            st.write(f"**Encaminhado para:** {specialist_name}")
            st.write(f"**Enviado em:** {timestamp}")
            
            # Mostrar informações de urgência se for urgente
            if is_urgent:
                with st.expander("Detalhes de Urgência"):
                    st.write(f"**Motivo da urgência:** {urgency_reasoning}")
            
            # Botão para voltar ao formulário de nova consulta
            if st.button("Nova Consulta"):
                clear_form()
                st.rerun()
        
        with col2:
            st.subheader(f"Chat com {specialist_name}")
            
            # Exibir histórico de chat
            chat_container = st.container()
            
            # Inicializar o histórico de chat para esta consulta se não existir
            if query_text not in st.session_state.chat_history:
                st.session_state.chat_history[query_text] = []
                # Adicionar a primeira resposta do agente como mensagem do sistema
                if 'triagem_result' in query_data:
                    query_context = query_data.get('query_context')
                    formatted_response = format_output_with_urgency_info(
                        query_data['triagem_result'], 
                        query_context
                    )
                    st.session_state.chat_history[query_text].append({
                        "role": "system", 
                        "content": formatted_response
                    })
            
            # Campo para digitar mensagem
            with st.form("chat_form"):
                user_message = st.text_area("Sua mensagem:", height=100)
                send_message = st.form_submit_button("Enviar")
                
                if send_message and user_message:
                    # Adicionar mensagem do usuário ao histórico
                    st.session_state.chat_history[query_text].append({
                        "role": "user", 
                        "content": user_message
                    })
                    
                    # Processar a resposta do especialista
                    with st.spinner('Aguardando resposta do especialista...'):
                        specialist_response = run_async(
                            chat_with_specialist(query_data, user_message)
                        )
                        
                        # Adicionar resposta do especialista ao histórico
                        st.session_state.chat_history[query_text].append({
                            "role": "assistant", 
                            "content": specialist_response
                        })
                    
                    # Recarregar a página para mostrar a nova mensagem
                    st.rerun()
            
            # Exibir histórico de mensagens
            with chat_container:
                for message in st.session_state.chat_history[query_text]:
                    if message["role"] == "user":
                        st.write(f"👤 **Você:** {message['content']}")
                    elif message["role"] == "system":
                        st.info(f"ℹ️ **Sistema:** {message['content']}")
                    else:
                        st.write(f"👨‍💼 **{specialist_name}:** {message['content']}")
            
            # Adicionar opção para exportar o chat
            if st.button("Exportar Conversa"):
                # Criar um DataFrame com o histórico do chat
                chat_data = []
                for msg in st.session_state.chat_history[query_text]:
                    role_name = "Você" if msg["role"] == "user" else (
                        "Sistema" if msg["role"] == "system" else specialist_name
                    )
                    chat_data.append({
                        "Quem": role_name,
                        "Mensagem": msg["content"]
                    })
                
                # Converter para CSV
                chat_df = pd.DataFrame(chat_data)
                csv = chat_df.to_csv(index=False)
                
                # Criar link para download
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"suporte_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )

# Adicionar rodapé
st.markdown("---")
st.markdown("""
<div style="text-align: center">
    <p>Sistema de Suporte ao Cliente | Desenvolvido com Streamlit e OpenAI Agents</p>
</div>
""", unsafe_allow_html=True) 