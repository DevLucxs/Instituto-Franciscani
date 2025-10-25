async function carregarPerfilAtleta() {
    const partes = window.location.pathname.split("/");
    const atletaId = partes[partes.length - 1]; // extrai o ID da URL

    try {
        const response = await fetch(`/api/alunos/${atletaId}`);
        if (!response.ok) throw new Error("Erro ao buscar dados do atleta");

        const atleta = await response.json();
        document.getElementById("nome-atleta").textContent = atleta.nome;
        document.getElementById("modalidade-atleta").textContent = atleta.modalidade;
        document.getElementById("data-ingresso").textContent = `Atleta desde ${atleta.ano_ingresso} | Foco: ${atleta.foco}`;
        document.getElementById("foto-atleta").src = atleta.foto;
        document.getElementById("foto-atleta").alt = atleta.nome;
    } catch (err) {
        console.error("❌ Erro ao carregar perfil do atleta:", err);
    }
}

document.addEventListener("DOMContentLoaded", carregarPerfilAtleta);
