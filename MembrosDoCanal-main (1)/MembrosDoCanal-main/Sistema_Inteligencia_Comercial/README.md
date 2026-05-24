
# Agente de Estoque Inteligente com Gemini

Este projeto é uma aplicação web construída com Streamlit que utiliza o poder do modelo de linguagem Gemini do Google para analisar um banco de dados de produtos, identificar itens inativos e sugerir ações estratégicas para otimização de estoque.

## Funcionalidades

- **Análise de Inatividade:** Identifica produtos que não são vendidos há um período configurável (padrão: 90 dias).
- **Sugestões com IA:** Envia os dados dos produtos inativos para a API do Gemini para obter sugestões de ações (ex: promoções, combos, queima de estoque).
- **Interface Web Simples:** Utiliza o Streamlit para criar uma interface de usuário limpa e interativa.
- **Banco de Dados Simulado:** Acompanha um script para criar e popular um banco de dados SQLite com dados hipotéticos para fácil demonstração.

## Estrutura do Projeto

```
/Agente_De_Estoque
|-- database/               # Diretório para o banco de dados
|   |-- estoque.db
|-- .env                    # Arquivo para a chave da API do Google
|-- venv/                   # Ambiente virtual do Python
|-- agent.py                # Lógica principal do agente (análise e IA)
|-- app.py                  # Aplicação principal do Streamlit (Frontend)
|-- data_setup.py           # Script para criar e popular o banco de dados
|-- requirements.txt        # Dependências do Python
|-- README.md               # Este arquivo
```

## Como Executar

Siga os passos abaixo para configurar e rodar o projeto.

### 1. Pré-requisitos

- Python 3.8 ou superior
- Uma chave de API do **Google AI Studio**. Você pode obter uma gratuitamente [aqui](https://aistudio.google.com/app/apikey).

### 2. Clone o Repositório

```bash
git clone <URL_DO_REPOSITORIO>
cd Agente_De_Estoque
```

### 3. Crie o Ambiente Virtual e Instale as Dependências

É altamente recomendável usar um ambiente virtual para isolar as dependências do projeto.

**No Windows:**
```bash
# Criar o ambiente virtual
python -m venv venv

# Ativar o ambiente
venv\Scripts\activate

# Instalar as dependências
pip install -r requirements.txt
```

**No macOS/Linux:**
```bash
# Criar o ambiente virtual
python3 -m venv venv

# Ativar o ambiente
source venv/bin/activate

# Instalar as dependências
pip install -r requirements.txt
```

### 4. Configure a Chave da API

1.  Renomeie o arquivo `.env.example` para `.env` (se aplicável) ou crie um novo arquivo chamado `.env`.
2.  Abra o arquivo `.env` e adicione sua chave de API do Google:

    ```
    GOOGLE_API_KEY="SUA_API_KEY_AQUI"
    ```

    Substitua `SUA_API_KEY_AQUI` pela sua chave real.

### 5. Crie o Banco de Dados

Execute o script `data_setup.py` para criar o banco de dados `estoque.db` e populá-lo com dados de exemplo.

```bash
python data_setup.py
```

Você verá uma mensagem confirmando que o banco de dados foi criado.

### 6. Inicie a Aplicação

Com o ambiente virtual ainda ativado, inicie a aplicação Streamlit:

```bash
streamlit run app.py
```

A aplicação será aberta automaticamente no seu navegador padrão.

## Como Usar

1.  Abra a aplicação no seu navegador.
2.  Clique no botão **"🔍 Analisar Estoque Inativo"**.
3.  Aguarde enquanto o agente analisa os dados e consulta a IA.
4.  Os resultados serão exibidos na tela, mostrando cada produto inativo e as sugestões geradas pelo Gemini.
