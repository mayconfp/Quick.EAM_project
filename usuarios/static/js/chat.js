document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector(".chat-form form");
    const messageArea = document.getElementById("message_area");
    const submitButton = document.getElementById("submitbutton");
    const chatHistory = document.getElementById("chatHistory");
    const fileInput = document.getElementById("file-upload");
    const fileNameDisplay = document.getElementById("file-name");
    const sugestoesContainer = document.getElementById("sugestoes-mensagens");

    function scrollToBottom() {
        if (chatHistory) {
            setTimeout(() => {
                chatHistory.scrollTop = chatHistory.scrollHeight;
            }, 100);
        }
    }

    // ✅ Exibir sugestões se não houver mensagens
    function verificarSugestoes() {
        setTimeout(() => {
            if (chatHistory && chatHistory.querySelectorAll(".message_user, .message_bot").length === 0) {
                sugestoesContainer.style.display = "flex";
            } else {
                sugestoesContainer.style.display = "none";
            }
        }, 300);
    }

    verificarSugestoes();

    // ✅ Inserir sugestão no campo de mensagem e enviar
    document.querySelectorAll(".sugestao-btn").forEach(button => {
        button.addEventListener("click", function () {
            const texto = this.getAttribute("data-sugestao");
            messageArea.value = texto;
            sugestoesContainer.style.display = "none";

            if (texto.trim() !== "") {
                form.dispatchEvent(new Event("submit", { bubbles: true, cancelable: true }));
            }
        });
    });

    // ✅ Botão copiar conteúdo
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

    // ✅ Enviar mensagem
    if (form) {
        form.addEventListener("submit", function (event) {
            event.preventDefault();

            const userMessage = messageArea.value.trim();
            const uploadedFile = fileInput.files[0];

            if (!userMessage && !uploadedFile) return;

            sugestoesContainer.style.display = "none";

            if (userMessage) {
                chatHistory.innerHTML += `
                    <div class="message_user">
                        <p><strong>Você:</strong> ${userMessage}</p>
                    </div>
                `;
            }

            scrollToBottom();
            messageArea.value = "";
            messageArea.style.height = "40px";
            fileInput.value = "";
            fileNameDisplay.textContent = "";

            const loadingIndicator = document.createElement("div");
            loadingIndicator.classList.add("loading-dots");
            loadingIndicator.innerHTML = `<span>.</span><span>.</span><span>.</span>`;
            chatHistory.appendChild(loadingIndicator);
            scrollToBottom();

            const formData = new FormData();
            formData.append("message", userMessage);
            if (uploadedFile) {
                formData.append("file", uploadedFile);
            }

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

                    const formattedResponse = formatarTextoParaHTML(data.response);
                    const tempDiv = document.createElement("div");
                    tempDiv.innerHTML = formattedResponse;

                    ajustarFormatacaoResposta(tempDiv);

                    const hasListOrTable = tempDiv.querySelector("ul, ol, table");
                    const copyButton = hasListOrTable
                        ? `<button class="copy-btn" onclick="copyToClipboard(this)">📋 Copiar</button>`
                        : "";

                    botMessage.innerHTML = `
                        <p><strong>Manuela:</strong></p>
                        <span class="bot-response">${tempDiv.innerHTML}</span>
                        ${copyButton}
                    `;

                    chatHistory.appendChild(botMessage);
                    scrollToBottom();
                })
                .catch(error => {
                    console.error("❌ Erro ao enviar a mensagem:", error);
                    loadingIndicator.remove();
                });
        });
    }

    // ✅ Botão de copiar no carregamento da página (para histórico)
    document.querySelectorAll(".message_bot").forEach(botMessage => {
        const response = botMessage.querySelector(".bot-response");
        if (response && (response.querySelector("ul") || response.querySelector("ol") || response.querySelector("table"))) {
            if (!botMessage.querySelector(".copy-btn")) {
                const copyBtn = document.createElement("button");
                copyBtn.classList.add("copy-btn");
                copyBtn.textContent = "📋 Copiar";
                copyBtn.onclick = () => copyToClipboard(copyBtn);
                botMessage.appendChild(copyBtn);
            }
        }
    });

    // ✅ Textarea auto expand
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

    // ✅ Scroll inicial
    scrollToBottom();
    window.addEventListener("resize", scrollToBottom);

    // ✅ Sidebars
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

    overlay.addEventListener("click", closeAllSidebars);
    sidebar.addEventListener("click", event => event.stopPropagation());
    sidebar2.addEventListener("click", event => event.stopPropagation());
});

// 🔧 Ajustes visuais das respostas
function ajustarFormatacaoResposta(container) {
    container.querySelectorAll("table").forEach(table => {
        table.style.borderCollapse = "collapse";
        table.style.width = "100%";
        table.style.margin = "10px 0";
    });

    container.querySelectorAll("th, td").forEach(cell => {
        cell.style.border = "1px solid #ddd";
        cell.style.padding = "8px";
    });

    container.querySelectorAll("p").forEach(p => {
        if (p.innerText.trim() === "") p.remove();
    });
}

// 🔧 Segurança para HTML
function formatarTextoParaHTML(texto) {
    const tempDiv = document.createElement("div");
    tempDiv.innerHTML = texto;
    return tempDiv.innerHTML;
}
