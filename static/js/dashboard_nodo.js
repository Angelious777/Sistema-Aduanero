/**
 * dashboard_nodo.js - Orquestador Analítico Real para Nodos Distribuidos
 */
document.addEventListener("DOMContentLoaded", function() {
    consumirMetricasBackend();
});

async function consumirMetricasBackend() {
    // 1. Detectar dinámicamente el nodo desde la URL actual de la sede regional
    const path = window.location.pathname.toLowerCase().replace(/-/g, "_");
    let nodoActual = "la_paz"; 

    if (path.includes("santa_cruz") || path.includes("scz")) {
        nodoActual = "santa_cruz";
    } else if (path.includes("la_paz") || path.includes("lp")) {
        nodoActual = "la_paz";
    }

    const tbody = document.getElementById("tabla-actividad-local-body");

    try {
        // 2. Realizar petición asíncrona a la API del Coordinador
        const response = await fetch(`/api/dashboard/metricas?nodo=${nodoActual}`);
        const data = await response.json();

        if (!data.success) {
            if (tbody) tbody.innerHTML = `<tr><td colspan="4" style="color:var(--danger); text-align:center;">❌ Error del servidor: ${data.error}</td></tr>`;
            return;
        }

        // 3. Renderizar Etiquetas Institucionales y Configuración de Sede
        if(document.getElementById("lbl-sidebar-nodo")) {
            document.getElementById("lbl-sidebar-nodo").textContent = data.config.id.replace("_", " ");
        }
        if(document.getElementById("lbl-nombre-nodo")) {
            document.getElementById("lbl-nombre-nodo").textContent = `${data.config.nombre} - [${data.config.motor}]`;
        }
        if(document.getElementById("lbl-meta-paquetes")) {
            document.getElementById("lbl-meta-paquetes").textContent = `Catálogo: ${data.config.tabla_paquetes}`;
        }

        // 4. Inyectar los Contadores en las Tarjetas Analíticas
        document.getElementById("dash-local-paquetes").textContent = data.paquetes_count;
        document.getElementById("dash-local-movimientos").textContent = data.movimientos_count;
        document.getElementById("dash-local-clientes").textContent = data.clientes_count;
        document.getElementById("dash-local-almacenes").textContent = data.almacenes_count;

        // 5. Poblar Bitácora Reciente de la Tabla
        if (!tbody) return;
        tbody.innerHTML = "";

        if (data.movimientos.length === 0) {
            tbody.innerHTML = `<tr><td colspan="4" style="text-align:center; color:#64748b;">No hay movimientos registrados en la rampa el día de hoy.</td></tr>`;
            return;
        }

        data.movimientos.forEach(m => {
            const fila = document.createElement("tr");
            fila.innerHTML = `
                <td><strong>${m.fecha}</strong></td>
                <td><code class="codigo-paquete" style="background:#f1f5f9; padding:3px 6px; border-radius:4px; font-family:monospace;">${m.paquete}</code></td>
                <td><span class="badge-status info" style="background:#e0f2fe; color:#0369a1; padding:2px 8px; border-radius:12px; font-size:12px; font-weight:600;">${m.evento}</span></td>
                <td>${m.almacen}</td>
            `;
            tbody.appendChild(fila);
        });

    } catch (error) {
        console.error("Fallo de red en Dashboard:", error);
        if (tbody) {
            tbody.innerHTML = `<tr><td colspan="4" style="color:var(--danger); text-align:center;">❌ Error crítico: Sin comunicación con el segmento de red local.</td></tr>`;
        }
    }
}