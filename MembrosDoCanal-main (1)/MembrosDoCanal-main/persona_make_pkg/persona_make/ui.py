import json
import os
import gradio as gr
from typing import Optional
from .constants import STYLE_HINTS
from .storage import (list_personas, load_persona, save_persona_atomic, slugify,
                      unique_slug, save_avatar_file)
from .persona import (build_persona, clickable_sources_md, try_json_loads,
                      validate_persona, chat_with_persona)
from .llm import SUPPORTED_MODELS

# ---- helpers ----
def get_avatar_path(slug: str):
    data = load_persona(slug)
    p = (data or {}).get("avatar_path")
    return p if (p and os.path.exists(p)) else None

def set_chatbot_avatar(slug: str):
    path = get_avatar_path(slug)
    return gr.update(avatar_images=(None, path))

# ---- callbacks ----
def create_and_save_persona(subject: str, region_lang: str, web_search: bool,
                            style_key: str, model: str, avatar_file: str):
    if not subject.strip():
        choices = list_personas()
        return (gr.update(value=""),
                gr.update(choices=choices),
                gr.update(choices=choices),
                "Informe um nome ou personagem.",
                None)

    raw_text, warn = build_persona(subject, region_lang, web_search, style_key, model)
    try:
        data = try_json_loads(raw_text)
        errs = validate_persona(data)
        if errs:
            choices = list_personas()
            return (gr.update(value=""), gr.update(choices=choices), gr.update(choices=choices),
                    " | ".join(errs), None)

        base = slugify(data.get("name") or subject)
        slug = unique_slug(base)
        saved_path = save_persona_atomic(slug, data)

        avatar_path = save_avatar_file(slug, avatar_file)
        if avatar_path:
            data["avatar_path"] = avatar_path
            save_persona_atomic(slug, data)

        msg = f"Persona salva como: {slug}\nArquivo: {saved_path}"
        links_md = clickable_sources_md(data)
        if links_md:
            msg += f"\n\n**Fontes detectadas:**\n{links_md}"
        choices = list_personas()
        return (
            json.dumps(data, ensure_ascii=False, indent=2),
            gr.update(choices=choices, value=slug),
            gr.update(choices=choices, value=slug),
            msg,
            avatar_path or None,
        )
    except Exception as e:
        preview = (raw_text or "")[:600]
        choices = list_personas()
        msg = f"Erro ao criar persona: {e}"
        if preview:
            msg += f"\nPrévia:\n{preview}"
        return (gr.update(value=""), gr.update(choices=choices), gr.update(choices=choices), msg, None)

def load_persona_ui(slug: str):
    data = load_persona(slug)
    return json.dumps(data, ensure_ascii=False, indent=2) if data else ""

def save_manual_edits(current_json: str, current_slug: Optional[str]):
    try:
        data = json.loads(current_json)
        errs = validate_persona(data)
        if errs:
            return " | ".join(errs), gr.update(), gr.update()
        target = slugify(data.get("name") or current_slug or "persona")
        if current_slug and target == current_slug:
            slug = current_slug
        else:
            slug = unique_slug(target)
        saved_path = save_persona_atomic(slug, data)
        msg = f"Alterações salvas em: {slug}\nArquivo: {saved_path}"
        links_md = clickable_sources_md(data)
        if links_md:
            msg += f"\n\n**Fontes detectadas:**\n{links_md}"
        choices = list_personas()
        return msg, gr.update(choices=choices, value=slug), gr.update(choices=choices, value=slug)
    except Exception as e:
        return f"Erro ao salvar alterações: {e}", gr.update(), gr.update()

# ---- app ----
def build_app():
    with gr.Blocks(title="Persona Make — GPT-5", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# Persona Make — GPT-5\nCrie personas de celebridades, personagens e converse com eles.")

        with gr.Tab("Criar Persona"):
            subject = gr.Textbox(label="Quem/qual personagem?")
            with gr.Row():
                region_lang = gr.Dropdown(["pt-BR"], value="pt-BR", label="Idioma")
                web_search = gr.Checkbox(False, label="Usar busca na web (preview)")
                style_create = gr.Dropdown(list(STYLE_HINTS.keys()), value="Equilibrado", label="Estilo preferido")
                model_create = gr.Dropdown(SUPPORTED_MODELS, value="gpt-5", label="Modelo (criar)")

            avatar_upload = gr.Image(label="Foto do persona (opcional)", type="filepath")

            build_btn = gr.Button("Criar persona")
            persona_preview = gr.Code(label="Perfil JSON", value="")
            status = gr.Markdown("")
            personas_list = gr.Dropdown(label="Personas salvas", choices=list_personas())
            save_edits_btn = gr.Button("Salvar alterações do JSON atual")
            refresh_btn = gr.Button("Recarregar lista (todas as abas)")

        with gr.Tab("Chat com a Persona"):
            chat_persona = gr.Dropdown(label="Escolha a persona", choices=list_personas())
            style_chat = gr.Dropdown(list(STYLE_HINTS.keys()), value="Equilibrado", label="Estilo no chat")
            model_chat = gr.Dropdown(SUPPORTED_MODELS, value="gpt-5", label="Modelo (chat)")

            persona_avatar = gr.Image(label="Avatar da persona", interactive=False, height=220)

            chat_box = gr.Chatbot(height=420)
            gr.Markdown("### Converse com a persona")

            gr.ChatInterface(
                fn=lambda m, h, p, s, mdl: chat_with_persona(m, h,
                                                             json.dumps(load_persona(p) or {}, ensure_ascii=False),
                                                             s, mdl),
                additional_inputs=[chat_persona, style_chat, model_chat],
                chatbot=chat_box,
                description="Responde no estilo da persona, com salvaguardas.",
                textbox=gr.Textbox(placeholder="Digite sua pergunta...")
            )

        # eventos
        build_btn.click(
            fn=create_and_save_persona,
            inputs=[subject, region_lang, web_search, style_create, model_create, avatar_upload],
            outputs=[persona_preview, personas_list, chat_persona, status, persona_avatar]
        ).then(
            set_chatbot_avatar, inputs=[chat_persona], outputs=[chat_box]
        )

        personas_list.change(load_persona_ui, inputs=[personas_list], outputs=[persona_preview])

        save_edits_btn.click(
            fn=save_manual_edits,
            inputs=[persona_preview, personas_list],
            outputs=[status, personas_list, chat_persona]
        )

        def _refresh_choices():
            choices = list_personas()
            return gr.update(choices=choices), gr.update(choices=choices)

        refresh_btn.click(_refresh_choices, outputs=[personas_list, chat_persona])

        chat_persona.change(get_avatar_path, inputs=[chat_persona], outputs=[persona_avatar])
        chat_persona.change(set_chatbot_avatar, inputs=[chat_persona], outputs=[chat_box])

    return demo
