export function verificarSessaoOuRedirecionar() {
    const token = localStorage.getItem('jwt_token');
    const usuarioInfo = JSON.parse(localStorage.getItem('usuario_info') || '{}');

    if (!token || !usuarioInfo.id) {
        console.warn('🔒 Sessão inválida. Redirecionando...');
        window.location.replace('/');
    }
}


document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('jwt_token');
    const usuarioInfo = JSON.parse(localStorage.getItem('usuario_info') || '{}');

    if (!token || !usuarioInfo.id) {
        window.location.replace('/');
    }
});