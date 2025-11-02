
function getParametrosDaURL() {
    const params = new URLSearchParams(window.location.search);
    return {
        atletaId: params.get("id"),
        atletaNome: params.get("nome"),
        atletaModalidade: params.get("modalidade")
    };
}


// 🔐 Realiza login e salva token + dados do usuário
async function realizarLogin() {
    const email = document.getElementById("email").value;
    const senha = document.getElementById("senha").value;

    try {
        const response = await fetch("/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, senha })
        });

        if (!response.ok) throw new Error("Login inválido");

        const resultado = await response.json();

        localStorage.setItem("jwt_token", resultado.token);
        localStorage.setItem("usuario_info", JSON.stringify({
            id: resultado.usuario.id,
            nome: resultado.usuario.nome,
            email: resultado.usuario.email,
            tipo: resultado.usuario.tipo
        }));

        if (resultado.usuario.tipo === "aluno") {
            window.location.href = `/aluno/dashboard/${resultado.usuario.id}`;
        } else if (resultado.usuario.tipo === "treinador") {
            window.location.href = `/treinador/dashboard/${resultado.usuario.id}`;
        } else {
            alert("Tipo de usuário desconhecido.");
        }

    } catch (err) {
        console.error("❌ Erro no login:", err);
        alert("Email ou senha inválidos");
    }
}


// Salvar avaliação
async function salvarAvaliacao() {
    const token = localStorage.getItem("jwt_token");
    if (!token) {
        alert("Você precisa estar logado para salvar uma avaliação.");
        return;
    }

    const { atletaId } = getParametrosDaURL();
    const texto = document.getElementById("avaliacaoTexto").value.trim();

    if (!texto) {
        alert("Por favor, escreva uma avaliação.");
        return;
    }

    const dados = {
        aluno_id: parseInt(atletaId),
        texto: texto
    };

    try {
        const response = await fetch("/api/feedbacks", {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            },
            body: JSON.stringify(dados)
        });

        let resultado = {};
        try {
            resultado = await response.json();
        } catch (jsonError) {
            console.warn("⚠️ Erro ao interpretar JSON:", jsonError);
        }

        if (response.status === 403) {
            alert("❌ Apenas treinadores podem enviar avaliações.");
            return;
        }

        if (response.ok && resultado.sucesso) {
            alert("✅ Avaliação salva com sucesso!");
            document.getElementById("avaliacaoTexto").value = "";
        } else {
            alert("❌ Erro ao salvar: " + (resultado.detail || resultado.erro || "Erro desconhecido"));
        }
    } catch (error) {
        console.error("❌ Erro na requisição:", error);
        alert("Erro ao conectar com o servidor.");
    }
}



// Carrega dados do atleta na tela
function carregarDadosDoAtleta() {
    const { atletaId, atletaNome, atletaModalidade } = getParametrosDaURL();
    const usuarioInfo = localStorage.getItem("usuario_info");

    if (!usuarioInfo) {
        alert("⚠️ Você precisa estar logado.");
        window.location.href = "/";
        return;
    }

    let usuario;
    try {
        usuario = JSON.parse(usuarioInfo);
    } catch (e) {
        console.error("❌ Erro ao interpretar os dados do usuário:", e);
        alert("Erro ao carregar sessão. Faça login novamente.");
        window.location.href = "/";
        return;
    }

    // 🔒 Proteção: aluno só pode acessar sua própria página
    if (usuario.tipo === "aluno" && usuario.id !== parseInt(atletaId)) {
        alert("⚠️ Você não tem permissão para acessar este atleta.");
        window.location.href = `/aluno/dashboard/${usuario.id}`;
        return;
    }

    // ✅ Exibe os dados do atleta na tela
    document.getElementById("nome-atleta").textContent = decodeURIComponent(atletaNome);
    document.getElementById("modalidade-atleta").textContent = decodeURIComponent(atletaModalidade);
}

