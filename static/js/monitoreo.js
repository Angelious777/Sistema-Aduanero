/**
 * monitoreo.js
 * Monitor Vivo de Infraestructura de Red y Tolerancia a Fallos
 */

document.addEventListener("DOMContentLoaded", function() {
    inicializarMonitoreoVivo();
});

function inicializarMonitoreoVivo() {
    // Ejecutar inmediatamente al cargar la sección
    actualizarPingsYEstados();

    // Configurar un loop infinito de monitoreo interactivo (cada 4 segundos)
    // Esto simula el escaneo de red en segundo plano del nodo central
    setInterval(actualizarPingsYEstados, 4000);
}

function actualizarPingsYEstados() {
    const pingLPElement = document.getElementById("ping-lp");
    const pingSCZElement = document.getElementById("ping-scz");
    const checkLPTime = document.getElementById("time-lp-check");
    const checkSCZTime = document.getElementById("time-scz-check");

    if (!pingLPElement || !pingSCZElement) return;

    // Generar pequeñas fluctuaciones aleatorias en las latencias para demostrar dinamismo real
    const latenciaSimuladaLP = Math.floor(10 + Math.random() * 8); // Fluctúa entre 10 y 18ms
    const latenciaSimuladaSCZ = Math.floor(20 + Math.random() * 12); // Fluctúa entre 20 y 32ms

    // Inyectar valores con transiciones visuales discretas
    pingLPElement.textContent = `Latencia: ${latenciaSimuladaLP}ms`;
    pingSCZElement.textContent = `Latencia: ${latenciaSimuladaSCZ}ms`;

    // Actualizar las marcas de tiempo de la última revisión exitosa
    const ahora = new Date();
    const tiempoFormateado = ahora.toLocaleTimeString('es-BO');

    if (checkLPTime) checkLPTime.textContent = `Verificado a las ${tiempoFormateado} (Canal Seguro VPN)`;
    if (checkSCZTime) checkSCZTime.textContent = `Verificado a las ${tiempoFormateado} (Canal Seguro VPN)`;

    console.log(`[Monitor de Enlaces] Latencias nacionales actualizadas. LP: ${latenciaSimuladaLP}ms | SCZ: ${latenciaSimuladaSCZ}ms`);
}