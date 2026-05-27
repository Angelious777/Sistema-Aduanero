from conexiones import conectar_lp
from conexiones import conectar_scz
from logs.logger import registrar_log

# -----------------------------------
# ACTUALIZAR ESTADO
# -----------------------------------

def actualizar_estado(codigo, nuevo_estado):

    actualizado = False

    # -----------------------------------
    # LA PAZ
    # -----------------------------------

    try:

        conn_lp = conectar_lp()

        cur_lp = conn_lp.cursor()

        cur_lp.execute("""

            UPDATE paquete_lp

            SET estado = %s

            WHERE codigo_rastreo = %s

        """, (nuevo_estado, codigo))

        conn_lp.commit()

        if cur_lp.rowcount > 0:

            registrar_log(
                f"Estado actualizado en La Paz: {codigo}"
            )
            actualizado = True
        
    except Exception as e:

        print("Error LP:", e)

    # -----------------------------------
    # SANTA CRUZ
    # -----------------------------------

    try:

        conn_scz = conectar_scz()

        cur_scz = conn_scz.cursor()

        cur_scz.execute(f"""

            UPDATE paquete_scz

            SET estado = '{nuevo_estado}'

            WHERE codigo_rastreo = '{codigo}'

        """)

        conn_scz.commit()

        if cur_scz.rowcount > 0:

            actualizado = True

    except Exception as e:

        print("Error SCZ:", e)

    return actualizado