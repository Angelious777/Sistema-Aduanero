from sincronizacion import cantidad_pendientes

# -----------------------------------
# METRICAS
# -----------------------------------

def obtener_metricas():

    return {

        "pendientes": cantidad_pendientes(),

        "nodos_activos": 2,

        "fragmentos": 4,

        "motor_lp": "PostgreSQL",

        "motor_scz": "SQL Server"
    }