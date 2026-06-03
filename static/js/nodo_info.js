document.addEventListener("DOMContentLoaded", function() {
    cargarFichaInfraestructuraNodo();
});

function cargarFichaInfraestructuraNodo() {
    const db = window.DB_NODO_LOCAL;
    if(!db) return;

    document.getElementById("info-lbl-nodo").textContent = db.config.nombre;
    document.getElementById("info-lbl-motor").textContent = db.config.motor;
    
    const d = new Date();
    document.getElementById("info-lbl-fecha").textContent = d.getFullYear()+"-"+String(d.getMonth()+1).padStart(2,'0')+"-"+String(d.getDate()).padStart(2,'0')+" "+String(d.getHours()) + ":00";

    const tbody = document.getElementById("tabla-fragmentos-info-body");
    if(!tbody) return;
    tbody.innerHTML = "";

    let fragmentos = [];
    if(db.config.id === "NODO_LA_PAZ") {
        fragmentos = [
            { tabla: "PAQUETE_OPERATIVO_LP", tipo: "Horizontal Disjunta", criterio: "Origen = 'La Paz'" },
            { tabla: "MOVIMIENTO_LP", tipo: "Horizontal Disjunta", criterio: "Ubicación = Sede La Paz" },
            { tabla: "CLIENTE_PUBLICO", tipo: "Réplica Total", criterio: "Copia Sincronizada Nacional" }
        ];
    } else {
        fragmentos = [
            { tabla: "PAQUETE_OPERATIVO_SCZ", tipo: "Horizontal Disjunta", criterio: "Origen = 'Santa Cruz'" },
            { tabla: "MOVIMIENTO_SCZ", tipo: "Horizontal Disjunta", criterio: "Ubicación = Sede Santa Cruz" },
            { tabla: "CLIENTE_PUBLICO", tipo: "Réplica Total", criterio: "Copia Sincronizada Nacional" }
        ];
    }

    fragmentos.forEach(f => {
        const fila = document.createElement("tr");
        fila.innerHTML = `
            <td><code>${f.tabla}</code></td>
            <td><span class="badge-status info">${f.tipo}</span></td>
            <td><span style="font-family:monospace; font-size:0.8rem;">${f.criterio}</span></td>
        `;
        tbody.appendChild(fila);
    });
}

function activarResaltadoFragmentos() {
    const tbl = document.getElementById("tabla-fragmentos-auditoria");
    tbl.style.outline = "3px solid var(--azul-primario)";
    tbl.style.transform = "scale(1.01)";
    tbl.style.transition = "all 0.3s ease";
    setTimeout(() => {
        tbl.style.outline = "none";
        tbl.style.transform = "none";
    }, 1500);
}