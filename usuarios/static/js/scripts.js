document.addEventListener("DOMContentLoaded", function () {
    let menuToggle = document.getElementById("menuToggle");
    let menu = document.getElementById("menu");

    if (menuToggle && menu) {  
        // Alterna a classe 'hidden' ao clicar no botão do menu
        menuToggle.addEventListener("click", function (event) {
            event.stopPropagation(); // Evita que o clique no botão feche o menu imediatamente
            menu.classList.toggle("hidden");
        });

        // Fecha o menu se clicar fora dele
        document.addEventListener("click", function (event) {
            let isClickInside = menu.contains(event.target) || menuToggle.contains(event.target);
            if (!isClickInside) {
                menu.classList.add("hidden"); // Fecha o menu
            }
        });
    } else {
        console.error("Erro: Elementos da navbar não encontrados!");
    }
});




document.addEventListener('DOMContentLoaded', function () {
    const sidebar = document.getElementById('sidebar');
    const openBtn = document.getElementById('open_btn');

    if (openBtn && sidebar) {
        openBtn.addEventListener('click', function () {
            sidebar.classList.toggle('open_sidebar');
        });

        // Fechar a sidebar ao clicar fora dela
        document.addEventListener('click', function (event) {
            if (!sidebar.contains(event.target) && !openBtn.contains(event.target)) {
                sidebar.classList.remove('open_sidebar');
            }
        });
    } else {
        console.error("Sidebar não encontrada.");
    }
});