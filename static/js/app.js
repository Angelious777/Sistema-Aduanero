document.addEventListener('DOMContentLoaded', () => {
  bindSidebar();
  bindModals();
  showPanel('dashboard');
});

// ===================================
// FUNCIONES DEL DASHBOARD
// ===================================

async function cargarDashboard() {
    try {
        const response = await fetch(`${API_BASE}/dashboard`);
        const data = await response.json();

        // 1. Llenar las tarjetas numéricas principales del HTML
        if (data.coordinador) {
            if (document.getElementById('dash-totales')) document.getElementById('dash-totales').innerText = data.coordinador.paquetes_totales || 0;
            if (document.getElementById('dash-transito')) document.getElementById('dash-transito').innerText = data.coordinador.en_transito || 0;
            if (document.getElementById('dash-entregadas')) document.getElementById('dash-entregadas').innerText = data.coordinador.entregadas || 0;
            if (document.getElementById('dash-pendientes')) document.getElementById('dash-pendientes').innerText = data.coordinador.pendientes_retenidos || 0;
            if (document.getElementById('dash-clientes')) document.getElementById('dash-clientes').innerText = data.coordinador.clientes_registrados || 0;
            if (document.getElementById('dash-movimientos')) document.getElementById('dash-movimientos').innerText = data.coordinador.movimientos_dia || 0;

            // 2. Llenar los contadores del Mapa Operativo Nacional
            if (document.getElementById('mapa-count-lp')) document.getElementById('mapa-count-lp').innerText = data.coordinador.paquetes_lp || 0;
            if (document.getElementById('mapa-count-scz')) document.getElementById('mapa-count-scz').innerText = data.coordinador.paquetes_scz || 0;
        }

        // 3. Actualizar los indicadores de estado de los Nodos (Cargando -> Conectado/Desconectado)
        if (data.nodos) {
            const estadoLP = document.getElementById('estado-lp');
            const estadoSCZ = document.getElementById('estado-scz');
            
            if (estadoLP) {
                const est = data.nodos['La Paz'] || 'Desconectado';
                estadoLP.textContent = `● ${est}`;
                estadoLP.className = `status-indicator ${est === 'Conectado' ? 'online' : 'offline'}`;
            }
            if (estadoSCZ) {
                const est = data.nodos['Santa Cruz'] || 'Desconectado';
                estadoSCZ.textContent = `● ${est}`;
                estadoSCZ.className = `status-indicator ${est === 'Conectado' ? 'online' : 'offline'}`;
            }
        }

        // 4. Llenar la tabla de "Actividad Reciente del Sistema"
        const tbodyActividad = document.getElementById('tabla-actividad-reciente');
        if (tbodyActividad && data.actividad_reciente) {
            if (data.actividad_reciente.length === 0) {
                tbodyActividad.innerHTML = `<tr><td colspan="4">No hay eventos recientes.</td></tr>`;
            } else {
                tbodyActividad.innerHTML = data.actividad_reciente.map(act => `
                    <tr>
                        <td><strong>${act.fecha || act}</strong></td>
                        <td>${act.encomienda || '-'}</td>
                        <td>${act.evento || '-'}</td>
                        <td>${act.nodo || '-'}</td>
                    </tr>
                `).join('');
            }
        }

        // 5. Aprovechamos este ciclo para cargar también las tablas globales pesadas
        await cargarTablasConsolidadas();

    } catch (error) {
        console.error("Error crítico al cargar datos del dashboard:", error);
    }
}

// Mantiene las tablas de fondo actualizadas (Vista Consolidada e Historial Unificado)
async function cargarTablasConsolidadas() {
    try {
        // Cargar paquetes globales del ID 'tabla-paquetes'
        const resPaquetes = await fetch(`${API_BASE}/tabla/paquetes_globales`);
        if (resPaquetes.ok) {
            const dataPaquetes = await resPaquetes.json();
            if (dataPaquetes.success) populateTbody('tabla-paquetes', dataPaquetes.data);
        }

        // Cargar movimientos globales del ID 'tabla-movimientos-global'
        const resMovimientos = await fetch(`${API_BASE}/tabla/movimientos_globales`);
        if (resMovimientos.ok) {
            const dataMovimientos = await resMovimientos.json();
            if (dataMovimientos.success) populateTbody('tabla-movimientos-global', dataMovimientos.data);
        }
    } catch (error) {
        console.error("Error al cargar tablas consolidadas de respaldo:", error);
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
