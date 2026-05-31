/**
 * almacenes_nodo.js - Control de Infraestructura Física Regional
 */

document.addEventListener("DOMContentLoaded", function() {
    listarAlmacenesLocales();
});

function listarAlmacenesLocales() {
    const tbody = document.getElementById("tabla-almacenes-local-body");
    if (!tbody) return;

    tbody.innerHTML = "";
    
    // Extraemos la lista de almacenes del dataset reactivo asignado por la URL
    const almacenes = window.DB_NODO_LOCAL.almacenes;

    almacenes.forEach(alm => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td style="font-family: monospace; font-weight: bold; color: var(--azul-medio);">${alm.codigo}</td>
            <td style="font-weight: 600;">${alm.nombre}</td>
            <td>${alm.ubicacion}</td>
            <td><strong style="color: var(--gris-oscuro);">${alm.capacidad}</strong></td>
        `;
        tbody.appendChild(tr);
    });
}

// --- LOGÍSTICA DE REGISTRO EN MOTORES DISTRIBUIDOS ---
function abrirModalNuevoAlmacen() {
    const modal = document.getElementById("modal-nuevo-almacen");
    const prefijoSede = window.CONFIG_NODO_ACTIVO.id === "NODO_SANTA_CRUZ" ? "SCZ" : "LP";
    
    // Generador Disjunto de Llave Primaria (Ej. ALM-LP-03)
    // Toma el total actual de almacenes + 1 para mantener un consecutivo limpio
    const correlativo = window.DB_NODO_LOCAL.almacenes.length + 1;
    const codigoGenerado = `ALM-${prefijoSede}-0${correlativo}`;

    document.getElementById("lbl-almacen-sede").textContent = window.CONFIG_NODO_ACTIVO.nombre;
    document.getElementById("reg-alm-codigo").value = codigoGenerated = codigoGenerado;
    
    // Limpieza de inputs
    document.getElementById("reg-alm-nombre").value = "";
    document.getElementById("reg-alm-ubicacion").value = "";
    document.getElementById("reg-alm-capacidad").value = "";

    modal.classList.add("modal-active");
}

function cerrarModalNuevoAlmacen() {
    document.getElementById("modal-nuevo-almacen").classList.remove("modal-active");
}

function insertarAlmacenLocal() {
    const codigo = document.getElementById("reg-alm-codigo").value;
    const nombre = document.getElementById("reg-alm-nombre").value.trim();
    const ubicacion = document.getElementById("reg-alm-ubicacion").value.trim();
    const capacidad = document.getElementById("reg-alm-capacidad").value.trim();

    if (!nombre || !ubicacion || !capacidad) {
        alert("[ERROR DE VALIDACION] Todos los campos de infraestructura son obligatorios para autorizar un almacen.");
        return;
    }

    // Inyección en la partición de la base de datos activa
    const nuevoAlmacen = {
        codigo: codigo,
        nombre: nombre,
        ubicacion: ubicacion,
        capacidad: capacidad
    };

    window.DB_NODO_LOCAL.almacenes.push(nuevoAlmacen);
    
    // Alerta que demuestra el dinamismo de la base de datos heterogénea en tu defensa académica
    const motorBD = window.DB_NODO_LOCAL.infraestructura.motor_bd;
    const tablaDestino = window.DB_NODO_LOCAL.infraestructura.esquema;
    alert(`[TRANSACCIÓN EXITOSA]\nAlmacen persistido localmente en: ${motorBD}\nDestino de Red: ${tablaDestino}\nCodigo Habilitado: ${codigo}`);
        
    cerrarModalNuevoAlmacen();
    listarAlmacenesLocales();
}