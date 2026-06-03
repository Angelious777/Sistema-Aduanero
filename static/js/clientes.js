/**
 * clientes.js - Controlador Transaccional para Inserciones Distribuidas
 */

window.CLIENTES_GLOBAL = [];

document.addEventListener("DOMContentLoaded", function() {
    listarClientesReplicados();
    
    // Filtros dinámicos reactivos mapeados al JSON real
    document.getElementById("clt-buscar-nombre")?.addEventListener("input", renderizarClientesReplicados);
    document.getElementById("clt-buscar-tel")?.addEventListener("input", renderizarClientesReplicados);
});

// =========================================================
// GESTIÓN DE MODALES (CONMUTACIÓN INMEDIATA)
// =========================================================

function abrirModalRegistroCliente() {
    const modal = document.getElementById("modal-registro-cliente");
    if (modal) {
        modal.classList.add("modal-active");
    }
}

function cerrarModalRegistroCliente() {
    const modal = document.getElementById("modal-registro-cliente");
    if (modal) {
        modal.classList.remove("modal-active");
    }
}

function cerrarModalVerCliente() {
    const modal = document.getElementById("modal-ver-cliente");
    if (modal) {
        modal.classList.remove("modal-active");
    }
}

// =========================================================
// API QUERY & RENDERIZADO REPLICADO LOCAL
// =========================================================

async function listarClientesReplicados() {
    const tbody = document.getElementById("tabla-clientes-replicados-body");
    if (!tbody) return;
    tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;">🔄 Cargando datos del nodo local...</td></tr>`;

    const path = window.location.pathname.toLowerCase().replace(/-/g, "_");
    let nodoActual = "global"; 

    if (path.includes("la_paz") || path.includes("lp")) {
        nodoActual = "nodo_lp";
    } else if (path.includes("santa_cruz") || path.includes("scz")) {
        nodoActual = "nodo_scz";
    }

    try {
        // Consulta directa al puerto del coordinador
        const response = await fetch(`/api/clientes?nodo=${nodoActual}`);
        const resultado = await response.json();
        
        if (resultado.success) {
            window.CLIENTES_GLOBAL = resultado.data || [];
            renderizarClientesReplicados();
        } else {
            tbody.innerHTML = `<tr><td colspan="5" style="color:var(--danger); text-align:center;">❌ Error: ${resultado.error}</td></tr>`;
        }
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="5" style="color:var(--danger); text-align:center;">❌ Desconectado de la red distribuida local</td></tr>`;
    }
}

function renderizarClientesReplicados() {
    const tbody = document.getElementById("tabla-clientes-replicados-body");
    if (!tbody) return;

    const fNombre = document.getElementById("clt-buscar-nombre")?.value.trim().toLowerCase() || "";
    const fTel = document.getElementById("clt-buscar-tel")?.value.trim().toLowerCase() || "";

    tbody.innerHTML = "";
    let filtrados = window.CLIENTES_GLOBAL || [];

    // Filtros utilizando las llaves exactas de tu JSON ("nombre", "telefono")
    if (fNombre) filtrados = filtrados.filter(c => c.nombre && c.nombre.toLowerCase().includes(fNombre));
    if (fTel) filtrados = filtrados.filter(c => c.telefono && c.telefono.toLowerCase().includes(fTel));

    if (filtrados.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;">No hay registros locales en este fragmento.</td></tr>`;
        return;
    }

    filtrados.forEach((c, idx) => {
        const fila = document.createElement("tr");
        fila.innerHTML = `
            <td><code>${idx + 1}</code></td>
            <td><strong>${c.nombre}</strong></td>
            <td><span style="background:#f1f5f9; padding:4px 8px; border-radius:4px; font-family:monospace;">${c.telefono || '—'}</span></td>
            <td><small style="color:#64748b;">${c.registro || 'Automático'}</small></td>
            <td style="text-align: center;">
                <button class="btn-secundario btn-ver-ficha" style="padding: 4px 10px; font-size: 11px; cursor:pointer;">Ver Ficha</button>
            </td>
        `;
        
        // Listener seguro que inyecta el objeto mapeado de la fila
        fila.querySelector(".btn-ver-ficha").addEventListener("click", () => verFichaCliente(c));
        tbody.appendChild(fila);
    });
}

