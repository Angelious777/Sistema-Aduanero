// ===================================
// CONFIGURACION GLOBAL
// ===================================

const API_BASE = '/api';
const PANEL_IDS = ['dashboard', 'coordinator', 'lapaz', 'scz'];

// Estado global de la aplicación
const APP_STATE = {
  currentPanel: 'dashboard',
  dashboardData: null,
  selectedNodo: null,
  paqueteActual: null
};

// ===================================
// INICIALIZACION
// ===================================

document.addEventListener('DOMContentLoaded', () => {
  bindSidebar();
  bindModals();
  bindFormularios();
  cargarDashboard();
  showPanel('dashboard');
  
  // Recargar datos cada 30 segundos
  setInterval(cargarDashboard, 30000);
});

// ===================================
// FUNCIONES DEL DASHBOARD
// ===================================

async function cargarDashboard() {
  try {
    const response = await fetch(`${API_BASE}/dashboard`);
    const data = await response.json();
    
    if (data.success) {
      APP_STATE.dashboardData = data.data;
      actualizarDashboard(data.data);
    }
  } catch (error) {
    console.error('Error cargando dashboard:', error);
  }
}

function actualizarDashboard(dashboard) {
  // Actualizar métricas principales
  const metricas = dashboard.metricas;
  
  const metricCards = document.querySelectorAll('#dashboard-panel .metric-card');
  if (metricCards.length >= 4) {
    metricCards[0].querySelector('strong').textContent = metricas.nodos_sincronizados || 0;
    metricCards[1].querySelector('strong').textContent = (metricas.trafico_distribuido || 0) + ' trans.';
    metricCards[2].querySelector('strong').textContent = metricas.operaciones_pendientes || 0;
    metricCards[3].querySelector('strong').textContent = metricas.fragmentos_activos || 0;
  }
  
  // Actualizar estado de conectividad
  const conectividadGrid = document.querySelector('.connectivity-grid');
  if (conectividadGrid && dashboard.estado_conectividad) {
    conectividadGrid.innerHTML = '';
    dashboard.estado_conectividad.forEach(nodo => {
      const status = nodo.estado === 'Conectado' ? 'online' : 'offline';
      const html = `
        <div class="connection-row">
          <div class="connection-name">${nodo.nombre}</div>
          <span class="status-pill ${status}">${nodo.estado}</span>
        </div>
      `;
      conectividadGrid.innerHTML += html;
    });
  }
  
  // Actualizar topología
  if (dashboard.topologia && dashboard.topologia.nodos_regionales) {
    const topologyGrid = document.querySelector('.topology-grid');
    if (topologyGrid) {
      // Limpiar y reconstruir
      const nodos = dashboard.topologia.nodos_regionales;
      let html = '';
      
      // Nodo 1
      if (nodos[0]) {
        html += `
          <article class="topology-node remote-node">
            <strong>${nodos[0].nombre}</strong>
            <span>${nodos[0].motor}</span>
            <div class="node-fragments">
              ${nodos[0].fragmentos.map(f => `<span>${f}</span>`).join('')}
            </div>
          </article>
        `;
      }
      
      // Coordinador
      html += `
        <div class="topology-center">
          <span class="topology-label">Coordinador</span>
          <span class="topology-status">SQL Server · Query Parser · 2PC</span>
        </div>
      `;
      
      // Nodo 2
      if (nodos[1]) {
        html += `
          <article class="topology-node remote-node">
            <strong>${nodos[1].nombre}</strong>
            <span>${nodos[1].motor}</span>
            <div class="node-fragments">
              ${nodos[1].fragmentos.map(f => `<span>${f}</span>`).join('')}
            </div>
          </article>
        `;
      }
      
      topologyGrid.innerHTML = html;
    }
  }
  
  // Actualizar actividad reciente
  if (dashboard.actividad_reciente) {
    const actividad = document.querySelector('#dashboard-panel .split-panel .compact-panel:first-child .status-list');
    if (actividad) {
      actividad.innerHTML = dashboard.actividad_reciente
        .map(act => `<li>${act}</li>`)
        .join('');
    }
  }
}

async function cargarCatalogoFragmentacion() {
  try {
    const response = await fetch(`${API_BASE}/catalogo`);
    const data = await response.json();
    const tbody = document.getElementById('catalogo-body');

    if (!tbody) return;

    if (!data.success || !Array.isArray(data.data) || data.data.length === 0) {
      tbody.innerHTML = `<tr><td colspan='6'>No hay fragmentos disponibles en el nodo central.</td></tr>`;
      return;
    }

    tbody.innerHTML = data.data.map(item => `
      <tr>
        <td>${item.id_fragmento || ''}</td>
        <td>${item.nombre_fragmento || ''}</td>
        <td>${item.tabla_original || ''}</td>
        <td>${item.tipo_fragmentacion || ''}</td>
        <td>${item.nodo_ubicacion || ''}</td>
        <td>${item.descripcion || ''}</td>
      </tr>
    `).join('');
  } catch (error) {
    console.error('Error cargando catálogo de fragmentación:', error);
    const tbody = document.getElementById('catalogo-body');
    if (tbody) {
      tbody.innerHTML = `<tr><td colspan='6'>Error cargando catálogo: ${error.message || error}</td></tr>`;
    }
  }
}

