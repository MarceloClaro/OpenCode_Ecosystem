import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv # Importar a biblioteca python-dotenv
import re # Importar a biblioteca re para expressões regulares
import urllib.parse # Importar para codificar URLs

# --- CARREGAR VARIÁVEIS DE AMBIENTE DO ARQUIVO .ENV ---
load_dotenv() # Carrega variáveis do arquivo .env para o ambiente

# --- CONFIGURAÇÃO DA API KEY DO GEMINI ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

try:
    if GOOGLE_API_KEY:
        genai.configure(api_key=GOOGLE_API_KEY)
    else:
        # Não exibir erro aqui ainda, será tratado na UI se a chave não estiver configurada
        pass
except Exception as e:
    st.error(f"Erro ao configurar a API do Gemini: {e}. Verifique se sua API Key é válida.")
    st.stop()


# --- FUNÇÃO PARA CHAMAR A API DO GEMINI (sem alterações nesta função em si) ---
def get_ai_gift_suggestions(person_desc, relationship, occasion, budget, avoid_items):
    if not GOOGLE_API_KEY:
        st.error("A GOOGLE_API_KEY não está configurada. Verifique seu arquivo .env ou as variáveis de ambiente.")
        return []

    model = genai.GenerativeModel('gemini-2.5-pro-exp-03-25')
    
    prompt = f"""
Você é um especialista em encontrar o presente perfeito e criativo.
Com base nas seguintes informações, sugira EXATAMENTE 3 ideias de presentes únicas e personalizadas:

Para quem: {person_desc}
Relacionamento: {relationship}
Ocasião: {occasion}
Orçamento (se informado): {budget}
A evitar (se informado): {avoid_items}

Para CADA UMA DAS 3 SUGESTÕES, inclua EXATAMENTE e NESTA ORDEM:
1. **Nome do Presente:** [Nome claro e conciso do presente]
2. **Justificativa:** [Explicação detalhada de por que este presente seria bom para ESSA pessoa, considerando seus interesses e a ocasião.]
3. **Dica Extra:** [Uma ideia de como tornar o presente ainda mais especial, uma sugestão de onde encontrar (tipo de loja/site, sem links diretos), ou uma ideia de DIY, se aplicável. Se não houver dica relevante, escreva 'Nenhuma dica extra desta vez.']

Formate a resposta para que cada sugestão seja claramente separada por "---".
A sua resposta DEVE começar com '---', seguido da primeira sugestão. Não inclua nenhum preâmbulo ou introdução antes do primeiro '---'.
Exemplo de uma sugestão (note a ausência de markdown nos rótulos no output real):
---
Nome do Presente: Livro X
Justificativa: Porque a pessoa gosta de ler.
Dica Extra: Compre a edição de capa dura.
---
"""
    
    st.sidebar.subheader("Prompt Enviado ao Gemini:")
    st.sidebar.text_area("Prompt", prompt, height=350)

    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.75,
            )
        )
        raw_response_text = response.text
        st.sidebar.subheader("Resposta Bruta do Gemini:")
        st.sidebar.text_area("Resposta Bruta", raw_response_text, height=200)
    except Exception as e:
        st.error(f"Erro ao chamar a API do Gemini: {e}")
        st.sidebar.subheader("Resposta Bruta do Gemini (Erro):")
        st.sidebar.text_area("Resposta Bruta", f"Erro: {e}", height=200)
        return []

    suggestions = []
    if raw_response_text:
        raw_suggestion_blocks = raw_response_text.strip().split("---")
        for raw_block in raw_suggestion_blocks:
            current_suggestion_text = raw_block.strip()
            if not current_suggestion_text:
                continue
            
            parts = {}
            lines = current_suggestion_text.split('\n')
            for line in lines:
                line_stripped = line.strip()
                if not line_stripped:
                    continue

                match_nome = re.match(r"^\**\s*Nome do Presente\s*:\**(.*)", line_stripped, re.IGNORECASE)
                if match_nome:
                    parts["Nome do Presente"] = match_nome.group(1).strip()
                    continue

                match_just = re.match(r"^\**\s*Justificativa\s*:\**(.*)", line_stripped, re.IGNORECASE)
                if match_just:
                    parts["Justificativa"] = match_just.group(1).strip()
                    continue

                match_dica = re.match(r"^\**\s*Dica Extra\s*:\**(.*)", line_stripped, re.IGNORECASE)
                if match_dica:
                    parts["Dica Extra"] = match_dica.group(1).strip()
                    continue
            
            if "Nome do Presente" in parts and "Justificativa" in parts:
                if "Dica Extra" not in parts:
                    parts["Dica Extra"] = "Nenhuma dica extra desta vez." 
                suggestions.append(parts)
                 
    return suggestions

# --- INTERFACE DO STREAMLIT (com links de busca adicionados) ---
st.set_page_config(page_title="Gift Whisperer AI", layout="wide")

st.title("🎁 Presentes Bot AI 🤖")
st.markdown("Seu conselheiro de presentes personalizado com Inteligência Artificial!")
st.markdown("---")

col1, col2 = st.columns([2,1.5])

