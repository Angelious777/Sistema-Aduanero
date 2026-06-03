/**
 * dashboard.js - Controlador del Dashboard Operativo Central
 * Ahora consume datos reales desde /api/dashboard y llena las métricas
 * del coordinador sin usar datos de prueba en memoria.
 */

document.addEventListener("DOMContentLoaded", function() {
    cargarDashboardOperativo();
});

async function inicializarDashboardOperativo() {
    try {
        const response = await fetch('/api/dashboard');
        const data = await response.json();

        if (!data.success) {
            console.error('Error obteniendo datos del dashboard del coordinador:', data.error);
            return;
        }

        const dashboard = data.data || {};
        const coords = dashboard.coordinador || {};

        document.getElementById('dash-totales').textContent = coords.paquetes_totales || 0;
        document.getElementById('dash-transito').textContent = coords.en_transito || 0;
        document.getElementById('dash-entregadas').textContent = coords.entregadas || 0;
        document.getElementById('dash-pendientes').textContent = coords.pendientes_retenidos || 0;
        document.getElementById('dash-clientes').textContent = coords.clientes_registrados || 0;
        document.getElementById('dash-movimientos').textContent = coords.movimientos_dia || 0;

        document.getElementById('mapa-count-lp').textContent = coords.paquetes_lp || 0;
        document.getElementById('mapa-count-scz').textContent = coords.paquetes_scz || 0;

        const actividadTbody = document.getElementById('tabla-actividad-reciente');
        if (actividadTbody) {
            actividadTbody.innerHTML = '';
            const items = Array.isArray(dashboard.actividad_reciente) ? dashboard.actividad_reciente.slice(0, 4) : [];
            if (items.length === 0) {
                actividadTbody.innerHTML = '<tr class="placeholder-row"><td colspan="4">No hay eventos recientes disponibles.</td></tr>';
            } else {
                items.forEach(item => {
                    const fila = document.createElement('tr');
                    fila.innerHTML = `<td colspan="4">${item}</td>`;
                    actividadTbody.appendChild(fila);
                });
            }
        }
    } catch (error) {
        console.error('Error inicializando dashboard operativo:', error);
    }
}
