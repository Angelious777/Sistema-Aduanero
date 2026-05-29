from conexiones import conectar_central

# -----------------------------------
# CATALOGO DE FRAGMENTOS
# -----------------------------------


def obtener_fragmentos():
    conn = conectar_central()
    cur = conn.cursor()
    
    cur.execute("""

        SELECT
            nombre_fragmento,
            nodo_fisico

        FROM catalogo_fragmentos

    """)
    datos = cur.fetchall()
    
    return datos
    