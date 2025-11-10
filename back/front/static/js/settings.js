function showSettings() {
    const idiomaAtual = window.sistemaIdiomas ? window.sistemaIdiomas.obterIdiomaAtual() : 'pt';

    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.style.display = 'flex';
    modal.innerHTML = `
              <div class="modal-content" style="max-width: 600px;">
                <div class="modal-header">
                  <h2 data-translate="config.titulo">Configurações do Sistema</h2>
                  <button class="close-modal" onclick="this.parentElement.parentElement.parentElement.remove()" data-translate-title="geral.fechar">&times;</button>
                </div>
                <div class="settings-content">
                  <div class="form-group">
                    <label data-translate="config.notificacoes_email">Notificações por Email</label>
                    <input type="checkbox" checked>
                  </div>
                  <div class="form-group">
                    <label data-translate="config.notificacoes_push">Notificações Push</label>
                    <input type="checkbox" checked>
                  </div>
                  <div class="form-group">
                    <label data-translate="config.idioma">Idioma</label>
                    <select id="selectIdioma" onchange="alterarIdioma(this.value)">
                      <option value="pt" ${idiomaAtual === 'pt' ? 'selected' : ''} data-translate="config.portugues">Português</option>
                      <option value="en" ${idiomaAtual === 'en' ? 'selected' : ''} data-translate="config.ingles">English</option>
                      <option value="es" ${idiomaAtual === 'es' ? 'selected' : ''} data-translate="config.espanhol">Español</option>
                    </select>
                  </div>
                  <div class="form-group">
                    <label data-translate="config.tema">Tema</label>
                    <select>
                      <option data-translate="config.claro">Claro</option>
                      <option data-translate="config.escuro">Escuro</option>
                    </select>
                  </div>
                </div>
                <div class="modal-actions">
                  <button class="btn btn-outline" onclick="this.parentElement.parentElement.parentElement.remove()" data-translate="config.cancelar">Cancelar</button>
                  <button class="btn btn-primary" onclick="salvarConfiguracoes()" data-translate="config.salvar">Salvar</button>
                </div>
              </div>
            `;

    document.body.appendChild(modal);

    // Aplicar traduções ao modal
    if (window.sistemaIdiomas) {
        window.sistemaIdiomas.aplicarIdioma(window.sistemaIdiomas.obterIdiomaAtual());
    }

    // Fechar modal ao clicar fora
    modal.addEventListener('click', function (e) {
        if (e.target === modal) {
            modal.remove();
        }
    });
}

function salvarConfiguracoes() {
    const emailNotificacoes = document.getElementById('emailNotifications').checked;
    const pushNotificacoes = document.getElementById('pushNotifications').checked;
    const idioma = document.querySelector('select[name="idioma"]')?.value || 'Português';
    const tema = document.querySelector('select[name="tema"]')?.value || 'Claro';

    console.log("Configurações salvas:");
    console.log("Email:", emailNotificacoes);
    console.log("Push:", pushNotificacoes);
    console.log("Idioma:", idioma);
    console.log("Tema:", tema);

    alert("Configurações salvas com sucesso!");
    document.querySelector('.modal-overlay')?.remove();
}