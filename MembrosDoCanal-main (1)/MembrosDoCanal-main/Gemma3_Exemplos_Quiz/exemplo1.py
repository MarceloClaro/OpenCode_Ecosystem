
import ollama

def process_with_llm(questao):
    prompt = f"""
    Você é um assistente útil responda a seguinte questão: 
    
    Questão: "{questao}"
    
    Estruture o resultado como:
    - resposta:    
    """
    
    response = ollama.chat(
        model="gemma3:4b",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response["message"]["content"]

if __name__ == "__main__":
    questao = "Quem descobriu o Brasil?"
    if questao:
        structured_output = process_with_llm(questao)
        print("\nLLM:\n", structured_output)