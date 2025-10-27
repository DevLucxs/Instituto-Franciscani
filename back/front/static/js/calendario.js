      document.addEventListener("DOMContentLoaded", function () {
        // Variáveis globais
        let currentDate = new Date();
        let currentMonth = currentDate.getMonth();
        let currentYear = currentDate.getFullYear();
        const months = [
          "Janeiro",
          "Fevereiro",
          "Março",
          "Abril",
          "Maio",
          "Junho",
          "Julho",
          "Agosto",
          "Setembro",
          "Outubro",
          "Novembro",
          "Dezembro",
        ];

        let events = [];

        async function fetchEvents() {
        try {
            const response = await fetch("/api/eventos");
            if (!response.ok) throw new Error("Não foi possível carregar os eventos.");
            
            const serverEvents = await response.json();
            
            // Converte os dados da API para o formato que seu JS espera
            events = serverEvents.map(ev => ({
                id: ev.id,
                title: ev.title,
                date: ev.date,
                time: ev.time,
                location: ev.location,
                type: ev.type,
                description: ev.description,
                alunos: ev.alunos || []
            }));
            
        } catch (error) {
            console.error(error);
            // Mesmo se falhar, continue com um array vazio
            events = []; 
        }
    }

        // Elementos do DOM
        const calendarTitle = document.querySelector(".calendar-title");
        const calendarGrid = document.getElementById("calendarGrid");
        const prevMonthBtn = document.getElementById("prevMonth");
        const nextMonthBtn = document.getElementById("nextMonth");
        const addEventBtn = document.getElementById("addEventBtn");
        const eventModal = document.getElementById("eventModal");
        const closeModalBtn = document.querySelector(".close-modal");
        const cancelEventBtn = document.getElementById("cancelEvent");
        const eventForm = document.getElementById("eventForm");

        const selectAlunosElement = document.getElementById("eventAlunos");

        let choicesAlunos = new Choices(selectAlunosElement, {
        removeItemButton: true,
        placeholder: true,
        searchEnabled: true,
        searchChoices: false, 
        loadingText: 'Carregando...',
        noResultsText: 'Nenhum aluno encontrado',
        noChoicesText: 'Digite 2 ou mais letras para buscar...',
        searchResultLimit: 6,
        fuseOptions: {
            shouldSort: false,
            threshold: 1,
        },
    });

        selectAlunosElement.addEventListener('search', async function(event){
          const query = event.detail.value;

        // Limpa resultados antigos se o usuário apagar a busca
        // A sua API exige 2+ caracteres
        if (!query || query.length < 2) {
            choicesAlunos.clearChoices();
            // Mostra a mensagem "Digite 2 ou mais..."
            choicesAlunos.setChoices([{ value: '', label: 'Digite 2 ou mais letras para buscar...', disabled: true }]);
            return;
        }

        try {
            // Mostra o "Carregando..."
            choicesAlunos.clearChoices();
            choicesAlunos.setChoices([{ value: '', label: 'Carregando...', disabled: true }]);

            // Chama sua API de busca
            const response = await fetch(`/api/search/alunos/?q=${encodeURIComponent(query)}`);
            if (!response.ok) throw new Error('Falha na busca');
            
            const sugestoes = await response.json(); // Ex: [{"id": 1, "nome": "João"}]

            // Formata os dados para o Choices.js (ele quer 'value' e 'label')
            const choicesData = sugestoes.map(aluno => ({
                value: aluno.id.toString(), // O ID do aluno
                label: aluno.nome          // O Nome do aluno
            }));

            // Limpa o "Carregando..."
            choicesAlunos.clearChoices(); 

            if (choicesData.length > 0) {
                // Entrega os dados para o Choices.js
                choicesAlunos.setChoices(choicesData, 'value', 'label', false);
            } else {
                // Mostra a mensagem de "Nenhum resultado"
                choicesAlunos.setChoices([{ value: '', label: 'Nenhum aluno encontrado', disabled: true }]);
            }

        } catch (error) {
            console.error("Erro ao buscar alunos:", error);
            choicesAlunos.clearChoices();
            choicesAlunos.setChoices([{ value: '', label: 'Erro ao buscar', disabled: true }]);
        }
    });

        // Inicializar o calendário
        async function initCalendar() { 
        updateCalendarTitle();
        
        
        await fetchEvents(); 
        
        renderCalendar(); // Agora renderiza com os dados do banco
        setupEventListeners();
        renderUpcomingEvents(); // E renderiza a lista de próximos
        }

        // Atualizar o título do calendário
        function updateCalendarTitle() {
          calendarTitle.textContent = `${months[currentMonth]} ${currentYear}`;
        }

        // Renderizar o calendário
        function renderCalendar() {
          // Limpar o grid do calendário
          calendarGrid.innerHTML = "";

          // Obter o primeiro dia do mês e o número de dias no mês
          const firstDay = new Date(currentYear, currentMonth, 1).getDay();
          const daysInMonth = new Date(
            currentYear,
            currentMonth + 1,
            0
          ).getDate();

          // Dias do mês anterior
          const daysInPrevMonth = new Date(
            currentYear,
            currentMonth,
            0
          ).getDate();

          // Preencher os dias do mês anterior
          for (let i = firstDay - 1; i >= 0; i--) {
            const day = daysInPrevMonth - i;
            const dateStr = formatDate(currentYear, currentMonth - 1, day);
            calendarGrid.appendChild(
              createDayElement(day, "other-month", dateStr)
            );
          }

          // Preencher os dias do mês atual
          const today = new Date();
          for (let i = 1; i <= daysInMonth; i++) {
            const dateStr = formatDate(currentYear, currentMonth, i);
            const isToday =
              today.getDate() === i &&
              today.getMonth() === currentMonth &&
              today.getFullYear() === currentYear;
            const dayClass = isToday ? "today" : "";
            calendarGrid.appendChild(createDayElement(i, dayClass, dateStr));
          }

          // Preencher os dias do próximo mês
          const totalCells = 42; // 6 semanas * 7 dias
          const remainingCells = totalCells - (firstDay + daysInMonth);
          for (let i = 1; i <= remainingCells; i++) {
            const dateStr = formatDate(currentYear, currentMonth + 1, i);
            calendarGrid.appendChild(
              createDayElement(i, "other-month", dateStr)
            );
          }
        }

        // Criar elemento de dia
        function createDayElement(day, className, dateStr) {
          const dayElement = document.createElement("div");
          dayElement.className = `calendar-day ${className}`;

          const dayNumber = document.createElement("div");
          dayNumber.className = "day-number";
          dayNumber.textContent = day;
          dayElement.appendChild(dayNumber);

          const eventsContainer = document.createElement("div");
          eventsContainer.className = "day-events";

          // Adicionar eventos para este dia
          const dayEvents = events.filter((event) => event.date === dateStr);
          if (dayEvents.length > 0) {
            dayElement.classList.add("has-events");
            dayEvents.forEach((event) => {
              const eventElement = document.createElement("div");
              eventElement.className = `event-item event-${event.type}`;
              eventElement.textContent = event.title;
              eventElement.setAttribute("data-event-id", event.id);
              eventsContainer.appendChild(eventElement);
            });
          }

          dayElement.appendChild(eventsContainer);
          dayElement.setAttribute("data-date", dateStr);

          // Adicionar evento de clique para abrir o modal
          dayElement.addEventListener("click", function () {
            openAddEventModal(dateStr);
          });

          return dayElement;
        }

        // Formatar data como YYYY-MM-DD
        function formatDate(year, month, day) {
          // Ajustar o mês para ser baseado em 1
          const adjustedMonth = month + 1;
          return `${year}-${adjustedMonth.toString().padStart(2, "0")}-${day.toString().padStart(2, "0")}`;
        }

        // Configurar event listeners
        function setupEventListeners() {
          prevMonthBtn.addEventListener("click", function () {
            currentMonth--;
            if (currentMonth < 0) {
              currentMonth = 11;
              currentYear--;
            }
            updateCalendarTitle();
            renderCalendar();
          });

          nextMonthBtn.addEventListener("click", function () {
            currentMonth++;
            if (currentMonth > 11) {
              currentMonth = 0;
              currentYear++;
            }
            updateCalendarTitle();
            renderCalendar();
          });

          addEventBtn.addEventListener("click", function () {
            openAddEventModal();
          });

          closeModalBtn.addEventListener("click", closeEventModal);
          cancelEventBtn.addEventListener("click", closeEventModal);

          eventForm.addEventListener("submit", function (e) {
            e.preventDefault();
            saveEvent();
          });

          // Fechar modal ao clicar fora dele
          window.addEventListener("click", function (e) {
            if (e.target === eventModal) {
              closeEventModal();
            }
          });
        }

        // Abrir modal para adicionar evento
        function openAddEventModal(dateStr = "") {
          const modalTitle = document.querySelector("#eventModal h2");
          const deleteBtn = document.getElementById("deleteEvent");

          modalTitle.textContent = "Adicionar Evento";
          deleteBtn.style.display = "none";

          eventForm.removeAttribute("data-editing-id");
          eventForm.reset();

          choicesAlunos.removeActiveItems();

          if (dateStr) {
            document.getElementById("eventDate").value = dateStr;
          } else {
            document.getElementById("eventDate").value = formatDate(
              currentYear,
              currentMonth,
              currentDate.getDate()
            );
          }

          // Limpar outros campos do formulário
          document.getElementById("eventTitle").value = "";
          document.getElementById("eventTime").value = "";
          document.getElementById("eventLocation").value = "";
          document.getElementById("eventType").value = "competition";
          document.getElementById("eventDescription").value = "";
          eventForm.setAttribute("data-editing-id", "");

          eventModal.style.display = "flex";
        }

        // Abrir modal para editar evento
        function openEditEventModal(eventId) {
    const modalTitle = document.querySelector("#eventModal h2");
    const deleteBtn = document.getElementById("deleteEvent");
    const eventData = events.find((ev) => ev.id == eventId);

    if (!eventData) return;

    modalTitle.textContent = "Editar Evento";
    deleteBtn.style.display = "inline-block";
    eventForm.setAttribute("data-editing-id", eventData.id);

    // Preenche os campos do formulário
    document.getElementById("eventTitle").value = eventData.title;
    document.getElementById("eventDate").value = eventData.date;
    document.getElementById("eventTime").value = eventData.time || "";
    document.getElementById("eventLocation").value = eventData.location || "";
    document.getElementById("eventType").value = eventData.type;
    document.getElementById("eventDescription").value = eventData.description || "";

    // --- LÓGICA ATUALIZADA PARA PRÉ-SELECIONAR ALUNOS ---
    const alunos_atuais = eventData.alunos || [];
    
    choicesAlunos.clearStore();

    if (alunos_atuais.length > 0) {
        // 3. Formata os dados para o Choices.js
        const choicesData = alunos_atuais.map(aluno => ({
            value: aluno.id.toString(),
            label: aluno.nome
        }));

        // 4. Adiciona estes alunos como as *opções iniciais*
        choicesAlunos.setChoices(choicesData, 'value', 'label', false);

        // 5. E define todos eles como *selecionados*
        const ids_strings = alunos_atuais.map(a => a.id.toString());
        choicesAlunos.setValue(ids_strings);
    }

    deleteBtn.onclick = function () {
        deleteEvent(eventData.id);
    };

    eventModal.style.display = "flex";
}

        // Fechar modal
        function closeEventModal() {
          eventModal.style.display = "none";
        }

        // Salvar evento (novo ou edição)
       // Função saveEvent() completa e atualizada
async function saveEvent() {
    const editingId = eventForm.getAttribute("data-editing-id");
    
    const alunosSelect = document.getElementById("eventAlunos");
    const alunos_ids = choicesAlunos.getValue(true).map(id => parseInt(id));
    const treinadorId = document.body.dataset.treinadorId; 
    const timeValue = document.getElementById("eventTime").value; 
    let formattedTime = null;

    if (timeValue) {
        formattedTime = timeValue + ":00"; 
    }

    const newEventData = {
        title: document.getElementById("eventTitle").value,
        date: document.getElementById("eventDate").value,
        time: formattedTime || null,
        location: document.getElementById("eventLocation").value,
        type: document.getElementById("eventType").value,
        description: document.getElementById("eventDescription").value,
        treinador_id: parseInt(treinadorId),
        alunos_ids: alunos_ids,
    };

    try {
        let eventoSalvo; // Variável para armazenar a resposta

        if (editingId) {
            // --- INÍCIO DA LÓGICA DE ATUALIZAÇÃO (PUT) ---
            const response = await fetch(`/api/eventos/${editingId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(newEventData)
            });
            if (!response.ok) throw new Error("Falha ao atualizar o evento.");
            eventoSalvo = await response.json();
            
            // Atualiza o evento na lista local
            const index = events.findIndex(ev => ev.id == editingId);
            if (index !== -1) {
                events[index] = eventoSalvo; // Substitui o antigo pelo novo
            }
            // --- FIM DA LÓGICA DE ATUALIZAÇÃO ---

        } else {
            // --- LÓGICA DE CRIAR (POST) ---
            const response = await fetch("/api/CriarEventos", {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(newEventData)
            });
            
            if (!response.ok) throw new Error("Falha ao salvar o evento.");
            
            const errorData = await response.json();
            console.error("Erro de validação do servidor:", errorData);
            throw new Error("Falha na validação dos dados: " + JSON.stringify(errorData));
            eventoSalvo = await response.json();
            events.push(eventoSalvo); // Adiciona o novo evento à lista local
        }
        
        renderCalendar();
        renderUpcomingEvents();
        closeEventModal();

    } catch (error) {
        console.error("Erro ao salvar evento:", error);
        alert("Não foi possível salvar o evento.");
    }
}
        // Excluir evento
        async function deleteEvent(eventId) { 
        try {
            const response = await fetch(`/api/DeletarEventos/${eventId}`, {
                method: 'DELETE'
            });
            
            if (!response.ok) throw new Error("Falha ao deletar o evento.");

            // Remove o evento da lista local
            const index = events.findIndex((ev) => ev.id == eventId);
            if (index !== -1) {
                events.splice(index, 1);
            }
            
            renderCalendar();
            renderUpcomingEvents();
            closeEventModal();
            
        } catch (error) {
            console.error("Erro ao deletar evento:", error);
            alert("Não foi possível deletar o evento.");
        }
    }
        /**
 * Renderiza a lista de "Próximos Eventos" na seção correspondente do HTML,
 * usando os dados da variável global 'events' (preenchida por fetchEvents).
 */
function renderUpcomingEvents() {
    
    // 1. Encontra o contêiner principal da lista
    const eventsListContainer = document.querySelector(".events-list"); 
    
    // 2. Encontra (ou cria) o local específico para os itens da lista
    //    Vamos usar um ID para ficar mais fácil
    let itemsContainer = document.getElementById("upcoming-events-items");
    if (!itemsContainer) {
        // Se o container específico não existir, criamos ele (mantendo o h3)
        eventsListContainer.innerHTML = '<h3>Próximos Eventos</h3>'; // Garante que o título esteja lá
        itemsContainer = document.createElement('div');
        itemsContainer.id = 'upcoming-events-items';
        eventsListContainer.appendChild(itemsContainer);
    } else {
        // Se já existir, apenas limpa os itens antigos
        itemsContainer.innerHTML = ''; 
    }

    // 3. Filtra e ordena os eventos futuros (a partir da data atual)
    const hoje = new Date();
    hoje.setHours(0, 0, 0, 0); // Zera a hora para comparar apenas a data

    const upcoming = events
        // Filtra: A data do evento deve ser hoje ou depois
        .filter(ev => new Date(ev.date + 'T00:00:00') >= hoje) 
        // Ordena: Do mais próximo para o mais distante
        .sort((a, b) => new Date(a.date + 'T00:00:00') - new Date(b.date + 'T00:00:00'));

    // 4. Constrói e insere o HTML
    if (upcoming.length === 0) {
        itemsContainer.innerHTML = '<p style="padding: 10px;">Sem eventos futuros.</p>';
        return;
    }

    // Variável para acumular o HTML de todos os itens
    let allEventsHtml = ''; 

    upcoming.forEach(ev => {
        // Formata a data (ex: 15 SET)
        const dataObj = new Date(ev.date + 'T00:00:00');
        const dia = dataObj.getDate();
        const mes = dataObj.toLocaleString('pt-BR', { month: 'short' }).toUpperCase().replace('.', '');

        // Formata a hora (ex: 09:00h) - Garantindo que não quebre se for null
        let horaFormatada = '--:--h'; // Valor padrão
        if (ev.time) {
            try {
                 // Tenta formatar - assume formato HH:MM:SS ou HH:MM
                 const [h, m] = ev.time.split(':');
                 horaFormatada = `${h.padStart(2, '0')}:${m.padStart(2, '0')}h`;
            } catch (e) {
                console.warn("Formato de hora inválido para evento:", ev.id, ev.time);
                // Mantém o valor padrão se o formato for inesperado
            }
        }

        // Gera o HTML para este item
        allEventsHtml += `
            <div class="event-list-item" data-event-id="${ev.id}">
                <div class="event-date">
                    <div class="event-day">${dia}</div>
                    <div class="event-month">${mes}</div>
                </div>
                <div class="event-details">
                    <div class="event-title">${ev.title || 'Evento sem título'}</div>
                    <div class="event-info">
                        <span class="event-time">
                            <i class="fas fa-clock"></i> ${horaFormatada}
                        </span>
                        ${ev.location ? `
                        <span class="event-location">
                            <i class="fas fa-map-marker-alt"></i> ${ev.location}
                        </span>` : ''}
                    </div>
                </div>
                <div class="event-actions">
                    <button class="event-action-btn" onclick="openEditEventModal(${ev.id})">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="event-action-btn" onclick="deleteEvent(${ev.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
    });

    // Insere todo o HTML de uma vez no contêiner (mais eficiente)
    itemsContainer.innerHTML = allEventsHtml;
    }

        // Inicializar
        initCalendar();

        // Expor funções globais para botões inline
        window.openEditEventModal = openEditEventModal;
        window.deleteEvent = deleteEvent;
      });

      
    