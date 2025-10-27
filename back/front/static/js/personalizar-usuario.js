// personalizar-usuario.js

document.addEventListener("DOMContentLoaded", () => {
    console.log("[PERSONALIZAÇÃO] Script carregado com sucesso.");

    // Exemplo: personalizar saudação
    const userName = localStorage.getItem("usuario_nome");
    if (userName) {
        const saudacao = document.getElementById("userGreeting");
        if (saudacao) {
            saudacao.textContent = `Olá, ${userName}!`;
        }
    }

    // Exemplo: aplicar tema escuro se preferido
    const tema = localStorage.getItem("tema_usuario");
    if (tema === "escuro") {
        document.body.classList.add("dark-mode");
    }

    // Exemplo: destacar atletas favoritos
    const favoritos = JSON.parse(localStorage.getItem("atletas_favoritos") || "[]");
    favoritos.forEach(id => {
        const linha = document.querySelector(`tr[data-id="${id}"]`);
        if (linha) {
            linha.classList.add("favorito");
        }
    });
});