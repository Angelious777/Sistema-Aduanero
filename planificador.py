# -----------------------------------
# PLANIFICADOR DISTRIBUIDO
# -----------------------------------

def generar_plan(analisis):

    plan = []

    for fragmento in analisis['fragmentos']:

        plan.append({

            "nodo": fragmento,
            "tabla": analisis['tabla'],
            "operacion": analisis['operacion']
        })

    return plan