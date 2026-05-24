# JanAI RAG Assistant

Este 
 um assistente de IA que utiliza um modelo de linguagem (LLM) para responder a perguntas sobre documentos PDF fornecidos pelo usu
rio. A arquitetura 
 baseada em RAG (Retrieval-Augmented Generation), utilizando o Qdrant como banco de dados vetorial e o Streamlit para a interface do usu
rio.

## Pr
-requisitos

- Python 3.7+
- Um servi
 de LLM compat
vel com a API da OpenAI em execu

 (como o JanAI com o modelo gemma3:1b).

## Instala

1. **Clone o reposit
rio:**
   ```bash
   git clone https://github.com/seu-usuario/JanAI_RAG.git
   cd JanAI_RAG
   ```

2. **Crie e ative um ambiente virtual:**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # No Windows
   # source venv/bin/activate  # No macOS/Linux
   ```

3. **Instale as depend
cias:**
   ```bash
   pip install -r requirements.txt
   ```

## Execu

1. **Inicie o seu servi
 de LLM (por exemplo, JanAI) e certifique-se de que ele esteja acess
vel em `http://127.0.0.1:1337`**.

2. **Execute a aplica

 Streamlit:**
   ```bash
   streamlit run app.py
   ```

3. **Abra o seu navegador e acesse o endere
 fornecido pelo Streamlit (geralmente `http://localhost:8501`).**

## Como Usar

1. **Carregue um ou mais arquivos PDF** na barra lateral.
2. **Aguarde o processamento dos documentos.**
3. **Fa
 perguntas** sobre o conte
do dos seus documentos na caixa de bate-papo.
