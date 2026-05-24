import gradio as gr
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

def generate(prompt, temperature=1, max_tokens=32000):
    """Generate essay using Groq API"""
    client = Groq()
    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=temperature,
        max_completion_tokens=max_tokens,
        top_p=1,
        reasoning_effort="medium",
        stream=True,
        stop=None
    )
    
    response = ""
    for chunk in completion:
        content = chunk.choices[0].delta.content or ""
        response += content
        yield response

# Gradio interface
with gr.Blocks(title="AI Essay Generator") as demo:
    gr.Markdown("# AI Essay Generator")
    gr.Markdown("Generate essays using Groq's GPT-OSS-120B model")
    
    with gr.Row():
        with gr.Column():
            prompt_input = gr.Textbox(
                label="Prompt",
                placeholder="Write Essay about AI in 1000 words",
                value="Write Essay about AI in 1000 words",
                lines=3
            )
            
            with gr.Row():
                temperature_slider = gr.Slider(
                    minimum=0.1,
                    maximum=2.0,
                    value=1.0,
                    step=0.1,
                    label="Temperature"
                )
                max_tokens_slider = gr.Slider(
                    minimum=1000,
                    maximum=32000,
                    value=32000,
                    step=1000,
                    label="Max Tokens"
                )
            
            generate_btn = gr.Button("Generate", variant="primary")
        
        with gr.Column():
            output_text = gr.Textbox(
                label="Generated Essay",
                lines=20,
                interactive=False
            )
    
    generate_btn.click(
        fn=generate,
        inputs=[prompt_input, temperature_slider, max_tokens_slider],
        outputs=output_text
    )

if __name__ == "__main__":
    demo.launch()