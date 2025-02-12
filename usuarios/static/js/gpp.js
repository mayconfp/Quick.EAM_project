document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("categoriaForm").addEventListener("submit", function (event) {
        event.preventDefault();

        const nomeCategoria = document.getElementById("nomeCategoria").value;

        if (nomeCategoria.trim() !== "") {
            const categoriaLista = document.getElementById("categoriaLista");

            // Adiciona a nova categoria na tabela
            const newRow = document.createElement("tr");
            newRow.innerHTML = `
                <td>#</td>
                <td>${nomeCategoria}</td>
                <td><button class="btn btn-secondary">Editar</button> <button class="btn btn-danger">Excluir</button></td>
            `;
            categoriaLista.appendChild(newRow);

            // Limpar campo após adicionar
            document.getElementById("nomeCategoria").value = "";
        }
    });
});
