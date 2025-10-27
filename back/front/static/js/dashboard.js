document.addEventListener('DOMContentLoaded', () => { // <-- UM ÚNICO BLOCO PARA TUDO

    // ================================================================
    // SEÇÃO 1: LÓGICA DO MOTOR DE PESQUISA
    // ================================================================
    function setupSearchFeature() {
        const searchInput = document.getElementById('searchInput');
        const suggestionsBox = document.getElementById('suggestionsBox');
        
        if (!searchInput || !suggestionsBox) {
            console.error("Elementos da barra de pesquisa não encontrados.");
            return;
        }

        let debounceTimer;

        const fetchSuggestions = async (query) => {
            if (query.length < 2) {
                suggestionsBox.innerHTML = '';
                suggestionsBox.style.display = 'none';
                return;
            }
            try {
                const response = await fetch(`/api/search/alunos/?q=${query}`);
                if (!response.ok) throw new Error(`Erro na rede: ${response.status}`);
                
                const suggestions = await response.json();
                suggestionsBox.innerHTML = '';

                if (suggestions.length > 0) {
                    suggestions.forEach(aluno => {
                        const item = document.createElement('div');
                        item.className = 'suggestion-item';
                        item.textContent = aluno.nome;
                        item.addEventListener('click', () => {
                            searchInput.value = aluno.nome;
                            suggestionsBox.style.display = 'none';
                        });
                        suggestionsBox.appendChild(item);
                    });
                    suggestionsBox.style.display = 'block';
                } else {
                    suggestionsBox.style.display = 'none';
                }
            } catch (error) {
                console.error('Erro ao buscar sugestões:', error);
                suggestionsBox.style.display = 'none';
            }
        };

        searchInput.addEventListener('input', (event) => {
            clearTimeout(debounceTimer);
            const query = event.target.value;
            debounceTimer = setTimeout(() => fetchSuggestions(query), 300);
        });

        document.addEventListener('click', (event) => {
            const searchBar = document.querySelector('.search-bar');
            if (searchBar && !searchBar.contains(event.target)) {
                suggestionsBox.style.display = 'none';
            }
        });
    }


    // ================================================================
    // SEÇÃO 2: LÓGICA DO MODAL DE DIETA
    // ================================================================
    function setupDietModal() {
        const modal = document.getElementById('dietModal');
        const openModalBtn = document.getElementById('openModal');
        const closeModalBtn = modal.querySelector('.close-modal');
        const cancelDietBtn = document.getElementById('cancelDietBtn');
        const submitDietBtn = document.getElementById('submitDietBtn');

        if (!modal || !openModalBtn || !closeModalBtn || !cancelDietBtn || !submitDietBtn) {
            console.error("Elementos do modal de dieta não encontrados.");
            return;
        }

        const openModal = () => { modal.style.display = 'flex'; };
        const closeModal = () => { modal.style.display = 'none'; };

        openModalBtn.addEventListener('click', openModal);
        closeModalBtn.addEventListener('click', closeModal);
        cancelDietBtn.addEventListener('click', closeModal);
        window.addEventListener('click', (event) => {
            if (event.target === modal) {
                closeModal();
            }
        });

        submitDietBtn.addEventListener('click', async () => {
            const athleteSelect = document.getElementById('athleteSelect');
            const dietFile = document.getElementById('dietFile').files[0];
            const atletaId = athleteSelect.value;

            if (!atletaId || !dietFile) {
                alert('Por favor, selecione um atleta e um arquivo.');
                return;
            }

            const formData = new FormData();
            formData.append('file', dietFile);

            try {
                const response = await fetch(`/api/dieta/${atletaId}`, {
                    method: 'POST',
                    body: formData,
                });
                const result = await response.json();
                if (response.ok) {
                    alert(result.message);
                    closeModal();
                } else {
                    throw new Error(result.message || 'Erro ao enviar a dieta.');
                }
            } catch (error) {
                console.error('Erro:', error);
                alert(error.message);
            }
        });
    }

    // ================================================================
    // SEÇÃO 3: LÓGICA DO MODAL DOS VÍDEOS  
    // ================================================================

function setupVideoModal() {
    const videoModal = document.getElementById('videoModal'); // Assumindo que o modal tem este ID
    const postVideoBtn = document.getElementById('postVideoBtn'); // Assumindo que o botão "Postar Vídeo" tem este ID

    if (!videoModal || !postVideoBtn) {
        console.error("Elementos do modal de vídeo não encontrados.");
        return;
    }

    postVideoBtn.addEventListener('click', async () => {
        const titulo = document.getElementById('videoTitle').value;
        const descricao = document.getElementById('videoDescription').value;
        const file = document.getElementById('videoFile').files[0];
        const alunoId = document.getElementById('videoAthleteSelect').value;

        if (!titulo || !file) {
            alert('Por favor, preencha o título e selecione um arquivo de vídeo.');
            return;
        }

        const formData = new FormData();
        formData.append('titulo', titulo);
        formData.append('descricao', descricao);
        formData.append('file', file);
        if (alunoId) { // Só anexa o aluno_id se um for selecionado
            formData.append('aluno_id', alunoId);
        }

        try {
            const response = await fetch('/api/videos', {
                method: 'POST',
                body: formData,
            });

            const result = await response.json();
            if (response.ok) {
                alert(result.message);
                videoModal.style.display = 'none'; // Fecha o modal
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            alert('Erro: ' + error.message);
        }
    });
}

    setupSearchFeature();
    setupDietModal();
    setupVideoModal();

}); 