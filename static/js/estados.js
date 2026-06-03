// =========================================================
// CONTROLADOR: GESTIÓN DE ESTADOS DISTRIBUIDOS
// =========================================================

document.addEventListener("DOMContentLoaded", async function() {
    // 1. Inicialización de configuraciones base si no existen
    if (!window.CONFIG_NODO_ACTIVO) {
        window.CONFIG_NODO_ACTIVO = { id: "la_paz", nombre: "Sede Occidental (La Paz)" };
    }
    
    // 2. Cargamos el catálogo en memoria de manera segura sin romper el hilo principal
    try {
        if (typeof cargarEstadosDesdeBD === "function") {
            await cargarEstadosDesdeBD();
        } else {
            console.warn("⚠️ cargarEstadosDesdeBD() no está disponible en este contexto global.");
        }
    } catch (err) {
        console.error("⚠️ Error no crítico al precargar estados en memoria:", err);
    }
    
    // 3. ¡CRÍTICO!: Disparar el renderizado de la tabla si el contenedor existe en el HTML actual
    if (document.getElementById("tabla-estados-replicados-body")) {
        console.log("📊 Inicializando tabla de estados distribuidos...");
        await listarEstadosReplicados();
    }
    
    // 4. Carga colateral de paquetes si estás en la vista operativa
    if (document.getElementById("tabla-paquetes-operativos-body")) {
        try {
            if (typeof cargarPaquetesPorTipo === "function") {
                cargarPaquetesPorTipo();
            }
        } catch (err) {
            console.error("No se pudo cargar paquetes correlacionados:", err);
        }
    }
});

// Control de Modales
function abrirModalRegistroEstado() {
    document.getElementById("form-registro-estado").reset();
    document.getElementById("modal-registro-estado").classList.add("modal-active");
}

function cerrarModalRegistroEstado() {
    document.getElementById("modal-registro-estado").classList.remove("modal-active");
}

// =========================================================
// ACCIÓN: RENDERIZAR FILAS DESDE EL API CENTRAL
// =========================================================
async function listarEstadosReplicados() {
    const tbody = document.getElementById("tabla-estados-replicados-body");
    if (!tbody) return;

    try {
        const response = await fetch('/api/estados');
        const resultado = await response.json();

        tbody.innerHTML = "";

        if (response.ok && resultado.success) {
            const estados = resultado.data || [];
            if (estados.length === 0) {
                tbody.innerHTML = `<tr><td colspan="3" style="text-align:center; color: #64748b; padding: 20px;">Catálogo vacío en el clúster.</td></tr>`;
                return;
            }

            estados.forEach(est => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td style="font-family: monospace; font-weight: bold; color: #1e293b;">${est.id_estado}</td>
                    <td><span class="badge status-proceso" style="background: #e0f2fe; color: #0369a1; padding: 4px 8px; border-radius: 6px; font-weight: 500;">${est.nombre}</span></td>
                    <td style="text-align: center;">
                        <button class="btn-secundario" style="padding: 6px 12px; font-size: 0.8rem; color: #ef4444; border: 1px solid #fca5a5; background: #fff; border-radius: 6px; cursor: pointer;" onclick="eliminarEstadoCatalogo(${est.id_estado})">Remover</button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        } else {
            tbody.innerHTML = `<tr><td colspan="3" style="text-align:center; color: #ef4444;">Error del backend: ${resultado.error}</td></tr>`;
        }
    } catch (error) {
        console.error("❌ Fallo crítico al listar estados:", error);
        tbody.innerHTML = `<tr><td colspan="3" style="text-align:center; color: #ef4444;">Error de conexión con el clúster.</td></tr>`;
    }
}

// =========================================================
// ACCIÓN: REGISTRAR NUEVO ESTADO (INSERCIÓN)
// =========================================================
async function despacharRegistroEstadoCoordinador() {
    const idEstado = document.getElementById("reg-est-id").value;
    const nombreEstado = document.getElementById("reg-est-nombre").value.trim();

    if (!idEstado || !nombreEstado) {
        alert("⚠️ Todos los campos son obligatorios.");
        return;
    }

    const payload = {
        id_estado: parseInt(idEstado, 10),
        nombre: nombreEstado
    };

    try {
        const response = await fetch('/api/estado/crear', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const resultado = await response.json();

        if (response.ok && resultado.success) {
            alert(`🎉 [NUEVO ESTADO GLOBAL]: ${nombreEstado} guardado con éxito.`);
            cerrarModalRegistroEstado();
            await listarEstadosReplicados(); 
        } else {
            alert(`❌ Error al insertar en el clúster:\n${resultado.error}`);
        }
    } catch (error) {
        alert(`❌ Fallo crítico de red: ${error.message}`);
    }
}

// =========================================================
// ACCIÓN: REMOVER ESTADO DEL CATÁLOGO
// =========================================================
async function eliminarEstadoCatalogo(idEstado) {
    if (!confirm(`⚠️ ¿Está seguro de eliminar el ID Estado: ${idEstado}?\nEsto podría generar inconsistencias relacionales si existen paquetes usándolo.`)) {
        return;
    }

    try {
        const response = await fetch(`/api/estado/eliminar/${idEstado}`, {
            method: 'DELETE'
        });
        const resultado = await response.json();

        if (response.ok && resultado.success) {
            alert("✅ Estado removido correctamente del catálogo global.");
            await listarEstadosReplicados();
        } else {
            alert(`❌ Error al remover:\n${resultado.error}`);
        }
    } catch (error) {
        alert(`❌ Fallo en la comunicación distribuida: ${error.message}`);
    }
}

// =========================================================
// ACCIÓN: SINCRONIZACIÓN EN CASCADA
// =========================================================
async function ejecutarSincronizacionEstadosCascada() {
    const btn = document.getElementById("btn-sincronizar-estados-master");
    if(!btn) return;
    
    btn.disabled = true;
    btn.textContent = "⏳ Sincronizando Nodos...";

    try {
        const response = await fetch('/api/estados/sincronizar-cascada', { method: 'POST' });
        const resultado = await response.json();

        if (response.ok && resultado.success) {
            alert(`⚡ [CONSOLIDACIÓN COMPLETADA]\n${resultado.mensaje}`);
            await listarEstadosReplicados();
        } else {
            alert(`❌ Fallo de replicación: ${resultado.error}`);
        }
    } catch (error) {
        alert(`❌ Fallo de red con el cluster coordinador: ${error.message}`);
    } finally {
        btn.disabled = false;
        btn.textContent = "⚡ Sincronizar Catálogo";
    }
}