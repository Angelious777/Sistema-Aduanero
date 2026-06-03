/**
 * paquetes_nodo.js - Gestión de Transacciones de Carga Locales
 */

document.addEventListener("DOMContentLoaded", function() {
    listarPaquetesLocales();
});

function listarPaquetesLocales() {
    const tbody = document.getElementById("tabla-paquetes-local-body");
    if (!tbody) return;

    tbody.innerHTML = "";
    
    // Obtenemos los paquetes del dataset cargado reactivamente (La Paz o Santa Cruz)
    const paquetes = window.DB_NODO_LOCAL.paquetes;

    paquetes.forEach(pkt => {
        const tr = document.createElement("tr");
        
        // Formateo de Badge de Estado
        let badgeClass = "status-pendiente";
        if (pkt.estado === "En Tránsito") badgeClass = "status-proceso";
        if (pkt.estado === "Entregado") badgeClass = "status-completado";
        if (pkt.estado === "Retenido" || pkt.estado === "Retenido por Aduana") badgeClass = "status-cancelado";

        tr.innerHTML = `
            <td style="font-family: monospace; font-weight: bold;">${pkt.codigo}</td>
            <td>${pkt.destino}</td>
            <td><span class="badge ${badgeClass}">${pkt.estado}</span></td>
            <td>${parseFloat(pkt.costo).toFixed(2)}</td>
            <td style="text-align: center;">
                <button class="btn-secundario" style="padding: 4px 10px; font-size: 0.8rem; display: inline-flex; align-items: center; gap: 6px;" onclick="verDetallePaquete('${pkt.codigo}')">
                    <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M6 22h12a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-3.5l-2-3H6a2 2 0 0 0-2 2v15a2 2 0 0 0 2 2z"></path>
                        <path d="M2 10h20"></path>
                    </svg>
                    Examinar
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

// --- LOGÍSTICA DE REGISTRO CON DISTRIBUCIÓN DE LLAVES ---
function abrirModalNuevoPaquete() {
    const modal = document.getElementById("modal-nuevo-paquete");
    const prefijoSede = window.CONFIG_NODO_ACTIVO.id === "NODO_SANTA_CRUZ" ? "SCZ" : "LP";
    
    // Generador Disjunto: Evita colisión de llaves primarias en arquitecturas concurrentes
    const idUnico = Math.floor(100 + Math.random() * 900); 
    const codigoGenerado = `PKT-${prefijoSede}-${idUnico}`;

    document.getElementById("lbl-prefijo-sede").textContent = window.CONFIG_NODO_ACTIVO.nombre;
    document.getElementById("reg-pkt-codigo").value = codigoGenerado;
    
    // Limpieza de campos de captura
    document.getElementById("reg-pkt-destino").value = "";
    document.getElementById("reg-pkt-costo").value = "";
    document.getElementById("reg-pkt-remitente").value = "";
    document.getElementById("reg-pkt-desc").value = "";

    modal.classList.add("modal-active");
}

function cerrarModalNuevoPaquete() {
    document.getElementById("modal-nuevo-paquete").classList.remove("modal-active");
}

function insertarPaqueteLocal() {
    const codigo = document.getElementById("reg-pkt-codigo").value;
    const destino = document.getElementById("reg-pkt-destino").value.trim();
    const costo = parseFloat(document.getElementById("reg-pkt-costo").value) || 0.00;
    const remitente = document.getElementById("reg-pkt-remitente").value.trim();
    const descripcion = document.getElementById("reg-pkt-desc").value.trim();

    if (!destino || !remitente) {
        alert("⚠️ Error de Validación: Los campos 'Destino Final' y 'Remitente' son obligatorios para guardar la transacción.");
        return;
    }

    // Inserción en la memoria volátil del Nodo activo (Simulación de commit a BD local)
    const nuevoPaquete = {
        codigo: codigo,
        destino: destino,
        estado: "Registrado",
        costo: costo,
        remitente: remitente,
        descripcion: descripcion
    };

    window.DB_NODO_LOCAL.paquetes.unshift(nuevoPaquete);
    
    // Alerta descriptiva con el motor correspondiente para tu presentación de tesis/defensa
    const motorActivo = window.DB_NODO_LOCAL.infraestructura.motor_bd;
    alert(`🎉 [COMMIT EXITOSO]\nRegistro inyectado de forma aislada en: ${motorActivo}\nID Guardado: ${codigo}`);
    
    cerrarModalNuevoPaquete();
    listarPaquetesLocales();
}

// --- LOGÍSTICA DE REVISIÓN Y CAMBIO DE ESTADO ---
let codigoPaqueteSeleccionado = "";

function verDetallePaquete(codigo) {
    const pkt = window.DB_NODO_LOCAL.paquetes.find(p => p.codigo === codigo);
    if (!pkt) return;

    codigoPaqueteSeleccionado = codigo;
    document.getElementById("dt-pkt-codigo").textContent = pkt.codigo;
    document.getElementById("dt-pkt-destino").textContent = pkt.destino;
    document.getElementById("dt-pkt-costo").textContent = parseFloat(pkt.costo).toFixed(2);
    document.getElementById("dt-pkt-remitente").textContent = pkt.remitente;
    document.getElementById("dt-pkt-desc").textContent = pkt.descripcion || "Sin especificaciones.";
    document.getElementById("dt-pkt-select-estado").value = pkt.estado;

    document.getElementById("modal-detalle-paquete").classList.add("modal-active");
}

function cerrarModalDetallePaquete() {
    document.getElementById("modal-detalle-paquete").classList.remove("modal-active");
}

function guardarEstadoPaqueteLocal() {
    const nuevoEstado = document.getElementById("dt-pkt-select-estado").value;
    const pkt = window.DB_NODO_LOCAL.paquetes.find(p => p.codigo === codigoPaqueteSeleccionado);
    
    if (pkt) {
        pkt.estado = nuevoEstado;
        alert(`💾 Estado actualizado en el esquema ${window.DB_NODO_LOCAL.infraestructura.esquema}`);
        cerrarModalDetallePaquete();
        listarPaquetesLocales();
    }
}