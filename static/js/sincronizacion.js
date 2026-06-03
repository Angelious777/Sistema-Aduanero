/**
 * sincronizacion.js
 * Control del Demonio de Sincronización Asíncrona (Consistencias Eventuales)
 */

// Operaciones iniciales que quedaron pendientes en los nodos regionales mientras trabajaban sin conexión directa
let MOCK_COLA_PENDIENTES = [
    { id: "OP-901", nodo: "NODO_LA_PAZ", accion: "UPDATE PAQUETE_OPERATIVO_LP SET estado='En Tránsito' WHERE codigo='PK-LP-2026-003'", fecha: "2026-05-31 12:10", prioridad: "Alta", estado: "En Cola" },
    { id: "OP-902", nodo: "NODO_SANTA_CRUZ", accion: "INSERT INTO MOVIMIENTO_SCZ (fecha, codigo, almacen, accion) VALUES (...)", fecha: "2026-05-31 12:45", prioridad: "Media", estado: "En Cola" },
    { id: "OP-903", nodo: "NODO_LA_PAZ", accion: "UPDATE PAQUETE_FINANCIERO_LP SET seguro=15.00 WHERE codigo='PK-LP-2026-001'", fecha: "2026-05-31 13:02", prioridad: "Baja", estado: "En Cola" }
];

let MOCK_LOGS_HISTORICOS = [
    { fecha: "2026-05-31 06:00", nodo: "NODO_SANTA_CRUZ", operacion: "Sincronización Periódica Automatizada", filas: 12, estado: "ÉXITO" },
    { fecha: "2026-05-31 10:00", nodo: "NODO_LA_PAZ", operacion: "Vaciado de Cola - Consistencia Post-Caída VPN", filas: 4, estado: "ÉXITO" }
];

document.addEventListener("DOMContentLoaded", function() {
    const btnSincronizar = document.getElementById("btnSincronizar");
    if (btnSincronizar) {
        btnSincronizar.addEventListener("click", ejecutarDemonioSincronizacion);
    }
    inicializarSincronizacion();
});

function inicializarSincronizacion() {
    renderizarTablasSincronizacion();
    actualizarBadgesContadores();
}

function actualizarBadgesContadores() {
    const countLP = MOCK_COLA_PENDIENTES.filter(p => p.nodo === "NODO_LA_PAZ" && p.estado === "En Cola").length;
    const countSCZ = MOCK_COLA_PENDIENTES.filter(p => p.nodo === "NODO_SANTA_CRUZ" && p.estado === "En Cola").length;
    
    document.getElementById("cola-lp-estado").textContent = `${countLP} Pendientes`;
    document.getElementById("cola-lp-estado").className = countLP > 0 ? "text-alert" : "text-success";
    
    document.getElementById("cola-scz-estado").textContent = `${countSCZ} Pendientes`;
    document.getElementById("cola-scz-estado").className = countSCZ > 0 ? "text-alert" : "text-success";

    // Compartir el total de pendientes con el Dashboard (localStorage para consistencia entre scripts)
    localStorage.setItem("totalPendientesCola", countLP + countSCZ);
}

function renderizarTablasSincronizacion() {
    const tbodyPendientes = document.getElementById("tablaPendientes");
    const tbodyLogs = document.getElementById("tablaLogs");

    if (tbodyPendientes) {
        tbodyPendientes.innerHTML = "";
        const elementosActivos = MOCK_COLA_PENDIENTES.filter(p => p.estado === "En Cola");
        
        if (elementosActivos.length === 0) {
            tbodyPendientes.innerHTML = `<tr class="placeholder-row"><td colspan="6" class="text-success">✔ Todos los canales aduaneros se encuentran perfectamente al día.</td></tr>`;
        } else {
            elementosActivos.forEach(item => {
                const fila = document.createElement("tr");
                fila.innerHTML = `
                    <td><code>${item.id}</code></td>
                    <td><strong>${item.nodo}</strong></td>
                    <td class="text-truncate-sql">${item.accion}</td>
                    <td>${item.fecha}</td>
                    <td><span class="badge-prioridad ${item.prioridad.toLowerCase()}">${item.prioridad}</span></td>
                    <td><span class="badge-status waiting">${item.estado}</span></td>
                `;
                tbodyPendientes.appendChild(fila);
            });
        }
    }

    if (tbodyLogs) {
        tbodyLogs.innerHTML = "";
        MOCK_LOGS_HISTORICOS.forEach(log => {
            const fila = document.createElement("tr");
            fila.innerHTML = `
                <td>${log.fecha}</td>
                <td>${log.nodo}</td>
                <td>${log.operacion}</td>
                <td>${log.filas}</td>
                <td><span class="badge-status success">${log.estado}</span></td>
            `;
            tbodyLogs.appendChild(fila);
        });
    }
}

function ejecutarDemonioSincronizacion() {
    const btn = document.getElementById("btnSincronizar");
    const spinner = document.getElementById("sync-spinner");
    const activos = MOCK_COLA_PENDIENTES.filter(p => p.estado === "En Cola");

    if (activos.length === 0) {
        alert("No existen operaciones pendientes en la cola diferida.");
        return;
    }

    // Bloquear controles e iniciar animación
    btn.disabled = true;
    spinner.classList.remove("hidden");
    btn.querySelector("span").textContent = "⏳";

    // Simular procesamiento secuencial de replicación asíncrona
    setTimeout(() => {
        const ahora = new Date().toISOString().replace('T', ' ').substring(0, 16);
        const totalProcesados = activos.length;

        // Cambiar estados internos
        MOCK_COLA_PENDIENTES.forEach(p => p.estado = "Procesado");
        
        // Agregar registro de éxito al historial de auditoría
        MOCK_LOGS_HISTORICOS.unshift({
            fecha: ahora,
            nodo: totalProcesados > 1 ? "MULTINODO_GLOBAL" : activos[0].nodo,
            operacion: "Vaciado manual forzado por el operador central",
            filas: totalProcesados,
            estado: "ÉXITO"
        });

        // Actualizar vistas y liberar componentes
        inicializarSincronizacion();
        btn.disabled = false;
        spinner.classList.add("hidden");
        btn.querySelector("span").textContent = "🔄";
        
        alert(`Demonio completado con éxito: Se han reconciliado ${totalProcesados} transacciones distribuidas en los nodos regionales.`);
        
        // Actualizar la métrica en el dashboard directamente si está cargado
        if (typeof cargarResumen === 'function') cargarResumen();
    }, 1500); // 1.5 segundos de retraso para dar sensación de procesamiento en red
}