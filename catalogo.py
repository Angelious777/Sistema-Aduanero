from conexiones import conectar_central

# -----------------------------------
# CATALOGO DE FRAGMENTOS
# -----------------------------------


def obtener_fragmentos():
    conn = conectar_central()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT
                id_fragmento,
                nombre_fragmento,
                tabla_original,
                tipo_fragmentacion,
                nodo_ubicacion,
                descripcion
            FROM catalogo_fragmentacion
        """)
        columnas = [desc[0] for desc in cur.description]
        datos = [dict(zip(columnas, fila)) for fila in cur.fetchall()]
        return datos
    finally:
        cur.close()
        conn.close()
