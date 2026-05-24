import gradio as gr
from groq import Groq
from dotenv import load_dotenv
from typing import Generator, Tuple

# Carrega variáveis de ambiente (GROQ_API_KEY)
load_dotenv()

# Modelo 20B na Groq
GROQ_MODEL = "openai/gpt-oss-20b"

# ---------- Prompts base para cada modo ----------
PROMPT_IDEIAS = """Você é um estrategista de conteúdo para YouTube.
Gere 10 IDEIAS de vídeos sobre: "{tema}".
Para cada ideia, traga:
- Título atrativo (<= 60 caracteres)
- Público-alvo
- Por que é interessante (1 frase)
- Gancho de abertura (1 frase)
Formato:
1) Título — Público — Por quê — Gancho"""

PROMPT_ROTEIRO = """Você é um roteirista. Crie um ROTEIRO para um vídeo sobre: "{tema}".
Formato:
# Gancho (20-30s)
# Contexto (o que e por quê)
# Tópicos principais (bullet points)
# Demonstração / exemplos (se aplicável)
# Objeções e respostas (2-3)
# CTA (claro e específico)
# Falas sugeridas (texto natural, 2-3 linhas por seção)
Tom: claro, didático, ritmo dinâmico."""

PROMPT_CAPITULOS = """Gere CAPÍTULOS e CORTES CURTOS para o tema: "{tema}".
1) Capítulos com timestamps ESTIMADOS (mm:ss) e título conciso.
2) 3 cortes curtos (<= 30s) com:
   - Título do corte
   - Legenda/overlay em 1 linha
   - Prompt de thumbnail (descrição visual)
   - Hook de 1 frase para os 2 primeiros segundos.
Entregue em Markdown limpo."""

# ---------- Cliente ----------
def get_client() -> Groq:
    # Usa GROQ_API_KEY do .env automaticamente
    return Groq()

# ---------- Função de geração com streaming ----------
def stream_completion(
    system_prompt: str,
    user_prompt: str,
    temperature: float,
    max_tokens: int
) -> Generator[str, None, None]:
    """
    Gera saída incremental (stream) concatenando em buffer
    e emitindo texto parcial para o componente Markdown do Gradio.
    """
    client = get_client()
    completion = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": system_prompt.strip()
                if system_prompt
                else "Você é um assistente útil e conciso."
            },
            {"role": "user", "content": user_prompt.strip()},
        ],
        temperature=temperature,
        max_tokens=max_tokens,   # <- nome correto no SDK
        top_p=1,
        stream=True,
    )
    buf = ""
    for chunk in completion:
        delta = (chunk.choices[0].delta.content or "")
        if delta:
            buf += delta
            # Emite o buffer acumulado (efeito de streaming no Markdown)
            yield buf

# ---------- Handlers dos modos (cada um 'yield from' o streamer) ----------
def gerar_ideias(tema: str, system_prompt: str, temperature: float, max_tokens: int):
    prompt = PROMPT_IDEIAS.format(tema=tema)
    yield from stream_completion(system_prompt, prompt, temperature, max_tokens)

def gerar_roteiro(tema: str, system_prompt: str, temperature: float, max_tokens: int):
    prompt = PROMPT_ROTEIRO.format(tema=tema)
    yield from stream_completion(system_prompt, prompt, temperature, max_tokens)

def gerar_capitulos(tema: str, system_prompt: str, temperature: float, max_tokens: int):
    prompt = PROMPT_CAPITULOS.format(tema=tema)
    yield from stream_completion(system_prompt, prompt, temperature, max_tokens)

def laboratorio_temperatura(
    tema: str,
    system_prompt: str,
    max_tokens: int
) -> Tuple[str, str, str]:
    """
    Gera 3 respostas (sem stream) fixando top_p=1 e variando temperatura,
    para comparação didática em aula.
    """
    client = get_client()
    temps = [0.2, 0.7, 1.3]
    outputs = []
    for t in temps:
        chat = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt.strip()
                    if system_prompt
                    else "Você é um assistente útil e conciso."
                },
                {
                    "role": "user",
                    "content": (
                        f"Explique em 1 parágrafo sobre: {tema}. "
                        "Foque em clareza e objetividade."
                    ),
                },
            ],
            temperature=t,
            max_tokens=max_tokens,  # <- nome correto aqui também
            top_p=1,
            stream=False,
        )
        outputs.append(chat.choices[0].message.content)
    # (baixa, média, alta)
    return tuple(outputs)  # type: ignore[return-value]

# ---------- UI ----------
with gr.Blocks(title="Estúdio de Conteúdo — GPT-OSS 20B") as demo:
    gr.Markdown(
        "## 🎬 Estúdio de Conteúdo com **GPT-OSS-20B** (Groq)\n"
        "Gere ideias, roteiros, capítulos & shorts — e compare temperaturas ao vivo."
    )

    with gr.Row():
        system_prompt = gr.Textbox(
            label="System prompt (opcional)",
            placeholder="Defina o comportamento do modelo (ex.: 'Você é um roteirista premiado...')",
            lines=2,
        )

    with gr.Row():
        temperature = gr.Slider(0.0, 2.0, value=0.8, step=0.1, label="Temperature")
        max_tokens = gr.Slider(256, 32768, value=1500, step=128, label="Max tokens")

    with gr.Tab("💡 Ideias"):
        tema_ideias = gr.Textbox(
            label="Tema do vídeo",
            placeholder="Ex.: Como usar GPT-OSS 20B para estudar"
        )
        out_ideias = gr.Markdown()
        btn_ideias = gr.Button("Gerar ideias", variant="primary")
        btn_ideias.click(
            gerar_ideias,
            inputs=[tema_ideias, system_prompt, temperature, max_tokens],
            outputs=out_ideias,
        )

    with gr.Tab("📝 Roteiro"):
        tema_roteiro = gr.Textbox(
            label="Tema do vídeo",
            placeholder="Ex.: Tutorial prático de GPT-OSS 20B"
        )
        out_roteiro = gr.Markdown()
        btn_roteiro = gr.Button("Gerar roteiro", variant="primary")
        btn_roteiro.click(
            gerar_roteiro,
            inputs=[tema_roteiro, system_prompt, temperature, max_tokens],
            outputs=out_roteiro,
        )

    with gr.Tab("🎯 Capítulos & Shorts"):
        tema_caps = gr.Textbox(
            label="Tema do vídeo",
            placeholder="Ex.: 7 ideias de uso para GPT-OSS 20B"
        )
        out_caps = gr.Markdown()
        btn_caps = gr.Button("Gerar capítulos & shorts", variant="primary")
        btn_caps.click(
            gerar_capitulos,
            inputs=[tema_caps, system_prompt, temperature, max_tokens],
            outputs=out_caps,
        )

    with gr.Tab("🧪 Laboratório de Temperatura"):
        tema_lab = gr.Textbox(
            label="Tema (um parágrafo de explicação)",
            placeholder="Ex.: O que é GPT-OSS 20B?"
        )
        col_baixa = gr.Markdown(label="Temperatura 0.2 (mais estável)")
        col_media = gr.Markdown(label="Temperatura 0.7 (equilíbrio)")
        col_alta = gr.Markdown(label="Temperatura 1.3 (mais criativa)")
        btn_lab = gr.Button("Comparar respostas")
        btn_lab.click(
            laboratorio_temperatura,
            inputs=[tema_lab, system_prompt, max_tokens],
            outputs=[col_baixa, col_media, col_alta],
        )

if __name__ == "__main__":
    # A app abre em http://127.0.0.1:7860
    # .queue() melhora streaming e estabilidade em produção
    demo.queue().launch()

