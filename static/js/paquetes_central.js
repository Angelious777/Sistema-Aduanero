document.addEventListener("DOMContentLoaded", () => {
    let listaPaquetesGlobal = [];

    // Selectores del DOM
    const tablaBody = document.getElementById("tabla-paquetes-body");
    const btnFiltrar = document.getElementById("btn-filtrar-paquetes");
    const filtroCodigo = document.getElementById("filtro-codigo-paquete");
    const filtroEstado = document.getElementById("filtro-estado-paquete");
    const filtroOrigen = document.getElementById("filtro-ciudad-origen");
    const filtroDestino = document.getElementById("filtro-ciudad-destino");

    // Modal (Mapeado con el ID correcto del HTML)
    const modal = document.getElementById("modal-detalle-paquete");
    const btnCerrarModal = document.getElementById("btn-cerrar-modal-paquete");

    // Cargar datos al iniciar
    async function cargarPaquetes() {
        try {
            const response = await fetch('/api/paquetes');
            const resJson = await response.json();
            if (resJson.success) {
                listaPaquetesGlobal = resJson.data;
                renderizarTabla(listaPaquetesGlobal);
            } else {
                console.error("Error al obtener paquetes de aduana:", resJson.error);
            }
        } catch (error) {
            console.error("Fallo de red en el nodo coordinador:", error);
        }
    }

    function renderizarTabla(paquetes) {
        tablaBody.innerHTML = "";
        if (paquetes.length === 0) {
            tablaBody.innerHTML = `<tr><td colspan="9" style="text-align:center; color: #64748b; padding:20px;">No se encontraron registros de paquetes federados.</td></tr>`;
            return;
        }

        paquetes.forEach(p => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td><strong>${p.codigo}</strong></td>
                <td>${p.remitente}</td>
                <td>${p.destinatario}</td>
                <td><span style="color:#0f766e; font-weight:500;">🏭 ${p.almacen_actual}</span></td>
                <td>${p.ciudad_origen}</td>
                <td>${p.ciudad_destino}</td>
                <td><span class="badge state-${p.estado.toLowerCase().replace(/\s+/g, '-')}">${p.estado}</span></td>
                <td><small>${p.registro}</small></td>
                <td style="text-align: center;">
                    <button class="btn-accion-ver" style="background:#0284c7; color:#fff; border:none; padding:6px 12px; border-radius:4px; cursor:pointer; font-size:12px;">
                        🔎 Ver Ficha
                    </button>
                </td>
            `;
            
            // Asignar evento al botón de detalles
            tr.querySelector(".btn-accion-ver").addEventListener("click", () => abrirModalDetalle(p));
            tablaBody.appendChild(tr);
        });
    }

    // Filtros lógicos en cliente
    btnFiltrar.addEventListener("click", () => {
        const cod = filtroCodigo.value.toLowerCase().trim();
        const est = filtroEstado.value;
        const ori = filtroOrigen.value;
        const des = filtroDestino.value;

        const filtrados = listaPaquetesGlobal.filter(p => {
            const matchCod = p.codigo.toLowerCase().includes(cod);
            const matchEst = est === "" || p.estado === est;
            const matchOri = ori === "" || p.ciudad_origen === ori;
            const matchDes = des === "" || p.ciudad_destino === des;
            return matchCod && matchEst && matchOri && matchDes;
        });

        renderizarTabla(filtrados);
    });

    // Despliegue de Ficha Unificada (Modal)
    async function abrirModalDetalle(paquete) {
        document.getElementById("modal-paquete-titulo").innerText = `Detalle de Paquete: ${paquete.codigo}`;
        
        // 1. Renderizar Bloque Logístico Físico
        document.getElementById("modal-paquete-info-general").innerHTML = `
            <p><strong>📦 Descripción:</strong> ${paquete.descripcion}</p>
            <p><strong>⚖️ Peso Clínico:</strong> ${paquete.peso} Kg.</p>
            <p><strong>📐 Volumen Ocupado:</strong> ${paquete.volumen} m³</p>
            <p><strong>🚨 Prioridad de Despacho:</strong> <span style="font-weight:bold; color:#b45309;">${paquete.prioridad}</span></p>
        `;

        // 2. Renderizar Bloque Financiero Aduanero
        document.getElementById("modal-paquete-info-financiera").innerHTML = `
            <p><strong>💵 Valor Declarado CIF:</strong> Bs. ${paquete.valor_declarado.toFixed(2)}</p>
            <p><strong>🛡️ Seguro de Mercancía:</strong> Bs. ${paquete.seguro.toFixed(2)}</p>
            <p><strong>💳 Costo Operativo Envío:</strong> Bs. ${paquete.costo_envio.toFixed(2)}</p>
            <div style="margin-top:10px; background:#f0fdf4; border:1px solid #bbf7d0; padding:6px; border-radius:4px; font-size:11px; color:#166534;">
                ✅ Liquidación fiscal unificada por Nodo Central.
            </div>
        `;

        // 3. Consultar Historial de Movimientos Real mediante API
        const tablaHistorial = document.getElementById("modal-paquete-tabla-historial");
        tablaHistorial.innerHTML = `<tr><td colspan="4" style="text-align:center;">⌛ Cargando traza de auditoría...</td></tr>`;

        try {
            const res = await fetch(`/api/paquetes/historial/${paquete.id}`);
            const resJson = await res.json();
            
            if (resJson.success && resJson.data.length > 0) {
                tablaHistorial.innerHTML = "";
                resJson.data.forEach(h => {
                    const row = document.createElement("tr");
                    row.innerHTML = `
                        <td><small>${h.fecha}</small></td>
                        <td>${h.observacion}</td>
                        <td><strong>🏭 ${h.almacen}</strong></td>
                        <td><code style="background:#f1f5f9; padding:2px 6px; border-radius:4px; color:#0f172a;">${h.nodo}</code></td>
                    `;
                    tablaHistorial.appendChild(row);
                });
            } else {
                // 🔄 MODIFICACIÓN AQUÍ: Mensaje oficial de "Sin movimientos"
                tablaHistorial.innerHTML = `
                    <tr>
                        <td colspan="4" style="text-align: center; color: var(--gris-medio); padding: 20px; font-style: italic;">
                            No existen movimientos ni trazas de auditoría registradas para este paquete.
                        </td>
                    </tr>`;
            }
        } catch (err) {
            tablaHistorial.innerHTML = `<tr><td colspan="4" style="color:#991b1b; text-align:center;">⚠️ No se pudo reconstruir el historial.</td></tr>`;
        }

        // 🟢 SOLUCIÓN: Usar la variable "modal" declarada arriba con el ID correcto
        if (modal) {
            modal.style.display = "flex";
            modal.classList.add("open");
        }
    }

    // Eventos para cerrar el modal de manera segura
    if (btnCerrarModal) {
        btnCerrarModal.addEventListener("click", cerrarModalActual);
    }
    
    window.addEventListener("click", (e) => { 
        if (e.target === modal) {
            cerrarModalActual();
        } 
    });

    function cerrarModalActual() {
        if (modal) {
            modal.style.display = "none";
            modal.classList.remove("open");
        }
    }

    // Carga inicial
    cargarPaquetes();
});

// Función global de escape (en caso de llamarse externamente)
function cerrarModal() {
    const modal = document.getElementById("modal-detalle-paquete");
    if (modal) {
        modal.style.display = "none";
        modal.classList.remove("open");
    }
}