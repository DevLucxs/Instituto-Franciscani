async function carregarPerfilAtleta() {
    const usuarioInfo = localStorage.getItem('usuario_info');
    if (!usuarioInfo) {
        console.warn('⚠️ Nenhum usuário logado');
        return;
    }

    let email = '';
    try {
        const usuario = JSON.parse(usuarioInfo);
        email = usuario.email;
    } catch (error) {
        console.error('❌ Erro ao ler dados do usuário:', error);
        return;
    }

    try {
        const response = await fetch(`/api/alunos?email=${encodeURIComponent(email)}`);
        if (!response.ok) throw new Error('Erro ao buscar atleta');

        const atleta = await response.json();
        preencherPerfil(atleta);
    } catch (error) {
        console.error('❌ Erro ao carregar perfil do atleta:', error);
    }
}