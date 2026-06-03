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
    """
    Efectúa una inserción distribuida coordinada global.
    Maneja marcadores híbridos: %s para PostgreSQL (La Paz) y ? para SQL Server (Santa Cruz y Central).
    """
    # 1. Generar la llave primaria unificada (UUID)
    id_cliente_nuevo = str(uuid.uuid4())
    fecha_actual = datetime.now()

    conn_central = None
    conn_lp = None
    conn_scz = None

    try:
        # Abrir canales con los componentes del clúster
        conn_central = conectar_central() 
        conn_lp = conectar_lp()
        conn_scz = conectar_scz()

        if not conn_central or not conn_lp or not conn_scz:
            print("❌ Error de infraestructura: Al menos un nodo de la red está inaccesible.")
            return False

        cursor_central = conn_central.cursor()
        cursor_lp = conn_lp.cursor()
        cursor_scz = conn_scz.cursor()

        # =====================================================================
        # PASO A: DEFINICIÓN DE QUERIES SEGÚN EL MOTOR DE BASE DE DATOS
        # =====================================================================
        
        # Query para POSTGRESQL (Nodo La Paz) -> Utiliza %s
        sql_publico_postgres = """
            INSERT INTO cliente_publico (id_cliente, nombre, apellido_paterno, apellido_materno, telefono, fecha_registro)
            VALUES (%s, %s, %s, %s, %s, %s);
        """

        # Query para SQL SERVER (Nodo Santa Cruz y Central) -> Utiliza ?
        sql_publico_sqlserver = """
            INSERT INTO CLIENTE_PUBLICO (id_cliente, nombre, apellido_paterno, apellido_materno, telefono, fecha_registro)
            VALUES (?, ?, ?, ?, ?, ?);
        """
        
        valores_publico = (id_cliente_nuevo, nombre, apellido_paterno, apellido_materno, telefono, fecha_actual)

        # =====================================================================
        # PASO B: INSERCIÓN EN COMPONENTE PÚBLICO
        # =====================================================================
        # Inserción en La Paz (PostgreSQL) usando su respectiva sintaxis
        cursor_lp.execute(sql_publico_postgres, valores_publico)

        # Inserción en Santa Cruz (SQL Server)
        cursor_scz.execute(sql_publico_sqlserver, valores_publico)

        # Inserción en el Nodo Central (SQL Server)
        cursor_central.execute(sql_publico_sqlserver, valores_publico)

        # =====================================================================
        # PASO C: INSERCIÓN EN COMPONENTE PRIVADO (Exclusivo de Nodo Central - SQL Server)
        # =====================================================================
        sql_privado_sqlserver = """
            INSERT INTO CLIENTE_PRIVADO (id_cliente, documento_identidad, direccion, email)
            VALUES (?, ?, ?, ?);
        """
        valores_privado = (id_cliente_nuevo, nit_ci, direccion, email)
        cursor_central.execute(sql_privado_sqlserver, valores_privado)

        # =====================================================================
        # PASO D: COMMIT ATÓMICO MULTI-NODO
        # =====================================================================
        conn_lp.commit()
        conn_scz.commit()
        conn_central.commit()
        
        print(f"✅ Transacción multi-nodo exitosa. UUID: {id_cliente_nuevo} replicado globalmente.")
        return True

    except Exception as e:
        print(f"🚨 Error en la transacción distribuida, aplicando Rollback general. Motivo: {str(e)}")
        for conn in [conn_lp, conn_scz, conn_central]:
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
        return False

    finally:
        # Cierre seguro de recursos
        if 'cursor_central' in locals(): cursor_central.close()
        if 'cursor_lp' in locals(): cursor_lp.close()
        if 'cursor_scz' in locals(): cursor_scz.close()
        if conn_central: conn_central.close()
        if conn_lp: conn_lp.close()
        if conn_scz: conn_scz.close()


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