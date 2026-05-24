async function sendMessage() {
    const userInput = document.getElementById("user-input").value;
    if (!userInput) return;

    addMessageToChatBox("Usuário: " + userInput);
    document.getElementById("user-input").value = "";

    try {
        const response = await fetch('https://fabiosantos-api-chatbot.hf.space/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ "text": userInput })
        });

        if (!response.ok) {
            throw new Error("Erro na resposta da API");
        }

        const data = await response.json();
        if (data && data.response) {
            addMessageToChatBox("Chatbot: " + data.response);
        } else {
            addMessageToChatBox("Chatbot: Resposta não encontrada.");
        }
    } catch (error) {
        console.error("Erro:", error);
        addMessageToChatBox("Chatbot: Desculpe, ocorreu um erro ao processar sua solicitação.");
    }
}

function addMessageToChatBox(message) {
    const chatBox = document.getElementById("chat-box");
    const messageElement = document.createElement("div");
    messageElement.textContent = message;
    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight;
}

