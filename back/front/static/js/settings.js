function showSettings() {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
    <div class="modal-content settings-modal">
      <header class="modal-header">
         <h2>Configurações do Sistema</h2>
         <button class="close-modal" onclick="this.closest('.modal-overlay').remove()" title="Fechar configurações" aria-label="Fechar modal de configurações">&times;</button>
      </header>
      <div class="settings-content">
        <div class="form-group">
          <label>Notificações por Email</label>
          <input type="checkbox" id="emailNotifications" name="emailNotifications" checked>
        </div>
        <div class="form-group">
          <label>Notificações Push</label>
          <input type="checkbox" id="pushNotifications" name="pushNotifications" checked>
        </div>
        <div class="form-group">
          <label>Idioma</label>
          <select name="idioma">
            <option>Português</option>
            <option>English</option>
            <option>Español</option>
          </select>
        </div>
        <div class="form-group">
          <label>Tema</label>
          <select name="tema">
            <option>Claro</option>
            <option>Escuro</option>
            <option>Automático</option>
          </select>
        </div>
      </div>
      <div class="modal-actions">
        <button class="btn btn-outline" onclick="this.closest('.modal-overlay').remove()" title="Cancelar configurações" aria-label="Fechar modal sem salvar">Cancelar</button>
        <button class="btn btn-primary" onclick="salvarConfiguracoes()" title="Salvar configurações" aria-label="Salvar alterações nas configurações">Salvar</button>
      </div>
    </div>
  `;

    document.body.appendChild(modal);

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