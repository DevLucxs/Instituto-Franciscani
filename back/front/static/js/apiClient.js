const apiClient = {
    getAtletasDebug: async () => {
        return await fetch('/api/alunos').then(res => res.json());
    },
    getEstatisticasAtleta: async (id) => {
        return await fetch(`/api/alunos/${id}/estatisticas`).then(res => res.json());
    },
    getAvaliacoesAtleta: async (id) => {
        return await fetch(`/api/alunos/${id}/feedbacks`).then(res => res.json());
    }
};