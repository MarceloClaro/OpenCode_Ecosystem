# Persona Make — GPT-5

Aplicação Gradio para **criar personas**, **anexar avatar** (imagem) e **conversar** com elas escolhendo o modelo entre `gpt-5`, `gpt-5-mini` e `gpt-5-nano` (com **fallback silencioso**).

## ✨ Recursos
- Criação de persona em **JSON estruturado** (name, summary, traits, etc.).
- **Upload de avatar** na criação; preview no chat e **avatar nas mensagens** do bot.
- Seleção de **modelo** na criação e no chat.
- **Fallback automático**: tenta o modelo escolhido; se falhar, reexecuta sem web; depois `gpt-5-mini` e `gpt-5-nano` (sem exibir avisos).
- Edição manual do JSON e recarregamento de personas salvas.

---

## ⚙️ Requisitos
- **Python 3.9+** (recomendado 3.10/3.11)
- **API key da OpenAI**
- Pip atualizado: `python -m pip install --upgrade pip`

---

## 🧩 Instalação

> Execute **somente** os comandos do seu sistema operacional.

### Windows (PowerShell)
```powershell
# 1) Entre na pasta do projeto (após extrair o .zip)
cd caminho\para\persona_make_avatar_pkg_v2

# 2) Crie e ative o ambiente virtual
python -m venv .venv
.\.venv\Scripts\Activate

# 3) Instale as dependências
pip install -r .\requirements.txt

# 4) Defina a chave (opção A - arquivo .env na raiz)
# Crie um arquivo .env com a linha abaixo:
# OPENAI_API_KEY=SUA_CHAVE_AQUI

# (opção B - variável de ambiente do usuário)
setx OPENAI_API_KEY "SUA_CHAVE_AQUI"
```

### macOS / Linux (bash/zsh)
```bash
cd /caminho/para/persona_make_avatar_pkg_v2
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Arquivo .env na raiz do projeto:
echo "OPENAI_API_KEY=SUA_CHAVE_AQUI" > .env
```

---

## 🚀 Executando
Com o ambiente virtual **ativado**:
```bash
python -m persona_make.main
```
Abra o link exibido (ex.: `http://127.0.0.1:7860`).

> Porta diferente? Ajuste no `app.launch()` em `main.py` ou execute com argumentos do Gradio (`--server.port 8080`).

---

## 🧠 Como usar

1. **Criar Persona**
   - Preencha **Quem/qual personagem?** e (opcional) **Usar busca na web**.
   - Escolha **Estilo preferido** e **Modelo (criar)**.
   - (Opcional) **Envie um avatar** (imagem).
   - Clique **Criar persona** → o **JSON** aparece e a persona é salva em `personas/`.

2. **Chat com a Persona**
   - Selecione a persona em **Escolha a persona**.
   - Escolha **Estilo no chat** e **Modelo (chat)**.
   - O **avatar** aparece acima e nas **mensagens do bot**.
   - Envie mensagens no campo de texto.

3. **Editar Persona**
   - Na aba “Criar Persona”: selecione em **Personas salvas**, edite o JSON e **Salvar alterações do JSON atual**.

> **Trocar avatar depois**: sobrescreva o arquivo correspondente em `personas_media/` (mesmo nome do slug da persona) ou recadastre a persona subindo uma nova imagem.

---

## 🗂️ Estrutura do projeto
```
persona_make_avatar_pkg_v2/
├─ requirements.txt          # Dependências (Gradio, python-dotenv, openai)
├─ personas/                 # (gerado) JSONs de personas salvas
├─ personas_media/           # (gerado) imagens de avatar (slug.ext)
└─ persona_make/             # Pacote Python
   ├─ __init__.py            # Marca o pacote
   ├─ main.py                # Ponto de entrada: cria e lança o app Gradio
   ├─ ui.py                  # Interface (abas, widgets, callbacks, Chatbot com avatar)
   ├─ persona.py             # Prompts/fluxo para criar persona e conversar; validações
   ├─ llm.py                 # Chamadas à OpenAI + extração robusta 
   ├─ storage.py             # Persistência de JSON e mídia (avatar), utilidades de arquivo
   └─ constants.py           # Templates de prompts, regras, estilos de resposta
```

### Finalidade de cada arquivo
- **`requirements.txt`**: bibliotecas necessárias do projeto.  
- **`persona_make/main.py`**: inicia a UI com `build_app()` e chama `app.launch()`.  
- **`persona_make/ui.py`**: define as abas *Criar Persona* e *Chat*, cadastra eventos, exibe o avatar e atualiza o avatar do Chatbot.  
- **`persona_make/persona.py`**: cria mensagens para gerar o JSON da persona e conduz o chat (sem incluir aviso de “simulação” nas respostas).  
- **`persona_make/llm.py`**: integra com a OpenAI Responses API, seleciona modelo e faz **fallback** se necessário; extrai texto de respostas em múltiplos formatos do SDK.  
- **`persona_make/storage.py`**: salva/carrega JSON, cria slugs únicos, grava **avatar** em `personas_media/`.  
- **`persona_make/constants.py`**: regras e templates (sistema/chat), incluindo estilos disponíveis.

---

## 🔧 Variáveis de ambiente
- `OPENAI_API_KEY` — **obrigatória**. Pode estar em `.env` ou no ambiente do sistema.

---

## 🧩 Modelos disponíveis
- `gpt-5` (preferencial)  
- `gpt-5-mini`  
- `gpt-5-nano`  

> O app tenta o modelo preferido; se não houver saída útil, tenta novamente sem web e, por fim, `gpt-5-mini` → `gpt-5-nano` (sem poluir a UI com avisos).

---

## ❗ Solução de Problemas
- **`ImportError: attempted relative import with no known parent package`**  
  Execute como **módulo**: `python -m persona_make.main` (na pasta do projeto).

- **Sem resposta do modelo**  
  Verifique a `OPENAI_API_KEY` e limites de uso. O fallback cobre casos transitórios.

- **Chat não aparece**  
  Confira a versão do Gradio (>= 4.31). Recarregue a página (Ctrl+F5).

- **Avatar não aparece**  
  O arquivo deve existir em `personas_media/` com o **mesmo slug** da persona (ex.: `batman_bruce_wayne.png`).

---

## 📄 Licença
Uso educacional/demonstrativo. Adapte conforme sua necessidade.
