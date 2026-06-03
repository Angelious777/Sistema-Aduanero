/**
 * paquetes_nodo.js - Gestión de Transacciones de Carga Locales de acuerdo al API Flask
 */

// Usamos una función asíncrona inmediata para garantizar el orden estricto de carga
document.addEventListener("DOMContentLoaded", async function() {
    if (!window.CONFIG_NODO_ACTIVO) {
        window.CONFIG_NODO_ACTIVO = { id: "la_paz", nombre: "Sede Occidental (La Paz)" };
    }
    
    // Bloqueamos el renderizado hasta que los estados reales existan en memoria
    await cargarEstadosDesdeBD();
    
    // Una vez garantizados los estados de la BD, traemos y pintamos los paquetes
    cargarPaquetesPorTipo();
});

// Catálogo dinámico en memoria extraído de la BD
window.ESTADOS_GLOBALES = [];

// Helper para deducir el identificador del nodo activo
function obtenerNodoActualId() {
    const pathNormalizado = window.location.pathname.toLowerCase().replace(/-/g, "_");
    if (pathNormalizado.includes("la_paz") || pathNormalizado.includes("lp")) {
        return "la_paz";
    } else if (pathNormalizado.includes("santa_cruz") || pathNormalizado.includes("scz")) {
        return "santa_cruz";
    } else {
        return window.CONFIG_NODO_ACTIVO.id.toLowerCase().includes("santa") ? "santa_cruz" : "la_paz";
    }
}

// =========================================================
// CONSUMO DINÁMICO DEL CATÁLOGO DE ESTADOS DESDE LA BD
// =========================================================
async function cargarEstadosDesdeBD() {
    try {
        const response = await fetch('/api/estados');
        const resultado = await response.json();
        
        if (response.ok && resultado.success) {
            window.ESTADOS_GLOBALES = resultado.data || [];
        } else {
            console.error("❌ Error en el motor de base de datos al traer estados:", resultado.error);
        }
    } catch (error) {
        console.error("❌ Fallo crítico de red al conectar con /api/estados:", error);
    }
}

// Helper para mapear el id_estado con el nombre real de la fila SQL
function obtenerNombreEstado(idEstado) {
    const estadoEncontrado = window.ESTADOS_GLOBALES.find(e => e.id_estado == idEstado);
    return estadoEncontrado ? estadoEncontrado.nombre : `ID Estado: ${idEstado} (No existe en BD)`;
}

// =========================================================
// RENDERIZADO ASÍNCRONO DE LAS TABLAS DEL NODO DESDE EL API
// =========================================================
async function cargarPaquetesPorTipo() {
    const nodoId = obtenerNodoActualId();

    try {
        const response = await fetch(`/api/paquetes/por-tipo/${nodoId}`);
        const resultado = await response.json();

        if (!response.ok || resultado.success === false) {
            console.error("❌ Error al cargar paquetes del clúster:", resultado.error);
            return;
        }

        window.PAQUETES_NODO = resultado.data || { operativos: [], financieros: [] };
        mostrarPaquetesOperativos();
        mostrarPaquetesFinancieros();
    } catch (error) {
        console.error("❌ Error de red en cargarPaquetesPorTipo:", error);
    }
}

