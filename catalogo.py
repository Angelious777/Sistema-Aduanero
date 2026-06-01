from conexiones import conectar_central

# -----------------------------------
# CATALOGO DE FRAGMENTOS
# -----------------------------------


def obtener_fragmentos():
    conn = conectar_central()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT * FROM catalogo_fragmentacion
        """)
        columnas = [desc[0] for desc in cur.description]
        datos = [dict(zip(columnas, fila)) for fila in cur.fetchall()]
        return datos
    finally:
        cur.close()
        conn.close()
