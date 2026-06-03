/**
 * consultas.js - Motor Académico de Consultas Distribuidas (Pipeline Engine)
 */
document.addEventListener("DOMContentLoaded", function() {
    const btn = document.getElementById("btn-ejecutar-query-parser");
    if (btn) btn.addEventListener("click", simularPipelineProcesamiento);
});

function simularPipelineProcesamiento() {
    const codigo = document.getElementById("input-query-codigo").value.trim().toUpperCase();
    const panel = document.getElementById("panel-pipeline-distribuido");
    
    if (!codigo) {
        alert("Por favor, introduzca un código válido para iniciar el parser.");
        return;
    }

    const paquete = window.DB_PROYECTO_GLOBAL.paquetes.find(p => p.codigo === codigo);
    if (!paquete) {
        alert("Código no localizado. Intente con: PK-LP-2026-001 o PK-SCZ-2026-002");
        return;
    }

    // Mostrar el contenedor e iniciar animación limpia
    panel.style.display = "flex";
    const steps = ["step-gateway", "step-parser", "step-catalogo", "step-optimizador", "step-planificador", "step-ensamblador"];
    
    // Limpiar clases previas
    steps.forEach(id => document.getElementById(id).classList.remove("active-step"));

    // Pipeline secuencial animado con timers para defensa académica
    let delay = 0;
    steps.forEach((stepId, index) => {
        setTimeout(() => {
            document.getElementById(stepId).classList.add("active-step");
            
            // Cuando llega al final (ensamblador), inyecta los datos de auditoría técnica
            if (index === steps.length - 1) {
                finalizarCargaMetricas(paquete);
            }
        }, delay);
        delay += 350; // Velocidad de la animación (350ms por salto de componente)
    });
}

function finalizarCargaMetricas(paquete) {
    const esLP = paquete.nodo === "NODO_LA_PAZ";
    
    // Rellenar etiquetas de control interno
    document.getElementById("lbl-tech-fragments").textContent = esLP ? "PAQUETE_OPERATIVO_LP, PAQUETE_FINANCIERO_LP" : "PAQUETE_OPERATIVO_SCZ, PAQUETE_FINANCIERO_SCZ";
    document.getElementById("lbl-tech-nodo").textContent = paquete.nodo + (esLP ? " [PostgreSQL]" : " [MS SQL Server]");
    document.getElementById("lbl-tech-time").textContent = `${Math.floor(Math.random() * (45 - 15) + 15)} ms`;

    // Buscar correspondencia de cliente para simular la vista relacional unificada completa
    const cliente = window.DB_PROYECTO_GLOBAL.clientes.find(c => c.nombre.includes(paquete.remitente.split(' ')[0])) || {};

    // Construcción del objeto JSON simulado de respuesta
    const jsonOutput = {
        "SELECT_FEDERADO": {
            "status": "SUCCESS",
            "execution_plan": "RECONSTRUCCION_VERTICAL_HORIZONTAL",
            "data": {
                "codigo": paquete.codigo,
                "descripcion_mercaderia": paquete.descripcion || "Componentes e Insumos consolidados de aduana",
                "origen_datos": paquete.origen,
                "destino_datos": paquete.destino,
                "esquema_financiero": {
                    "costo_envio_bs": paquete.costo,
                    "impuesto_arancelario": paquete.impuestos,
                    "auditoria_pago": paquete.pago
                },
                "esquema_cliente_unificado": {
                    "titular": cliente.nombre || paquete.remitente,
                    "nit_ci": cliente.documento || "4892019 BO",
                    "esquema_origen": cliente.tipo || "CLIENTE_PRIVADO"
                }
            }
        }
    };

    document.getElementById("json-resultado-output").textContent = JSON.stringify(jsonOutput, null, 4);
}