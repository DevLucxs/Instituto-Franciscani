document.addEventListener('DOMContentLoaded', () => {
    // Chama a função que configura a barra de pesquisa.
    setupSearchFeature();
});

function setupSearchFeature() {
    const searchInput = document.getElementById('searchInput');
    const suggestionsBox = document.getElementById('suggestionsBox');
    const searchBar = document.querySelector('.search-bar');
    
    // Se algum dos elementos essenciais não for encontrado, a função para.
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
            
            if (!response.ok) {
                throw new Error(`A resposta da rede não foi bem-sucedida. Status: ${response.status}`);
            }

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
        debounceTimer = setTimeout(() => {
            fetchSuggestions(query);
        }, 300); // 300ms de espera
    });

    document.addEventListener('click', (event) => {
        if (!event.target.closest('.search-bar')) {
            suggestionsBox.style.display = 'none';
        }
    });
}

