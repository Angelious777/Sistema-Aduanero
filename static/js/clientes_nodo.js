/**
 * clientes_nodo.js - Controlador Transaccional para Inserciones Distribuidas
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
        
        fila.querySelector(".btn-ver-ficha").addEventListener("click", () => verFichaCliente(c));
        tbody.appendChild(fila);
    });
}

function verFichaCliente(cliente) {
    const modal = document.getElementById("modal-ver-cliente");
    const contenedor = document.getElementById("modal-ver-cliente-content");
    
    if (!modal || !contenedor) {
        console.error("❌ Elementos del modal no encontrados en el DOM.");
        return;
    }

    let bloquePrivadoHTML = "";

    if (cliente.documento === "Consulte a Central" || cliente.correo === "Consulte a Central") {
        bloquePrivadoHTML = `
            <div style="background: #fdf2f2; border: 1px solid #fca5a5; padding: 12px; border-radius: 8px; margin-top: 12px; color: #991b1b; font-size: 13px; line-height: 1.5;">
                🔒 <strong>Datos Privados Resguardados:</strong> Los campos Documento, Correo y Dirección pertenecen al fragmento de seguridad vertical regional y solo pueden auditarse con privilegios desde el Nodo Central.
            </div>
        `;
    } else {
        bloquePrivadoHTML = `
            <div style="margin-top: 14px; border-top: 1px dashed #e2e8f0; padding-top: 14px;">
                <p style="margin: 8px 0; color: #475569;"><strong>🪪 Documento Identidad:</strong><br>
                    <code style="background: #e0e7ff; color: #3730a3; padding: 3px 8px; border-radius: 4px; font-family: monospace; font-size: 13px; display: inline-block; margin-top: 4px;">${cliente.documento_identidad || cliente.documento || 'S/D'}</code>
                </p>
                <p style="margin: 12px 0; color: #475569;"><strong>✉️ Correo Electrónico:</strong><br>
                    <span style="color:#0f172a; font-size: 14px;">${cliente.email || cliente.correo || '—'}</span>
                </p>
                <p style="margin: 12px 0; color: #475569;"><strong>🏠 Dirección Fiscal:</strong><br>
                    <span style="color:#0f172a; font-size: 14px;">${cliente.direccion || '—'}</span>
                </p>
            </div>
        `;
    }

    contenedor.innerHTML = `
        <div style="font-family: system-ui, sans-serif; font-size: 14px; color: #1e293b;">
            <p style="margin: 8px 0; color: #475569;"><strong>📍 Cliente / Razón Social:</strong><br>
                <span style="color:#0f172a; font-weight:600; font-size: 16px;">${cliente.nombre} ${cliente.apellido_paterno || ''} ${cliente.apellido_materno || ''}</span>
            </p>
            <p style="margin: 12px 0; color: #475569;"><strong>📞 Teléfono de Contacto:</strong><br>
                <span style="color:#0f172a; font-size: 14px; font-family: monospace;">${cliente.telefono || '—'}</span>
            </p>
            <p style="margin: 12px 0; color: #475569;"><strong>📅 Registro de Auditoría (ID):</strong><br>
                <small style="color:#64748b; display:block;">Fecha Alta: ${cliente.fecha_registro || cliente.registro || 'Automático'}</small>
                <small style="color:#94a3b8; font-family: monospace; font-size: 11px; display:block; margin-top: 2px;">UUID: ${cliente.id_cliente || cliente.id || '—'}</small>
            </p>
            ${bloquePrivadoHTML}
        </div>
    `;

    modal.classList.add("modal-active");
}

// ==============================================================================
// EJECUCIÓN DEL REGISTRO (CONTRATO CORRECTO CON FLASK)
// ==============================================================================
async function despacharRegistroClienteCoordinador() {
    // 1. Extraer datos del formulario respetando los IDs de tu HTML
    const nombre = document.getElementById("reg-clt-nombre")?.value.trim();
    const paterno = document.getElementById("reg-clt-paterno")?.value.trim();
    const materno = document.getElementById("reg-clt-materno")?.value.trim() || "";
    const telefono = document.getElementById("reg-clt-tel")?.value.trim() || "";
    const documento = document.getElementById("reg-clt-doc")?.value.trim();
    const correo = document.getElementById("reg-clt-correo")?.value.trim() || "";
    const direccion = document.getElementById("reg-clt-direccion")?.value.trim() || "";

    // 2. Mapeo dinámico del fragmento regional según la URL activa
    const path = window.location.pathname.toLowerCase().replace(/-/g, "_");
    let nodoActual = "global";
    if (path.includes("la_paz") || path.includes("lp")) {
        nodoActual = "nodo_lp";
    } else if (path.includes("santa_cruz") || path.includes("scz")) {
        nodoActual = "nodo_scz";
    }

    // 3. Validación de campos obligatorios antes de enviar el paquete de red
    if (!nombre || !paterno || !documento || nodoActual === "global") {
        alert("⚠️ Complete los campos requeridos (*) y asegúrese de estar operando desde un nodo regional.");
        return;
    }

    // 4. Construcción del Payload con las llaves exactas que recibe tu Python (data.get)
    const payload = {
        documento_identidad: documento,
        nombre: nombre,
        apellido_paterno: paterno,
        apellido_materno: materno,
        telefono: telefono,
        direccion: direccion,
        email: correo,
        nodo: nodoActual
    };

    // 5. Bloqueo visual de seguridad del botón interactivo
    const btnRegistrar = document.querySelector(".modal-footer-aduanero button.btn-primario");
    if (btnRegistrar) {
        btnRegistrar.disabled = true;
        btnRegistrar.style.opacity = "0.6";
        btnRegistrar.innerText = "⏳ Registrando...";
    }

    try {
        // CORRECCIÓN CRUCIAL: Apuntar exactamente a tu ruta registrada en Flask
        const response = await fetch('/api/cliente/crear', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        const resultado = await response.json();

        if (response.ok && resultado.success) {
            alert(`✅ ${resultado.data.mensaje}`);
            
            // Reestablecer el entorno gráfico y actualizar los componentes dinámicos
            document.getElementById("form-registro-cliente")?.reset();
            cerrarModalRegistroCliente();
            await listarClientesReplicados();
        } else {
            // Manejar errores de campos NULL o restricciones de unicidad del CI/NIT
            alert(`❌ Error devuelto por el Coordinador:\n${resultado.error || 'Operación rechazada'}`);
        }
    } catch (error) {
        alert(`❌ Fallo en el canal distribuido: No se pudo enlazar comunicación con el clúster.`);
        console.error(error);
    } finally {
        // Devolver la funcionalidad normal al botón
        if (btnRegistrar) {
            btnRegistrar.disabled = false;
            btnRegistrar.style.opacity = "1";
            btnRegistrar.innerText = "Registrar Cliente";
        }
    }
}

// ==============================================================================
// OTROS PROCESOS (SINCRONIZACIÓN Y ACTUALIZACIÓN)
// ==============================================================================
async function ejecutarSincronizacionCascada() {
    const btn = document.getElementById("btn-sincronizar-master");
    if (!btn) return;

    btn.disabled = true;
    btn.style.opacity = "0.6";
    btn.innerText = "⏳ Reconciliando Red de Nodos...";

    try {
        const response = await fetch('/api/clientes/sincronizar', { method: 'POST' });
        const resultado = await response.json();

        if (response.ok && resultado.success) {
            let mensajeExito = "✅ PROCESO DE SINCRONIZACIÓN FINALIZADO\n\n";
            for (const [nodo, metricas] of Object.entries(resultado.reporte)) {
                mensajeExito += `📍 Fragmento: ${nodo.toUpperCase().replace('_', ' ')}\n`;
                mensajeExito += `   • Estado Operativo: ${metricas.estado}\n`;
                mensajeExito += `   • Clientes Nuevos: ${metricas.inserciones}\n\n`;
            }
            alert(mensajeExito);
            await listarClientesReplicados();
        } else {
            alert(`❌ Error: ${resultado.error}`);
        }
    } catch (error) {
        alert(`❌ Fallo de red: ${error.message}`);
    } finally {
        btn.disabled = false;
        btn.style.opacity = "1";
        btn.innerText = "⚡ Sincronizar Datos Regionales";
    }
}

async function forzarActualizacionClientes() {
    await listarClientesReplicados();
}