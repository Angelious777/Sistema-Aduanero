// rutas.js
window.RUTAS_GLOBAL = [];

document.addEventListener("DOMContentLoaded", () => {
    listarRutasReplicadas();
    configurarFiltrosRuta();
});

// Función clave para cargar los select de manera dinámica
async function poblarComboboxAlmacenes(idOrigenSeleccionado = null, idDestinoSeleccionado = null) {
    const selectOrigen = document.getElementById("reg-ruta-origen");
    const selectDestino = document.getElementById("reg-ruta-destino");

    if (!selectOrigen || !selectDestino) return;

    // Marcamos estado de carga
    selectOrigen.innerHTML = '<option value="" disabled selected>⏳ Buscando catálogos...</option>';
    selectDestino.innerHTML = '<option value="" disabled selected>⏳ Buscando catálogos...</option>';

    try {
        // Consultamos la API global de almacenes de tu controlador Flask
        const response = await fetch('/api/almacen/listar'); 
        const resultado = await response.json();

        if (response.ok && resultado.success) {
            let opcionesHTML = '<option value="" disabled selected>-- Seleccione Almacén --</option>';
            
            resultado.data.forEach(alm => {
                // Suponiendo que la estructura de almacen es { id_almacen, nombre, ciudad }
                opcionesHTML += `<option value="${alm.id_almacen}">[ID: ${alm.id_almacen}] ${alm.nombre} (${alm.ciudad || 'Catálogo Master'})</option>`;
            });

            selectOrigen.innerHTML = opcionesHTML;
            selectDestino.innerHTML = opcionesHTML;

            // Si es edición, pre-seleccionamos los valores que ya tenía la ruta
            if (idOrigenSeleccionado) selectOrigen.value = idOrigenSeleccionado;
            if (idDestinoSeleccionado) selectDestino.value = idDestinoSeleccionado;
        } else {
            const errStr = `<option value="" disabled>❌ Error al cargar catálogos</option>`;
            selectOrigen.innerHTML = errStr;
            selectDestino.innerHTML = errStr;
        }
    } catch (error) {
        const errStr = `<option value="" disabled>❌ Error de conexión de red</option>`;
        selectOrigen.innerHTML = errStr;
        selectDestino.innerHTML = errStr;
    }
}

async function abrirModalRegistroRuta() {
    const modal = document.getElementById("modal-registro-ruta");
    if (modal) {
        modal.style.display = "flex";
        // Si es una creación nueva, cargamos los combobox limpios
        if (document.getElementById("reg-ruta-accion").value === "CREAR") {
            await poblarComboboxAlmacenes();
        }
    }
}

function cerrarModalRegistroRuta() {
    const modal = document.getElementById("modal-registro-ruta");
    if (modal) {
        modal.style.display = "none";
        document.getElementById("form-registro-ruta").reset();
        document.getElementById("reg-ruta-id").disabled = false;
        document.getElementById("reg-ruta-accion").value = "CREAR";
        document.getElementById("modal-ruta-titulo").innerText = "📝 Registrar Nueva Ruta Distribuida";
        document.getElementById("btn-ruta-guardar").innerText = "Confirmar Inserción";
    }
}

async function prepararEdicionRuta(id, id_origen, id_destino, descripcion) {
    document.getElementById("reg-ruta-accion").value = "EDITAR";
    document.getElementById("modal-ruta-titulo").innerText = "✏️ Editar Ruta Replicada";
    document.getElementById("btn-ruta-guardar").innerText = "Guardar Cambios";
    
    const inputId = document.getElementById("reg-ruta-id");
    inputId.value = id;
    inputId.disabled = true; 

    document.getElementById("reg-ruta-descripcion").value = descripcion;
    
    // Primero forzamos la carga de almacenes y pasamos los IDs para seleccionarlos
    await poblarComboboxAlmacenes(id_origen, id_destino);
    
    // Abrimos el modal con los combos listos
    const modal = document.getElementById("modal-registro-ruta");
    if (modal) modal.style.display = "flex";
}

async function listarRutasReplicadas() {
    const tbody = document.getElementById("tabla-rutas-replicadas-body");
    if (!tbody) return;

    tbody.innerHTML = `<tr><td colspan="4" style="text-align: center; padding: 24px;">⏳ Consultando topología de rutas...</td></tr>`;

    const path = window.location.pathname.toLowerCase();
    let urlEndpoint = '/api/ruta/listar';
    
    if (path.includes("la_paz") || path.includes("lp")) {
        urlEndpoint = '/api/rutas/la-paz';
    } else if (path.includes("santa_cruz") || path.includes("scz")) {
        urlEndpoint = '/api/rutas/santa-cruz';
    }

    try {
        const response = await fetch(urlEndpoint);
        const resultado = await response.json();

        if (response.ok && resultado.success) {
            window.RUTAS_GLOBAL = resultado.data;
            inyectarFilasRutas(window.RUTAS_GLOBAL);
        } else {
            tbody.innerHTML = `<tr><td colspan="4" style="text-align: center; color:red; padding: 24px;">❌ Error: ${resultado.error}</td></tr>`;
        }
    } catch (error) {
        tbody.innerHTML = `<tr><td colspan="4" style="text-align: center; color: red; padding: 24px;">❌ Fallo de comunicación.</td></tr>`;
    }
}

