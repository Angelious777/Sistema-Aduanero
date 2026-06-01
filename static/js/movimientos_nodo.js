/**
 * movimientos_nodo.js - Control e Inserciones directas bajo esquema relacional rígido
 */

document.addEventListener("DOMContentLoaded", function() {
    listarMovimientosLocales();
});

// Detectamos el nodo activo configurado en el entorno global
function obtenerNodoActual() {
    const nodoId = window.CONFIG_NODO_ACTIVO ? window.CONFIG_NODO_ACTIVO.id : null;
    return nodoId === "NODO_SANTA_CRUZ" ? "santa_cruz" : "la_paz";
}

async function listarMovimientosLocales() {
    const tbody = document.getElementById("tabla-movimientos-local-body");
    if (!tbody) return;

    tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;">Consultando fragmento local...</td></tr>`;
    const nodoParam = obtenerNodoActual();

    try {
        const response = await fetch(`/api/movimientos/listar/${nodoParam}`);
        const resultado = await response.json();

        if (!resultado.success) throw new Error(resultado.error);

        const ops = resultado.data || [];
        tbody.innerHTML = "";

        if (ops.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; color:gray;">No hay registros físicos en este fragmento.</td></tr>`;
            return;
        }

        // Pintamos las columnas idénticas a los atributos de las tablas SQL
        ops.forEach(m => {
            const fila = document.createElement("tr");
            fila.innerHTML = `
                <td style="font-family:monospace; font-size:11px; color:var(--gris-oscuro);">${m.id_movimiento}</td>
                <td style="font-family:monospace; font-size:11px; color:var(--azul-medio); font-weight:bold;">${m.id_paquete}</td>
                
                <td style="text-align:center;">
                    <span class="badge-almacen" style="background:#eef; padding:4px 8px; border-radius:4px;">
                        ${m.nombre_almacen}
                    </span>
                </td>
                
                <td><strong style="color:var(--azul-oscuro);">${m.fecha_movimiento}</strong></td>
                <td style="font-size:13px; max-width:250px; word-wrap:break-word;">${m.observacion}</td>
            `;
            tbody.appendChild(fila);
        });
    } catch (error) {
        console.error("Error al listar movimientos:", error);
        tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; color:red;">Error de comunicación con la base de datos: ${error.message}</td></tr>`;
    }
}

async function abrirModalNuevoMovimiento() {
    const selPaquetes = document.getElementById("mov-form-paquete");
    const selAlmacenes = document.getElementById("mov-form-almacen");
    const nodoParam = obtenerNodoActual();

    selPaquetes.innerHTML = "<option>Cargando encomiendas...</option>";
    selAlmacenes.innerHTML = "<option>Cargando almacenes...</option>";

    document.getElementById("modal-nuevo-movimiento").classList.add("modal-active");

    try {
        // 1. Consumir paquetes operativos
        const resPkt = await fetch(`/api/tabla/paquete/${nodoParam}`);
        const dataPkt = await resPkt.json();
        
        // 2. Consumir almacenes (Replicación Total)
        const resAlm = await fetch(`/api/almacenes/${nodoParam}`);
        const dataAlm = await resAlm.json();

        selPaquetes.innerHTML = "";
        if (dataPkt.success && dataPkt.data) {
            dataPkt.data.forEach(p => {
                const opt = document.createElement("option");
                opt.value = p.id_paquete; // El UUID para la FK
                // Visualización amigable para el usuario:
                opt.textContent = `${p.codigo_rastreo} | ${p.descripcion || 'Sin descripción'}`;
                selPaquetes.appendChild(opt);
            });
        }

        selAlmacenes.innerHTML = "";
        if (dataAlm.success && dataAlm.data) {
            dataAlm.data.forEach(a => {
                const opt = document.createElement("option");
                opt.value = a.id_almacen; 
                opt.textContent = `${a.nombre} (${a.ciudad})`;
                selAlmacenes.appendChild(opt);
            });
        }
    } catch (err) {
        console.error("Error cargando llaves foráneas:", err);
        selPaquetes.innerHTML = "<option>Error de carga</option>";
    }
}

function cerrarModalNuevoMovimiento() { 
    document.getElementById("modal-nuevo-movimiento").classList.remove("modal-active"); 
}

async function insertarMovimientoLocal() {
    const idPapa = document.getElementById("mov-form-paquete").value;
    const idAlm = document.getElementById("mov-form-almacen").value;
    const obs = document.getElementById("mov-form-obs").value.trim();
    const nodoParam = obtenerNodoActual();

    if (!idPapa || !idAlm || !obs) {
        alert("Todos los campos obligatorios correspondientes a las restricciones de integridad SQL deben llenarse.");
        return;
    }

    // Generamos un UUID/UNIQUEIDENTIFIER en caliente en el cliente para la PK id_movimiento
    const idMovimiento = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });

    const payload = {
        nodo: nodoParam,
        id_movimiento: idMovimiento,
        id_paquete: idPapa,
        id_almacen: parseInt(idAlm),
        observacion: obs
    };

    try {
        const response = await fetch('/api/movimientos/insertar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const resultado = await response.json();

        if (!resultado.success) throw new Error(resultado.error);

        alert(`[INSERT SUCCESS] Registro inyectado exitosamente con ID: ${idMovimiento}`);
        cerrarModalNuevoMovimiento();
        listarMovimientosLocales();
    } catch (error) {
        alert(`Fallo en la restricción o conectividad del motor distribuido: ${error.message}`);
    }
}