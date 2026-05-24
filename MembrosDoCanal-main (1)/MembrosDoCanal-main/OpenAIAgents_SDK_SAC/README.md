# Sistema Integrado de Suporte e Triagem

Este projeto contém sistems baseado em Agentes de IA:

1. **Sistema de Suporte ao Cliente** - Classifica e direciona consultas de clientes para especialistas

## Requisitos

- Python 3.8+
- Streamlit
- OpenAI API (via Ollama)
- Outras dependências (veja `requirements.txt`)

## Configuração

1. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

2. Verifique se o Ollama está instalado e rodando com o modelo Llama 3.1
   ```
   ollama pull llama3.1:8b
   ```

3. Execute o backend do Ollama
   ```
   ollama serve
   ```

## Executando os Sistemas

### Sistema de Suporte ao Cliente

```
streamlit run frontend_suporte.py
```

O sistema de suporte classifica consultas de clientes e direciona para os especialistas:
- Suporte Técnico
- Suporte de Faturamento
- Tratamento de Reclamações
- Suporte Geral



## Estrutura do Projeto

- `frontend_suporte.py` - Interface do sistema de suporte ao cliente
- `backend_suporte.py` - Lógica dos agentes de suporte


