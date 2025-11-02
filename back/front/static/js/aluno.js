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
        // Atualize o DOM com os dados aqui

    } catch (error) {
        console.error("❌ Erro ao carregar perfil do atleta:", error);
    }
}
