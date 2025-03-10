document.addEventListener("DOMContentLoaded", function () {
    // 🔥 Seleciona elementos do chat
    const form = document.querySelector(".chat-form form");
    const messageArea = document.getElementById("message_area");
    const submitButton = document.getElementById("submitbutton");
    const chatHistory = document.getElementById("chatHistory");

    function scrollToBottom() {
        if (chatHistory) {
            setTimeout(() => {
                chatHistory.scrollTop = chatHistory.scrollHeight;
            }, 100);
        }
    }

    if (form) {
        form.addEventListener("submit", function (event) {
            event.preventDefault(); // Impede o envio padrão do formulário

            const userMessage = messageArea.value.trim();
            if (userMessage === "") return;

            // 🔹 Adiciona a mensagem do usuário no chat imediatamente
            chatHistory.innerHTML += `
                <div class="message_user">
                    <p><strong>Você:</strong> ${userMessage}</p>
                </div>
            `;
            scrollToBottom();

            messageArea.value = ""; // Limpa o campo de entrada
            messageArea.style.height = "40px"; // Reseta a altura do textarea

            // 🔹 Criar e adicionar os pontos piscando ANTES de chamar o fetch
            const loadingIndicator = document.createElement("div");
            loadingIndicator.classList.add("loading-dots");
            loadingIndicator.innerHTML = `<span>.</span><span>.</span><span>.</span>`;
            chatHistory.appendChild(loadingIndicator);
            scrollToBottom();

            // Criar um objeto FormData para enviar os dados corretamente
            const formData = new FormData();
            formData.append("message", userMessage);

            // Adiciona o token CSRF para evitar erro 403 no Django
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            // 🔹 Enviar a mensagem via AJAX para o servidor Django
            fetch(form.action, {
                method: "POST",
                body: formData,
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "X-CSRFToken": csrfToken,
                },
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error("Erro ao enviar a mensagem.");
                }
                return response.json(); // Esperamos um JSON como resposta
            })
            .then(data => {
                // 🔹 Remove os pontos piscando quando a resposta chegar
                loadingIndicator.remove();

                // 🔹 Adiciona a resposta da IA no chat
                chatHistory.innerHTML += `
                    <div class="message_bot">
                        <p><strong>Manuela:</strong> ${data.response}</p>
                    </div>
                `;

                scrollToBottom();
            })
            .catch(error => {
                console.error("❌ Erro ao enviar a mensagem:", error);
                loadingIndicator.remove();
            });
        });
    }

    // 🔥 Sidebar Controls
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
});
