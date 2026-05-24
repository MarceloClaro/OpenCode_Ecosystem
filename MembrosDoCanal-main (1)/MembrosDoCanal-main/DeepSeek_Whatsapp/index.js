// Importação das bibliotecas necessárias
const { Client, LocalAuth } = require('whatsapp-web.js'); // Biblioteca para automação do WhatsApp Web
const qrcode = require('qrcode-terminal'); // Biblioteca para gerar QR Code no terminal
const axios = require('axios'); // Biblioteca para fazer requisições HTTP

// Objeto para armazenar o histórico das conversas dos usuários
const conversationHistory = {};

// Função para criar o prompt que será enviado à IA
function criarPrompt(pergunta) {
    const prompt = `
    Você é o Genius Bot, o assistente útil disposto a ajudar e conversar.
    Se o usuário lhe enviar uma saudação, você deverá responder: "Como posso lhe ajudar?".
    Responda de forma agradável e educada essa pergunta: ${pergunta}.
    `;

    return prompt.trim(); // Remove espaços extras no início e no fim
}

// Função para processar mensagens enviadas pelos usuários
async function messageProcess(text, userId) {
    try {
        // Se o usuário ainda não tiver um histórico salvo, inicializa um array para ele
        if (!conversationHistory[userId]) {
            conversationHistory[userId] = [];
        }

        // Adiciona a mensagem do usuário ao histórico
        conversationHistory[userId].push({ role: "user", content: text });

        // Mantém apenas as últimas 10 mensagens no histórico para evitar consumo excessivo de memória
        if (conversationHistory[userId].length > 10) {
            conversationHistory[userId].shift();
        }

        // Envia a mensagem do usuário para a API da IA
        const response = await axios.post('http://127.0.0.1:11434/api/generate', {
            model: "hf.co/FabioSantos/DeepSeek-R1-fine-tuned_v3-PCB:latest", // Define o modelo de IA a ser utilizado
            prompt: criarPrompt(text),  // Gera o prompt para a IA com base na mensagem do usuário
            stream: false // Garante que a resposta será enviada completa e não em fragmentos
        });

        console.log("Resposta da API:", response.data); // Log da resposta recebida da IA

        // Verifica se a resposta da API é válida antes de tentar acessá-la
        if (!response.data || !response.data.response) {
            console.error("Resposta inesperada da API:", response.data);
            return "Desculpe, ocorreu um erro ao processar sua mensagem."; // Resposta de erro amigável
        }

        let reply = response.data.response.trim(); // Obtém a resposta e remove espaços extras

        // Remove qualquer trecho do tipo <think>...</think> da resposta da IA
        reply = reply.replace(/<think>[\s\S]*?<\/think>/g, '').trim();

        // Adiciona a resposta da IA ao histórico do usuário
        conversationHistory[userId].push({ role: "assistant", content: reply });

        console.log(`Resposta gerada para ${userId}: ${reply}`); // Exibe a resposta no console
        return reply; // Retorna a resposta processada para ser enviada ao usuário
    } catch (error) {
        console.error('Erro ao processar mensagem:', error.message); // Captura e exibe erros no console
        return 'Desculpe, não consegui processar sua mensagem.'; // Resposta amigável de erro
    }
}

// Inicializa o cliente do WhatsApp com autenticação local
const client = new Client({
    authStrategy: new LocalAuth() // Salva a sessão localmente para evitar necessidade de login recorrente
});

// Evento acionado quando o QR Code for gerado
client.on('qr', (qr) => {
    qrcode.generate(qr, { small: true }); // Gera e exibe o QR Code no terminal
});

// Evento acionado quando o bot estiver pronto para uso
client.on('ready', () => {
    console.log('Client is ready!'); // Exibe uma mensagem informando que o bot está ativo
});

// Evento acionado quando o bot recebe uma mensagem no WhatsApp
client.on('message', async (message) => {
    console.log(`Mensagem recebida de ${message.from}: ${message.body}`); // Exibe a mensagem recebida no console

    // Processa a mensagem do usuário e obtém uma resposta da IA
    const response = await messageProcess(message.body, message.from);

    // Responde a mensagem diretamente no WhatsApp
    message.reply(response);
});

// Inicializa o cliente do WhatsApp e conecta à conta do usuário
client.initialize();
