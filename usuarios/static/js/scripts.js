
document.addEventListener("DOMContentLoaded", function () {
    const navbar = document.getElementById("navbar");
    const logo = document.querySelector(".logo img");
    const navLinks = document.querySelectorAll(".nav-links a");

    let lastScrollY = window.scrollY;

    window.addEventListener("scroll", function () {
        if (window.scrollY > lastScrollY) {
            // 🔽 Descendo: Adiciona efeito de redução
            navbar.classList.add("scrolled");
            logo.classList.add("small-logo");
            navLinks.forEach(link => link.classList.add("hide-text"));
        } else {
            // 🔼 Subindo: Volta ao estado original
            navbar.classList.remove("scrolled");
            logo.classList.remove("small-logo");
            navLinks.forEach(link => link.classList.remove("hide-text"));
        }

        lastScrollY = window.scrollY;
    });
});

function togglePassword(inputId, iconId) {
    let passwordInput = document.getElementById(inputId);
    let toggleIcon = document.getElementById(iconId);

    if (passwordInput.type === "password") {
        passwordInput.type = "text";
        toggleIcon.classList.remove("fa-eye");
        toggleIcon.classList.add("fa-eye-slash");
    } else {
        passwordInput.type = "password";
        toggleIcon.classList.remove("fa-eye-slash");
        toggleIcon.classList.add("fa-eye");
    }
}