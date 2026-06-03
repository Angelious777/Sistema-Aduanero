# rutas.py
from conexiones import conectar_central, conectar_lp, conectar_scz

def obtener_rutas_global():
    """Consulta el clúster central para mapear las rutas globales con origen y destino."""
    rutas = []
    conn = None
    cur = None
    try:
        conn = conectar_central()
        cur = conn.cursor()
        cur.execute("SELECT id_ruta, id_almacen_origen, id_almacen_destino, descripcion FROM ruta")
        for fila in cur.fetchall():
            rutas.append({
                "id_ruta": int(fila[0]),
                "id_almacen_origen": int(fila[1]),
                "id_almacen_destino": int(fila[2]),
                "descripcion": str(fila[3]) if fila[3] is not None else ""
            })
    finally:
        if cur: cur.close()
        if conn: conn.close()
    return rutas


def registrar_ruta_nodo(id_ruta, id_almacen_origen, id_almacen_destino, descripcion):
    """Inserta síncronamente una ruta en los tres fragmentos forzando el tipado correcto."""
    conn_central = None
    conn_lp = None
    conn_scz = None
    try:
        conn_central = conectar_central()
        conn_lp = conectar_lp()
        conn_scz = conectar_scz()

        cur_central = conn_central.cursor()
        cur_lp = conn_lp.cursor()
        cur_scz = conn_scz.cursor()

        sql_postgres = "INSERT INTO ruta (id_ruta, id_almacen_origen, id_almacen_destino, descripcion) VALUES (%s, %s, %s, %s);"
        sql_sqlserver = "INSERT INTO ruta (id_ruta, id_almacen_origen, id_almacen_destino, descripcion) VALUES (?, ?, ?, ?);"
        
        # Forzar tipado explícito para evitar fallas de mapeo en los drivers relacionales
        valores = (int(id_ruta), int(id_almacen_origen), int(id_almacen_destino), str(descripcion))

        # 1. Inyección en Nodo Regional La Paz (PostgreSQL)
        cur_lp.execute(sql_postgres, valores)
        
        # 2. Inyección en Nodo Regional Santa Cruz (SQL Server)
        cur_scz.execute(sql_sqlserver, valores)
        
        # 3. Inyección en Nodo Coordinador Central (SQL Server / Postgres)
        cur_central.execute(sql_sqlserver, valores)

        # Confirmación de la transacción en la red distribuida
        conn_lp.commit()
        conn_scz.commit()
        conn_central.commit()
        return True
    except Exception as e:
        print(f"🚨 Falla transaccional en Ruta Nueva: {str(e)}")
        # Rollback inmediato ante cualquier fallo de réplica
        for conn in [conn_lp, conn_scz, conn_central]:
            if conn: conn.rollback()
        return False
    finally:
        if conn_central: conn_central.close()
        if conn_lp: conn_lp.close()
        if conn_scz: conn_scz.close()


def modificar_ruta_nodo(id_ruta, id_almacen_origen, id_almacen_destino, descripcion):
    """Modifica los almacenes y la descripción en toda la red."""
    conn_central = None
    conn_lp = None
    conn_scz = None
    try:
        conn_central = conectar_central()
        conn_lp = conectar_lp()
        conn_scz = conectar_scz()

        cur_central = conn_central.cursor()
        cur_lp = conn_lp.cursor()
        cur_scz = conn_scz.cursor()

        sql_postgres = "UPDATE ruta SET id_almacen_origen = %s, id_almacen_destino = %s, descripcion = %s WHERE id_ruta = %s;"
        sql_sqlserver = "UPDATE ruta SET id_almacen_origen = ?, id_almacen_destino = ?, descripcion = ? WHERE id_ruta = ?;"
        valores = (id_almacen_origen, id_almacen_destino, descripcion, id_ruta)

        cur_lp.execute(sql_postgres, valores)
        cur_scz.execute(sql_sqlserver, valores)
        cur_central.execute(sql_sqlserver, valores)

        conn_lp.commit()
        conn_scz.commit()
        conn_central.commit()
        return True
    except Exception as e:
        print(f"🚨 Falla en modificación distribuida de ruta: {str(e)}")
        for conn in [conn_lp, conn_scz, conn_central]:
            if conn: conn.rollback()
        return False
    finally:
        if conn_central: conn_central.close()
        if conn_lp: conn_lp.close()
        if conn_scz: conn_scz.close()


