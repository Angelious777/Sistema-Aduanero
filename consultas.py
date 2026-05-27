from parser import analizar_consulta
from planificador import generar_plan
from ejecutor import ejecutar_consultas_paralelas

# -----------------------------------
# CONSULTA GLOBAL
# -----------------------------------

def obtener_trazabilidad(codigo):

    analisis = analizar_consulta(
        "trazabilidad"
    )

    plan = generar_plan(analisis)

    resultado = ejecutar_consultas_paralelas(
        codigo
    )

    return {

        "analisis": analisis,
        "plan": plan,
        "resultado": resultado
    }