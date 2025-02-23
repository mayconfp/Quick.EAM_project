document.addEventListener("DOMContentLoaded", function () {
    // 🔥 FUNÇÃO PARA DECODIFICAR E FORMATAR A RESPOSTA DA IA
    function processarResposta(resposta) {
        try {
            // Remove caracteres Unicode desnecessários (\u000A, \u002D, etc.)
            const respostaDecodificada = resposta.replace(/\\u[\dA-Fa-f]{4}/g, '');

            // Converte Markdown para HTML usando `marked.js`
            return marked.parse(respostaDecodificada);
        } catch (error) {
            console.error("Erro ao processar resposta:", error);
            return resposta; // Retorna a resposta original se houver erro
        }
    }

    // 🔥 Atualiza todas as respostas da IA corretamente ao carregar a página
    document.querySelectorAll(".chat-response").forEach(element => {
        const respostaOriginal = element.getAttribute("data-resposta");
        if (respostaOriginal) {
            element.innerHTML = processarResposta(respostaOriginal);
        }
    });

    // 🔥 SIDEBAR ESQUERDA
    const openBtn = document.getElementById("open_btn");
    const sidebar = document.getElementById("sidebar");

    if (openBtn && sidebar) {
        openBtn.addEventListener("click", function (event) {
            sidebar.classList.toggle("open_sidebar");
            event.stopPropagation();
        });

        document.addEventListener("click", function (event) {
            if (!sidebar.contains(event.target) && event.target !== openBtn) {
                sidebar.classList.remove("open_sidebar");
            }
        });
    } else {
        console.warn("❌ Sidebar ESQUERDA ou botão não encontrado.");
    }

    // 🔥 SIDEBAR DIREITA
    const openRightBtn = document.getElementById("openright_btn");
    const sidebar2 = document.getElementById("sidebar2");

    if (openRightBtn && sidebar2) {
        openRightBtn.addEventListener("click", function (event) {
            sidebar2.classList.toggle("open_sidebar");
            event.stopPropagation();
        });

        document.addEventListener("click", function (event) {
            if (!sidebar2.contains(event.target) && event.target !== openRightBtn) {
                sidebar2.classList.remove("open_sidebar");
            }
        });
    } else {
        console.warn("❌ Sidebar DIREITA ou botão não encontrado.");
    }

    // 🔥 AJUSTE DO SCROLL NO CHAT
    function scrollToBottom() {
        const chatHistory = document.getElementById("chatHistory");
        if (chatHistory) {
            setTimeout(() => {
                chatHistory.scrollTop = chatHistory.scrollHeight;
            }, 100);
        }
    }

    scrollToBottom();

    window.addEventListener("resize", () => {
        scrollToBottom();
    });

    // 🔥 AJUSTE AUTOMÁTICO DO TEXTAREA NO CHAT
    const messageArea = document.getElementById("message_area");
    const submitButton = document.getElementById("submitbutton");

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

    // 🔥 BUSCAR RESPOSTA DA IA E ATUALIZAR O CHAT
    function obterRespostaIA() {
        fetch("/chat/")
            .then(response => {
                if (!response.ok) {
                    console.error("Erro na requisição ao chat:", response.status);
                    return null;
                }
                return response.json();
            })
            .then(data => {
                if (data && data.response) {
                    const respostaElement = document.getElementById("resposta");
                    if (respostaElement) {
                        respostaElement.innerHTML = processarResposta(data.response);
                    }
                } else {
                    console.warn("Nenhuma resposta válida recebida da IA.");
                }
            })
            .catch(error => {
                console.error("Erro ao buscar resposta do chat:", error);
            });
    }
    
});
