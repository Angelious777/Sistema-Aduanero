from conexiones import conectar_central


def obtener_clientes_global():
    """Obtiene la lista de clientes globales desde la base de datos del Nodo Central."""
    clientes = []

    conn = None
    cur = None
    try:
        conn = conectar_central()
        cur = conn.cursor()

        try:
            cur.execute("""
                SELECT id_cliente, nombre, apellido_paterno, apellido_materno,
                       telefono, fecha_registro, documento_identidad, direccion, email
                FROM CLIENTE_GLOBAL
            """)
        except Exception:
            cur.execute("""
                SELECT cp.id_cliente, cp.nombre, cp.apellido_paterno, cp.apellido_materno,
                       cp.telefono, cp.fecha_registro, cv.documento_identidad, cv.direccion, cv.email
                FROM CLIENTE_PUBLICO cp
                INNER JOIN CLIENTE_PRIVADO cv ON cp.id_cliente = cv.id_cliente
            """)

        filas = cur.fetchall()
        for fila in filas:
            fecha_registro = fila[5]
            if hasattr(fecha_registro, 'strftime'):
                fecha_registro = fecha_registro.strftime('%Y-%m-%d %H:%M:%S')

            nombre_completo = " ".join(filter(None, [fila[1], fila[2], fila[3]])).strip()

            clientes.append({
                "nombre": nombre_completo,
                "documento": fila[6],
                "telefono": fila[4],
                "correo": fila[8],
                "registro": fecha_registro,
                "direccion": fila[7]
            })

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

    return clientes
