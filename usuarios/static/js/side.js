document.getElementById('open_btn').addEventListener('click', function(){
    document.getElementById('sidebar').classList.toggle('open_sidebar');
});



// Fechar a sidebar ao clicar fora dela
document.addEventListener('click', function(event) {
    const sidebar = document.getElementById('sidebar');
    const isClickInside = sidebar.contains(event.target);

    if (!isClickInside) {
        sidebar.classList.remove('open_sidebar');
    }
});

