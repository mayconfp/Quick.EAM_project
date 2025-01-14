
function scrollToBottom() {
    const chatHistory = document.getElementById("chatHistory");
    setTimeout(() => {
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }, 100); // Pequeno atraso para renderização
}

document.addEventListener("DOMContentLoaded", function () {
    scrollToBottom(); // Garante que rola ao final ao carregar
});

window.addEventListener("resize", () => {
    scrollToBottom(); // Ajusta ao redimensionar
});


document.querySelectorAll('.message_user, .message_bot').forEach(function (message) {
    message.style.maxWidth = '70%'; // Limita a largura máxima
    message.style.wordWrap = 'break-word'; // Quebra palavras longas
    message.style.whiteSpace = 'normal'; // Permite quebras de linha
    message.style.overflowWrap = 'break-word'; // Compatibilidade adicional
});

const messageArea = document.getElementById("message_area");
const submitButton = document.getElementById("submitbutton");
const chatContainer = document.getElementById("chatHistory");




messageArea.addEventListener("input", function () {
    this.style.height = "auto"; // Reseta a altura
    if (this.scrollHeight <= 100) {
        this.style.height = this.scrollHeight + "px"; // Ajusta para o conteúdo
    } else {
        this.style.height = "100px"; // Limita a altura máxima
    }

    // Rola o chat para o final
    scrollToBottom();
});

messageArea.addEventListener("keydown",function sendMessage(event){
    if (event.key === "Enter" && !event.shiftKey){
        event.preventDefault();
        submitButton.click();
    }
});

const newChatBtn = document.getElementById("newChatBtn");
if (newChatBtn) {
    newChatBtn.addEventListener("click", function () {
        window.location.href = "/chat/?nova_conversa=true";
    });
}

const toggleHistory = document.getElementById("menuToggle");
const mobileHistory = document.getElementById("mobileHistory");

// Alterna o menu móvel
toggleHistory.addEventListener("click", () => {
    mobileHistory.classList.toggle("hidden");
});

// Fecha o menu ao clicar fora
document.addEventListener("click", (event) => {
    if (!mobileHistory.contains(event.target) && !toggleHistory.contains(event.target)) {
        mobileHistory.classList.add("hidden");
    }
});
