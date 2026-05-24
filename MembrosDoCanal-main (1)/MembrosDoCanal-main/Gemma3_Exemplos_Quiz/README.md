# Quiz RAG - Gerador de Quiz com IA

Um aplicativo interativo que gera quizzes personalizados a partir de documentos ou imagens usando técnicas de Retrieval-Augmented Generation (RAG).

## 📋 Descrição

O Quiz RAG é uma aplicação Streamlit que permite aos usuários fazer upload de documentos (PDF) ou imagens e gerar automaticamente um quiz interativo baseado no conteúdo. O sistema utiliza modelos de IA para extrair texto, gerar perguntas de múltipla escolha relevantes e fornecer feedback personalizado.

## ✨ Funcionalidades

- **Upload de Conteúdo**: Suporte para arquivos PDF e imagens
- **Extração de Texto**: Extração automática de texto de PDFs e OCR para imagens
- **Geração de Perguntas**: Criação de perguntas de múltipla escolha baseadas no conteúdo
- **Interface Interativa**: Quiz com múltiplas fases e feedback imediato
- **Análise de Desempenho**: Avaliação do conhecimento do usuário ao final do quiz
- **Sugestões de Estudo**: Recomendações personalizadas baseadas nas respostas incorretas

## 🔧 Requisitos

- Python 3.8+
- Ollama (para execução local dos modelos de IA)
- Modelos necessários:
  - `gemma3:4b` (para geração de perguntas e verificação de respostas)
  - `nomic-embed-text:latest` (para geração de embeddings)

## 📦 Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/quiz-rag.git
   cd quiz-rag
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Instale e configure o Ollama:
   - Siga as instruções em [ollama.ai](https://ollama.ai) para instalar o Ollama
   - Baixe os modelos necessários:
     ```bash
     ollama pull gemma3:4b
     ollama pull nomic-embed-text:latest
     ```

## 🚀 Como Usar

1. Inicie o aplicativo:
   ```bash
   streamlit run quiz_rag.py
   ```

2. Acesse o aplicativo no navegador (geralmente em http://localhost:8501)

3. Faça upload de um documento PDF ou imagem

4. O sistema processará o conteúdo e gerará perguntas automaticamente

5. Responda às perguntas e receba feedback imediato

6. Ao final do quiz, veja sua análise de desempenho e sugestões de estudo

## 🧠 Como Funciona

1. **Processamento de Conteúdo**:
   - O texto é extraído do documento ou imagem
   - O conteúdo é dividido em pequenos chunks
   - Embeddings são gerados para cada chunk usando o modelo nomic-embed-text

2. **Geração de Perguntas**:
   - Chunks relevantes são selecionados usando busca semântica (FAISS)
   - Perguntas de múltipla escolha são geradas usando o modelo Gemma

3. **Interação e Avaliação**:
   - O usuário responde às perguntas
   - O sistema verifica as respostas e fornece feedback
   - Ao final, uma análise de desempenho e sugestões de estudo são geradas

## 📝 Personalização

Você pode personalizar o quiz modificando os seguintes parâmetros na classe `QuizState`:

- `questions_per_phase`: Número de perguntas por fase (padrão: 3)
- `total_phases`: Número total de fases (padrão: 2)

## 📄 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests. 