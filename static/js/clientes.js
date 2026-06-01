/**
 * clientes.js - Controlador Transaccional para Inserciones Distribuidas
 */

window.CLIENTES_GLOBAL = [];

document.addEventListener("DOMContentLoaded", function() {
    listarClientesReplicados();
    
    // Filtros dinámicos reactivos con desestructuración segura
    document.getElementById("clt-buscar-nombre")?.addEventListener("input", renderizarClientesReplicados);
    document.getElementById("clt-buscar-doc")?.addEventListener("input", renderizarClientesReplicados);
    document.getElementById("clt-buscar-tel")?.addEventListener("input", renderizarClientesReplicados);
});

// =========================================================
// GESTIÓN DE MODALES (Control Seguro de Interfaz de Usuario)
// =========================================================

// =========================================================
// GESTIÓN DE MODALES (Sincronizado con clases CSS Activas)
// =========================================================

function abrirModalRegistroCliente() {
    console.log("--> Intentando abrir el modal de registro...");
    const modal = document.getElementById("modal-registro-cliente");
    if (modal) {
        // En lugar de usar .style.display, añadimos la clase que quita el pointer-events y sube la opacidad
        modal.classList.add("modal-active");
        console.log("--> Modal desplegado e interactuable con éxito.");
    } else {
        console.error("❌ Error Crítico: No se localizó 'modal-registro-cliente' en el DOM actual.");
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
// API QUERY & RENDERIZADO REPLICADO
// =========================================================

async function listarClientesReplicados() {
    const tbody = document.getElementById("tabla-clientes-replicados-body");
    if (!tbody) return;
    tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;">🔄 Cargando datos del nodo local...</td></tr>`;

    // === DETECCIÓN DEL NODO ACTUAL (Igual a tu lógica de guardado) ===
    const path = window.location.pathname.toLowerCase().replace(/-/g, "_");
    let nodoActual = "global"; // Por si estás en una vista de administración central

    if (path.includes("la_paz") || path.includes("lp")) {
        nodoActual = "nodo_lp";
    } else if (path.includes("santa_cruz") || path.includes("scz")) {
        nodoActual = "nodo_scz";
    }

    try {
        // Enviamos el nodo como Query Parameter
        const response = await fetch(`/api/clientes?nodo=${nodoActual}`);
        const resultado = await response.json();
        if (resultado.success) {
            window.CLIENTES_GLOBAL = resultado.data || [];
            renderizarClientesReplicados();
        } else {
            tbody.innerHTML = `<tr><td colspan="6" style="color:var(--danger);">❌ Error: ${resultado.error}</td></tr>`;
        }
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="6" style="color:var(--danger);">❌ Desconectado de la red distribuida local</td></tr>`;
    }
}

function renderizarClientesReplicados() {
    const tbody = document.getElementById("tabla-clientes-replicados-body");
    if (!tbody) return;

    const fNombre = document.getElementById("clt-buscar-nombre")?.value.trim().toLowerCase() || "";
    const fDoc = document.getElementById("clt-buscar-doc")?.value.trim().toLowerCase() || "";
    const fTel = document.getElementById("clt-buscar-tel")?.value.trim().toLowerCase() || "";

    tbody.innerHTML = "";
    let filtrados = window.CLIENTES_GLOBAL || [];

    if (fNombre) filtrados = filtrados.filter(c => c.nombre && c.nombre.toLowerCase().includes(fNombre));
    if (fDoc) filtrados = filtrados.filter(c => c.documento && c.documento.toLowerCase().includes(fDoc));
    if (fTel) filtrados = filtrados.filter(c => c.telefono && c.telefono.toLowerCase().includes(fTel));

    if (filtrados.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;">No hay registros unificados disponibles.</td></tr>`;
        return;
    }

    filtrados.forEach((c, idx) => {
        const fila = document.createElement("tr");
        fila.innerHTML = `
            <td><code>${idx + 1}</code></td>
            <td><strong>${c.nombre}</strong></td>
            <td><span style="background:#e0e7ff; padding:2px 6px; border-radius:4px;">${c.documento || 'S/D'}</span></td>
            <td>${c.telefono || '—'}</td>
            <td><small>${c.correo || '—'}</small></td>
            <td style="text-align: center;">
                <button class="btn-secundario" style="padding: 4px 8px; font-size: 11px;" onclick='verFichaCliente(${JSON.stringify(c)})'>Ver Ficha</button>
            </td>
        `;
        tbody.appendChild(fila);
    });
}

// =========================================================
// PROCESAMIENTO Y ENVÍO DEL JSON AL COORDINADOR BACKEND
// =========================================================

async function despacharRegistroClienteCoordinador() {
    // Lectura defensiva de nodos para evitar congelamientos en consola
    const elNombre = document.getElementById("reg-clt-nombre");
    const elPaterno = document.getElementById("reg-clt-paterno");
    const elMaterno = document.getElementById("reg-clt-materno");
    const elDoc = document.getElementById("reg-clt-doc");
    const elTel = document.getElementById("reg-clt-tel");
    const elCorreo = document.getElementById("reg-clt-correo");
    const elDireccion = document.getElementById("reg-clt-direccion");

    const nombre = elNombre ? elNombre.value.trim() : "";
    const apellidoPaterno = elPaterno ? elPaterno.value.trim() : "";
    const apellidoMaterno = elMaterno ? elMaterno.value.trim() : "";
    const documento = elDoc ? elDoc.value.trim() : "";
    const telefono = elTel ? elTel.value.trim() : "";
    const correo = elCorreo ? elCorreo.value.trim() : "";
    const direccion = elDireccion ? elDireccion.value.trim() : "";

    if (!nombre || !apellidoPaterno || !documento) {
        alert("⚠️ Los campos Nombre, Apellido Paterno y Documento de Identidad son estrictamente obligatorios (Restricción SQL NOT NULL).");
        return;
    }

    // === DETECCIÓN NORMALIZADA DE NODO REGIONAL ===
    const path = window.location.pathname.toLowerCase();
    let nodoDestino = "";

    // Reemplazamos guiones medios por guiones bajos para estandarizar la búsqueda
    const pathNormalizado = path.replace(/-/g, "_");

    if (pathNormalizado.includes("la_paz") || pathNormalizado.includes("lp")) {
        nodoDestino = "nodo_lp";
    } else if (pathNormalizado.includes("santa_cruz") || pathNormalizado.includes("scz")) {
        nodoDestino = "nodo_scz";
    } else {
        // Fallback por si usan el Badge visual del sistema
        const badgeTexto = document.querySelector(".badge-nodo")?.textContent.toLowerCase() || "";
        if (badgeTexto.includes("scz") || badgeTexto.includes("cruz")) {
            nodoDestino = "nodo_scz";
        } else if (badgeTexto.includes("lp") || badgeTexto.includes("paz")) {
            nodoDestino = "nodo_lp";
        } else {
            console.error(`Detección fallida. Path original: "${path}"`);
            alert(`❌ Error de Enrutamiento Regional:\nNo se pudo deducir el nodo desde la URL ("${path}").`);
            return;
        }
    }
    console.log(`--> Nodo asignado con éxito: ${nodoDestino}`);

    const payload = {
        documento_identidad: documento,
        nombre: nombre,
        apellido_paterno: apellidoPaterno,
        apellido_materno: apellidoMaterno || null,
        telefono: telefono || null,
        direccion: direccion || null,
        email: correo || null,
        nodo: nodoDestino
    };

    try {
        const response = await fetch('/api/cliente/crear', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const resultado = await response.json();
        if (response.ok && resultado.success) {
            alert(`✅ Inserción Exitosa:\n${resultado.data.mensaje}`);
            cerrarModalRegistroCliente();
            document.getElementById("form-registro-cliente")?.reset();
            listarClientesReplicados();
        } else {
            alert(`❌ Error del Motor Relacional:\n${resultado.error}`);
        }
    } catch (error) {
        alert(`❌ Error crítico en red de nodos: ${error.message}`);
    }
}

function verFichaCliente(cliente) {
    const modal = document.getElementById("modal-ver-cliente");
    const contenedor = document.getElementById("modal-ver-cliente-content");
    if (!modal || !contenedor) return;
    contenedor.innerHTML = `
        <p><strong>📍 Cliente / Razón Social:</strong><br>${cliente.nombre}</p>
        <p><strong>🪪 Documento Identidad:</strong><br><code>${cliente.documento}</code></p>
        <p><strong>📞 Teléfono:</strong><br>${cliente.telefono || '—'}</p>
        <p><strong>✉️ Correo Electrónico:</strong><br>${cliente.correo || '—'}</p>
        <p><strong>🏠 Dirección Fiscal:</strong><br>${cliente.direccion || 'No visible en este fragmento'}</p>
        <p><strong>📅 Registro de Auditoría:</strong><br><small>${cliente.registro || 'Automático'}</small></p>
    `;
    modal.style.setProperty("display", "flex", "important");
}