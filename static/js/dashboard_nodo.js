/**
 * dashboard_nodo.js - Orquestador Analítico del Dashboard de la Sede Regional
 */
document.addEventListener("DOMContentLoaded", function() {
    inicializarDashboardLocal();
});

function inicializarDashboardLocal() {
    const db = window.DB_NODO_LOCAL;
    if (!db) return;

    // Actualizar etiquetas institucionales de la barra y encabezados
    document.getElementById("lbl-sidebar-nodo").textContent = db.config.id.replace("_", " ");
    document.getElementById("lbl-nombre-nodo").textContent = `${db.config.nombre} - [${db.config.motor}]`;
    document.getElementById("lbl-meta-paquetes").textContent = `Catálogo: ${db.config.tabla_paquetes}`;

    // Cargar contadores analíticos locales
    document.getElementById("dash-local-paquetes").textContent = db.paquetes.length;
    document.getElementById("dash-local-movimientos").textContent = db.movimientos.length;
    document.getElementById("dash-local-clientes").textContent = db.clientes_publicos.length;
    document.getElementById("dash-local-almacenes").textContent = db.almacenes.length;

    // Poblar Bitácora de Actividad Reciente del Nodo
    const tbody = document.getElementById("tabla-actividad-local-body");
    if (!tbody) return;

    tbody.innerHTML = "";
    // Ordenar movimientos por fecha de forma descendente para ver la actividad reciente
    const recientes = [...db.movimientos].reverse();

    recientes.forEach(m => {
        const fila = document.createElement("tr");
        fila.innerHTML = `
            <td><strong>${m.fecha}</strong></td>
            <td><code class="codigo-paquete">${m.paquete}</code></td>
            <td><span class="badge-status info">${m.evento}</span></td>
            <td>${m.almacen}</td>
        `;
        tbody.appendChild(fila);
    });
}