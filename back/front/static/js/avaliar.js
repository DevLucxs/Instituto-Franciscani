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

// 💾 Salvar avaliação
async function salvarAvaliacao() {
    const token = localStorage.getItem("jwt_token");
    const usuarioInfo = JSON.parse(localStorage.getItem("usuario_info") || "{}");
    if (usuarioInfo.tipo !== "treinador") {
        alert("❌ Apenas treinadores podem enviar avaliações.");
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

        const resultado = await response.json();

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


// 📊 Atualiza gráfico de desempenho
function atualizarGraficoDesempenho(categoriasData) {
    if (!categoriasData || typeof categoriasData !== 'object') return;

    const categorias = Object.keys(categoriasData);
    const esperado = categorias.map(cat => categoriasData[cat]?.esperado ?? null);
    const atingido = categorias.map(cat => categoriasData[cat]?.atingido ?? null);

    const canvas = document.getElementById("performanceChart");
    const ctx = canvas?.getContext("2d");
    if (!ctx) return;

    if (window.performanceChartInstance) {
        window.performanceChartInstance.destroy();
        window.performanceChartInstance = null;
    }

    window.performanceChartInstance = new Chart(ctx, {
        type: "bar",
        data: {
            labels: categorias,
            datasets: [
                {
                    label: "Esperado",
                    data: esperado,
                    backgroundColor: "rgba(0, 0, 94, 0.6)",
                },
                {
                    label: "Atingido",
                    data: atingido,
                    backgroundColor: "rgba(72, 149, 239, 0.6)",
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            },
            plugins: {
                datalabels: {
                    anchor: 'end',
                    align: 'top',
                    formatter: Math.round,
                    font: {
                        weight: 'bold'
                    }
                }
            }
        }
    });
}



// 📡 Carrega desempenho do atleta com cache
async function carregarDesempenhoDoAtleta(atletaId) {
    const token = localStorage.getItem("jwt_token");
    const baseURL = window.location.protocol === "file:" ? "http://localhost:8000" : "";
    const cacheKey = `desempenho_atleta_${atletaId}`;

    const cache = localStorage.getItem(cacheKey);
    if (cache) {
        try {
            const dados = JSON.parse(cache);
            console.log(`📊 Usando cache para atleta ${atletaId}`);
            atualizarGraficoDesempenho(dados.categorias);
            return;
        } catch (e) {
            console.warn("⚠️ Erro ao interpretar cache:", e);
        }
    }

    try {
        const response = await fetch(`${baseURL}/api/atletas/${atletaId}/desempenho`, {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            }
        });

        const data = await response.json();
        if (response.ok && data.sucesso && data.desempenho) {
            localStorage.setItem(cacheKey, JSON.stringify(data.desempenho));
            atualizarGraficoDesempenho(data.desempenho.categorias);
        }
    } catch (error) {
        console.error(`❌ Erro ao buscar desempenho do atleta ${atletaId}:`, error);
    }
}

// 🧠 Carrega dados do atleta na tela
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

    if (usuario.tipo === "aluno" && usuario.id !== parseInt(atletaId)) {
        alert("⚠️ Você não tem permissão para acessar este atleta.");
        window.location.href = `/aluno/dashboard/${usuario.id}`;
        return;
    }

    document.getElementById("atletaNome").textContent = decodeURIComponent(atletaNome);
    document.getElementById("atletaModalidade").textContent = decodeURIComponent(atletaModalidade);


    carregarDesempenhoDoAtleta(atletaId);
}



async function carregarResumoTreinos(atletaId) {
    try {
        const token = localStorage.getItem("token") || localStorage.getItem("jwt_token");
        const response = await fetch(`/api/treinamentos?atleta_id=${atletaId}`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            console.warn('⚠️ Erro ao buscar treinos do atleta:', response.status);
            return;
        }

        const treinos = await response.json();

        const total = treinos.length;
        const concluidos = treinos.filter(t => t.completed).length;
        const horas = treinos
            .filter(t => t.completed && t.carga)
            .reduce((soma, t) => soma + t.carga, 0);

        document.getElementById('totalTreinos').textContent = total;
        document.getElementById('treinosConcluidos').textContent = concluidos;
        document.getElementById('horasTreinamento').textContent = `${horas}h`;

        console.log('📊 Resumo carregado:', { total, concluidos, horas });

    } catch (error) {
        console.error('❌ Erro ao carregar resumo de treinos:', error);
    }
}

// 🚀 Inicia tudo ao carregar a página
document.addEventListener("DOMContentLoaded", function () {
    const { atletaId } = getParametrosDaURL();
    carregarDadosDoAtleta();
    carregarResumoTreinos(atletaId);
});

