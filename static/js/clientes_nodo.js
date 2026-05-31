document.addEventListener("DOMContentLoaded", function() {
    listarClientesReplicados();
    document.getElementById("clt-buscar-nombre").addEventListener("input", listarClientesReplicados);
    document.getElementById("clt-buscar-doc").addEventListener("input", listarClientesReplicados);
    document.getElementById("clt-buscar-tel").addEventListener("input", listarClientesReplicados);
});

function listarClientesReplicados() {
    const tbody = document.getElementById("tabla-clientes-replicados-body");
    if (!tbody) return;

    const fNombre = document.getElementById("clt-buscar-nombre").value.toLowerCase();
    const fDoc = document.getElementById("clt-buscar-doc").value.toLowerCase();
    const fTel = document.getElementById("clt-buscar-tel").value.toLowerCase();

    tbody.innerHTML = "";
    let filtrados = window.DB_NODO_LOCAL.clientes_publicos;

    if (fNombre) filtrados = filtrados.filter(c => c.nombre.toLowerCase().includes(fNombre));
    if (fDoc) filtrados = filtrados.filter(c => c.documento.toLowerCase().includes(fDoc));
    if (fTel) filtrados = filtrados.filter(c => c.telefono.toLowerCase().includes(fTel));

    filtrados.forEach(c => {
        const fila = document.createElement("tr");
        fila.innerHTML = `
            <td><code>CLT-${c.id}</code></td>
            <td><strong>${c.nombre}</strong></td>
            <td>${c.documento}</td>
            <td>${c.telefono}</td>
            <td>${c.correo}</td>
            <td style="text-align:center;">
                <button class="btn-secundario" style="padding:4px 10px; font-size:0.78rem;" onclick="verClientePublico(${c.id})">Ver</button>
            </td>
        `;
        tbody.appendChild(fila);
    });
}

function abrirModalRegistroCliente() {
    document.getElementById("form-registro-cliente").reset();
    document.getElementById("modal-registro-cliente").classList.add("modal-active");
}
function cerrarModalRegistroCliente() { document.getElementById("modal-registro-cliente").classList.remove("modal-active"); }

function verClientePublico(id) {
    const clt = window.DB_NODO_LOCAL.clientes_publicos.find(c => c.id === id);
    if(!clt) return;
    const box = document.getElementById("modal-ver-cliente-content");
    box.innerHTML = `
        <p><strong>Identificador:</strong> CLT-${clt.id}</p>
        <p><strong>Razón Social:</strong> ${clt.nombre}</p>
        <p><strong>Documentación:</strong> ${clt.documento}</p>
        <p><strong>Teléfono Fijo/Cel:</strong> ${clt.telefono}</p>
        <p><strong>E-mail Central:</strong> ${clt.correo}</p>
    `;
    document.getElementById("modal-ver-cliente").classList.add("modal-active");
}
function cerrarModalVerCliente() { document.getElementById("modal-ver-cliente").classList.remove("modal-active"); }

function despacharRegistroClienteCoordinador() {
    const nom = document.getElementById("reg-clt-nombre").value.trim();
    const doc = document.getElementById("reg-clt-doc").value.trim();
    const tel = document.getElementById("reg-clt-tel").value.trim();
    const mail = document.getElementById("reg-clt-correo").value.trim();
    
    // Atributos privados
    const dir = document.getElementById("reg-clt-direccion").value.trim();
    const nit = document.getElementById("reg-clt-nit").value.trim();

    if(!nom || !doc || !tel || !mail || !dir || !nit) {
        alert("Atención: Complete los campos requeridos de ambas secciones.");
        return;
    }

    const nId = 100 + window.DB_NODO_LOCAL.clientes_publicos.length + 1;
    
    // Simula POST /api/registrar-cliente
    console.log("POST /api/registrar-cliente hacia el Nodo Coordinador exitoso.");

    window.DB_NODO_LOCAL.clientes_publicos.push({ id: nId, nombre: nom, documento: doc, telefono: tel, correo: mail });
    
    alert(`[API TRANSACTION SUCCESS]\nPetición POST enviada al Coordinador.\n\n` +
          `• INSERT INTO CLIENTE_PUBLICO -> Exitoso\n• INSERT INTO CLIENTE_PRIVADO -> Guardado Cifrado\n\n` +
          `La réplica total fue esparcida de vuelta a los nodos regionales.`);
          
    cerrarModalRegistroCliente();
    listarClientesReplicados();
    if(typeof inicializarDashboardLocal === "function") inicializarDashboardLocal();
}