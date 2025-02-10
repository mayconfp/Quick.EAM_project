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