// ===================================
// FUNCIONES DE PAQUETES
// ===================================

async function cargarPaquetesNodo(nodo) {
  try {
    if (nodo.toLowerCase() === 'scz') {
      // Cargar tabla operativa y financiera por separado
      await cargarPaqueteOperativoSCZ();
      await cargarPaqueteFinancieroSCZ();
      return;
    }

    const response = await fetch(`${API_BASE}/tabla/paquete/${nodo}`);
    const data = await response.json();

    if (data.success) {
      mostrarTabla(data.data, nodo, 'paquete');
    }
  } catch (error) {
    console.error('Error cargando paquetes:', error);
  }
}

async function cargarMovimientosNodo(nodo) {
  try {
    if (nodo.toLowerCase() === 'scz') {
      // Cargar movimientos SCZ y volcarlos en su tabla específica
      const response = await fetch(`${API_BASE}/tabla/movimiento/scz`);
      const data = await response.json();
      if (data.success) {
        populateTbody('movimiento-scz-body', data.data);
      }
      return;
    }

    const response = await fetch(`${API_BASE}/tabla/movimiento/${nodo}`);
    const data = await response.json();

    if (data.success) {
      mostrarTabla(data.data, nodo, 'movimiento');
    }
  } catch (error) {
    console.error('Error cargando movimientos:', error);
  }
}

function mostrarTabla(datos, nodo, tipo) {
  let panelId = '';
  let tablaSelector = '';
  
  if (tipo === 'paquete') {
    if (nodo.toLowerCase() === 'lapaz') {
      panelId = 'lapaz-panel';
      tablaSelector = '#lapaz-panel .topology-panel table';
    } else {
      panelId = 'scz-panel';
      tablaSelector = '#scz-panel .topology-panel table';
    }
  } else {
    if (nodo.toLowerCase() === 'lapaz') {
      panelId = 'lapaz-panel';
      tablaSelector = '#lapaz-panel .topology-panel table';
    } else {
      panelId = 'scz-panel';
      tablaSelector = '#scz-panel .topology-panel table';
    }
  }
  
  // Mostrar datos en tabla (si existe)
  const tabla = document.querySelector(tablaSelector);
  if (tabla && datos.length > 0) {
    const tbody = tabla.querySelector('tbody');
    if (tbody) {
      const filas = Object.entries(datos[0]).map(([key, value]) => `<td>${value}</td>`).join('');
      tbody.innerHTML = datos.map(row => 
        `<tr>${Object.values(row).map(v => `<td>${v}</td>`).join('')}</tr>`
      ).join('');
    }
  }
}

function populateTbody(tbodyId, datos) {
  const tbody = document.getElementById(tbodyId);
  if (!tbody) return;

  if (!Array.isArray(datos) || datos.length === 0) {
    tbody.innerHTML = `<tr><td colspan='${tbody.parentElement.querySelectorAll('th').length}'>No hay datos.</td></tr>`;
    return;
  }

  // Generar filas tomando las claves del primer objeto como orden
  const keys = Object.keys(datos[0]);
  tbody.innerHTML = datos.map(row => `
    <tr>
      ${keys.map(k => `<td>${row[k] !== null && row[k] !== undefined ? row[k] : ''}</td>`).join('')}
    </tr>
  `).join('');
}

async function cargarPaqueteOperativoSCZ() {
  try {
    const response = await fetch(`${API_BASE}/tabla/paquete_operativo/scz`);
    const data = await response.json();
    if (data.success) {
      populateTbody('paquete-operativo-scz-body', data.data);
    }
  } catch (error) {
    console.error('Error cargando paquete operativo SCZ:', error);
  }
}

async function cargarPaqueteFinancieroSCZ() {
  try {
    const response = await fetch(`${API_BASE}/tabla/paquete_financiero/scz`);
    const data = await response.json();
    if (data.success) {
      populateTbody('paquete-financiero-scz-body', data.data);
    }
  } catch (error) {
    console.error('Error cargando paquete financiero SCZ:', error);
  }
}

