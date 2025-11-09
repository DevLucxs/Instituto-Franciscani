document.addEventListener('DOMContentLoaded', () => {
    // ================================================================
    // SEÇÃO 0: CARREGAMENTO DE EVENTOS DO DASHBOARD
    // ================================================================
    async function fetchAndRenderDashboardEvents() {
        const container = document.getElementById('upcoming-events-items');
        if (!container) {
            console.warn("⚠️ Contêiner #upcoming-events-items não encontrado. Ignorando carregamento de eventos.");
            return;
        }

        try {
            const response = await fetch('/api/eventos/proximos');
            if (!response.ok) throw new Error(`Erro ${response.status}: ${response.statusText}`);

            const eventos = await response.json();
            container.innerHTML = '';

            if (eventos.length === 0) {
                container.innerHTML = `
                <div class="no-competitions">
                    <i class="fas fa-calendar-times"></i>
                    <p>Nenhum evento encontrado.</p>
                </div>
            `;
                return;
            }

            eventos.forEach(evento => {
                const item = document.createElement('div');
                item.className = `competition-item ${evento.tipo?.toLowerCase() || ''}`;

                const data = new Date(evento.data);
                const dia = data.getDate();
                const mes = data.toLocaleDateString('pt-BR', { month: 'short' });

                const tipoIcon = {
                    "competicao": "fa-trophy",
                    "treinamento": "fa-dumbbell",
                    "reuniao": "fa-users"
                }[evento.tipo?.toLowerCase()] || "fa-calendar";

                item.innerHTML = `
                <div class="competition-date">
                    <div class="day">${dia}</div>
                    <div class="month">${mes}</div>
                </div>
                <div class="competition-details">
                    <h4><i class="fas ${tipoIcon}"></i> ${evento.nome}</h4>
                    <p>${evento.local}</p>
                    <p>${evento.descricao}</p>
                </div>
            `;

                container.appendChild(item);
            });

        } catch (error) {
            console.error('❌ Erro ao carregar eventos:', error);
            container.innerHTML = '<p>Erro ao carregar eventos.</p>';
        }
    }



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
        if (!modal) {
            console.warn("⚠️ dietModal não encontrado.");
            return;
        }

        const openModalBtn = document.getElementById('openModal');
        const closeModalBtn = modal.querySelector('.close-modal');
        const cancelDietBtn = document.getElementById('cancelDietBtn');
        const submitDietBtn = document.getElementById('submitDietBtn');

        if (!openModalBtn || !closeModalBtn || !cancelDietBtn || !submitDietBtn) {
            console.warn("⚠️ Botões do modal de dieta não encontrados.");
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
        const videoModal = document.getElementById('videoModal');
        const postVideoBtn = document.getElementById('postVideoBtn');

        if (!videoModal || !postVideoBtn) {
            console.warn("⚠️ Elementos do modal de vídeo não encontrados.");
            return;
        }

        postVideoBtn.addEventListener('click', async () => {
            const tituloInput = document.getElementById('videoTitle');
            const descricaoInput = document.getElementById('videoDescription');
            const fileInput = document.getElementById('videoFile');
            const alunoSelect = document.getElementById('videoAthleteSelect');

            if (!tituloInput || !fileInput) {
                alert('Campos obrigatórios não encontrados.');
                return;
            }

            const titulo = tituloInput.value;
            const descricao = descricaoInput?.value || '';
            const file = fileInput.files[0];
            const alunoId = alunoSelect?.value || '';

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

    const container = document.getElementById('upcoming-events-items');
    if (container) {
        fetchAndRenderDashboardEvents();
    }

    setupSearchFeature();
    setupDietModal();
    setupVideoModal();
});