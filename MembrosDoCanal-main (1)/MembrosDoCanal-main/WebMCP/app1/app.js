// Array que guarda todas as tarefas (to-dos) em memória (não persiste ao recarregar a página)
const todos = [];

// Helpers DOM
const $ = (id) => document.getElementById(id);

function setStatus(message) {
  const status = $("status");
  if (!message) {
    status.style.display = "none";
    status.textContent = "";
    return;
  }
  status.style.display = "block";
  status.textContent = message;

  // some automaticamente depois de alguns segundos (toast simples)
  window.clearTimeout(setStatus._t);
  setStatus._t = window.setTimeout(() => {
    status.style.display = "none";
  }, 4500);
}

function updateCountAndEmpty() {
  $("count").textContent = String(todos.length);
  $("empty").style.display = todos.length ? "none" : "block";
}

// Função responsável por “desenhar” (renderizar) a lista de tarefas na tela
function render() {
  const ul = $("list");
  ul.innerHTML = "";

  for (const [idx, t] of todos.entries()) {
    const li = document.createElement("li");
    li.className = "item";

    const left = document.createElement("div");
    left.className = "left";

    const text = document.createElement("div");
    text.className = "text";
    text.textContent = t.text;

    const meta = document.createElement("div");
    meta.className = "meta";

    if (t.source) {
      const badge = document.createElement("span");
      badge.className = "badge";
      badge.dataset.source = t.source;
      badge.textContent = t.source;
      meta.appendChild(badge);
    }

    left.appendChild(text);
    left.appendChild(meta);

    const remove = document.createElement("button");
    remove.className = "remove";
    remove.type = "button";
    remove.textContent = "Remover";
    remove.addEventListener("click", () => {
      todos.splice(idx, 1);
      render();
    });

    li.appendChild(left);
    li.appendChild(remove);
    ul.appendChild(li);
  }

  updateCountAndEmpty();
}

// Função que adiciona uma tarefa nova no array e atualiza a UI
function addTodo(text, source = "UI") {
  const clean = String(text || "").trim();
  if (!clean) return;

  todos.push({ text: clean, source });
  render();
}

// UI normal (humano clicando)
$("addBtn").addEventListener("click", () => {
  addTodo($("todoText").value, "UI");
  $("todoText").value = "";
  $("todoText").focus();
});

// UX: Enter para adicionar
$("todoText").addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    e.preventDefault();
    $("addBtn").click();
  }
});

// Limpar tudo
$("clearAllBtn").addEventListener("click", () => {
  if (!todos.length) return;
  const ok = confirm("Remover todas as tarefas?");
  if (!ok) return;
  todos.length = 0;
  render();
});

// --- WebMCP tool registration (proposal) ---
function registerWebMcpTools() {
  const status = $("status");

  // Feature-detect: proposal define window.navigator.modelContext
  if (!("modelContext" in window.navigator)) {
    setStatus(
      "WebMCP não está disponível neste navegador/ambiente. " +
      "A página funciona via UI normal, mas não registrará tools para agentes."
    );
    return;
  }

  window.navigator.modelContext.provideContext({
    tools: [
      {
        name: "add-todo",
        description: "Adiciona uma tarefa (to-do) na lista exibida na página.",
        inputSchema: {
          type: "object",
          properties: {
            text: { type: "string", description: "Texto da tarefa" }
          },
          required: ["text"]
        },

        async execute({ text }, ctxOrAgent) {
          const agent = ctxOrAgent?.requestUserInteraction
            ? ctxOrAgent
            : ctxOrAgent?.agent;

          const requestUI = agent?.requestUserInteraction
            ? (fn) => agent.requestUserInteraction(fn)
            : async (fn) => await fn();

          const confirmed = await requestUI(async () => {
            return confirm(`Adicionar a tarefa?\n\n"${text}"`);
          });

          if (!confirmed) {
            throw new Error("Ação cancelada pelo usuário.");
          }

          addTodo(text, "AGENT");
          setStatus('✅ Tool executada: "add-todo" (origem: AGENT).');

          return {
            content: [
              {
                type: "text",
                text: `OK! Tarefa adicionada: "${text}". Total: ${todos.length}.`
              }
            ]
          };
        }
      }
    ]
  });

  setStatus('✅ Tool registrada: "add-todo". Um agente conectado pode chamar essa tool.');
}

registerWebMcpTools();
render();;

