document.addEventListener("DOMContentLoaded", function () {
    // 🔥 Selecionando elementos do chat
    const form = document.querySelector(".chat-form form");
    const messageArea = document.getElementById("message_area");
    const submitButton = document.getElementById("submitbutton");
    const chatHistory = document.getElementById("chatHistory");
    const fileInput = document.getElementById("file_input");

    function scrollToBottom() {
        if (chatHistory) {
            setTimeout(() => {
                chatHistory.scrollTop = chatHistory.scrollHeight;
            }, 100);
        }
    }

    // 📎 Evento para anexar arquivos e mostrar no textarea
    if (fileInput) {
        fileInput.addEventListener("change", function (event) {
            const file = event.target.files[0];

            if (file) {
                if (file.type.startsWith("image/")) {
                    const reader = new FileReader();
                    reader.onload = function (e) {
                        const imgTag = `<img src="${e.target.result}" style="max-width: 100px; border-radius: 5px;">`;
                        messageArea.value += "\n" + imgTag;
                    };
                    reader.readAsDataURL(file);
                } else {
                    messageArea.value += `\n📎 Arquivo anexado: ${file.name}`;
                }
            }
        });
    }

    // ✅ Função para copiar resposta ao clicar no botão
    window.copyToClipboard = function (button) {
        const responseElement = button.closest(".message_bot").querySelector(".bot-response");
        if (!responseElement) return;

        const responseText = responseElement.innerText.trim();
        if (!responseText) return;

        navigator.clipboard.writeText(responseText)
            .then(() => {
                button.textContent = "✅ Copiado!";
                setTimeout(() => {
                    button.textContent = "📋 Copiar";
                }, 2000);
            });
    };

    // 🔥 Função para envio de mensagens
    if (form) {
        form.addEventListener("submit", function (event) {
            event.preventDefault();

            const userMessage = messageArea.value.trim();
            if (userMessage === "") return;

            chatHistory.innerHTML += `
                <div class="message_user">
                    <p><strong>Você:</strong> ${userMessage}</p>
                </div>
            `;
            scrollToBottom();

            messageArea.value = "";
            messageArea.style.height = "40px";

            const loadingIndicator = document.createElement("div");
            loadingIndicator.classList.add("loading-dots");
            loadingIndicator.innerHTML = `<span>.</span><span>.</span><span>.</span>`;
            chatHistory.appendChild(loadingIndicator);
            scrollToBottom();

            const formData = new FormData();
            formData.append("message", userMessage);
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            fetch(form.action, {
                method: "POST",
                body: formData,
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "X-CSRFToken": csrfToken,
                },
            })
            .then(response => response.json())
            .then(data => {
                loadingIndicator.remove();
                const botMessage = document.createElement("div");
                botMessage.classList.add("message_bot");

                // Criando um elemento temporário para processar a resposta
                const tempDiv = document.createElement("div");
                tempDiv.innerHTML = data.response;

                // Verifica se há listas ou tabelas dentro da resposta
                const hasListOrTable = tempDiv.querySelector("ul, ol, table");

                // Só adiciona o botão se houver listas/tabelas
                const copyButton = hasListOrTable 
                    ? `<button class="copy-btn" onclick="copyToClipboard(this)">📋 Copiar</button>` 
                    : "";

                botMessage.innerHTML = `
                    <p><strong>Manuela:</strong></p>
                    <span class="bot-response">${data.response}</span>
                    ${copyButton}
                `;

                chatHistory.appendChild(botMessage);
                scrollToBottom();
            });
        });
    }

    // 🔥 Ajuste automático do textarea no chat
    if (messageArea) {
        messageArea.addEventListener("input", function () {
            this.style.height = "auto";
            this.style.height = this.scrollHeight + "px";
            scrollToBottom();
        });

        messageArea.addEventListener("keydown", function (event) {
            if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                submitButton.click();
            }
        });
    }

    // 🔥 Controles da Sidebar
    const openBtn = document.getElementById("open_btn");
    const sidebar = document.getElementById("sidebar");
    const openRightBtn = document.getElementById("openright_btn");
    const sidebar2 = document.getElementById("sidebar2");
    const overlay = document.getElementById("overlay");

    function closeAllSidebars() {
        sidebar.classList.remove("open_sidebar");
        sidebar2.classList.remove("open_sidebar");
        document.body.classList.remove("menu-open");
    }

    if (openBtn && sidebar && overlay) {
        openBtn.addEventListener("click", function (event) {
            const isOpen = sidebar.classList.contains("open_sidebar");

            closeAllSidebars();
            if (!isOpen) {
                sidebar.classList.add("open_sidebar");
                document.body.classList.add("menu-open");
            }
            event.stopPropagation();
        });
    }

    if (openRightBtn && sidebar2 && overlay) {
        openRightBtn.addEventListener("click", function (event) {
            const isOpen = sidebar2.classList.contains("open_sidebar");

            closeAllSidebars();
            if (!isOpen) {
                sidebar2.classList.add("open_sidebar");
                document.body.classList.add("menu-open");
            }
            event.stopPropagation();
        });
    }

    overlay.addEventListener("click", function () {
        closeAllSidebars();
    });

    sidebar.addEventListener("click", function (event) {
        event.stopPropagation();
    });

    sidebar2.addEventListener("click", function (event) {
        event.stopPropagation();
    });

    // 🔥 Scroll automático no chat
    scrollToBottom();
    window.addEventListener("resize", scrollToBottom);
});
