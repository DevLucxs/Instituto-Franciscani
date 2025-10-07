document.addEventListener("DOMContentLoaded", () => {
    const formAluno = document.getElementById("loginAluno");

    if (formAluno) {
        formAluno.addEventListener("submit", async (event) => {
            event.preventDefault();

            const email = document.getElementById("email").value.trim();
            const senha = document.getElementById("senha").value.trim();
            const errorMsg = document.getElementById("errorMsg");
            errorMsg.style.display = "none";

            try {
                const response = await fetch("http://127.0.0.1:8000/login", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ email, senha })
                });

                const data = await response.json();

                if (data.success) {
                    if (data.tipo === "aluno") {
                        window.location.href = "templates/pages_aluno/dashboard.html";
                    } else if (data.tipo === "treinador") {
                        window.location.href = "templates/pages/dashboard.html";
                    }
                } else {
                    errorMsg.textContent = data.message || "Usuário ou senha inválidos";
                    errorMsg.style.display = "block";
                }

            } catch (err) {
                errorMsg.textContent = "Erro ao conectar com o servidor.";
                errorMsg.style.display = "block";
                console.error(err);
            }
        });
    }
});