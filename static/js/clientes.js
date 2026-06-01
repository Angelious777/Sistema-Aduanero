/**
 * clientes.js - Controlador del Esquema de Clientes Federados
 */

window.CLIENTES_GLOBAL = [];

document.addEventListener("DOMContentLoaded", function() {
    cargarClientesGlobal();
    document.getElementById("btn-buscar-clientes").addEventListener("click", renderizarClientes);
});

async function cargarClientesGlobal() {
    const tbody = document.getElementById("tabla-clientes-body");
    if (!tbody) return;

    try {
        const response = await fetch('/api/clientes');
        const resultado = await response.json();

        if (!response.ok || resultado.success === false) {
            tbody.innerHTML = `<tr><td colspan="6">No se pudieron cargar los clientes: ${resultado.error || 'Error desconocido'}</td></tr>`;
            return;
        }

        window.CLIENTES_GLOBAL = resultado.data || [];
        renderizarClientes();
    } catch (error) {
        tbody.innerHTML = `<tr><td colspan="6">Error al conectar con el servidor: ${error.message}</td></tr>`;
    }
}

function renderizarClientes() {
    const tbody = document.getElementById("tabla-clientes-body");
    if (!tbody) return;

    const fNombre = document.getElementById("buscar-cliente-nombre").value.trim().toLowerCase();
    const fDoc = document.getElementById("buscar-cliente-doc").value.trim().toLowerCase();

    tbody.innerHTML = "";
    let filtrados = window.CLIENTES_GLOBAL || [];

    if (fNombre) filtrados = filtrados.filter(c => c.nombre.toLowerCase().includes(fNombre));
    if (fDoc) filtrados = filtrados.filter(c => c.documento.toLowerCase().includes(fDoc));

    if (filtrados.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6">No se encontraron clientes.</td></tr>`;
        return;
    }

    filtrados.forEach(c => {
        const fila = document.createElement("tr");
        fila.innerHTML = `
            <td><strong>${c.nombre}</strong></td>
            <td>${c.documento || ''}</td>
            <td>${c.telefono || ''}</td>
            <td>${c.correo || ''}</td>
            <td>${c.registro || ''}</td>
            <td>${c.direccion || ''}</td>
        `;
        tbody.appendChild(fila);
    });
}