with col1:
    st.subheader("Conte-nos sobre quem vai receber o presente:")
    
    person_desc = st.text_area(
        "Descreva a pessoa (interesses, hobbies, personalidade, idade aproximada, etc.)",
        height=100,
        placeholder="Ex: Minha irmã, 30 anos, ama ler ficção científica, é vegana, adora gatos e fazer trilhas"
    )
    
    relationship_options = ["Amigo(a)", "Parceiro(a)", "Irmão/Irmã", "Mãe", "Pai", "Filho(a)", "Colega de trabalho", "Outro"]
    relationship = st.selectbox("Qual seu relacionamento com ela/ele?", relationship_options)
    
    occasion_options = ["Aniversário", "Natal", "Dia dos Namorados", "Dia das Mães", "Dia dos Pais", "Amigo Secreto", "Agradecimento", "Formatura", "Casamento", "Só porque sim", "Outra"]
    occasion = st.selectbox("Qual a ocasião?", occasion_options)
    
    budget_options = ["Indiferente", "Até R$50", "R$50 - R$100", "R$100 - R$200", "R$200 - R$500", "Acima de R$500"]
    budget = st.selectbox("Qual seu orçamento (opcional)?", budget_options)
    
    avoid_items = st.text_input(
        "Algo a evitar? (Ex: já dei perfume, não gosta de amarelo)",
        placeholder="Opcional"
    )
    
    if 'suggestions_state' not in st.session_state:
        st.session_state.suggestions_state = []

    if st.button("✨ Sugerir Presentes!"):
        if not GOOGLE_API_KEY:
            st.error("A GOOGLE_API_KEY não está configurada. Verifique seu arquivo .env ou as variáveis de ambiente e reinicie o app.")
            st.session_state.suggestions_state = []
        elif not person_desc:
            st.error("Por favor, descreva a pessoa para receber sugestões.")
            st.session_state.suggestions_state = []
        else:
            with st.spinner("O Gift Whisperer AI está pensando nas melhores ideias... Por favor, aguarde!"):
                st.session_state.suggestions_state = get_ai_gift_suggestions(person_desc, relationship, occasion, budget, avoid_items)
            
            if not st.session_state.suggestions_state and GOOGLE_API_KEY:
                 st.warning("Não consegui gerar sugestões no momento ou o formato da resposta não foi o esperado. Tente ser mais específico ou tente novamente!")


with col2:
    st.subheader("💡 Nossas Sugestões Para Você:")
    if not GOOGLE_API_KEY:
        st.warning("Configure sua GOOGLE_API_KEY no arquivo .env para usar o app.")
    elif not st.session_state.get('suggestions_state'):
        st.info("Preencha os campos à esquerda e clique em 'Sugerir Presentes!' para ver a mágica acontecer.")
    else:
        suggestions_to_display = st.session_state.suggestions_state
        if suggestions_to_display:
            for i, sug in enumerate(suggestions_to_display):
                gift_name = sug.get('Nome do Presente', 'N/A')
                st.markdown(f"#### **Sugestão {i+1}: {gift_name}**")
                st.markdown(f"**Por que é uma boa ideia:** {sug.get('Justificativa', 'N/A')}")
                
                dica_extra = sug.get('Dica Extra')
                if dica_extra and dica_extra.lower() != 'nenhuma dica extra desta vez.' and dica_extra.lower() != "n/a":
                    st.markdown(f"**Dica Extra:** {dica_extra}")

                # --- SEÇÃO ADICIONADA PARA LINKS DE BUSCA ---
                if gift_name and gift_name != 'N/A':
                    encoded_gift_name = urllib.parse.quote_plus(gift_name) # Codifica para URL
                    
                    st.markdown(f"""
                        <div style="margin-top: 10px; margin-bottom: 10px; padding: 8px; background-color: #f0f2f6; border-radius: 5px;">
                        <strong>🔗 Encontre este presente online:</strong>
                        <ul>
                            <li><a href="https://www.google.com/search?q={encoded_gift_name}&tbm=shop" target="_blank">Buscar no Google Shopping</a></li>
                            <li><a href="https://www.amazon.com.br/s?k={encoded_gift_name}" target="_blank">Buscar na Amazon.com.br</a></li>
                            <li><a href="https://lista.mercadolivre.com.br/{encoded_gift_name}" target="_blank">Buscar no Mercado Livre</a></li>
                            <li><a href="https://www.google.com/search?q={encoded_gift_name}" target="_blank">Buscar no Google (Geral)</a></li>
                        </ul>
                        </div>
                    """, unsafe_allow_html=True)
                # --- FIM DA SEÇÃO DE LINKS DE BUSCA ---
                
                st.markdown("---") # Separador entre sugestões
        else: # Este 'else' é para o caso de suggestions_to_display ser uma lista vazia após uma tentativa de busca
            if GOOGLE_API_KEY: # Só mostra este aviso se a API key está configurada, senão o outro aviso já cobre
                 # A mensagem de "Não consegui gerar sugestões..." já é mostrada no 'col1' se a API falhar.
                 # Podemos adicionar uma mensagem mais genérica aqui se 'suggestions_state' for vazio por outra razão.
                 st.info("Nenhuma sugestão encontrada com os critérios fornecidos ou a resposta da IA não pôde ser processada.")


st.sidebar.markdown("---")
st.sidebar.caption("Este app usa a API do Google Gemini.")
st.sidebar.markdown("Lembre-se que a qualidade das sugestões depende da IA e do prompt enviado.")