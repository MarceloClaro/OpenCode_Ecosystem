import streamlit as st
import requests
import json

# Configuração
chat_id = "bc30a5b8340c11f083bac6652a1ab271"
api_key = "ragflow-k5NTg5ZDA4MzU3ODExZjA4OWU4YzY2NT"
endpoint = f"http://localhost/api/v1/chats_openai/{chat_id}/chat/completions"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

# Título
st.title("Assistente CNN - API Chat")

# Campo de entrada
user_input = st.text_area("Digite sua pergunta:", height=100)

# Botão de envio
if st.button("Enviar"):
    if not user_input.strip():
        st.warning("Digite algo antes de enviar.")
    else:
        body = {
            "model": "model",
            "messages": [{"role": "user", "content": user_input}],
            "stream": True
        }

        # Exibição do streaming
        with st.spinner("Aguardando resposta..."):
            response = requests.post(endpoint, headers=headers, data=json.dumps(body), stream=True)

            # Mostrar resposta limpa
            resposta = ""
            placeholder = st.empty()

            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode("utf-8").strip()
                    if decoded_line.startswith("data:"):
                        try:
                            data = json.loads(decoded_line[5:].strip())
                            delta = data.get("choices", [{}])[0].get("delta", {})
                            content = delta.get("content", "")
                            resposta += content
                            placeholder.markdown(resposta)
                        except Exception as e:
                            continue
