document.getElementById("menuToggle").addEventListener("click", function () {
    const menu = document.getElementById("menu");
    menu.classList.toggle("hidden");
});

document.addEventListener("DOMContentLoaded", function () {
const passwordInput = document.getElementById("password1");
const requirements = document.querySelectorAll(".requerimentos-senha li"); // Atualizado para "requerimentos-senha"

passwordInput.addEventListener("input", function () {
const password = passwordInput.value;

// Valida os requisitos
requirements.forEach((item, index) => {
    let valid = false;
    switch (index) {
        case 0: valid = /\d/.test(password); break; // Número
        case 1: valid = /[!@#$%^&*]/.test(password); break; // Caractere especial
        case 2: valid = /[A-Z]/.test(password); break; // Letra maiúscula
        case 3: valid = password.length >= 8; break; // Mínimo de 8 caracteres
    }

    // Atualiza o estilo dos ícones
    const icon = item.querySelector(".requirement-icon");
    if (valid) {
        icon.style.backgroundColor = "#4CAF50"; // Verde para válido
    } else {
        icon.style.backgroundColor = "#f44336"; // Vermelho para inválido
    }
});
});
});