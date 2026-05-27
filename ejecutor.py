from concurrent.futures import ThreadPoolExecutor

from conexiones import conectar_lp
from conexiones import conectar_scz

# -----------------------------------
# CONSULTAR LP
# -----------------------------------

def consultar_lp(codigo):

    conn = conectar_lp()

    cur = conn.cursor()

    cur.execute("""

        SELECT
            ubicacion,
            observacion,
            fecha_movimiento

        FROM movimiento_lp

        WHERE id_paquete = (

            SELECT id_paquete
            FROM paquete_lp
            WHERE codigo_rastreo = %s
        )

    """, (codigo,))

    datos = cur.fetchall()

    resultado = []

    for row in datos:

        resultado.append({

            "nodo": "La Paz",
            "ubicacion": row[0],
            "observacion": row[1],
            "fecha": str(row[2])
        })

    return resultado

# -----------------------------------
# CONSULTAR SCZ
# -----------------------------------

def consultar_scz(codigo):

    conn = conectar_scz()

    cur = conn.cursor()

    cur.execute(f"""

        SELECT
            ubicacion,
            observacion,
            fecha_movimiento

        FROM movimiento_scz

        WHERE id_paquete = (

            SELECT id_paquete
            FROM paquete_scz
            WHERE codigo_rastreo = '{codigo}'
        )

    """)

    datos = cur.fetchall()

    resultado = []

    for row in datos:

        resultado.append({

            "nodo": "Santa Cruz",
            "ubicacion": row[0],
            "observacion": row[1],
            "fecha": str(row[2])
        })

    return resultado

# -----------------------------------
# EJECUCION PARALELA
# -----------------------------------

def ejecutar_consultas_paralelas(codigo):

    historial = []

    with ThreadPoolExecutor(max_workers=2) as executor:

        futuro_lp = executor.submit(
            consultar_lp,
            codigo
        )

        futuro_scz = executor.submit(
            consultar_scz,
            codigo
        )

        resultado_lp = futuro_lp.result()
        resultado_scz = futuro_scz.result()

        historial.extend(resultado_lp)
        historial.extend(resultado_scz)

    historial = sorted(
        historial,
        key=lambda x: x['fecha']
    )

    return historial