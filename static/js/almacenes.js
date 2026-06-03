// almacenes.js
window.ALMACENES_GLOBAL = [];

document.addEventListener("DOMContentLoaded", () => {
    listarAlmacenesReplicados();
    configurarFiltrosAlmacen();
});

function abrirModalRegistroAlmacen() {
    const modal = document.getElementById("modal-registro-almacen");
    if (modal) modal.style.display = "flex";
}

function cerrarModalRegistroAlmacen() {
    const modal = document.getElementById("modal-registro-almacen");
    if (modal) {
        modal.style.display = "none";
        document.getElementById("form-registro-almacen").reset();
        document.getElementById("reg-alm-id").disabled = false;
        document.getElementById("reg-alm-accion").value = "CREAR";
        document.getElementById("modal-almacen-titulo").innerText = "📝 Registrar Nuevo Almacén Distribuido";
        document.getElementById("btn-almacen-guardar").innerText = "Confirmar Inserción";
    }
}

function prepararEdicionAlmacen(id, nombre, ciudad, direccion, nodo_responsable) {
    document.getElementById("reg-alm-accion").value = "EDITAR";
    document.getElementById("modal-almacen-titulo").innerText = "✏️ Editar Almacén Replicado";
    document.getElementById("btn-almacen-guardar").innerText = "Guardar Cambios";
    
    const inputId = document.getElementById("reg-alm-id");
    inputId.value = id;
    inputId.disabled = true; 

    document.getElementById("reg-alm-nombre").value = nombre;
    
    // Mapeamos hacia el input combinado 'Ubicación' usando un guion para procesarlo después
    document.getElementById("reg-alm-ubicacion").value = `${ciudad} - ${direccion}`;
    
    abrirModalRegistroAlmacen();
}

async function listarAlmacenesReplicados() {
    const tbody = document.getElementById("tabla-almacenes-replicados-body");
    if (!tbody) return;

    tbody.innerHTML = `<tr><td colspan="4" style="text-align: center; padding: 24px;">⏳ Consultando topología de la red...</td></tr>`;

    const path = window.location.pathname.toLowerCase();
    let urlEndpoint = '/api/almacen/listar';
    
    if (path.includes("la_paz") || path.includes("lp")) {
        urlEndpoint = '/api/almacenes/la-paz';
    } else if (path.includes("santa_cruz") || path.includes("scz")) {
        urlEndpoint = '/api/almacenes/santa-cruz';
    }

    try {
        const response = await fetch(urlEndpoint);
        const resultado = await response.json();

        if (response.ok && resultado.success) {
            window.ALMACENES_GLOBAL = resultado.data;
            inyectarFilasFiltradas(window.ALMACENES_GLOBAL);
        } else {
            tbody.innerHTML = `<tr><td colspan="4" style="text-align: center; color:red; padding: 24px;">❌ Error: ${resultado.error}</td></tr>`;
        }
    } catch (error) {
        tbody.innerHTML = `<tr><td colspan="4" style="text-align: center; color: red; padding: 24px;">❌ Fallo de comunicación.</td></tr>`;
    }
}

async function despacharRegistroAlmacenCoordinador() {
    const accion = document.getElementById("reg-alm-accion").value;
    const id = document.getElementById("reg-alm-id").value;
    const nombre = document.getElementById("reg-alm-nombre").value.trim();
    const ubicacionRaw = document.getElementById("reg-alm-ubicacion").value.trim();

    // Dividimos de forma segura la entrada del input "Ciudad - Direccion"
    const partes = ubicacionRaw.split('-');
    const ciudad = partes[0] ? partes[0].trim() : "Central";
    const direccion = partes[1] ? partes[1].trim() : "General";

    // Deducción automática del nodo responsable para mantener la coherencia
    let nodo_responsable = "CENTRAL";
    if (ciudad.toUpperCase().includes("LA PAZ") || ciudad.toUpperCase().includes("LP")) nodo_responsable = "LA_PAZ";
    if (ciudad.toUpperCase().includes("SANTA CRUZ") || ciudad.toUpperCase().includes("SCZ")) nodo_responsable = "SANTA_CRUZ";

    const payload = { 
        id_almacen: parseInt(id), 
        nombre: nombre,
        ciudad: ciudad,
        direccion: direccion,
        nodo_responsable: nodo_responsable
    };
    
    const url = accion === "EDITAR" ? '/api/almacen/editar' : '/api/almacen/crear';

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const res = await response.json();
        if (res.success) {
            alert(`✅ Operación distribuida realizada con éxito.`);
            cerrarModalRegistroAlmacen();
            await listarAlmacenesReplicados();
        } else {
            alert(`❌ Error del Coordinador: ${res.error}`);
        }
    } catch (e) {
        alert(`🚨 Error en canal transaccional técnico: ${e.message}`);
    }
}

