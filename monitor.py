from tolerancia import NODOS_ACTIVOS
from conexiones import conectar_central

# -----------------------------------
# VER ESTADO
# -----------------------------------

def obtener_estado_nodos():

    return NODOS_ACTIVOS


def obtener_nodos():
    conn = conectar_central()
    cur = conn.cursor()
    
    cur.execute("""

        SELECT
            nombre,
            estado

        FROM nodos

    """)
    datos = cur.fetchall()
    
    return datos