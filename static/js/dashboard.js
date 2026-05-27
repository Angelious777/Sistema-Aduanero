async function cargarDashboard() {

    const response = await fetch('/dashboard')

    const data = await response.json()

    // -----------------------------
    // METRICAS
    // -----------------------------

    document.getElementById('nodos').innerText =
        data.metricas.nodos_activos

    document.getElementById('fragmentos').innerText =
        data.metricas.fragmentos

    document.getElementById('pendientes').innerText =
        data.metricas.pendientes

    // -----------------------------
    // TABLA NODOS
    // -----------------------------

    let tabla = ''

    for (const nodo in data.nodos) {

        const estado = data.nodos[nodo]

        tabla += `

            <tr>

                <td>${nodo}</td>

                <td>

                    ${
                        estado
                        ? '🟢 Activo'
                        : '🔴 Caído'
                    }

                </td>

            </tr>
        `
    }

    document.getElementById(
        'tabla_nodos'
    ).innerHTML = tabla


    const ctx = document
        .getElementById('graficoNodos')

    new Chart(ctx, {

        type: 'bar',

        data: {

            labels: [
                'La Paz',
                'Santa Cruz'
            ],

            datasets: [{

                label: 'Operaciones',

                data: [12, 19]

            }]
        }
    })
}

cargarDashboard()