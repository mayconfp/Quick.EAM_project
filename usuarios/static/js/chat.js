document.addEventListener("DOMContentLoaded", function () {
    

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

});