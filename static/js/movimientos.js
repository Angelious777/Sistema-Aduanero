/**
 * movimientos.js - Monitor de Bitácora basado en Tabla Física Global
 */

window.MOVIMIENTOS_GLOBAL = [];

document.addEventListener("DOMContentLoaded", function() {
    listarMovimientosDesdeTablaGlobal();

    // Filtros dinámicos interactivos de la interfaz
    document.getElementById("btn-filtrar-movimientos")?.addEventListener("click", renderizarTablaMovimientos);
    document.getElementById("buscar-movimiento-paquete")?.addEventListener("input", renderizarTablaMovimientos);
    document.getElementById("filtro-movimiento-nodo")?.addEventListener("change", renderizarTablaMovimientos);
});

async function listarMovimientosDesdeTablaGlobal() {
    const tbody = document.getElementById("tabla-movimientos-body");
    if (!tbody) return;

    tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;">📊 Leyendo bitácora de auditoría unificada (MOVIMIENTO_GLOBAL)...</td></tr>`;

    // Detectar contexto de nodo regional si aplica
    const path = window.location.pathname.toLowerCase().replace(/-/g, "_");
    let nodoActual = "global";

    if (path.includes("la_paz") || path.includes("lp")) {
        nodoActual = "nodo_lp";
    } else if (path.includes("santa_cruz") || path.includes("scz")) {
        nodoActual = "nodo_scz";
    }

    try {
        const response = await fetch(`/api/movimientos?nodo=${nodoActual}`);
        const resultado = await response.json();

        if (resultado.success) {
            window.MOVIMIENTOS_GLOBAL = resultado.data || [];
            renderizarTablaMovimientos();
        } else {
            tbody.innerHTML = `<tr><td colspan="5" style="color:var(--danger); text-align:center;">❌ Error al recuperar registros históricos.</td></tr>`;
        }
    } catch (error) {
        tbody.innerHTML = `<tr><td colspan="5" style="color:var(--danger); text-align:center;">❌ Desconectado del motor relacional central.</td></tr>`;
    }
}

function renderizarTablaMovimientos() {
    const tbody = document.getElementById("tabla-movimientos-body");
    if (!tbody) return;

    const fPaquete = document.getElementById("buscar-movimiento-paquete")?.value.trim().toLowerCase() || "";
    const fNodo = document.getElementById("filtro-movimiento-nodo")?.value || "";

    tbody.innerHTML = "";
    let filtrados = window.MOVIMIENTOS_GLOBAL;

    // Filtrar por texto del código de encomienda
    if (fPaquete) {
        filtrados = filtrados.filter(m => m.codigo && m.codigo.toLowerCase().includes(fPaquete));
    }

    // Filtrar por selector de nodo regional aduanero
    if (fNodo) {
        if (fNodo === "NODO_LA_PAZ") {
            filtrados = filtrados.filter(m => m.fragmento.includes("PostgreSQL"));
        } else if (fNodo === "NODO_SANTA_CRUZ") {
            filtrados = filtrados.filter(m => m.fragmento.includes("SQL Server"));
        }
    }

    if (filtrados.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; color:#64748b;">No existen movimientos registrados para los criterios seleccionados.</td></tr>`;
        return;
    }

    // Dibujar las filas físicas en el HTML
    filtrados.forEach(m => {
        const fila = document.createElement("tr");

        // Asignación de colores según la criticidad o tipo de evento logístico
        let badgeStyle = "background: #0284c7; color: white;"; // Por defecto: Azul (Tránsito)
        const accionTexto = m.accion.toUpperCase();
        
        if (accionTexto.includes("ADUANA") || accionTexto.includes("RETENIDO") || accionTexto.includes("REVISION")) {
            badgeStyle = "background: #e11d48; color: white;"; // Rojo (Alerta / Inspección)
        } else if (accionTexto.includes("ENTREGADO") || accionTexto.includes("DESPACHADO")) {
            badgeStyle = "background: #16a34a; color: white;"; // Verde (Completado)
        }

        fila.innerHTML = `
            <td><small style="font-family: monospace; color:#475569;">${m.fecha}</small></td>
            <td><strong style="font-family: monospace; color:#1e3a8a; font-size:13px;">${m.codigo}</strong></td>
            <td><span style="${badgeStyle} padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; text-transform: uppercase;">${m.accion}</span></td>
            <td><span style="color: #334155; font-size: 13px;">🏢 ${m.ubicacion}</span></td>
            <td><code style="background: #f1f5f9; padding: 4px 6px; border-radius: 4px; font-size: 11px; color: #0f172a;">${m.fragmento}</code></td>
        `;
        tbody.appendChild(fila);
    });
}