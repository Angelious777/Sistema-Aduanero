/**
 * seguimiento.js - Controlador de Línea de Tiempo e Historial de Trazabilidad
 */
document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("btn-ejecutar-rastreo").addEventListener("click", procesarRastreoLineaTiempo);
});

function procesarRastreoLineaTiempo() {
    const codigoInput = document.getElementById("txt-rastreo-codigo").value.trim().toUpperCase();
    const errorLbl = document.getElementById("rastreo-error");
    const cardResultado = document.getElementById("card-resultado-seguimiento");

    errorLbl.textContent = "";

    if (!codigoInput) {
        errorLbl.textContent = "Por favor, digite un código de rastreo válido.";
        cardResultado.classList.add("resultado-oculto");
        return;
    }

    // Buscar en la base unificada compartida
    const paquete = window.DB_PROYECTO_GLOBAL.paquetes.find(p => p.codigo === codigoInput);
    
    if (!paquete) {
        errorLbl.textContent = `La encomienda "${codigoInput}" no se encuentra registrada en el catálogo de datos del coordinador.`;
        cardResultado.classList.add("resultado-oculto");
        return;
    }

    // Buscar el último movimiento capturado para saber la ubicación actual
    const movimientos = window.DB_PROYECTO_GLOBAL.movimientos.filter(m => m.paquete === codigoInput);
    const ultimoMov = movimientos[movimientos.length - 1] || { evento: "En Cola", almacen: "Origen" };

    // Inyectar etiquetas de texto de resultados
    document.getElementById("txt-res-codigo").textContent = `ENCOMIENDA: ${paquete.codigo}`;
    document.getElementById("txt-res-estado").textContent = paquete.estado;
    document.getElementById("txt-res-ruta").textContent = `${paquete.origen} ➔ ${paquete.destino}`;
    document.getElementById("txt-res-remitente").textContent = paquete.remitente;
    document.getElementById("txt-res-desc").textContent = paquete.descripcion || "Mercadería general e insumos aduaneros.";
    document.getElementById("txt-res-ubica").textContent = ultimoMov.almacen;
    document.getElementById("txt-res-evento").textContent = ultimoMov.evento;
    document.getElementById("txt-res-nodo").textContent = paquete.nodo;

    // Actualizar estados visuales en el Timeline de forma precisa
    actualizarNodosTimeline(paquete.estado);

    // Hacer visible el card animado
    cardResultado.classList.remove("resultado-oculto");
}

function actualizarNodosTimeline(estadoActual) {
    const pasos = ["Registrado", "Despachado", "En Tránsito", "Recibido", "Entregado"];
    const idsMap = {
        "Registrado": "step-registrado",
        "Despachado": "step-despachado",
        "En Tránsito": "step-transito",
        "Recibido": "step-recibido",
        "Entregado": "step-entregado"
    };

    // Ajustes adaptativos basados en el estado del registro actual
    let indiceMapeado = 0;
    if (estadoActual === "Registrado") indiceMapeado = 0;
    if (estadoActual === "En Tránsito") indiceMapeado = 2; // Brinca Despachado conceptualmente
    if (estadoActual === "Retenido por Aduana") indiceMapeado = 2; // Se congela en tránsito
    if (estadoActual === "Entregado") indiceMapeado = 4; // Pipeline completo

    pasos.forEach((p, idx) => {
        const elemId = idsMap[p];
        const el = document.getElementById(elemId);
        if (!el) return;

        el.classList.remove("completed", "active");

        if (idx < indiceMapeado) {
            el.classList.add("completed");
        } else if (idx === indiceMapeado) {
            el.classList.add("active");
        }
    });
}