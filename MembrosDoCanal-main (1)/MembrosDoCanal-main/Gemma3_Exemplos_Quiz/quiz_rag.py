import streamlit as st
import base64
import io
from PIL import Image
import ollama
import faiss
import numpy as np
import PyPDF2
import random
import json

# A classe QuizState funciona como o "cérebro" do aplicativo, mantendo:
# Estado do jogo: fase atual, pontuação, perguntas respondidas
# Configurações: número de fases, perguntas por fase
# Dados do conteúdo: chunks de texto, embeddings, índice FAISS
# Estado da pergunta atual: pergunta sendo exibida no momento
class QuizState:
    def __init__(self):
        self.current_phase = 1
        self.score = 0
        self.questions_answered = 0
        self.current_question = None
        self.questions_per_phase = 3
        self.total_phases = 2
        self.content_embeddings = []
        self.content_chunks = []
        self.faiss_index = None

def encode_image_to_base64(image):
    """Converte uma imagem PIL para base64."""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def get_ocr_output_from_image(base64_image: str, model: str = "gemma3:4b") -> str:
    """Extrai texto de uma imagem usando OCR via Ollama."""
    prompt = f"""
    Analise esta imagem e extraia todo o texto visível nela.
    Retorne apenas o texto extraído, sem formatação adicional.
    
    [Imagem em base64: {base64_image}]
    """
    
    response = ollama.chat(
        model=model,
        messages=[{
            "role": "user",
            "content": prompt
        }]
    )
    
    return response.get('message', {}).get('content', '').strip()

def extract_text_from_pdf(pdf_file):
    """Extrai texto de um arquivo PDF."""
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def preprocess_content(text):
    """Pré-processa o conteúdo para melhor análise."""
    # Divide o texto em chunks menores
    chunks = [text[i:i+500] for i in range(0, len(text), 500)]
    return chunks

def generate_embedding(text: str, model: str = "nomic-embed-text:latest") -> np.ndarray:
    """Gera embeddings para o texto."""
    try:
        response = ollama.embeddings(model=model, prompt=text)
        if "embedding" in response:
            return np.array(response["embedding"], dtype=np.float32)
        return np.zeros((384,), dtype=np.float32)
    except Exception as e:
        print(f"Erro ao gerar embedding: {e}")
        return np.zeros((384,), dtype=np.float32)

def select_relevant_chunk(chunks: list, embeddings: list, faiss_index: faiss.Index) -> tuple:
    """Seleciona o chunk mais relevante para gerar uma pergunta."""
    # Gera embedding para a query
    query = "Crie uma pergunta de múltipla escolha sobre este conteúdo"
    query_embedding = generate_embedding(query)
    
    # Busca os chunks mais relevantes
    D, I = faiss_index.search(np.array([query_embedding]), 3)
    
    # Seleciona um dos chunks mais relevantes aleatoriamente
    selected_idx = random.choice(I[0])
    return chunks[selected_idx], selected_idx

