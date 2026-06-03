# almacenes.py
from conexiones import conectar_central, conectar_lp, conectar_scz

def obtener_almacenes_global():
    """Consulta el Nodo Central para traer la lista unificada forzando tipado."""
    almacenes = []
    conn = None
    cur = None
    try:
        conn = conectar_central()
        cur = conn.cursor()
        cur.execute("SELECT id_almacen, nombre, ciudad, direccion, nodo_responsable FROM almacen ORDER BY id_almacen ASC")
        filas = cur.fetchall()
        for fila in filas:
            almacenes.append({
                "id_almacen": int(fila[0]), # Forzamos entero para evitar strings o nulos en las FK
                "nombre": str(fila[1]) if fila[1] is not None else "Sin Nombre",
                "ciudad": str(fila[2]) if fila[2] is not None else "S/D",
                "direccion": str(fila[3]) if fila[3] is not None else "",
                "nodo_responsable": str(fila[4]).strip().upper() if fila[4] is not None else "CENTRAL"
            })
    finally:
        if cur: cur.close()
        if conn: conn.close()
    return almacenes


def registrar_almacen_nodo(id_almacen, nombre, ciudad, direccion, nodo_responsable):
    """Inserta síncronamente en los 3 nodos usando el estándar del motor respectivo."""
    conn_central = None
    conn_lp = None
    conn_scz = None
    try:
        conn_central = conectar_central()
        conn_lp = conectar_lp()
        conn_scz = conectar_scz()

        if not conn_central or not conn_lp or not conn_scz:
            return False

        cursor_central = conn_central.cursor()
        cursor_lp = conn_lp.cursor()
        cursor_scz = conn_scz.cursor()

        # Queries adaptadas por motor
        sql_postgres = "INSERT INTO almacen (id_almacen, nombre, ciudad, direccion, nodo_responsable) VALUES (%s, %s, %s, %s, %s);"
        sql_sqlserver = "INSERT INTO almacen (id_almacen, nombre, ciudad, direccion, nodo_responsable) VALUES (?, ?, ?, ?, ?);"
        valores = (id_almacen, nombre, ciudad, direccion, nodo_responsable)

        cursor_lp.execute(sql_postgres, valores)
        cursor_scz.execute(sql_sqlserver, valores)
        cursor_central.execute(sql_sqlserver, valores)

        conn_lp.commit()
        conn_scz.commit()
        conn_central.commit()
        return True
    except Exception as e:
        print(f"🚨 Error en inserción distribuida de almacén: {str(e)}")
        for conn in [conn_lp, conn_scz, conn_central]:
            if conn:
                try: conn.rollback()
                except: pass
        return False
    finally:
        if conn_central: conn_central.close()
        if conn_lp: conn_lp.close()
        if conn_scz: conn_scz.close()


def modificar_almacen_nodo(id_almacen, nombre, ciudad, direccion, nodo_responsable):
    """Efectúa un UPDATE síncronamente en todos los fragmentos."""
    conn_central = None
    conn_lp = None
    conn_scz = None
    try:
        conn_central = conectar_central()
        conn_lp = conectar_lp()
        conn_scz = conectar_scz()

        cursor_central = conn_central.cursor()
        cursor_lp = conn_lp.cursor()
        cursor_scz = conn_scz.cursor()

        sql_postgres = "UPDATE almacen SET nombre = %s, ciudad = %s, direccion = %s, nodo_responsable = %s WHERE id_almacen = %s;"
        sql_sqlserver = "UPDATE almacen SET nombre = ?, ciudad = ?, direccion = ?, nodo_responsable = ? WHERE id_almacen = ?;"
        valores = (nombre, ciudad, direccion, nodo_responsable, id_almacen)

        cursor_lp.execute(sql_postgres, valores)
        cursor_scz.execute(sql_sqlserver, valores)
        cursor_central.execute(sql_sqlserver, valores)

        conn_lp.commit()
        conn_scz.commit()
        conn_central.commit()
        return True
    except Exception as e:
        print(f"🚨 Error al editar almacén: {str(e)}")
        for conn in [conn_lp, conn_scz, conn_central]:
            if conn: conn.rollback()
        return False
    finally:
        if conn_central: conn_central.close()
        if conn_lp: conn_lp.close()
        if conn_scz: conn_scz.close()


