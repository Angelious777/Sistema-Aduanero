/**
 * clientes.js - Controlador del Esquema de Clientes Federados
 */
document.addEventListener("DOMContentLoaded", function() {
    renderizarClientes();
    document.getElementById("btn-buscar-clientes").addEventListener("click", renderizarClientes);
});

function renderizarClientes() {
    const tbody = document.getElementById("tabla-clientes-body");
    if (!tbody) return;

    const fNombre = document.getElementById("buscar-cliente-nombre").value.trim().toLowerCase();
    const fDoc = document.getElementById("buscar-cliente-doc").value.trim().toLowerCase();

    tbody.innerHTML = "";
    let filtrados = window.DB_PROYECTO_GLOBAL.clientes;

    if (fNombre) filtrados = filtrados.filter(c => c.nombre.toLowerCase().includes(fNombre));
    if (fDoc) filtrados = filtrados.filter(c => c.documento.toLowerCase().includes(fDoc));

    filtrados.forEach(c => {
        const fila = document.createElement("tr");
        fila.innerHTML = `
            <td><strong>${c.nombre}</strong></td>
            <td>${c.documento}</td>
            <td>${c.telefono}</td>
            <td>${c.correo}</td>
            <td>${c.registro}</td>
            <td><span class="badge-vertical">${c.tipo}</span></td>
        `;
        tbody.appendChild(fila);
    });
}