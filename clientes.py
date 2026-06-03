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
    id_cliente_global = str(uuid.uuid4())
    fecha_actual = datetime.now()

    conn_lp, cur_lp = None, None
    conn_scz, cur_scz = None, None
    conn_central, cur_central = None, None

    try:
        # 1. INSERCION EN LA PAZ (PostgreSQL)
        conn_lp = conectar_lp()
        cur_lp = conn_lp.cursor()
        sql_lp = """
            INSERT INTO cliente_publico (id_cliente, nombre, apellido_paterno, apellido_materno, telefono, fecha_registro)
            VALUES (%s, %s, %s, %s, %s, %s);
        """
        cur_lp.execute(sql_lp, (id_cliente_global, nombre, apellido_paterno, apellido_materno, telefono, fecha_actual))

        # 2. INSERCION EN SANTA CRUZ (SQL Server)
        conn_scz = conectar_scz()
        cur_scz = conn_scz.cursor()
        sql_scz = """
            INSERT INTO CLIENTE_PUBLICO (id_cliente, nombre, apellido_paterno, apellido_materno, telefono, fecha_registro)
            VALUES (?, ?, ?, ?, ?, ?);
        """
        cur_scz.execute(sql_scz, (id_cliente_global, nombre, apellido_paterno, apellido_materno, telefono, fecha_actual))

        # 3. INSERCION EN NODO CENTRAL (SQL Server)
        conn_central = conectar_central()
        cur_central = conn_central.cursor()

        sql_central_pub = """
            INSERT INTO CLIENTE_PUBLICO (id_cliente, nombre, apellido_paterno, apellido_materno, telefono, fecha_registro)
            VALUES (?, ?, ?, ?, ?, ?);
        """
        cur_central.execute(sql_central_pub, (id_cliente_global, nombre, apellido_paterno, apellido_materno, telefono, fecha_actual))

        sql_central_priv = """
            INSERT INTO CLIENTE_PRIVADO (id_cliente, documento_identidad, direccion, email)
            VALUES (?, ?, ?, ?);
        """
        cur_central.execute(sql_central_priv, (id_cliente_global, nit_ci, direccion, email))

        conn_lp.commit()
        conn_scz.commit()
        conn_central.commit()
        
        return True

    except Exception as e:
        if conn_lp: conn_lp.rollback()
        if conn_scz: conn_scz.rollback()
        if conn_central: conn_central.rollback()
        print(f"--> [DISTRIBUTED TRANSACTION ROLLBACK]: {str(e)}")
        raise e
    finally:
        if cur_lp: cur_lp.close()
        if conn_lp: conn_lp.close()
        if cur_scz: cur_scz.close()
        if conn_scz: conn_scz.close()
        if cur_central: cur_central.close()
        if conn_central: conn_central.close()


def obtener_clientes_local_lp():
    """Consulta la base de datos local de La Paz (PostgreSQL)"""
    clientes = []
    conn = None
    cur = None
    try:
        conn = conectar_lp()
        cur = conn.cursor()
        cur.execute("""
            SELECT id_cliente, nombre, apellido_paterno, apellido_materno, telefono, fecha_registro
            FROM cliente_publico
        """)
        filas = cur.fetchall()
        for fila in filas:
            fecha_registro = fila[5].strftime('%Y-%m-%d %H:%M:%S') if fila[5] else 'Automático'
            nombre_completo = " ".join(filter(None, [fila[1], fila[2], fila[3]])).strip()

            clientes.append({
                "id": str(fila[0]),
                "nombre": nombre_completo,
                "telefono": fila[4] if fila[4] else '—',
                "registro": fecha_registro,
                # Retorna la advertencia directa en lugar de nulos o nombres de nodo
                "documento": "Consulte a Central", 
                "correo": "Consulte a Central",
                "direccion": "Consulte a Central"
            })
    finally:
        if cur: cur.close()
        if conn: conn.close()
    return clientes


def obtener_clientes_local_scz():
    """Consulta la base de datos local de Santa Cruz (SQL Server Regional)"""
    clientes = []
    conn = None
    cur = None
    try:
        conn = conectar_scz()
        cur = conn.cursor()
        cur.execute("""
            SELECT id_cliente, nombre, apellido_paterno, apellido_materno, telefono, fecha_registro
            FROM CLIENTE_PUBLICO
        """)
        filas = cur.fetchall()
        for fila in filas:
            fecha_registro = fila[5].strftime('%Y-%m-%d %H:%M:%S') if fila[5] else 'Automático'
            nombre_completo = " ".join(filter(None, [fila[1], fila[2], fila[3]])).strip()

            clientes.append({
                "id": str(fila[0]),
                "nombre": nombre_completo,
                "telefono": fila[4] if fila[4] else '—',
                "registro": fecha_registro,
                # Retorna la advertencia directa en lugar de nulos o nombres de nodo
                "documento": "Consulte a Central", 
                "correo": "Consulte a Central",
                "direccion": "Consulte a Central"
            })
    finally:
        if cur: cur.close()
        if conn: conn.close()
    return clientes


def obtener_clientes_local_central():
    """Consulta la base de datos del Nodo Central (SQL Server Master)"""
    clientes = []
    conn = None
    cur = None
    try:
        conn = conectar_central()
        cur = conn.cursor()
        cur.execute("""
            SELECT p.id_cliente, p.nombre, p.apellido_paterno, p.apellido_materno, p.telefono, p.fecha_registro,
                   pr.documento_identidad, pr.email, pr.direccion
            FROM CLIENTE_PUBLICO p
            INNER JOIN CLIENTE_PRIVADO pr ON p.id_cliente = pr.id_cliente
        """)
        filas = cur.fetchall()
        for fila in filas:
            fecha_registro = fila[5]
            if hasattr(fecha_registro, 'strftime'):
                fecha_registro = fecha_registro.strftime('%Y-%m-%d %H:%M:%S')
            else:
                fecha_registro = 'Automático'

            nombre_completo = " ".join(filter(None, [fila[1], fila[2], fila[3]])).strip()

            clientes.append({
                # Forzar str() por si pyodbc retorna el objeto UUID binario directo de SQL Server
                "id": str(fila[0]), 
                "nombre": nombre_completo,
                "telefono": fila[4] if fila[4] else '—',
                "registro": fecha_registro,
                "documento": str(fila[6]) if fila[6] else 'S/D',
                "correo": fila[7] if fila[7] else '—',
                "direccion": fila[8] if fila[8] else '—'
            })
    finally:
        if cur: cur.close()
        if conn: conn.close()
    return clientes