def eliminar_almacen_nodo(id_almacen):
    """Elimina el registro de todos los nodos de forma coordinada."""
    conn_central = None
    conn_lp = None
    conn_scz = None
    try:
        conn_central = conectar_central()
        conn_lp = conectar_lp()
        conn_scz = conectar_scz()

        cursor_central = conn_central.cursor()
        cursor_lp = conn_lp.cursor()
        cursor_scz = conn_scz.cursor()

        sql_postgres = "DELETE FROM almacen WHERE id_almacen = %s;"
        sql_sqlserver = "DELETE FROM almacen WHERE id_almacen = ?;"

        cursor_lp.execute(sql_postgres, (id_almacen,))
        cursor_scz.execute(sql_sqlserver, (id_almacen,))
        cursor_central.execute(sql_sqlserver, (id_almacen,))

        conn_lp.commit()
        conn_scz.commit()
        conn_central.commit()
        return True
    except Exception as e:
        print(f"🚨 Error al eliminar almacén distribuido: {str(e)}")
        for conn in [conn_lp, conn_scz, conn_central]:
            if conn: conn.rollback()
        return False
    finally:
        if conn_central: conn_central.close()
        if conn_lp: conn_lp.close()
        if conn_scz: conn_scz.close()


def sincronizar_almacenes_cascada():
    """
    Fuerza la paridad de catálogos mediante UPSERT coordinado
    evitando colapsar las restricciones de llave foránea (FK).
    """
    conn_lp = None
    conn_scz = None
    try:
        almacenes_master = obtener_almacenes_global()
        conn_lp = conectar_lp()
        conn_scz = conectar_scz()
        
        cur_lp = conn_lp.cursor()
        cur_scz = conn_scz.cursor()
        
        # Sentencias UPSERT adaptadas a cada motor
        # PostgreSQL (La Paz): ON CONFLICT DO UPDATE
        sql_upsert_lp = """
            INSERT INTO almacen (id_almacen, nombre, ciudad, direccion, nodo_responsable)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (id_almacen) 
            DO UPDATE SET 
                nombre = EXCLUDED.nombre,
                ciudad = EXCLUDED.ciudad,
                direccion = EXCLUDED.direccion,
                nodo_responsable = EXCLUDED.nodo_responsable;
        """
        
        # SQL Server (Santa Cruz): Usamos MERGE para simular el Upsert
        sql_upsert_scz = """
            MERGE almacen AS target
            USING (SELECT ? AS id_almacen) AS source
            ON (target.id_almacen = source.id_almacen)
            WHEN MATCHED THEN
                UPDATE SET nombre = ?, ciudad = ?, direccion = ?, nodo_responsable = ?
            WHEN NOT MATCHED THEN
                INSERT (id_almacen, nombre, ciudad, direccion, nodo_responsable)
                VALUES (?, ?, ?, ?, ?);
        """
        
        for alm in almacenes_master:
            # Ejecutar en Postgres (La Paz)
            valores_lp = (alm['id_almacen'], alm['nombre'], alm['ciudad'], alm['direccion'], alm['nodo_responsable'])
            cur_lp.execute(sql_upsert_lp, valores_lp)
            
            # Ejecutar en SQL Server (Santa Cruz)
            valores_scz = (
                alm['id_almacen'],                  # Para el ON de la condición
                alm['nombre'], alm['ciudad'], alm['direccion'], alm['nodo_responsable'], # Para el UPDATE
                alm['id_almacen'], alm['nombre'], alm['ciudad'], alm['direccion'], alm['nodo_responsable'] # Para el INSERT
            )
            cur_scz.execute(sql_upsert_scz, valores_scz)
            
        conn_lp.commit()
        conn_scz.commit()
        return True
    except Exception as e:
        print(f"🚨 Error en sincronización forzada inteligente: {str(e)}")
        if conn_lp: conn_lp.rollback()
        if conn_scz: conn_scz.rollback()
        return False
    finally:
        if conn_lp: conn_lp.close()
        if conn_scz: conn_scz.close()