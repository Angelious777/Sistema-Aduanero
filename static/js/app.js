document.addEventListener('DOMContentLoaded', () => {
  bindSidebar();
  bindModals();
  showPanel('dashboard');
});
const PANEL_IDS = ['dashboard', 'coordinator', 'lapaz', 'scz'];
const MODAL_PROFILES = {
  'new-query': {
    title: 'Simulación de consulta distribuida',
    subtitle: 'Query Parser recibe la petición y decide los fragmentos',
    confirm: 'Iniciar simulación',
    body: `
      <div class="modal-section">
        <label>Consulta distribuida</label>
        <textarea rows="4" readonly>SELECT * FROM PAQUETE WHERE region IN ('LP','SCZ');</textarea>
      </div>
      <div class="modal-section">
        <label>Subconsultas generadas</label>
        <div class="status-list">
          <li>SELECT * FROM PAQUETE_LP WHERE region='LP'</li>
          <li>SELECT * FROM PAQUETE_SCZ WHERE region='SCZ'</li>
        </div>
      </div>
      <div class="modal-section">
        <label>Resultado esperado</label>
        <p>Dos fragmentos son ensamblados por el coordinador usando UNION ALL.</p>
      </div>
    `
  },
  'view-reconstruction': {
    title: 'Reconstrucción distribuida',
    subtitle: 'Visualización de unión y join en el coordinador',
    confirm: 'Cerrar',
    body: `
      <div class="modal-section">
        <span class="reconstruction-badge">PAQUETE_LP ∪ PAQUETE_SCZ → VISTA_GLOBAL_PAQUETE</span>
      </div>
      <div class="modal-section">
        <table class="table">
          <thead><tr><th>Fragmento</th><th>Expresión</th></tr></thead>
          <tbody>
            <tr><td>PAQUETE_LP</td><td>SELECT * FROM PAQUETE_LP</td></tr>
            <tr><td>PAQUETE_SCZ</td><td>SELECT * FROM PAQUETE_SCZ</td></tr>
          </tbody>
        </table>
      </div>
      <div class="modal-section">
        <span class="reconstruction-badge">CLIENTE_PUBLICO ⨝ CLIENTE_PRIVADO → CLIENTE_GLOBAL</span>
      </div>
      <div class="modal-section">
        <table class="table">
          <thead><tr><th>Fuente</th><th>Join</th></tr></thead>
          <tbody>
            <tr><td>CLIENTE_PUBLICO</td><td>INNER JOIN id_cliente</td></tr>
            <tr><td>CLIENTE_PRIVADO</td><td>INNER JOIN id_cliente</td></tr>
          </tbody>
        </table>
      </div>
    `
  },
  'global-trace': {
    title: 'Trazabilidad global',
    subtitle: 'Ruta completa de la consulta distribuida',
    confirm: 'Cerrar',
    body: `
      <ul class="status-list">
        <li>1. API Gateway recibe la consulta global.</li>
        <li>2. Coordinador decide fragmentos y planifica subconsultas.</li>
        <li>3. La Paz y Santa Cruz procesan pedidos independientes.</li>
        <li>4. Coordinador reconstruye el resultado final.</li>
      </ul>
    `
  },
  'sync-lp': {
    title: 'Sincronización regional - La Paz',
    subtitle: 'Envía fragmentos locales al coordinador',
    confirm: 'Cerrar',
    body: `
      <div class="modal-section">
        <p>La Paz transmite los fragmentos PAQUETE_LP y MOVIMIENTO_LP al coordinador.</p>
      </div>
      <div class="modal-section">
        <ul class="status-list">
          <li>1. Validación de integridad local.</li>
          <li>2. Envío asíncrono al coordinador.</li>
          <li>3. Actualización de la cola distribuida.</li>
        </ul>
      </div>
    `
  },
  'sync-scz': {
    title: 'Sincronización regional - Santa Cruz',
    subtitle: 'Envía fragmentos locales al coordinador',
    confirm: 'Cerrar',
    body: `
      <div class="modal-section">
        <p>Santa Cruz sincroniza PAQUETE_SCZ y MOVIMIENTO_SCZ con el nodo central.</p>
      </div>
      <div class="modal-section">
        <ul class="status-list">
          <li>1. Comprobación de consistencia.</li>
          <li>2. Envío a la cola de coordinación.</li>
          <li>3. Confirmación de recepción en el coordinador.</li>
        </ul>
      </div>
    `
  },
  'register-movement-lp': {
    title: 'Nuevo movimiento - La Paz',
    subtitle: 'Registro local de evento de transporte',
    confirm: 'Registrar movimiento',
    body: `
      <div class="modal-section"><label>ID Movimiento</label><input type="text" placeholder="MOV-XXX"></div>
      <div class="modal-section"><label>Paquete</label><input type="text" placeholder="LP-2026-009"></div>
      <div class="modal-section"><label>Ubicación</label><input type="text" placeholder="La Paz"></div>
      <div class="modal-section"><label>Estado</label><select><option>Listo</option><option>En cola</option><option>En ruta</option></select></div>
    `
  },
  'register-movement-scz': {
    title: 'Nuevo movimiento - Santa Cruz',
    subtitle: 'Registro local de evento de transporte',
    confirm: 'Registrar movimiento',
    body: `
      <div class="modal-section"><label>ID Movimiento</label><input type="text" placeholder="MOV-XXX"></div>
      <div class="modal-section"><label>Paquete</label><input type="text" placeholder="SCZ-2026-021"></div>
      <div class="modal-section"><label>Ubicación</label><input type="text" placeholder="Santa Cruz"></div>
      <div class="modal-section"><label>Estado</label><select><option>En ruta</option><option>Recibido</option><option>Finalizado</option></select></div>
    `
  }
};
function bindSidebar() {
  document.querySelectorAll('.node-toggle').forEach(button => {
    button.addEventListener('click', () => {
      document.querySelectorAll('.node-toggle').forEach(item => item.classList.remove('active'));
      button.classList.add('active');
      showPanel(button.dataset.node);
    });
  });
}
function showPanel(node) {
  PANEL_IDS.forEach(id => {
    const panel = document.getElementById(`${id}-panel`);
    if (!panel) return;
    panel.classList.toggle('active', id === node);
    panel.classList.toggle('hidden', id !== node);
  });
  const titles = {
    dashboard: 'Estado general del sistema',
    coordinator: 'Nodo coordinador central: orquestación y reconstrucción',
    lapaz: 'Nodo regional La Paz: fragmentación horizontal local',
    scz: 'Nodo regional Santa Cruz: fragmentación horizontal local'
  };
  const element = document.getElementById('page-subtitle');
  if (element) element.textContent = titles[node] || '';
}
function bindModals() {
  const overlay = document.getElementById('modal-overlay');
  const closeButton = document.getElementById('modal-close');
  const cancelButton = document.getElementById('modal-cancel');
  const confirmButton = document.getElementById('modal-confirm');
  document.querySelectorAll('[data-modal]').forEach(button => {
    button.addEventListener('click', () => openModal(button.dataset.modal));
  });
  overlay.addEventListener('click', event => {
    if (event.target === overlay) closeModal();
  });
  closeButton.addEventListener('click', closeModal);
  cancelButton.addEventListener('click', closeModal);
  confirmButton.addEventListener('click', closeModal);
}
function openModal(key) {
  const config = MODAL_PROFILES[key];
  if (!config) return;
  document.getElementById('modal-title').textContent = config.title;
  document.getElementById('modal-subtitle').textContent = config.subtitle;
  document.getElementById('modal-body').innerHTML = config.body;
  document.getElementById('modal-confirm').textContent = config.confirm;
  document.getElementById('modal-overlay').classList.remove('hidden');
}
function closeModal() {
  document.getElementById('modal-overlay').classList.add('hidden');
}