def eliminar_ruta_nodo(id_ruta):
    """Borra la ruta de forma unificada por su PK."""
    conn_central = None
    conn_lp = None
    conn_scz = None
    try:
        conn_central = conectar_central()
        conn_lp = conectar_lp()
        conn_scz = conectar_scz()

        cur_central = conn_central.cursor()
        cur_lp = conn_lp.cursor()
        cur_scz = conn_scz.cursor()

        sql_postgres = "DELETE FROM ruta WHERE id_ruta = %s;"
        sql_sqlserver = "DELETE FROM ruta WHERE id_ruta = ?;"

        cur_lp.execute(sql_postgres, (id_ruta,))
        cur_scz.execute(sql_sqlserver, (id_ruta,))
        cur_central.execute(sql_sqlserver, (id_ruta,))

        conn_lp.commit()
        conn_scz.commit()
        conn_central.commit()
        return True
    except Exception as e:
        print(f"🚨 Falla al revocar trayecto: {str(e)}")
        for conn in [conn_lp, conn_scz, conn_central]:
            if conn: conn.rollback()
        return False
    finally:
        if conn_central: conn_central.close()
        if conn_lp: conn_lp.close()
        if conn_scz: conn_scz.close()


def sincronizar_rutas_cascada():
    """Ejecuta alineación masiva mediante UPSERT adaptado a las columnas reales."""
    conn_lp = None
    conn_scz = None
    try:
        rutas_master = obtener_rutas_global()
        conn_lp = conectar_lp()
        conn_scz = conectar_scz()
        
        cur_lp = conn_lp.cursor()
        cur_scz = conn_scz.cursor()
        
        # Postgres (La Paz)
        sql_upsert_lp = """
            INSERT INTO ruta (id_ruta, id_almacen_origen, id_almacen_destino, descripcion) 
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (id_ruta) DO UPDATE SET 
                id_almacen_origen = EXCLUDED.id_almacen_origen, 
                id_almacen_destino = EXCLUDED.id_almacen_destino, 
                descripcion = EXCLUDED.descripcion;
        """
        
        # SQL Server (Santa Cruz)
        sql_upsert_scz = """
            MERGE ruta AS target
            USING (SELECT ? AS id_ruta) AS source ON (target.id_ruta = source.id_ruta)
            WHEN MATCHED THEN 
                UPDATE SET id_almacen_origen = ?, id_almacen_destino = ?, descripcion = ?
            WHEN NOT MATCHED THEN 
                INSERT (id_ruta, id_almacen_origen, id_almacen_destino, descripcion) VALUES (?, ?, ?, ?);
        """
        
        for r in rutas_master:
            cur_lp.execute(sql_upsert_lp, (r['id_ruta'], r['id_almacen_origen'], r['id_almacen_destino'], r['descripcion']))
            
            valores_scz = (
                r['id_ruta'], 
                r['id_almacen_origen'], r['id_almacen_destino'], r['descripcion'],
                r['id_ruta'], r['id_almacen_origen'], r['id_almacen_destino'], r['descripcion']
            )
            cur_scz.execute(sql_upsert_scz, valores_scz)
            
        conn_lp.commit()
        conn_scz.commit()
        return True
    except Exception as e:
        print(f"🚨 Colapso en cascada de trayectos: {str(e)}")
        if conn_lp: conn_lp.rollback()
        if conn_scz: conn_scz.rollback()
        return False
    finally:
        if conn_lp: conn_lp.close()
        if conn_scz: conn_scz.close()