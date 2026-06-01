document.addEventListener('DOMContentLoaded', () => {

    cargarEstadoNodos();

    setInterval(
        cargarEstadoNodos,
        5000
    );

});

async function cargarEstadoNodos() {

    try {

        const response = await fetch('/api/estado_nodos');
        const result = await response.json();

        console.log("RESPUESTA COMPLETA:", result);

        const estados = result.data ?? result;

        console.log("ESTADOS:", estados);

        actualizarEstado('estado-lp', estados['La Paz']);
        actualizarEstado('estado-scz', estados['Santa Cruz']);
        actualizarEstado('estado-central', estados['Coordinador']);

    } catch (error) {
        console.error("ERROR:", error);
    }
}

function actualizarEstado(idElemento, estado) {

    const elemento = document.getElementById(idElemento);
    if (!elemento) return;

    if (estado) {

        elemento.className = 'status-indicator online';
        elemento.textContent = '● Conectado';

    } else {

        elemento.className = 'status-indicator offline';
        elemento.textContent = '● Desconectado';
    }
}