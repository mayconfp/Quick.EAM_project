document.addEventListener("DOMContentLoaded", function () {
    console.log("JS carregado!"); // 🔥 Teste se o JavaScript está rodando corretamente

    // Lógica da primeira sidebar (esquerda)
    const openBtn = document.getElementById("open_btn");
    const sidebar = document.getElementById("sidebar");

    if (openBtn && sidebar) {
        openBtn.addEventListener("click", function (event) {
            console.log("Abrindo primeira sidebar!"); // 🔥 Teste no console
            sidebar.classList.toggle("open_sidebar");
            event.stopPropagation(); 
        });

        document.addEventListener("click", function (event) {
            if (!sidebar.contains(event.target) && event.target !== openBtn) {
                sidebar.classList.remove("open_sidebar");
            }
        });
    }

    // Lógica da segunda sidebar (direita)
    const openRightBtn = document.getElementById("openright_btn");
    const sidebar2 = document.getElementById("sidebar2");

    if (openRightBtn && sidebar2) {
        openRightBtn.addEventListener("click", function (event) {
            console.log("Abrindo segunda sidebar!"); // 🔥 Teste no console
            sidebar2.classList.toggle("open_sidebar");
            event.stopPropagation(); 
        });

        document.addEventListener("click", function (event) {
            if (!sidebar2.contains(event.target) && event.target !== openRightBtn) {
                sidebar2.classList.remove("open_sidebar");
            }
        });
    }
});