async function despacharRegistroRutaCoordinador() {
    const accion = document.getElementById("reg-ruta-accion").value;
    const id = document.getElementById("reg-ruta-id").value;
    const id_origen = document.getElementById("reg-ruta-origen").value;
    const id_destino = document.getElementById("reg-ruta-destino").value;
    const descripcion = document.getElementById("reg-ruta-descripcion").value.trim();

    if (!id_origen || !id_destino) {
        alert("⚠️ Por favor seleccione los almacenes de Origen y Destino.");
        return;
    }

    if (id_origen === id_destino) {
        alert("⚠️ Validación Local: El almacén de origen no puede ser igual al de destino.");
        return;
    }

    const payload = { 
        id_ruta: parseInt(id), 
        id_almacen_origen: parseInt(id_origen),
        id_almacen_destino: parseInt(id_destino),
        descripcion: descripcion
    };
    
    const url = accion === "EDITAR" ? '/api/ruta/editar' : '/api/ruta/crear';

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const res = await response.json();
        if (res.success) {
            alert(`✅ Operación distribuida realizada con éxito.`);
            cerrarModalRegistroRuta();
            await listarRutasReplicadas();
        } else {
            alert(`❌ Restricción del Coordinador: ${res.error}`);
        }
    } catch (e) {
        alert(`🚨 Error en canal transaccional técnico: ${e.message}`);
    }
}

async function eliminarRutaCoordinador(id) {
    if (!confirm(`⚠️ ¿Está seguro de eliminar la Ruta ID ${id} de forma síncrona en toda la red?`)) return;

    try {
        const response = await fetch('/api/ruta/eliminar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id_ruta: id })
        });
        const res = await response.json();
        if (res.success) {
            alert("🗑️ Registro revocado del ecosistema global.");
            await listarRutasReplicadas();
        } else {
            alert(`❌ Restricción: ${res.error}`);
        }
    } catch (e) {
        alert("❌ Error al procesar la revocación.");
    }
}

function configurarFiltrosRuta() {
    const inputDesc = document.getElementById("ruta-buscar-descripcion");
    const inputCodigo = document.getElementById("ruta-buscar-codigo");

    const ejecutarFiltro = () => {
        const valDesc = inputDesc?.value.toLowerCase().trim() || "";
        const valCodigo = inputCodigo?.value.toLowerCase().trim() || "";

        const filtrados = window.RUTAS_GLOBAL.filter(rut => {
            const cumpleDesc = String(rut.descripcion).toLowerCase().includes(valDesc);
            const cumpleCodigo = String(rut.id_ruta).toLowerCase().includes(valCodigo) || 
                                 String(rut.id_almacen_origen).toLowerCase().includes(valCodigo) ||
                                 String(rut.id_almacen_destino).toLowerCase().includes(valCodigo);
            return cumpleDesc && cumpleCodigo;
        });
        inyectarFilasRutas(filtrados);
    };

    inputDesc?.addEventListener("input", ejecutarFiltro);
    inputCodigo?.addEventListener("input", ejecutarFiltro);
}

function inyectarFilasRutas(lista) {
    const tbody = document.getElementById("tabla-rutas-replicadas-body");
    if (!tbody) return;

    if (lista.length === 0) {
        tbody.innerHTML = `<tr><td colspan="4" style="text-align: center; padding: 24px; color: #94a3b8;">🔍 Sin resultados.</td></tr>`;
        return;
    }

    tbody.innerHTML = "";
    lista.forEach((r) => {
        const fila = document.createElement("tr");
        fila.innerHTML = `
            <td><code>${r.id_ruta}</code></td>
            <td><strong>${r.descripcion || 'Sin descripción'}</strong></td>
            <td>
                <div style="display:flex; align-items:center; gap:8px; font-family:monospace; font-size:12px;">
                    <span style="background:#e0f2fe; color:#0369a1; padding:4px 8px; border-radius:6px; font-weight:600;">ID: ${r.id_almacen_origen}</span>
                    <span style="color:#94a3b8; font-weight:bold;">➔</span>
                    <span style="background:#f0fdf4; color:#166534; padding:4px 8px; border-radius:6px; font-weight:600;">ID: ${r.id_almacen_destino}</span>
                </div>
            </td>
            <td style="text-align: center;">
                <div style="display:flex; gap:6px; justify-content:center;">
                    <button class="btn-secundario" style="padding: 4px 10px; font-size: 12px; background:#f59e0b; color:white; border:none; border-radius:4px; cursor:pointer;" onclick="prepararEdicionRuta(${r.id_ruta}, ${r.id_almacen_origen}, ${r.id_almacen_destino}, '${r.descripcion}')">✏️ Editar</button>
                    <button class="btn-danger" style="padding: 4px 10px; font-size: 12px; background:#ef4444; color:white; border:none; border-radius:4px; cursor:pointer;" onclick="eliminarRutaCoordinador(${r.id_ruta})">🗑️ Eliminar</button>
                </div>
            </td>
        `;
        tbody.appendChild(fila);
    });
}

async function ejecutarSincronizacionRutasCascada() {
    const btn = document.getElementById("btn-sincronizar-rutas-master");
    if (btn) {
        btn.disabled = true;
        btn.innerText = "⏳ Sincronizando...";
    }
    try {
        const response = await fetch('/api/ruta/sincronizar', { method: 'POST' });
        const res = await response.json();
        if (response.ok && res.success) {
            alert(`⚡ ${res.mensaje}`);
            await listarRutasReplicadas();
        } else {
            alert(`❌ Error: ${res.error}`);
        }
    } catch (error) {
        alert("❌ Error crítico en infraestructura de red.");
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerText = "⚡ Sincronizar Catálogo";
        }
    }
}