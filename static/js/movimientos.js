/**
 * movimientos.js - Bitácora de Movimientos Distribuidos de Cargas
 */
document.addEventListener("DOMContentLoaded", function() {
    renderizarMovimientos();
    document.getElementById("btn-filtrar-movimientos").addEventListener("click", renderizarMovimientos);
});

function renderizarMovimientos() {
    const tbody = document.getElementById("tabla-movimientos-body");
    if (!tbody) return;

    const fPaquete = document.getElementById("buscar-movimiento-paquete").value.trim().toUpperCase();
    const fNodo = document.getElementById("filtro-movimiento-nodo").value;

    tbody.innerHTML = "";
    let filtrados = window.DB_PROYECTO_GLOBAL.movimientos;

    if (fPaquete) filtrados = filtrados.filter(m => m.paquete.includes(fPaquete));
    if (fNodo) filtrados = filtrados.filter(m => m.nodo === fNodo);

    filtrados.forEach(m => {
        const fila = document.createElement("tr");
        
        // Identificar dinámicamente el fragmento correspondiente
        const fragmentoLabel = (m.nodo === "NODO_LA_PAZ") ? "MOVIMIENTO_LP (PostgreSQL)" : "MOVIMIENTO_SCZ (MS SQL Server)";

        fila.innerHTML = `
            <td>${m.fecha}</td>
            <td><code class="codigo-paquete">${m.paquete}</code></td>
            <td><span class="badge-status info">${m.evento}</span></td>
            <td>${m.almacen}</td>
            <td><code class="codigo-fragmento">${fragmentoLabel}</code></td>
        `;
        tbody.appendChild(fila);
    });
}