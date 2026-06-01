/**
 * paquetes_nodo.js - Gestión de Transacciones de Carga Locales de acuerdo al API Flask
 */

document.addEventListener("DOMContentLoaded", function() {
    if (!window.CONFIG_NODO_ACTIVO) {
        window.CONFIG_NODO_ACTIVO = { id: "la_paz", nombre: "Sede Occidental (La Paz)" };
    }
    cargarPaquetesPorTipo();
});

// =========================================================
// RENDERIZADO ASÍNCRONO DE LAS TABLAS DEL NODO DESDE EL API
// =========================================================
async function cargarPaquetesPorTipo() {
    const pathNormalizado = window.location.pathname.toLowerCase().replace(/-/g, "_");
    let nodoId = "";
    
    if (pathNormalizado.includes("la_paz") || pathNormalizado.includes("lp")) {
        nodoId = "la_paz";
    } else if (pathNormalizado.includes("santa_cruz") || pathNormalizado.includes("scz")) {
        nodoId = "santa_cruz";
    } else {
        nodoId = window.CONFIG_NODO_ACTIVO.id.toLowerCase().includes("santa") ? "santa_cruz" : "la_paz";
    }

    try {
        const response = await fetch(`/api/paquetes/por-tipo/${nodoId}`);
        const resultado = await response.json();

        if (!response.ok || resultado.success === false) {
            console.error("❌ Error al cargar paquetes del clúster:", resultado.error);
            return;
        }

        window.PAQUETES_NODO = resultado.data || { operativos: [], financieros: [] };
        mostrarPaquetesOperativos();
        mostrarPaquetesFinancieros();
    } catch (error) {
        console.error("❌ Error de red en cargarPaquetesPorTipo:", error);
    }
}