function mostrarPaquetesOperativos() {
    const tbody = document.getElementById("tabla-paquetes-operativos-body");
    if (!tbody) return;

    tbody.innerHTML = "";
    const paquetes = (window.PAQUETES_NODO && window.PAQUETES_NODO.operativos) || [];

    if (paquetes.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;">No hay paquetes operativos registrados en este nodo.</td></tr>`;
        return;
    }

    paquetes.forEach(pkt => {
        // 🔍 IMPRIME EL PRIMER PAQUETE EN LA CONSOLA PARA INSPECCIÓN
        console.log("Estructura real del paquete devuelto por el API:", pkt);

        const tr = document.createElement("tr");
        
        // 🛠️ DETECTOR DE LLAVES (Intenta leer id_estado, estado, ID_ESTADO o id_estado_actual)
        const idEstadoReal = pkt.id_estado ?? pkt.estado ?? pkt.ID_ESTADO ?? pkt.id_estado_actual;
        
        // Mapeo directo con el catálogo de la BD
        const txtEstado = obtenerNombreEstado(idEstadoReal);

        tr.innerHTML = `
            <td style="font-family: monospace; font-weight: bold;">${pkt.codigo_rastreo || '--'}</td>
            <td><span style="background:#f1f5f9; padding:2px 6px; border-radius:4px;">Ruta ${pkt.id_ruta || '--'}</span></td>
            <td><span class="badge status-proceso">${txtEstado}</span></td>
            <td><small>${pkt.prioridad || 'Media'}</small></td>
            <td style="text-align: center;">
                <button class="btn-secundario" style="padding: 4px 10px; font-size: 0.8rem;" onclick="verDetallePaquete('${pkt.codigo_rastreo}')">Examinar</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function mostrarPaquetesFinancieros() {
    const tbody = document.getElementById("tabla-paquetes-financieros-body");
    if (!tbody) return;

    tbody.innerHTML = "";
    const paquetes = (window.PAQUETES_NODO && window.PAQUETES_NODO.financieros) || [];

    if (paquetes.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;">No hay registros financieros devueltos por el fragmento vertical.</td></tr>`;
        return;
    }

    paquetes.forEach(pkt => {
        const costo = parseFloat(pkt.costo_envio) || 0.0;
        const seguro = parseFloat(pkt.seguro) || 0.0;
        const valorDeclarado = parseFloat(pkt.valor_declarado) || 0.0;

        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td style="font-family: monospace; font-weight: bold; font-size:11px;">${pkt.id_paquete || '--'}</td>
            <td><strong>${costo.toFixed(2)} Bs</strong></td>
            <td>${seguro.toFixed(2)} Bs</td>
            <td>${valorDeclarado.toFixed(2)} Bs</td>
            <td style="text-align: center;">
                <button class="btn-secundario" style="padding: 4px 10px; font-size: 0.8rem;" onclick="alert('Auditoría ID: ${pkt.id_paquete}')">Ver</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

// =========================================================
// CARGA SEPARADA DE REMITENTE Y DESTINATARIO DESDE EL CATALOGO
// =========================================================
async function cargarComboboxModal() {
    try {
        const resClientes = await fetch('/api/clientes').then(r => r.json());
        const selectRemitente = document.getElementById("reg-pkt-remitente");
        const selectDestinatario = document.getElementById("reg-pkt-destinatario");

        if (resClientes.success && resClientes.data) {
            let optionsRem = '<option value="">-- Seleccione Remitente --</option>';
            let optionsDest = '<option value="">-- Seleccione Destinatario --</option>';
            
            resClientes.data.forEach(c => {
                const item = `<option value="${c.id_cliente || c.id}">${c.nombre} (Doc: ${c.documento || 'S/D'})</option>`;
                optionsRem += item;
                optionsDest += item;
            });
            
            if (selectRemitente) selectRemitente.innerHTML = optionsRem;
            if (selectDestinatario) selectDestinatario.innerHTML = optionsDest;
        }

        const selectDestino = document.getElementById("reg-pkt-destino");
        if (selectDestino) {
            let options = '<option value="">-- Seleccione Ruta de Tránsito Habilitada --</option>';
            const tusRutasReales = [
                { id: 1, descripcion: "Ruta 1: Almacén Central LP ➔ Almacén Central SCZ (Envío Terrestre)" },
                { id: 2, descripcion: "Ruta 2: Almacén Central SCZ ➔ Almacén Central LP (Retorno Terrestre)" }
            ];
            tusRutasReales.forEach(ruta => {
                options += `<option value="${ruta.id}">${ruta.descripcion}</option>`;
            });
            selectDestino.innerHTML = options;
        }
    } catch (err) {
        console.error("❌ Error inyectando llaves foráneas reales a la interfaz:", err);
    }
}

// =========================================================
// APERTURA DE MODAL Y GENERACIÓN DISJUNTA DE LLAVES
// =========================================================
function abrirModalNuevoPaquete() {
    const modal = document.getElementById("modal-nuevo-paquete");
    const nodoId = obtenerNodoActualId();
    const prefijoSede = nodoId === "santa_cruz" ? "SCZ" : "LP";
    
    const idUnico = Math.floor(1000 + Math.random() * 9000); 
    const codigoGenerated = `PKT-${prefijoSede}-${idUnico}`;

    document.getElementById("lbl-prefijo-sede").textContent = prefijoSede === "SCZ" ? "Sede Oriental (Santa Cruz)" : "Sede Occidental (La Paz)";
    
    document.getElementById("form-registro-paquete").reset();
    document.getElementById("reg-pkt-codigo").value = codigoGenerated;

    cargarComboboxModal();
    modal.classList.add("modal-active");
}

function cerrarModalNuevoPaquete() {
    document.getElementById("modal-nuevo-paquete").classList.remove("modal-active");
}

// =========================================================
// TRANSMISIÓN POST AL COORDINADOR FLASK CON TODOS LOS CAMPOS
// =========================================================
async function insertarPaqueteLocal() {
    const codigo = document.getElementById("reg-pkt-codigo").value;
    const idRutaSeleccionada = document.getElementById("reg-pkt-destino").value;
    const prioridad = document.getElementById("reg-pkt-prioridad").value;
    const remitente = document.getElementById("reg-pkt-remitente").value;
    const destinatario = document.getElementById("reg-pkt-destinatario").value;
    const descripcion = document.getElementById("reg-pkt-desc").value.trim();
    
    const costo = document.getElementById("reg-pkt-costo").value;
    const peso = document.getElementById("reg-pkt-peso").value;
    const volumen = document.getElementById("reg-pkt-volumen").value;
    const valorDeclarado = document.getElementById("reg-pkt-valor-declarado").value;
    const seguro = document.getElementById("reg-pkt-seguro").value;

    if (!idRutaSeleccionada || !remitente || !destinatario) {
        alert("⚠️ Validación SQL: 'Ruta', 'Remitente' y 'Destinatario' son restricciones relacionales obligatorias.");
        return;
    }

    const nodoDestino = obtenerNodoActualId();
    const idAlmacenDefault = nodoDestino === "santa_cruz" ? 2 : 1; 

    const payload = {
        codigo: codigo,
        id_ruta: parseInt(idRutaSeleccionada), 
        prioridad: prioridad,
        nodo: nodoDestino,
        id_cliente_remitente: remitente,         
        id_cliente_destinatario: destinatario,   
        id_estado: 1,                            
        id_almacen_actual: idAlmacenDefault,
        descripcion: descripcion,
        costo: parseFloat(costo) || 0.0,
        peso: parseFloat(peso) || 1.0,
        volumen: parseFloat(volumen) || 1.0,
        valor_declarado: parseFloat(valorDeclarado) || 0.0,
        seguro: parseFloat(seguro) || 0.0
    };

    try {
        const response = await fetch('/api/paquete/crear', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const resultado = await response.json();

        if (response.ok && resultado.success) {
            alert(`🎉 [COMMIT EXITOSO]\nCódigo Tracking: ${codigo}`);
            cerrarModalNuevoPaquete();
            cargarPaquetesPorTipo(); 
        } else {
            alert(`❌ Error del Motor:\n${resultado.error}`);
        }
    } catch (error) {
        alert(`❌ Error de comunicación con el clúster: ${error.message}`);
    }
}

// =========================================================
// REVISIÓN LOCAL Y CONSUMO DEL BOTÓN ACTUALIZAR ESTADO
// =========================================================
function verDetallePaquete(codigo) {
    const paquetes = (window.PAQUETES_NODO && window.PAQUETES_NODO.operativos) || [];
    const pkt = paquetes.find(p => p.codigo_rastreo === codigo);
    
    if (!pkt) return;

    // Detectamos el ID del estado tal como venga del backend
    const idEstadoReal = pkt.id_estado ?? pkt.estado ?? pkt.ID_ESTADO ?? pkt.id_estado_actual;

    document.getElementById("dt-pkt-id-interno").value = pkt.id_paquete;
    document.getElementById("dt-pkt-codigo").textContent = pkt.codigo_rastreo;
    document.getElementById("dt-pkt-destino").textContent = `Línea de Tránsito: Ruta N° ${pkt.id_ruta || 1}`;
    document.getElementById("dt-pkt-prioridad-txt").textContent = pkt.prioridad || "Media";
    
    // Texto dinámico directo
    document.getElementById("dt-pkt-estado-txt").textContent = obtenerNombreEstado(idEstadoReal);
    document.getElementById("dt-pkt-desc").textContent = pkt.descripcion || "Sin descripción física.";
    
    // Población dinámica del SELECT
    const selectEstado = document.getElementById("dt-pkt-select-estado");
    if (selectEstado) {
        selectEstado.innerHTML = ""; 
        window.ESTADOS_GLOBALES.forEach(est => {
            const option = document.createElement("option");
            option.value = est.id_estado;
            option.textContent = est.nombre;
            // Comparación con el ID real detectado
            if (est.id_estado == idEstadoReal) {
                option.selected = true;
            }
            selectEstado.appendChild(option);
        });
    }

    document.getElementById("modal-detalle-paquete").classList.add("modal-active");
}

function cerrarModalDetallePaquete() {
    document.getElementById("modal-detalle-paquete").classList.remove("modal-active");
}

async function guardarEstadoPaqueteLocal() {
    const idPaquete = document.getElementById("dt-pkt-id-interno").value;
    const nuevoEstado = document.getElementById("dt-pkt-select-estado").value;
    const nodoId = obtenerNodoActualId();

    if (!idPaquete) {
        alert("❌ Error: Falta el Identificador de clave primaria del fragmento.");
        return;
    }

    const payload = {
        id_paquete: idPaquete,
        id_estado: parseInt(nuevoEstado),
        nodo: nodoId
    };

    try {
        const response = await fetch('/api/paquete/actualizar-estado', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const resultado = await response.json();

        if (response.ok && resultado.success) {
            alert("✅ [UPDATE COMPLETED] El estado de la carga aduanera se actualizó en el clúster.");
            cerrarModalDetallePaquete();
            cargarPaquetesPorTipo(); 
        } else {
            alert(`❌ Error al actualizar estado:\n${resultado.error || 'Fallo interno'}`);
        }
    } catch (error) {
        alert(`❌ Error de red con los nodos: ${error.message}`);
    }
}