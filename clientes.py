import uuid
from datetime import datetime
from conexiones import conectar_central, conectar_lp, conectar_scz

def obtener_clientes_global():
    """Obtiene la lista de clientes globales mapeando la vista del Nodo Central."""
    clientes = []
    conn = None
    cur = None
    try:
        conn = conectar_central()
        cur = conn.cursor()
        cur.execute("""
            SELECT id_cliente, nombre, apellido_paterno, apellido_materno,
                   telefono, fecha_registro, documento_identidad, direccion, email
            FROM CLIENTE_GLOBAL
        """)
        filas = cur.fetchall()
        for fila in filas:
            fecha_registro = fila[5]
            if hasattr(fecha_registro, 'strftime'):
                fecha_registro = fecha_registro.strftime('%Y-%m-%d %H:%M:%S')

            nombre_completo = " ".join(filter(None, [fila[1], fila[2], fila[3]])).strip()

            clientes.append({
                "id": str(fila[0]),
                "nombre": nombre_completo,
                "documento": fila[6],
                "telefono": fila[4],
                "correo": fila[8],
                "registro": fecha_registro,
                "direccion": fila[7]
            })
    finally:
        if cur: cur.close()
        if conn: conn.close()
    return clientes

def registrar_cliente_nodo(nit_ci, nombre, apellido_paterno, apellido_materno, telefono, direccion, email, nodo_destino):
    # Generación de UUID único global para todo el ecosistema
    id_cliente_global = str(uuid.uuid4())
    fecha_actual = datetime.now()

    conn_regional = None
    cur_regional = None
    conn_central = None
    cur_central = None

    try:
        # =========================================================
        # ACCIÓN 1: INSERT NATIVO EN EL NODO REGIONAL PERIMETRAL
        # =========================================================
        if nodo_destino == "nodo_lp":
            conn_regional = conectar_lp()
            cur_regional = conn_regional.cursor()
            # PostgreSQL: Sintaxis nativa %s (Minúsculas según tu DDL)
            sql_lp = """
                INSERT INTO cliente_publico (id_cliente, nombre, apellido_paterno, apellido_materno, telefono, fecha_registro)
                VALUES (%s, %s, %s, %s, %s, %s);
            """
            cur_regional.execute(sql_lp, (id_cliente_global, nombre, apellido_paterno, apellido_materno, telefono, fecha_actual))
            
        elif nodo_destino == "nodo_scz":
            conn_regional = conectar_scz()
            cur_regional = conn_regional.cursor()
            # SQL Server: Sintaxis nativa con marcadores ?
            sql_scz = """
                INSERT INTO CLIENTE_PUBLICO (id_cliente, nombre, apellido_paterno, apellido_materno, telefono, fecha_registro)
                VALUES (?, ?, ?, ?, ?, ?);
            """
            cur_regional.execute(sql_scz, (id_cliente_global, nombre, apellido_paterno, apellido_materno, telefono, fecha_actual))
        else:
            raise ValueError(f"Firma del nodo regional '{nodo_destino}' no válida.")

        # =========================================================
        # ACCIÓN 2: INSERCIÓN VERTICAL EN NODO_CENTRAL (SQL SERVER)
        # =========================================================
        conn_central = conectar_central()
        conn_central.autocommit = False  # Forzar entorno transaccional aislado
        cur_central = conn_central.cursor()

        # Primero la tabla padre debido a la restricción de clave foránea (FK)
        sql_central_pub = """
            INSERT INTO CLIENTE_PUBLICO (id_cliente, nombre, apellido_paterno, apellido_materno, telefono, fecha_registro)
            VALUES (?, ?, ?, ?, ?, ?);
        """
        cur_central.execute(sql_central_pub, (id_cliente_global, nombre, apellido_paterno, apellido_materno, telefono, fecha_actual))

        # Segundo la tabla dependiente privada que resguarda datos confidenciales
        sql_central_priv = """
            INSERT INTO CLIENTE_PRIVADO (id_cliente, documento_identidad, direccion, email)
            VALUES (?, ?, ?, ?);
        """
        cur_central.execute(sql_central_priv, (id_cliente_global, nit_ci, direccion, email))

        # =========================================================
        # ACCIÓN 3: CONFIRMACIÓN DE LA TRANSACCIÓN (COMMIT)
        # =========================================================
        conn_regional.commit()
        conn_central.commit()
        return True

    except Exception as e:
        # Si un nodo falla o está inaccesible por red, se aborta todo de forma inmediata
        if conn_regional: conn_regional.rollback()
        if conn_central: conn_central.rollback()
        print(f"--> [CRITICAL ROLLBACK EXECUTED]: {str(e)}")
        raise e

    finally:
        if cur_regional: cur_regional.close()
        if conn_regional: conn_regional.close()
        if cur_central: cur_central.close()
        if conn_central: conn_central.close()