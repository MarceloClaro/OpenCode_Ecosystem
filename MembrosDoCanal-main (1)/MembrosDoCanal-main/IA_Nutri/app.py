import io
import base64
import pandas as pd
from groq import Groq
import streamlit as st
from PIL import Image
from web import search_web

# 🔑 Substitua pela sua chave de API do Groq
KEY = "sua chave groq"

# ------------------------ Função para Processar a Imagem ------------------------

def process_image(image):
    """Processa a imagem, envia para o modelo e retorna o texto extraído."""
    
    # Converte a imagem para bytes
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    image_bytes = buffer.getvalue()

    # Codifica para Base64
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    data_uri = f"data:image/jpeg;base64,{image_base64}"
    
    # Mensagem para o modelo
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Extraia as informações nutricionais da imagem e retorne como uma tabela."},
                {"type": "image_url", "image_url": {"url": data_uri}}
            ]
        }
    ]

    # Chamada ao modelo Groq
    client = Groq(api_key=KEY)
    completion = client.chat.completions.create(
        model="llama-3.2-90b-vision-preview",
        messages=messages,
        temperature=0,
        max_completion_tokens=1024,
        top_p=1,
        stream=False,
        stop=None,
    )

    # Extrai a resposta do modelo
    return completion.choices[0].message.content

# ------------------------ Função para Extrair a Tabela ------------------------

def extract_table_from_text(text):
    """Extrai a parte tabular do texto da resposta do modelo."""
    
    lines = text.split("\n")
    table_lines = []
    table_started = False

    for line in lines:
        if "|" in line:  # Detecta início da tabela
            table_started = True
            table_lines.append(line.strip())
        elif table_started:  # Para quando a tabela termina
            break

    return "\n".join(table_lines) if table_lines else None

# ------------------------ Função para Converter para DataFrame ------------------------

def parse_markdown_table(markdown_table):
    """Converte a tabela Markdown para um DataFrame Pandas."""
    
    if not markdown_table:
        return None

    lines = [line.strip() for line in markdown_table.split("\n") if line.strip()]
    if len(lines) < 2:
        return None

    headers = [cell.strip() for cell in lines[0].split("|") if cell.strip()]
    rows = []

    for line in lines[1:]:
        if "|" not in line:
            continue
        row = [cell.strip() for cell in line.split("|") if cell.strip()]
        if len(row) == len(headers):
            rows.append(row)

    return pd.DataFrame(rows, columns=headers) if rows else None

# ------------------------ Função para Avaliação Nutricional ------------------------

def fetch_nutritional_restrictions(health_profile):
    """Busca na web informações sobre restrições nutricionais com base no perfil de saúde."""
    conditions = health_profile.get("condições", [])
    search_results = []
    
    for condition in conditions:
        query = f"restrições nutricionais para {condition}"
        results = search_web(query)
        search_results.append(f"### {condition}:\n{results}")
    
    return "\n\n".join(search_results)

# ------------------------ Função para Avaliação Nutricional ------------------------

def evaluate_nutrition(nutritional_info, health_profile):
    """Avalia se o alimento é apropriado para o perfil de saúde do usuário."""
    
    # Converte o perfil de saúde em string formatada
    health_profile_str = "\n".join(f"{chave}: {valor}" for chave, valor in health_profile.items())
    
    # Busca restrições nutricionais na web
    nutritional_restrictions = fetch_nutritional_restrictions(health_profile)
    
    # Construção do prompt estruturado para o modelo
    prompt = (
        f"### Informações Nutricionais Extraídas:\n{nutritional_info}\n\n"
        f"### Perfil de Saúde do Usuário:\n{health_profile_str}\n\n"
        f"### Restrições Nutricionais Encontradas:\n{nutritional_restrictions}\n\n"
        "Com base nesses dados, analise se esse alimento é adequado para o usuário.\n"
        "Se for adequado, diga '✅ Sim' e explique brevemente. Se não for adequado, diga '🚫 Não' e explique o motivo."
    )
    
    # Chamada ao modelo
    client = Groq(api_key=KEY)
    completion = client.chat.completions.create(
        model="deepseek-r1-distill-llama-70b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6,
        max_completion_tokens=1024,
        top_p=0.95,
        stream=False,
        stop=None,
    )

    # Extrai a resposta do modelo
    response = completion.choices[0].message.content

    # Tratamento de erro: Se a resposta for vazia ou inesperada
    if not response or len(response) < 10:
        return "⚠️ Não foi possível gerar uma resposta válida. Tente novamente."

    return response


# ------------------------ Interface no Streamlit ------------------------

def main():
    st.title("📊 Avaliação Nutricional do Alimento")
    st.write("📸 Envie uma foto do rótulo nutricional para extrair as informações e avaliar se o alimento é adequado para o seu perfil de saúde.")

    # Sidebar para entrada de dados do perfil de saúde
    st.sidebar.header("🩺 Perfil de Saúde")
    idade = st.sidebar.number_input("Idade", value=30, min_value=1)
    genero = st.sidebar.selectbox("Gênero", ["Masculino", "Feminino", "Outro"])
    condicoes = st.sidebar.multiselect("Condições de saúde", ["Hipertensão", "Diabetes", "Obesidade", "Alergia", "Pré-Diabetes"])

    # Criar dicionário do perfil de saúde
    health_profile = {"idade": idade, "gênero": genero, "condições": condicoes}

    # Upload da imagem
    uploaded_file = st.file_uploader("📤 Envie a imagem do rótulo", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="📷 Imagem enviada", use_container_width=True)

        with st.spinner("⏳ Processando a imagem..."):
            raw_text = process_image(image)

        #st.subheader("📜 Texto Retornado pelo Modelo")
        #st.text(raw_text)

        # Extração da tabela
        table_markdown = extract_table_from_text(raw_text)
        if table_markdown:
            st.subheader("📊 Tabela Extraída")
            df = parse_markdown_table(table_markdown)
            if df is not None:
                st.table(df)
            else:
                st.error("❌ Não foi possível converter a tabela.")
        else:
            st.warning("⚠️ Nenhuma tabela foi detectada.")

        # Avaliação nutricional
        with st.spinner("🔍 Analisando o alimento..."):
            advice = evaluate_nutrition(raw_text, health_profile)

        st.subheader("✅ Conclusão sobre o Alimento")
        st.success(advice)

if __name__ == "__main__":
    main()
