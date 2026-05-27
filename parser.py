# -----------------------------------
# ANALIZADOR DE CONSULTAS
# -----------------------------------

def analizar_consulta(tipo_consulta):

    # -----------------------------------
    # CONSULTA TRAZABILIDAD
    # -----------------------------------

    if tipo_consulta == "trazabilidad":

        return {

            "tabla": "MOVIMIENTO",
            "fragmentos": [
                "La Paz",
                "Santa Cruz"
            ],

            "operacion": "SELECT"
        }

    # -----------------------------------
    # CONSULTA PAQUETES
    # -----------------------------------

    elif tipo_consulta == "paquetes":

        return {

            "tabla": "PAQUETE",
            "fragmentos": [
                "La Paz",
                "Santa Cruz"
            ],

            "operacion": "SELECT"
        }

    # -----------------------------------

    return None