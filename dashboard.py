from metricas import obtener_metricas
from monitor import obtener_estado_nodos

# -----------------------------------
# DASHBOARD
# -----------------------------------

def construir_dashboard():

    return {

        "metricas": obtener_metricas(),

        "nodos": obtener_estado_nodos()
    }