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

    # Inicializamos todas las conexiones en None
    conn_lp, cur_lp = None, None
    conn_scz, cur_scz = None, None
    conn_central, cur_central = None, None

    try:
        # =========================================================
        # 1. INSERCIÓN EN LA PAZ (PostgreSQL) - Replicación Total
        # =========================================================
        conn_lp = conectar_lp()
        cur_lp = conn_lp.cursor()
        sql_lp = """
            INSERT INTO cliente_publico (id_cliente, nombre, apellido_paterno, apellido_materno, telefono, fecha_registro)
            VALUES (%s, %s, %s, %s, %s, %s);
        """
        cur_lp.execute(sql_lp, (id_cliente_global, nombre, apellido_paterno, apellido_materno, telefono, fecha_actual))

        # =========================================================
        # 2. INSERCIÓN EN SANTA CRUZ (SQL Server) - Replicación Total
        # =========================================================
        conn_scz = conectar_scz()
        cur_scz = conn_scz.cursor()
        sql_scz = """
            INSERT INTO CLIENTE_PUBLICO (id_cliente, nombre, apellido_paterno, apellido_materno, telefono, fecha_registro)
            VALUES (?, ?, ?, ?, ?, ?);
        """
        cur_scz.execute(sql_scz, (id_cliente_global, nombre, apellido_paterno, apellido_materno, telefono, fecha_actual))

        # =========================================================
        # 3. INSERCIÓN EN NODO CENTRAL (SQL Server)
        # =========================================================
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

        # =========================================================
        # 4. COMMITS EXPLÍCITOS EN TODOS LOS MOTORES
        # =========================================================
        conn_lp.commit()       # Asegura los datos en PostgreSQL
        conn_scz.commit()      # Asegura los datos en SQL Server Regional
        conn_central.commit()  # Asegura los datos en el Nodo Central
        
        return True

    except Exception as e:
        # Rollback en cascada si cualquiera de los 3 motores falla
        if conn_lp: conn_lp.rollback()
        if conn_scz: conn_scz.rollback()
        if conn_central: conn_central.rollback()
        print(f"--> [DISTRIBUTED TRANSACTION ROLLBACK]: {str(e)}")
        raise e

    finally:
        # Cierre limpio de todo el pool de conexiones abiertas
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
        # Nota: Usamos minúsculas de acuerdo al DDL de tu tabla en Postgres
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
                "documento": "Local LP", # El fragmento operativo local de LP no guarda el DNI/Dirección/Email
                "telefono": fila[4],
                "correo": "Consulte a Central",
                "registro": fecha_registro,
                "direccion": "Datos resguardados en Central"
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
        # Nota: Usamos MAYÚSCULAS de acuerdo al DDL de tu tabla en SQL Server Regional
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
                "documento": "Local SCZ", # El fragmento operativo local de SCZ tampoco guarda datos privados
                "telefono": fila[4] if fila[4] else '—',
                "correo": "Consulte a Central",
                "registro": fecha_registro,
                "direccion": "Datos resguardados en Central"
            })
    finally:
        if cur: cur.close()
        if conn: conn.close()
    return clientes


def obtener_clientes_local_central():
    """Consulta la base de datos local del Nodo Central (SQL Server) unificando sus fragmentos verticales"""
    clientes = []
    conn = None
    cur = None
    try:
        conn = conectar_central()
        cur = conn.cursor()
        # SQL Server: Unificamos la tabla operativa (pública) con la financiera/confidencial (privada)
        cur.execute("""
            SELECT pub.id_cliente, pub.nombre, pub.apellido_paterno, pub.apellido_materno, 
                   pub.telefono, pub.fecha_registro, priv.documento_identidad, priv.direccion, priv.email
            FROM CLIENTE_PUBLICO pub
            INNER JOIN CLIENTE_PRIVADO priv ON pub.id_cliente = priv.id_cliente
        """)
        filas = cur.fetchall()
        for fila in filas:
            fecha_registro = fila[5].strftime('%Y-%m-%d %H:%M:%S') if fila[5] else 'Automático'
            nombre_completo = " ".join(filter(None, [fila[1], fila[2], fila[3]])).strip()

            clientes.append({
                "id": str(fila[0]),
                "nombre": nombre_completo,
                "documento": fila[6] if fila[6] else 'S/D',
                "telefono": fila[4] if fila[4] else '—',
                "correo": fila[8] if fila[8] else '—',
                "registro": fecha_registro,
                "direccion": fila[7] if fila[7] else 'S/D'
            })
    finally:
        if cur: cur.close()
        if conn: conn.close()
    return clientes