def generate_question(content_chunk: str, model: str = "gemma3:4b") -> dict:
    """Gera uma pergunta baseada no conteúdo fornecido."""
    prompt = f"""
    Você é um gerador de perguntas de múltipla escolha.
    Crie uma pergunta baseada EXCLUSIVAMENTE no seguinte conteúdo:
    
    {content_chunk}
    
    IMPORTANTE: 
    1. A pergunta DEVE ser baseada apenas no conteúdo fornecido
    2. Responda APENAS com um objeto JSON válido no seguinte formato:
    {{
        "pergunta": "texto da pergunta",
        "opcoes": [
            "opção 1",
            "opção 2",
            "opção 3",
            "opção 4"
        ],
        "resposta_correta": 0,
        "explicacao": "explicação da resposta correta"
    }}
    
    Regras:
    1. A pergunta deve ser clara e objetiva
    2. Deve ter exatamente 4 opções
    3. resposta_correta deve ser um número entre 0 e 3
    4. Não inclua nenhum texto adicional além do JSON
    5. Todas as opções devem ser baseadas no conteúdo fornecido
    """
    
    try:
        response = ollama.chat(
            model=model,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        # Tenta extrair o JSON da resposta
        content = response.get('message', {}).get('content', '').strip()
        
        # Tenta encontrar o JSON na resposta
        start_idx = content.find('{')
        end_idx = content.rfind('}') + 1
        
        if start_idx == -1 or end_idx == 0:
            raise ValueError("Nenhum JSON encontrado na resposta")
            
        json_str = content[start_idx:end_idx]
        question = json.loads(json_str)
        
        # Verifica se a pergunta tem todos os campos necessários
        required_fields = ['pergunta', 'opcoes', 'resposta_correta', 'explicacao']
        if not all(field in question for field in required_fields):
            raise ValueError("Pergunta gerada não contém todos os campos necessários")
            
        # Verifica se tem exatamente 4 opções
        if len(question['opcoes']) != 4:
            raise ValueError("Pergunta deve ter exatamente 4 opções")
            
        # Verifica se o índice da resposta correta é válido
        if not (0 <= question['resposta_correta'] <= 3):
            raise ValueError("Índice da resposta correta deve estar entre 0 e 3")
            
        return question
        
    except Exception as e:
        print(f"Erro ao gerar pergunta: {e}")
        return None

def verify_answer(question: dict, user_answer: str, content_chunk: str, model: str = "gemma3:4b") -> bool:
    """Verifica se a resposta do usuário está correta."""
    prompt = f"""
    Verifique se a resposta do usuário está correta para a seguinte pergunta:
    
    Pergunta: {question['pergunta']}
    Resposta correta: {question['opcoes'][question['resposta_correta']]}
    Resposta do usuário: {user_answer}
    
    Contexto adicional:
    {content_chunk}
    
    Responda apenas com "true" ou "false".
    """
    
    response = ollama.chat(
        model=model,
        messages=[{
            "role": "user",
            "content": prompt
        }]
    )
    
    return response.get('message', {}).get('content', '').strip().lower() == "true"

def analyze_performance(quiz_state):
    """Analisa o desempenho do jogador e gera sugestões de estudo."""
    total_questions = quiz_state.total_phases * quiz_state.questions_per_phase
    score = quiz_state.score
    percentage = (score / total_questions) * 100
    
    # Categorias de desempenho
    if percentage >= 90:
        performance = "Excelente"
        message = "Você demonstrou um conhecimento excepcional sobre o conteúdo!"
    elif percentage >= 70:
        performance = "Bom"
        message = "Você tem um bom domínio do conteúdo, mas ainda há espaço para melhorias."
    elif percentage >= 50:
        performance = "Regular"
        message = "Você compreende os conceitos básicos, mas precisa aprofundar seu conhecimento."
    else:
        performance = "Precisa melhorar"
        message = "Recomendamos revisar o conteúdo com mais atenção para fortalecer seu conhecimento."
    
    return {
        "performance": performance,
        "message": message,
        "percentage": percentage,
        "score": score,
        "total": total_questions
    }

def generate_study_suggestions(content_chunks, wrong_answers, model="gemma3:4b"):
    """Gera sugestões de estudo baseadas nas respostas erradas."""
    if not wrong_answers:
        return "Você acertou todas as perguntas! Continue estudando para manter seu conhecimento atualizado."
    
    # Concatena os chunks para criar um contexto
    context = "\n\n".join(content_chunks[:5])  # Limita para não sobrecarregar
    
    # Cria um prompt para gerar sugestões
    prompt = f"""
    Com base no conteúdo abaixo e nas perguntas que o usuário errou, sugira 3-5 tópicos específicos para estudo adicional.
    
    CONTEÚDO:
    {context}
    
    PERGUNTAS QUE O USUÁRIO ERROU:
    {wrong_answers}
    
    Forneça sugestões específicas de estudo que ajudariam o usuário a compreender melhor esses tópicos.
    Inclua também uma breve explicação de por que cada tópico é importante.
    """
    
    response = ollama.chat(
        model=model,
        messages=[{
            "role": "user",
            "content": prompt
        }]
    )
    
    return response.get('message', {}).get('content', '').strip()

def create_quiz_interface():
    """Cria a interface do quiz usando Streamlit."""
    st.title("Quiz com IA 🎯")
    
    # Inicializa o estado do quiz
    if "quiz_state" not in st.session_state:
        st.session_state.quiz_state = QuizState()
        st.session_state.wrong_answers = []
    
    # Upload de arquivo
    if not st.session_state.quiz_state.content_chunks:
        st.write("Bem-vindo ao Quiz com IA! Faça upload de um documento ou imagem para começar.")
        uploaded_file = st.file_uploader("Escolha um arquivo", type=["pdf", "png", "jpg", "jpeg"])
        
        if uploaded_file is not None:
            with st.spinner("Processando o conteúdo..."):
                # Extrai texto do arquivo
                if uploaded_file.type == "application/pdf":
                    text = extract_text_from_pdf(uploaded_file)
                else:
                    # Para imagens, usa o OCR do RAG original
                    image = Image.open(uploaded_file)
                    base64_image = encode_image_to_base64(image)
                    text = get_ocr_output_from_image(base64_image)
                
                # Pré-processa o conteúdo
                chunks = preprocess_content(text)
                st.session_state.quiz_state.content_chunks = chunks
                
                # Gera embeddings
                embeddings = [generate_embedding(chunk) for chunk in chunks]
                st.session_state.quiz_state.content_embeddings = embeddings
                
                # Cria índice FAISS
                embedding_dim = embeddings[0].shape[0]
                index = faiss.IndexFlatL2(embedding_dim)
                index.add(np.array(embeddings))
                st.session_state.quiz_state.faiss_index = index
                
                st.rerun()
    
    # Verifica se o jogo foi concluído
    game_completed = (st.session_state.quiz_state.current_phase == st.session_state.quiz_state.total_phases and 
                     st.session_state.quiz_state.questions_answered >= st.session_state.quiz_state.questions_per_phase)
    
    # Tela de resultados finais
    if game_completed:
        st.balloons()
        st.success("🎉 Parabéns! Você completou todas as fases do quiz! 🎉")
        
        # Análise de desempenho
        analysis = analyze_performance(st.session_state.quiz_state)
        
        # Exibe resultados
        st.header("Análise de Desempenho")
        st.subheader(f"Desempenho: {analysis['performance']}")
        st.write(analysis['message'])
        
        # Gráfico de pontuação
        st.write(f"Pontuação final: {analysis['score']}/{analysis['total']} ({analysis['percentage']:.1f}%)")
        
        # Progresso visual
        st.progress(analysis['percentage'] / 100)
        
        # Sugestões de estudo
        st.header("Sugestões de Estudo")
        
        if 'study_suggestions' not in st.session_state:
            with st.spinner("Gerando sugestões de estudo personalizadas..."):
                st.session_state.study_suggestions = generate_study_suggestions(
                    st.session_state.quiz_state.content_chunks,
                    st.session_state.wrong_answers
                )
        
        st.write(st.session_state.study_suggestions)
        
        # Opção para reiniciar
        if st.button("Jogar Novamente"):
            st.session_state.quiz_state = QuizState()
            st.session_state.wrong_answers = []
            if 'study_suggestions' in st.session_state:
                del st.session_state.study_suggestions
            st.rerun()
    
    # Interface do quiz (durante o jogo)
    elif st.session_state.quiz_state.content_chunks:
        # Status do quiz
        st.sidebar.title("Status do Quiz")
        st.sidebar.write(f"Fase: {st.session_state.quiz_state.current_phase}/{st.session_state.quiz_state.total_phases}")
        st.sidebar.write(f"Pontuação: {st.session_state.quiz_state.score}")
        st.sidebar.write(f"Perguntas respondidas: {st.session_state.quiz_state.questions_answered}/{st.session_state.quiz_state.questions_per_phase}")
        
        # Gera nova pergunta se necessário
        if st.session_state.quiz_state.current_question is None:
            # Seleciona um chunk relevante
            chunk, chunk_idx = select_relevant_chunk(
                st.session_state.quiz_state.content_chunks,
                st.session_state.quiz_state.content_embeddings,
                st.session_state.quiz_state.faiss_index
            )
            
            # Gera pergunta
            with st.spinner("Gerando pergunta..."):
                question = generate_question(chunk)
                if question:  # Verifica se a pergunta foi gerada com sucesso
                    st.session_state.quiz_state.current_question = {
                        "question": question,
                        "chunk": chunk,
                        "chunk_idx": chunk_idx
                    }
                else:
                    st.error("Erro ao gerar pergunta. Tente novamente.")
                    st.rerun()
        
        # Exibe a pergunta atual
        if st.session_state.quiz_state.current_question:
            question = st.session_state.quiz_state.current_question["question"]
            chunk = st.session_state.quiz_state.current_question["chunk"]
            
            # Mostra o conteúdo base da pergunta
            with st.expander("Ver conteúdo base da pergunta"):
                st.write(chunk)
            
            st.subheader(f"Pergunta {st.session_state.quiz_state.questions_answered + 1}")
            st.write(question["pergunta"])
            
            # Opções de resposta
            user_answer = st.radio("Escolha sua resposta:", question["opcoes"])
            
            # Botão para verificar resposta
            if st.button("Verificar Resposta"):
                is_correct = verify_answer(
                    question,
                    user_answer,
                    chunk
                )
                
                if is_correct:
                    st.success("Correto! 🎉")
                    st.session_state.quiz_state.score += 1
                    st.write(f"Explicação: {question['explicacao']}")
                else:
                    st.error("Incorreto! 😢")
                    correct_answer = question['opcoes'][question['resposta_correta']]
                    st.write(f"A resposta correta era: {correct_answer}")
                    st.write(f"Explicação: {question['explicacao']}")
                    
                    # Registra a resposta errada para sugestões de estudo
                    st.session_state.wrong_answers.append({
                        "pergunta": question['pergunta'],
                        "resposta_correta": correct_answer,
                        "explicacao": question['explicacao']
                    })
                
                st.session_state.quiz_state.questions_answered += 1
                st.session_state.quiz_state.current_question = None
                
                # Verifica se a fase foi concluída
                if st.session_state.quiz_state.questions_answered >= st.session_state.quiz_state.questions_per_phase:
                    if st.session_state.quiz_state.current_phase < st.session_state.quiz_state.total_phases:
                        st.session_state.quiz_state.current_phase += 1
                        st.session_state.quiz_state.questions_answered = 0
                
                st.rerun()

if __name__ == "__main__":
    create_quiz_interface() 