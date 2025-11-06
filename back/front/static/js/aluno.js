async function carregarPerfilAtleta() {
    const token = localStorage.getItem("jwt_token");
    const atleta = JSON.parse(localStorage.getItem("usuario_info"));

    try {
        const response = await fetch(`/api/alunos/${atleta.id}`, {
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        if (!response.ok) throw new Error("Erro ao buscar dados do atleta");

        const dados = await response.json();
        console.log("👤 Perfil do atleta:", dados);

        // ✅ Atualiza o DOM com os dados recebidos
        document.getElementById("atletaNome").textContent = dados.nome || "Nome não disponível";
        document.getElementById("atletaId").textContent = dados.id || "-";
        document.getElementById("atletaModalidade").textContent = dados.modalidade || "Modalidade não definida";

        // ✅ Atualiza estatísticas se existirem
        document.getElementById("totalTreinos").textContent = dados.total_treinos ?? "0";
        document.getElementById("treinosConcluidos").textContent = dados.treinos_concluidos ?? "0";
        document.getElementById("horasTreinamento").textContent = dados.horas_treinamento ? `${dados.horas_treinamento}h` : "0h";

        // ✅ Atualiza avatar com iniciais
        const avatar = document.getElementById("atletaAvatar");
        if (dados.nome) {
            const partes = dados.nome.trim().split(" ");
            const iniciais = partes[0][0] + (partes[1]?.[0] || "");
            avatar.textContent = iniciais.toUpperCase();
        }

    } catch (error) {
        console.error("❌ Erro ao carregar perfil do atleta:", error);
    }
}