// ===================================
// FUNCIONES DE MODALES
// ===================================

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
      <div class="modal-section"><label>ID Movimiento</label><input type="text" class="mov-id" placeholder="MOV-XXX"></div>
      <div class="modal-section"><label>Paquete</label><input type="text" class="mov-paquete" placeholder="LP-2026-009"></div>
      <div class="modal-section"><label>Ubicación</label><input type="text" class="mov-ubicacion" placeholder="La Paz"></div>
      <div class="modal-section"><label>Estado</label><select class="mov-estado"><option>Listo</option><option>En cola</option><option>En ruta</option></select></div>
    `,
    handler: () => registrarMovimientoLaPaz()
  },
  'register-movement-scz': {
    title: 'Nuevo movimiento - Santa Cruz',
    subtitle: 'Registro local de evento de transporte',
    confirm: 'Registrar movimiento',
    body: `
      <div class="modal-section"><label>ID Movimiento</label><input type="text" class="mov-id" placeholder="MOV-XXX"></div>
      <div class="modal-section"><label>Paquete</label><input type="text" class="mov-paquete" placeholder="SCZ-2026-021"></div>
      <div class="modal-section"><label>Ubicación</label><input type="text" class="mov-ubicacion" placeholder="Santa Cruz"></div>
      <div class="modal-section"><label>Estado</label><select class="mov-estado"><option>En ruta</option><option>Recibido</option><option>Finalizado</option></select></div>
    `,
    handler: () => registrarMovimientoSantaCruz()
  }
};

function bindSidebar() {
  document.querySelectorAll('.node-toggle').forEach(button => {
    button.addEventListener('click', () => {
      document.querySelectorAll('.node-toggle').forEach(item => item.classList.remove('active'));
      button.classList.add('active');
      const node = button.dataset.node;
      APP_STATE.currentPanel = node;
      showPanel(node);
      
      // Cargar datos específicos del nodo
      if (node === 'lapaz') {
        cargarPaquetesNodo('lapaz');
        cargarMovimientosNodo('lapaz');
      } else if (node === 'scz') {
        cargarPaquetesNodo('scz');
        cargarMovimientosNodo('scz');
      }
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

  if (node === 'coordinator') {
    cargarCatalogoFragmentacion();
  }
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
  confirmButton.addEventListener('click', () => {
    const modalKey = confirmButton.dataset.modalKey;
    if (MODAL_PROFILES[modalKey] && MODAL_PROFILES[modalKey].handler) {
      MODAL_PROFILES[modalKey].handler();
    }
    closeModal();
  });
}

function openModal(key) {
  const config = MODAL_PROFILES[key];
  if (!config) return;
  
  document.getElementById('modal-title').textContent = config.title;
  document.getElementById('modal-subtitle').textContent = config.subtitle;
  document.getElementById('modal-body').innerHTML = config.body;
  document.getElementById('modal-confirm').textContent = config.confirm;
  document.getElementById('modal-confirm').dataset.modalKey = key;
  document.getElementById('modal-overlay').classList.remove('hidden');
}

function closeModal() {
  document.getElementById('modal-overlay').classList.add('hidden');
}

// ===================================
// FUNCIONES DE FORMULARIOS
// ===================================

function bindFormularios() {
  // Aquí se pueden agregar más binding de formularios si es necesario
}

async function registrarMovimientoLaPaz() {
  const idMov = document.querySelector('.mov-id')?.value;
  const paquete = document.querySelector('.mov-paquete')?.value;
  const ubicacion = document.querySelector('.mov-ubicacion')?.value;
  const estado = document.querySelector('.mov-estado')?.value;
  
  if (!idMov || !paquete || !ubicacion || !estado) {
    alert('Por favor complete todos los campos');
    return;
  }
  
  try {
    const response = await fetch(`${API_BASE}/movimiento/registrar`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        id_movimiento: idMov,
        id_paquete: paquete,
        ubicacion: ubicacion,
        estado: estado,
        nodo: 'lapaz'
      })
    });
    
    const data = await response.json();
    if (data.success) {
      alert('Movimiento registrado exitosamente');
      cargarMovimientosNodo('lapaz');
    } else {
      alert('Error: ' + data.error);
    }
  } catch (error) {
    alert('Error registrando movimiento: ' + error);
  }
}

async function registrarMovimientoSantaCruz() {
  const idMov = document.querySelector('.mov-id')?.value;
  const paquete = document.querySelector('.mov-paquete')?.value;
  const ubicacion = document.querySelector('.mov-ubicacion')?.value;
  const estado = document.querySelector('.mov-estado')?.value;
  
  if (!idMov || !paquete || !ubicacion || !estado) {
    alert('Por favor complete todos los campos');
    return;
  }
  
  try {
    const response = await fetch(`${API_BASE}/movimiento/registrar`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        id_movimiento: idMov,
        id_paquete: paquete,
        ubicacion: ubicacion,
        estado: estado,
        nodo: 'scz'
      })
    });
    
    const data = await response.json();
    if (data.success) {
      alert('Movimiento registrado exitosamente');
      cargarMovimientosNodo('scz');
    } else {
      alert('Error: ' + data.error);
    }
  } catch (error) {
    alert('Error registrando movimiento: ' + error);
  }
}
