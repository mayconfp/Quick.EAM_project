document.addEventListener("DOMContentLoaded", function () {
    
const openBtn = document.getElementById("open_btn");
const sidebar = document.getElementById("sidebar");
const openRightBtn = document.getElementById("openright_btn");
const sidebar2 = document.getElementById("sidebar2");
const overlay = document.getElementById("overlay"); // Usaremos apenas um overlay para cobrir tudo

function closeAllSidebars() {
    sidebar.classList.remove("open_sidebar");
    sidebar2.classList.remove("open_sidebar");
    document.body.classList.remove("menu-open");
}

if (openBtn && sidebar && overlay) {
    openBtn.addEventListener("click", function (event) {
        const isOpen = sidebar.classList.contains("open_sidebar");

        closeAllSidebars(); // Fecha qualquer sidebar aberta antes de abrir outra
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

        closeAllSidebars(); // Fecha qualquer sidebar aberta antes de abrir outra
        if (!isOpen) {
            sidebar2.classList.add("open_sidebar");
            document.body.classList.add("menu-open");
        }
        event.stopPropagation();
    });
}

// ✅ Fecha qualquer sidebar aberta ao clicar no overlay
overlay.addEventListener("click", function () {
    closeAllSidebars();
});

// ✅ Impede que a sidebar feche ao clicar dentro dela
sidebar.addEventListener("click", function (event) {
    event.stopPropagation();
});

sidebar2.addEventListener("click", function (event) {
    event.stopPropagation();
});
    


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
