// almacenes_nodo.js

document.addEventListener("DOMContentLoaded", () => {
    // Primera carga automática al abrir la pestaña o sección
    listarAlmacenesLocales();
});

/**
 * Trae los almacenes registrados consumiendo el endpoint global de tu app.py
 */
async function listarAlmacenesLocales() {
    const tbody = document.getElementById("tabla-almacenes-local-body");
    if (!tbody) return;

    // Loader visual estético
    tbody.innerHTML = `
        <tr>
            <td colspan="4" style="text-align: center; padding: 30px; color: var(--gris-medio, #64748b);">
                ⏳ Leyendo topología de almacenes desde el Clúster Central...
            </td>
        </tr>`;

    try {
        // Consumimos tu endpoint exacto: @app.route('/api/almacen/listar')
        const response = await fetch('/api/almacen/listar');
        const resultado = await response.json();

        if (response.ok && resultado.success) {
            const almacenes = resultado.data || [];

            if (almacenes.length === 0) {
                tbody.innerHTML = `<tr><td colspan="4" style="text-align: center; padding: 24px;">🔍 No hay almacenes creados en la red.</td></tr>`;
                return;
            }

            tbody.innerHTML = ""; // Limpiamos el loader

            almacenes.forEach(alm => {
                const tr = document.createElement("tr");

                // Mapeo uno a uno con las llaves JSON de tu app.py
                const id = alm.id_almacen;
                const nombre = alm.nombre || "Sin Nombre";
                const ciudad = alm.ciudad || "No Especificada";
                const direccion = alm.direccion || "Dirección ausente";
                const nodo = alm.nodo_responsable || "CENTRAL";

                tr.innerHTML = `
                    <td><code>${id}</code></td>
                    <td><strong>${nombre}</strong></td>
                    <td>
                        <div style="font-weight: 500; font-size: 13px;">${direccion}</div>
                        <small style="color: #64748b; font-size: 11px;">📍 ${ciudad}</small>
                    </td>
                    <td>
                        <span style="background: #e0f2fe; color: #0369a1; padding: 4px 8px; border-radius: 6px; font-size: 11px; font-weight: bold; font-family: monospace;">
                            ⚙️ ${nodo.toUpperCase()}
                        </span>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        } else {
            tbody.innerHTML = `<tr><td colspan="4" style="text-align: center; color: red; padding: 24px;">❌ Error de Lectura: ${resultado.error}</td></tr>`;
        }
    } catch (error) {
        console.error("Fallo crítico en listarAlmacenesLocales:", error);
        tbody.innerHTML = `<tr><td colspan="4" style="text-align: center; color: red; padding: 24px;">🚨 Error de comunicación con el clúster.</td></tr>`;
    }
}

/**
 * Gatillo del botón "Sincronizar con Central". 
 * Ejecuta el UPSERT en cascada e inmediatamente refresca la vista.
 */
async function sincronizarConCentralBoton() {
    console.log("⚡ Iniciando alineación de catálogos en cascada...");
    
    try {
        // Consumimos tu endpoint de sincronización forzada inteligente: @app.route('/api/almacen/sincronizar')
        const response = await fetch('/api/almacen/sincronizar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const resultado = await response.json();
        
        if (response.ok && resultado.success) {
            alert(`✅ [SINCRO EXITOSA] ${resultado.mensaje || 'Catálogos alineados sin quiebre de FK.'}`);
        } else {
            alert(`⚠️ Advertencia del Motor:\n${resultado.error || 'No se pudo completar la réplica'}`);
        }
    } catch (error) {
        alert(`❌ Error de red al intentar ejecutar la cascada distribuida: ${error.message}`);
    } finally {
        // Pase lo que pase, refrescamos la tabla local para reflejar el estado actual
        listarAlmacenesLocales();
    }
}