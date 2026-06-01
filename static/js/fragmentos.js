document.addEventListener('DOMContentLoaded', () => {
    cargarFragmentos();
});

async function cargarFragmentos() {

    try {

        const respuesta = await fetch('/fragmentos');
        const datos = await respuesta.json();

        const tbody = document.getElementById(
            'tabla-catalogo-fragmentacion'
        );

        tbody.innerHTML = '';

        datos.forEach(fragmento => {

            let claseMotor = 'success';

            if (fragmento.motor_bd.includes('PostgreSQL')) {
                claseMotor = 'info';
            }

            if (fragmento.motor_bd.includes('SQL Server')) {
                claseMotor = 'alert';
            }

            tbody.innerHTML += `
                <tr>
                    <td>${fragmento.id_fragmento}</td>

                    <td>
                        <code class="codigo-fragmento">
                            ${fragmento.nombre_fragmento}
                        </code>
                    </td>

                    <td>
                        <code class="codigo-nodo">
                            ${fragmento.nodo}
                        </code>
                    </td>

                    <td>
                        <span class="badge-status ${claseMotor}">
                            ${fragmento.motor_bd}
                        </span>
                    </td>

                    <td>
                        <strong>${fragmento.tabla_base}</strong>
                    </td>

                    <td>
                        ${fragmento.tipo_fragmentacion}
                    </td>
                </tr>
            `;
        });

    } catch (error) {

        console.error(
            'Error cargando fragmentos:',
            error
        );
    }
}