// =========================================================
// VISUALIZACIÓN DINÁMICA DE LA FICHA (CON PARSEO DE DATOS)
// =========================================================

function verFichaCliente(cliente) {
    const modal = document.getElementById("modal-ver-cliente");
    const contenedor = document.getElementById("modal-ver-cliente-content");
    
    if (!modal || !contenedor) {
        console.error("❌ Elementos del modal no encontrados en el DOM.");
        return;
    }

    let bloquePrivadoHTML = "";

    // Si viene enmascarado por la autonomía regional de seguridad vertical
    if (cliente.documento === "Consulte a Central" || cliente.correo === "Consulte a Central") {
        bloquePrivadoHTML = `
            <div style="background: #fdf2f2; border: 1px solid #fca5a5; padding: 12px; border-radius: 8px; margin-top: 12px; color: #991b1b; font-size: 13px; line-height: 1.5;">
                🔒 <strong>Datos Privados Resguardados:</strong> Los campos Documento, Correo y Dirección pertenecen al fragmento de seguridad vertical regional y solo pueden auditarse con privilegios desde el Nodo Central.
            </div>
        `;
    } else {
        // Estructura limpia para datos abiertos unificados desde el Nodo Central Master
        bloquePrivadoHTML = `
            <div style="margin-top: 14px; border-top: 1px dashed #e2e8f0; padding-top: 14px;">
                <p style="margin: 8px 0; color: #475569;"><strong>🪪 Documento Identidad:</strong><br>
                    <code style="background: #e0e7ff; color: #3730a3; padding: 3px 8px; border-radius: 4px; font-family: monospace; font-size: 13px; display: inline-block; margin-top: 4px;">${cliente.documento || 'S/D'}</code>
                </p>
                <p style="margin: 12px 0; color: #475569;"><strong>✉️ Correo Electrónico:</strong><br>
                    <span style="color:#0f172a; font-size: 14px;">${cliente.correo || '—'}</span>
                </p>
                <p style="margin: 12px 0; color: #475569;"><strong>🏠 Dirección Fiscal:</strong><br>
                    <span style="color:#0f172a; font-size: 14px;">${cliente.direccion || '—'}</span>
                </p>
            </div>
        `;
    }

    // Volcado de datos generales en el contenedor
    contenedor.innerHTML = `
        <div style="font-family: system-ui, sans-serif; font-size: 14px; color: #1e293b;">
            <p style="margin: 8px 0; color: #475569;"><strong>📍 Cliente / Razón Social:</strong><br>
                <span style="color:#0f172a; font-weight:600; font-size: 16px;">${cliente.nombre}</span>
            </p>
            <p style="margin: 12px 0; color: #475569;"><strong>📞 Teléfono de Contacto:</strong><br>
                <span style="color:#0f172a; font-size: 14px; font-family: monospace;">${cliente.telefono || '—'}</span>
            </p>
            <p style="margin: 12px 0; color: #475569;"><strong>📅 Registro de Auditoría (ID):</strong><br>
                <small style="color:#64748b; display:block;">Fecha Alta: ${cliente.registro || 'Automático'}</small>
                <small style="color:#94a3b8; font-family: monospace; font-size: 11px; display:block; margin-top: 2px;">UUID: ${cliente.id || '—'}</small>
            </p>
            ${bloquePrivadoHTML}
        </div>
    `;

    // CAMBIO CRUCIAL: Añade la clase operativa. 
    // Recuerda que en tu CSS debes tener: .modal-overlay.modal-active { display: flex !important; opacity: 1 !important; }
    modal.classList.add("modal-active");
}