function mostrarPaquetesOperativos() {
    const tbody = document.getElementById("tabla-paquetes-operativos-body");
    if (!tbody) return;

    tbody.innerHTML = "";
    const paquetes = (window.PAQUETES_NODO && window.PAQUETES_NODO.operativos) || [];

    if (paquetes.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;">No hay paquetes operativos registrados en este nodo.</td></tr>`;
        return;
    }

    paquetes.forEach(pkt => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td style="font-family: monospace; font-weight: bold;">${pkt.codigo_rastreo || pkt.codigo || '--'}</td>
            <td><span style="background:#f1f5f9; padding:2px 6px; border-radius:4px;">Ruta ${pkt.id_ruta || '--'}</span></td>
            <td><span class="badge status-proceso">${pkt.estado || 'Registrado'}</span></td>
            <td><small>${pkt.prioridad || 'Media'}</small></td>
            <td style="text-align: center;">
                <button class="btn-secundario" style="padding: 4px 10px; font-size: 0.8rem;" onclick="verDetallePaquete('${pkt.codigo_rastreo || pkt.codigo}')">Examinar</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function mostrarPaquetesFinancieros() {
    const tbody = document.getElementById("tabla-paquetes-financieros-body");
    if (!tbody) return;

    tbody.innerHTML = "";
    const paquetes = (window.PAQUETES_NODO && window.PAQUETES_NODO.financieros) || [];

    if (paquetes.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;">No hay registros financieros devueltos por el fragmento vertical.</td></tr>`;
        return;
    }

    paquetes.forEach(pkt => {
        const costo = parseFloat(pkt.costo_envio) || 0.0;
        const seguro = parseFloat(pkt.seguro) || 0.0;
        const valorDeclarado = parseFloat(pkt.valor_declarado) || 0.0;

        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td style="font-family: monospace; font-weight: bold; font-size:11px;">${pkt.id_paquete || '--'}</td>
            <td><strong>${costo.toFixed(2)} Bs</strong></td>
            <td>${seguro.toFixed(2)} Bs</td>
            <td>${valorDeclarado.toFixed(2)} Bs</td>
            <td style="text-align: center;">
                <button class="btn-secundario" style="padding: 4px 10px; font-size: 0.8rem;" onclick="alert('Auditoría ID: ${pkt.id_paquete}')">Ver</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

// =========================================================
// CARGA REAL DE FKs ASOCIADAS A CLIENTES Y RUTAS DEL CLUSTER
// =========================================================
async function cargarComboboxModal() {
    try {
        const resClientes = await fetch('/api/clientes').then(r => r.json());

        const selectRemitente = document.getElementById("reg-pkt-remitente");
        if (selectRemitente && resClientes.success) {
            let options = '<option value="">-- Seleccione Cliente Consignatario --</option>';
            resClientes.data.forEach(c => {
                options += `<option value="${c.id}">${c.nombre} (Doc: ${c.documento || 'S/D'})</option>`;
            });
            selectRemitente.innerHTML = options;
        }

        const selectDestino = document.getElementById("reg-pkt-destino");
        if (selectDestino) {
            let options = '<option value="">-- Seleccione Ruta de Tránsito Habilitada --</option>';
            const tusRutasReales = [
                { id: 1, descripcion: "Ruta 1: Almacén Central LP ➔ Almacén Central SCZ (Envío Terrestre)" },
                { id: 2, descripcion: "Ruta 2: Almacén Central SCZ ➔ Almacén Central LP (Retorno Terrestre)" }
            ];
            tusRutasReales.forEach(ruta => {
                options += `<option value="${ruta.id}">${ruta.descripcion}</option>`;
            });
            selectDestino.innerHTML = options;
        }
    } catch (err) {
        console.error("❌ Error inyectando llaves foráneas reales a la interfaz:", err);
    }
}

// =========================================================
// APERTURA DE MODAL Y GENERACIÓN DISJUNTA DE LLAVES
// =========================================================
function abrirModalNuevoPaquete() {
    const modal = document.getElementById("modal-nuevo-paquete");
    const pathNormalizado = window.location.pathname.toLowerCase().replace(/-/g, "_");
    const prefijoSede = (pathNormalizado.includes("santa_cruz") || pathNormalizado.includes("scz")) ? "SCZ" : "LP";
    
    const idUnico = Math.floor(1000 + Math.random() * 9000); 
    const codigoGenerado = `PKT-${prefijoSede}-${idUnico}`;

    document.getElementById("lbl-prefijo-sede").textContent = prefijoSede === "SCZ" ? "Sede Oriental (Santa Cruz)" : "Sede Occidental (La Paz)";
    document.getElementById("reg-pkt-codigo").value = codigoGenerado;
    
    document.getElementById("form-registro-paquete").reset();
    document.getElementById("reg-pkt-codigo").value = codigoGenerado;

    cargarComboboxModal();
    modal.classList.add("modal-active");
}

function cerrarModalNuevoPaquete() {
    document.getElementById("modal-nuevo-paquete").classList.remove("modal-active");
}

// =========================================================
// TRANSMISIÓN POST AL COORDINADOR FLASK CON TODOS LOS CAMPOS
// =========================================================
async function insertarPaqueteLocal() {
    const codigo = document.getElementById("reg-pkt-codigo").value;
    const idRutaSeleccionada = document.getElementById("reg-pkt-destino").value;
    const prioridad = document.getElementById("reg-pkt-prioridad").value;
    const remitente = document.getElementById("reg-pkt-remitente").value;
    const descripcion = document.getElementById("reg-pkt-desc").value.trim();
    
    const costo = document.getElementById("reg-pkt-costo").value;
    const peso = document.getElementById("reg-pkt-peso").value;
    const volumen = document.getElementById("reg-pkt-volumen").value;
    const valorDeclarado = document.getElementById("reg-pkt-valor-declarado").value;
    const seguro = document.getElementById("reg-pkt-seguro").value;

    if (!idRutaSeleccionada || !remitente) {
        alert("⚠️ Validación SQL: 'Ruta de Tránsito' y 'Remitente' actúan como restricciones relacionales obligatorias.");
        return;
    }

    const pathNormalizado = window.location.pathname.toLowerCase().replace(/-/g, "_");
    const nodoDestino = (pathNormalizado.includes("santa_cruz") || pathNormalizado.includes("scz")) ? "santa_cruz" : "la_paz";

    const payload = {
        codigo: codigo,
        id_ruta: parseInt(idRutaSeleccionada), 
        prioridad: prioridad,
        nodo: nodoDestino,
        remitente: remitente,
        descripcion: descripcion,
        costo: parseFloat(costo) || 0.0,
        peso: parseFloat(peso) || 1.0,
        volumen: parseFloat(volumen) || 1.0,
        valor_declarado: parseFloat(valorDeclarado) || 0.0,
        seguro: parseFloat(seguro) || 0.0
    };

    try {
        const response = await fetch('/api/paquete/crear', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const resultado = await response.json();

        if (response.ok && resultado.success) {
            alert(`🎉 [COMMIT EN CENTRAL Y LOCAL]\n${resultado.data.mensaje}\nCódigo Tracking: ${codigo}`);
            cerrarModalNuevoPaquete();
            cargarPaquetesPorTipo(); 
        } else {
            alert(`❌ Error devuelto por el Motor:\n${resultado.error}`);
        }
    } catch (error) {
        alert(`❌ Error de comunicación con el clúster: ${error.message}`);
    }
}

// =========================================================
// REVISIÓN LOCAL DE LOGÍSTICA DE DETALLES
// =========================================================
function verDetallePaquete(codigo) {
    const paquetes = (window.PAQUETES_NODO && window.PAQUETES_NODO.operativos) || [];
    const pkt = paquetes.find(p => (p.codigo_rastreo === codigo || p.codigo === codigo));
    
    if (!pkt) return;

    document.getElementById("dt-pkt-codigo").textContent = pkt.codigo_rastreo || pkt.codigo;
    document.getElementById("dt-pkt-destino").textContent = `Ruta Alterna / Código Interno: ${pkt.id_ruta || 1}`;
    document.getElementById("dt-pkt-prioridad-txt").textContent = pkt.prioridad || "Media";
    document.getElementById("dt-pkt-estado-txt").textContent = pkt.estado || "Registrado";
    document.getElementById("dt-pkt-desc").textContent = pkt.descripcion || "Sin descripción física del contenido.";

    document.getElementById("modal-detalle-paquete").classList.add("modal-active");
}

function cerrarModalDetallePaquete() {
    document.getElementById("modal-detalle-paquete").classList.remove("modal-active");
}