/**
 * transacciones.js
 * Control y Simulación Visual Interactiva del Protocolo Two-Phase Commit (2PC)
 */

let MOCK_BITACORA_2PC = [
    { id: "TX-10042", fecha: "2026-05-31 09:40", tipo: "Transferencia Interdepartamental", estado: "COMMIT_GLOBAL", votos: "LP: SI | SCZ: SI" },
    { id: "TX-10041", fecha: "2026-05-31 11:15", tipo: "Cierre de Póliza de Seguro", estado: "COMMIT_GLOBAL", votos: "LP: SI | SCZ: SI" },
    { id: "TX-10040", fecha: "2026-05-31 13:10", tipo: "Transferencia Fronteriza Fallida", estado: "ABORT_RECHAZADO", votos: "LP: SI | SCZ: NO (Timeout)" }
];

document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("btnPrepare").addEventListener("click", ejecutarFase1Prepare);
    document.getElementById("btnCommit").addEventListener("click", ejecutarFase2Commit);
    document.getElementById("btnAbort").addEventListener("click", ejecutarFase2Abort);
    
    inicializarTransacciones();
});

function inicializarTransacciones() {
    renderizarTablaTransacciones();
    resetearDiagramaVisual2PC();
}

function renderizarTablaTransacciones() {
    const tbody = document.getElementById("tablaTransacciones");
    if (!tbody) return;

    tbody.innerHTML = "";
    MOCK_BITACORA_2PC.forEach(tx => {
        let claseBadge = "info";
        if (tx.estado === "COMMIT_GLOBAL") claseBadge = "success";
        if (tx.estado === "ABORT_RECHAZADO") claseBadge = "danger";
        if (tx.estado === "PREPARE_EN_PROCESO") claseBadge = "waiting";

        const fila = document.createElement("tr");
        fila.innerHTML = `
            <td><strong>${tx.id}</strong></td>
            <td>${tx.fecha}</td>
            <td>${tx.tipo}</td>
            <td><span class="badge-status ${claseBadge}">${tx.estado}</span></td>
            <td><code>${tx.votos}</code></td>
        `;
        tbody.appendChild(fila);
    });
}

function resetearDiagramaVisual2PC() {
    // Valores por defecto del flujo gráfico
    document.getElementById("badge-coord-2pc").textContent = "IDLE / EN ESPERA";
    document.getElementById("badge-coord-2pc").className = "estado-fase-badge";
    
    document.getElementById("badge-lp-2pc").textContent = "ESPERANDO";
    document.getElementById("badge-lp-2pc").className = "estado-fase-badge";
    document.getElementById("badge-scz-2pc").textContent = "ESPERANDO";
    document.getElementById("badge-scz-2pc").className = "estado-fase-badge";

    document.getElementById("msg-lp-2pc").textContent = "...";
    document.getElementById("msg-scz-2pc").textContent = "...";
    
    // Habilitar solo botón de Fase 1
    document.getElementById("btnPrepare").disabled = false;
    document.getElementById("btnCommit").disabled = true;
    document.getElementById("btnCommit").classList.add("disabled");
    document.getElementById("btnAbort").disabled = true;
    document.getElementById("btnAbort").classList.add("disabled");
}

