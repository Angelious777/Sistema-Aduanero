document.addEventListener("DOMContentLoaded", function() {
    listarMovimientosLocales();
});

function listarMovimientosLocales() {
    const tbody = document.getElementById("tabla-movimientos-local-body");
    if (!tbody) return;

    tbody.innerHTML = "";
    // Clonar y revertir para ver los más recientes arriba
    const ops = [...window.DB_NODO_LOCAL.movimientos].reverse();

    ops.forEach(m => {
        const fila = document.createElement("tr");
        fila.innerHTML = `
            <td><strong>${m.fecha}</strong></td>
            <td><code class="codigo-paquete">${m.paquete}</code></td>
            <td><span class="badge-status success" style="background-color:rgba(245,158,11,0.1); color:var(--warning);">${m.evento}</span></td>
            <td>${m.almacen || m.observacion || 'Control Operativo Conforme'}</td>
        `;
        tbody.appendChild(fila);
    });
}

function abrirModalNuevoMovimiento(preSelectedCodigo = "") {
    const sel = document.getElementById("mov-form-paquete");
    sel.innerHTML = "";
    
    window.DB_NODO_LOCAL.paquetes.forEach(p => {
        const opt = document.createElement("option");
        opt.value = p.codigo;
        opt.textContent = p.codigo;
        if(p.codigo === preSelectedCodigo) opt.selected = true;
        sel.appendChild(opt);
    });

    document.getElementById("form-nuevo-movimiento").reset();
    if(preSelectedCodigo) document.getElementById("mov-form-paquete").value = preSelectedCodigo;
    
    document.getElementById("modal-nuevo-movimiento").classList.add("modal-active");
}
function cerrarModalNuevoMovimiento() { document.getElementById("modal-nuevo-movimiento").classList.remove("modal-active"); }

function insertarMovimientoLocal() {
    const pkt = document.getElementById("mov-form-paquete").value;
    const tipo = document.getElementById("mov-form-tipo").value;
    const obs = document.getElementById("mov-form-obs").value.trim();

    if(!pkt || !tipo || !obs) {
        alert("Escriba la observación técnica de control.");
        return;
    }

    const d = new Date();
    const stamp = d.getFullYear() + "-" + String(d.getMonth()+1).padStart(2,'0') + "-" + String(d.getDate()).padStart(2,'0') + " " + String(d.getHours()).padStart(2,'0') + ":" + String(d.getMinutes()).padStart(2,'0');

    // Inserta directamente en MOVIMIENTO_LP o MOVIMIENTO_SCZ
    window.DB_NODO_LOCAL.movimientos.push({
        fecha: stamp,
        paquete: pkt,
        evento: tipo,
        almacen: obs
    });

    alert(`[INSERT LOCAL SUCCESS] Transacción inyectada con éxito en la tabla local del nodo.`);
    cerrarModalNuevoMovimiento();
    listarMovimientosLocales();
    if(typeof inicializarDashboardLocal === "function") inicializarDashboardLocal();
}