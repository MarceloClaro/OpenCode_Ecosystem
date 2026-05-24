# Assistente de IA para Perguntas e Respostas em Documentos PDF

Este projeto é um assistente de IA que utiliza um modelo de linguagem (LLM) para responder a perguntas sobre documentos PDF fornecidos pelo usuário. A solução é baseada em RAG (Retrieval-Augmented Generation), utilizando o LLM Gemini 1.5 Flash, o banco de dados vetorial Qdrant e o Streamlit para a interface do usuário.

## Funcionalidades

- Upload de um ou mais arquivos PDF.
- Extração de texto dos documentos.
- Divisão do texto em pedaços (chunks) para processamento.
- Geração de embeddings (vetores) para os pedaços de texto usando o Gemini.
- Armazenamento e indexação dos embeddings no Qdrant.
- Interface de chat para o usuário fazer perguntas sobre os documentos.
- Geração de respostas com base no conteúdo dos PDFs, utilizando o Gemini.

## Tecnologias Utilizadas

- **Frontend:** Streamlit
- **LLM:** Google Gemini 2.0 Flash
- **Banco de Dados Vetorial:** Qdrant
- **Processamento de PDF:** PyPDF2
- **Orquestração:** LangChain
- `Pillow` e `Pytesseract` (para imagens)

## Pré-requisitos

- Python 3.8 ou superior
- Uma chave de API do Google Gemini. Você pode obter uma em [https://aistudio.google.com/](https://aistudio.google.com/)

## Instalação

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/seu-usuario/seu-repositorio.git
   cd seu-repositorio
   ```

2. **Crie e ative um ambiente virtual:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # No Windows, use: .venv\Scripts\activate
   ```

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure sua chave de API:**
   - Crie um arquivo chamado `.env` na raiz do projeto.
   - Adicione a seguinte linha ao arquivo `.env`:
     ```
     GOOGLE_API_KEY="SUA_CHAVE_DE_API_AQUI"
     ```

## Execução

Para iniciar a aplicação, execute o seguinte comando no terminal:

```bash
streamlit run app.py
```

A aplicação será aberta no seu navegador. Você poderá fazer o upload dos seus arquivos PDF, processá-los e, em seguida, fazer perguntas sobre o conteúdo deles.
