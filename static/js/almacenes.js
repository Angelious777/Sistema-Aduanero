/**
 * almacenes_nodo.js - Consulta de Infraestructura Física Autorizada desde BD Real
 */

document.addEventListener("DOMContentLoaded", function() {
    listarAlmacenesLocales();
});

async function listarAlmacenesLocales() {
    const tbody = document.getElementById("tabla-almacenes-local-body");
    if (!tbody) return;

    const nodoId = window.CONFIG_NODO_ACTIVO ? window.CONFIG_NODO_ACTIVO.id : null;
    if (!nodoId) {
        tbody.innerHTML = `<tr><td colspan="4" style="text-align:center; color:red;">Error: No se pudo verificar la identidad de la rampa regional.</td></tr>`;
        return;
    }

    const nodoParam = nodoId === "NODO_SANTA_CRUZ" ? "santa_cruz" : "la_paz";

    try {
        const response = await fetch(`/api/almacenes/${nodoParam}`);
        const resultado = await response.json();

        if (!resultado.success) {
            throw new Error(resultado.error || "Error al leer la base de datos distribuida");
        }

        const almacenes = resultado.data || [];
        tbody.innerHTML = "";

        if (almacenes.length === 0) {
            tbody.innerHTML = `<tr><td colspan="4" style="text-align:center; color: var(--gris-oscuro);">No se encontraron registros en la tabla 'almacen' para este nodo.</td></tr>`;
            return;
        }

        // Mapeo directo de las columnas SQL reales extraídas por el driver del backend
        almacenes.forEach(alm => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td style="font-family: monospace; font-weight: bold; color: var(--azul-medio);">ID-${alm.id_almacen}</td>
                <td style="font-weight: 600; color: var(--azul-oscuro);">${alm.nombre}</td>
                <td>${alm.direccion} (${alm.ciudad})</td>
                <td><strong style="color: var(--verde-exito);">${alm.nodo_responsable}</strong></td>
            `;
            tbody.appendChild(tr);
        });

    } catch (error) {
        console.error("❌ Error al sincronizar almacenes con la BD:", error);
        tbody.innerHTML = `<tr><td colspan="4" style="text-align:center; color:red;">Fallo de conexión con la tabla 'almacen': ${error.message}</td></tr>`;
    }
}