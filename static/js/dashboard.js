/**
 * dashboard.js - Controlador del Dashboard Operativo Central
 */
document.addEventListener("DOMContentLoaded", function() {
    inicializarDashboardOperativo();
});

function inicializarDashboardOperativo() {
    if (!window.DB_PROYECTO_GLOBAL) return;
    
    const pkts = window.DB_PROYECTO_GLOBAL.paquetes;
    const movs = window.DB_PROYECTO_GLOBAL.movimientos;
    const clts = window.DB_PROYECTO_GLOBAL.clientes;

    // Calcular las 6 métricas operativas requeridas
    document.getElementById("dash-totales").textContent = pkts.length;
    document.getElementById("dash-transito").textContent = pkts.filter(p => p.estado === "En Tránsito").length;
    document.getElementById("dash-entregadas").textContent = pkts.filter(p => p.estado === "Entregado").length;
    document.getElementById("dash-pendientes").textContent = pkts.filter(p => p.estado === "Retenido por Aduana" || p.estado === "Registrado").length;
    document.getElementById("dash-clientes").textContent = clts.length;
    document.getElementById("dash-movimientos").textContent = movs.length;

    // Poblar los Contadores del Mapa Operativo Nacional
    document.getElementById("mapa-count-lp").textContent = pkts.filter(p => p.nodo === "NODO_LA_PAZ").length;
    document.getElementById("mapa-count-scz").textContent = pkts.filter(p => p.nodo === "NODO_SANTA_CRUZ").length;

    // Poblar Tabla de Actividad Reciente (Últimos 4 movimientos del día)
    const tbody = document.getElementById("tabla-actividad-reciente");
    if (tbody) {
        tbody.innerHTML = "";
        movs.slice(0, 4).forEach(m => {
            const fila = document.createElement("tr");
            fila.innerHTML = `
                <td>${m.fecha}</td>
                <td><code class="codigo-paquete">${m.paquete}</code></td>
                <td><span class="badge-status info">${m.evento}</span></td>
                <td><code class="codigo-nodo">${m.nodo}</code></td>
            `;
            tbody.appendChild(fila);
        });
    }
}