function ejecutarFase1Prepare() {
    // 1. Cambiar estado del coordinador
    const coordBadge = document.getElementById("badge-coord-2pc");
    coordBadge.textContent = "FASE 1: PREPARE";
    coordBadge.classList.add("waiting");

    document.getElementById("btnPrepare").disabled = true;

    // Simular el envío de mensajes por los canales de red hacia los fragmentos
    document.getElementById("msg-lp-2pc").textContent = "VOTING_REQUEST ➔";
    document.getElementById("msg-lp-2pc").className = "flecha-msg envia-msg";
    document.getElementById("msg-scz-2pc").textContent = "VOTING_REQUEST ➔";
    document.getElementById("msg-scz-2pc").className = "flecha-msg envia-msg";

    // Retraso para simular la llegada del mensaje y votación positiva de los nodos regionales
    setTimeout(() => {
        document.getElementById("badge-lp-2pc").textContent = "VOTO: LISTO (SI)";
        document.getElementById("badge-lp-2pc").classList.add("success");
        document.getElementById("msg-lp-2pc").textContent = "🠔 VOTE_COMMIT";
        document.getElementById("msg-lp-2pc").className = "flecha-msg recibe-msg";

        document.getElementById("badge-scz-2pc").textContent = "VOTO: LISTO (SI)";
        document.getElementById("badge-scz-2pc").classList.add("success");
        document.getElementById("msg-scz-2pc").textContent = "🠔 VOTE_COMMIT";
        document.getElementById("msg-scz-2pc").className = "flecha-msg recibe-msg";

        // Coordinador recibe los votos afirmativos y se prepara para decidir
        coordBadge.textContent = "VOTOS RECIBIDOS: OK";
        
        // Habilitar controles de la Fase 2
        document.getElementById("btnCommit").disabled = false;
        document.getElementById("btnCommit").classList.remove("disabled");
        document.getElementById("btnAbort").disabled = false;
        document.getElementById("btnAbort").classList.remove("disabled");

    }, 1200);
}

function ejecutarFase2Commit() {
    const ahora = new Date().toISOString().replace('T', ' ').substring(0, 16);
    const nuevaId = "TX-" + Math.floor(10000 + Math.random() * 90000);

    // Actualizar flujo visual a confirmación exitosa global
    document.getElementById("badge-coord-2pc").textContent = "GLOBAL_COMMIT ➔";
    document.getElementById("badge-coord-2pc").className = "estado-fase-badge success";

    document.getElementById("msg-lp-2pc").textContent = "GLOBAL_COMMIT ➔";
    document.getElementById("msg-scz-2pc").textContent = "GLOBAL_COMMIT ➔";

    setTimeout(() => {
        document.getElementById("badge-lp-2pc").textContent = "REGISTRO ASEGURADO";
        document.getElementById("badge-scz-2pc").textContent = "REGISTRO ASEGURADO";
        
        // Registrar en la tabla de auditoría del coordinador
        MOCK_BITACORA_2PC.unshift({
            id: nuevaId,
            fecha: ahora,
            tipo: "Transferencia Interdepartamental",
            estado: "COMMIT_GLOBAL",
            votos: "LP: SI | SCZ: SI"
        });

        renderizarTablaTransacciones();
        alert("Operación Completa: Transacción atómica confirmada y escrita de manera segura en toda la red nacional.");
        resetearDiagramaVisual2PC();
    }, 1000);
}

function ejecutarFase2Abort() {
    const ahora = new Date().toISOString().replace('T', ' ').substring(0, 16);
    const nuevaId = "TX-" + Math.floor(10000 + Math.random() * 90000);

    // Cancelación forzada por el operador o por simulación de error en destino
    document.getElementById("badge-coord-2pc").textContent = "GLOBAL_ABORT ➔";
    document.getElementById("badge-coord-2pc").className = "estado-fase-badge danger";

    document.getElementById("msg-lp-2pc").textContent = "GLOBAL_ROLLBACK ➔";
    document.getElementById("msg-scz-2pc").textContent = "GLOBAL_ROLLBACK ➔";

    setTimeout(() => {
        document.getElementById("badge-lp-2pc").textContent = "TRANSACCIÓN ABORTADA";
        document.getElementById("badge-lp-2pc").className = "estado-fase-badge danger";
        document.getElementById("badge-scz-2pc").textContent = "TRANSACCIÓN ABORTADA";
        document.getElementById("badge-scz-2pc").className = "estado-fase-badge danger";
        
        MOCK_BITACORA_2PC.unshift({
            id: nuevaId,
            fecha: ahora,
            tipo: "Transferencia Interdepartamental",
            estado: "ABORT_RECHAZADO",
            votos: "Operador canceló la operación"
        });

        renderizarTablaTransacciones();
        alert("Rollback ejecutado: Se liberaron los bloqueos preventivos en los nodos regionales. Ninguna base de datos fue alterada.");
        resetearDiagramaVisual2PC();
    }, 1000);
}