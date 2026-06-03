/**
 * encomiendas.js - Controlador Maestro de Encomiendas y Modal Unificado
 */
document.addEventListener("DOMContentLoaded", function() {
    renderizarEncomiendas();
    
    document.getElementById("btn-filtrar-encomiendas").addEventListener("click", renderizarEncomiendas);
    document.getElementById("btn-cerrar-modal").addEventListener("click", cerrarModalDetalle);
});

function renderizarEncomiendas() {
    const tbody = document.getElementById("tabla-encomiendas-body");
    if (!tbody) return;

    const fCodigo = document.getElementById("filtro-codigo").value.trim().toUpperCase();
    const fEstado = document.getElementById("filtro-estado").value;
    const fOrigen = document.getElementById("filtro-origen").value;
    const fDestino = document.getElementById("filtro-destino").value;

    tbody.innerHTML = "";
    
    let filtrados = window.DB_PROYECTO_GLOBAL.paquetes;

    if (fCodigo) filtrados = filtrados.filter(p => p.codigo.includes(fCodigo));
    if (fEstado) filtrados = filtrados.filter(p => p.estado === fEstado);
    if (fOrigen) filtrados = filtrados.filter(p => p.origen === fOrigen);
    if (fDestino) filtrados = filtrados.filter(p => p.destino === fDestino);

    if (filtrados.length === 0) {
        tbody.innerHTML = `<tr><td colspan="8" style="text-align:center; color: var(--gris-medio);">No se encontraron encomiendas federadas con los criterios especificados.</td></tr>`;
        return;
    }

    filtrados.forEach(p => {
        const fila = document.createElement("tr");
        
        let badge = `<span class="badge-status info">${p.estado}</span>`;
        if (p.estado === "Retenido por Aduana") badge = `<span class="badge-status alert">${p.estado}</span>`;
        if (p.estado === "Entregado") badge = `<span class="badge-status success">${p.estado}</span>`;

        fila.innerHTML = `
            <td><strong>${p.codigo}</strong></td>
            <td>${p.remitente}</td>
            <td>${p.destinatario}</td>
            <td>${p.origen}</td>
            <td>${p.destino}</td>
            <td>${badge}</td>
            <td>${p.fecha}</td>
            <td style="text-align: center;">
                <button class="btn-secundario" style="padding: 6px 12px; font-size: 0.8rem;" onclick="abrirModalDetalle('${p.codigo}')">🔍 Ver Detalle</button>
            </td>
        `;
        tbody.appendChild(fila);
    });
}

function abrirModalDetalle(codigo) {
    const paquete = window.DB_PROYECTO_GLOBAL.paquetes.find(p => p.codigo === codigo);
    if (!paquete) return;

    document.getElementById("modal-titulo-codigo").textContent = `Ficha de Encomienda Integrada: ${paquete.codigo}`;
    
    // Inyectar Información General
    document.getElementById("modal-info-general").innerHTML = `
        <p><strong>Código Control:</strong> <span>${paquete.codigo}</span></p>
        <p><strong>Remitente Fijo:</strong> <span>${paquete.remitente}</span></p>
        <p><strong>Destinatario Final:</strong> <span>${paquete.destinatario}</span></p>
        <p><strong>Tramo Aduanero:</strong> <span>${paquete.origen} ➔ ${paquete.destino}</span></p>
        <p><strong>Estado Actual:</strong> <span class="badge-status-inline info">${paquete.estado}</span></p>
    `;

    // Inyectar Información Financiera (Reconstrucción Vertical)
    document.getElementById("modal-info-financiera").innerHTML = `
        <p><strong>Costo de Envío:</strong> <span>${paquete.costo.toFixed(2)} Bs.</span></p>
        <p><strong>Forma de Pago:</strong> <span>${paquete.pago}</span></p>
        <p><strong>Impuesto Arancelario:</strong> <span>${paquete.impuestos.toFixed(2)} Bs.</span></p>
        <p><strong>Liquidación:</strong> <span>Liberado para Tránsito</span></p>
        <p><strong>Nodo Almacenamiento:</strong> <code class="codigo-nodo">${paquete.nodo}</code></p>
    `;

    // Inyectar Historial de Movimientos Unificados (Reconstrucción Horizontal)
    const tHistorial = document.getElementById("modal-tabla-historial");
    tHistorial.innerHTML = "";
    
    const movimientosFiltrados = window.DB_PROYECTO_GLOBAL.movimientos.filter(m => m.paquete === codigo);
    
    if (movimientosFiltrados.length === 0) {
        tHistorial.innerHTML = `<tr><td colspan="4" style="text-align:center;">Sin registro de movimientos locales.</td></tr>`;
    } else {
        movimientosFiltrados.forEach(m => {
            const r = document.createElement("tr");
            r.innerHTML = `
                <td>${m.fecha}</td>
                <td><strong>${m.evento}</strong></td>
                <td>${m.almacen}</td>
                <td><code class="codigo-fragmento">${m.nodo === 'NODO_LA_PAZ' ? 'MOVIMIENTO_LP' : 'MOVIMIENTO_SCZ'}</code></td>
            `;
            tHistorial.appendChild(r);
        });
    }

    document.getElementById("modal-detalle-encomienda").classList.add("open");
}

function cerrarModalDetalle() {
    document.getElementById("modal-detalle-encomienda").classList.remove("open");
}