async function eliminarAlmacenCoordinador(id) {
    if (!confirm(`⚠️ ¿Está seguro de eliminar el Almacén ID ${id} de forma síncrona en toda la red?`)) return;

    try {
        const response = await fetch('/api/almacen/eliminar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id_almacen: id })
        });
        const res = await response.json();
        if (res.success) {
            alert("🗑️ Registro revocado del ecosistema global.");
            await listarAlmacenesReplicados();
        } else {
            alert(`❌ Restricción: ${res.error}`);
        }
    } catch (e) {
        alert("❌ Error al procesar la revocación.");
    }
}

function configurarFiltrosAlmacen() {
    const inputNombre = document.getElementById("alm-buscar-nombre");
    const inputCodigo = document.getElementById("alm-buscar-codigo");

    const ejecutarFiltro = () => {
        const valNombre = inputNombre?.value.toLowerCase().trim() || "";
        const valCodigo = inputCodigo?.value.toLowerCase().trim() || "";

        const filtrados = window.ALMACENES_GLOBAL.filter(alm => {
            const cumpleNombre = String(alm.nombre).toLowerCase().includes(valNombre);
            const cumpleCodigo = String(alm.id_almacen).toLowerCase().includes(valCodigo) || 
                                 String(alm.ciudad).toLowerCase().includes(valCodigo);
            return cumpleNombre && cumpleCodigo;
        });
        inyectarFilasFiltradas(filtrados);
    };

    inputNombre?.addEventListener("input", ejecutarFiltro);
    inputCodigo?.addEventListener("input", ejecutarFiltro);
}

function inyectarFilasFiltradas(lista) {
    const tbody = document.getElementById("tabla-almacenes-replicados-body");
    if (!tbody) return;

    if (lista.length === 0) {
        tbody.innerHTML = `<tr><td colspan="4" style="text-align: center; padding: 24px; color: #94a3b8;">🔍 Sin resultados.</td></tr>`;
        return;
    }

    tbody.innerHTML = "";
    lista.forEach((a) => {
        const fila = document.createElement("tr");
        fila.innerHTML = `
            <td><code>${a.id_almacen}</code></td>
            <td>
                <strong>${a.nombre}</strong><br>
                <small style="color:#64748b;">${a.ciudad} — ${a.direccion}</small>
            </td>
            <td><span style="background:#e0f2fe; color:#0369a1; padding:4px 8px; border-radius:6px; font-size:12px; font-family:monospace;">${a.nodo_responsable}</span></td>
            <td style="text-align: center;">
                <div style="display:flex; gap:6px; justify-content:center;">
                    <button class="btn-secundario" style="padding: 4px 10px; font-size: 12px; background:#f59e0b; color:white; border:none; border-radius:4px; cursor:pointer;" onclick="prepararEdicionAlmacen(${a.id_almacen}, '${a.nombre}', '${a.ciudad}', '${a.direccion}', '${a.nodo_responsable}')">✏️ Editar</button>
                    <button class="btn-danger" style="padding: 4px 10px; font-size: 12px; background:#ef4444; color:white; border:none; border-radius:4px; cursor:pointer;" onclick="eliminarAlmacenCoordinador(${a.id_almacen})">🗑️ Eliminar</button>
                </div>
            </td>
        `;
        tbody.appendChild(fila);
    });
}

async function ejecutarSincronizacionAlmacenesCascada() {
    const btn = document.getElementById("btn-sincronizar-almacenes-master");
    if (btn) {
        btn.disabled = true;
        btn.innerText = "⏳ Sincronizando...";
    }
    try {
        const response = await fetch('/api/almacen/sincronizar', { method: 'POST' });
        const res = await response.json();
        if (response.ok && res.success) {
            alert(`⚡ ${res.mensaje}`);
            await listarAlmacenesReplicados();
        } else {
            alert(`❌ Error: ${res.error}`);
        }
    } catch (error) {
        alert("❌ Error crítico en infraestructura.");
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerText = "⚡ Sincronizar Catálogo";
        }
    }
}