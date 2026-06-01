# -----------------------------------
# OPERACIONES DE MOVIMIENTOS
# -----------------------------------

from conexiones import conectar_lp, conectar_scz
from logs.logger import registrar_log
from datetime import datetime

def registrar_movimiento(id_movimiento, id_paquete, ubicacion, estado, nodo):
    """Registra un nuevo movimiento en el nodo especificado"""
    try:
        if nodo.lower() == 'lapaz':
            conn = conectar_lp()
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO movimiento_lp (id_movimiento, id_paquete, ubicacion, estado, fecha_movimiento)
                VALUES (%s, %s, %s, %s, %s)
            """, (id_movimiento, id_paquete, ubicacion, estado, datetime.now()))
            
        else:  # Santa Cruz
            conn = conectar_scz()
            cur = conn.cursor()
            
            cur.execute(f"""
                INSERT INTO movimiento_scz (id_movimiento, id_paquete, ubicacion, estado, fecha_movimiento)
                VALUES ('{id_movimiento}', '{id_paquete}', '{ubicacion}', '{estado}', GETDATE())
            """)
        
        conn.commit()
        cur.close()
        conn.close()
        
        registrar_log(f"Movimiento {id_movimiento} registrado en {nodo}")
        return True
    except Exception as e:
        print(f"Error registrando movimiento: {e}")
        return False


def obtener_movimientos_paquete(codigo_paquete, nodo):
    """Obtiene todos los movimientos asociados a un paquete"""
    movimientos = []
    
    try:
        if nodo.lower() == 'lapaz':
            conn = conectar_lp()
            cur = conn.cursor()
            
            cur.execute("""
                SELECT id_movimiento, ubicacion, estado, fecha_movimiento, observacion
                FROM movimiento_lp
                WHERE id_paquete = (
                    SELECT id_paquete FROM paquete_lp WHERE codigo_rastreo = %s
                )
                ORDER BY fecha_movimiento DESC
            """, (codigo_paquete,))
        else:
            conn = conectar_scz()
            cur = conn.cursor()
            
            cur.execute(f"""
                SELECT id_movimiento, ubicacion, estado, fecha_movimiento, observacion
                FROM movimiento_scz
                WHERE id_paquete = (
                    SELECT id_paquete FROM paquete_scz WHERE codigo_rastreo = '{codigo_paquete}'
                )
                ORDER BY fecha_movimiento DESC
            """)
        
        for row in cur.fetchall():
            movimientos.append({
                "id": row[0],
                "ubicacion": row[1],
                "estado": row[2],
                "fecha": str(row[3]),
                "observacion": row[4] if len(row) > 4 else ""
            })
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error obteniendo movimientos: {e}")
    
    return movimientos


def obtener_todos_movimientos(nodo):
    """Obtiene todos los movimientos de un nodo"""
    movimientos = []
    
    try:
        if nodo.lower() == 'lapaz':
            conn = conectar_lp()
            cur = conn.cursor()
            cur.execute("SELECT * FROM movimiento_lp ORDER BY fecha_movimiento DESC")
        else:
            conn = conectar_scz()
            cur = conn.cursor()
            cur.execute("SELECT * FROM movimiento_scz ORDER BY fecha_movimiento DESC")
        
        columnas = [descripcion[0] for descripcion in cur.description]
        filas = cur.fetchall()
        
        for fila in filas:
            movimientos.append(dict(zip(columnas, fila)))
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error obteniendo movimientos de {nodo}:", e)
    
    return movimientos


def actualizar_estado_movimiento(id_movimiento, nuevo_estado, nodo):
    """Actualiza el estado de un movimiento"""
    try:
        if nodo.lower() == 'lapaz':
            conn = conectar_lp()
            cur = conn.cursor()
            
            cur.execute("""
                UPDATE movimiento_lp
                SET estado = %s
                WHERE id_movimiento = %s
            """, (nuevo_estado, id_movimiento))
        else:
            conn = conectar_scz()
            cur = conn.cursor()
            
            cur.execute(f"""
                UPDATE movimiento_scz
                SET estado = '{nuevo_estado}'
                WHERE id_movimiento = '{id_movimiento}'
            """)
        
        conn.commit()
        cur.close()
        conn.close()
        
        registrar_log(f"Estado del movimiento {id_movimiento} actualizado a {nuevo_estado}")
        return True
    except Exception as e:
        print(f"Error actualizando movimiento: {e}")
        return False


def obtener_historial_completo(codigo_paquete):
    """Obtiene el historial completo de un paquete desde ambos nodos"""
    historial = []
    
    try:
        conn_lp = conectar_lp()
        cur_lp = conn_lp.cursor()
        
        cur_lp.execute("""
            SELECT ubicacion, estado, fecha_movimiento, observacion, 'La Paz' as nodo
            FROM movimiento_lp
            WHERE id_paquete = (
                SELECT id_paquete FROM paquete_lp WHERE codigo_rastreo = %s
            )
        """, (codigo_paquete,))
        
        for row in cur_lp.fetchall():
            historial.append({
                "ubicacion": row[0],
                "estado": row[1],
                "fecha": str(row[2]),
                "observacion": row[3] if len(row) > 3 else "",
                "nodo": row[4]
            })
        
        cur_lp.close()
        conn_lp.close()
    except:
        pass
    
    try:
        conn_scz = conectar_scz()
        cur_scz = conn_scz.cursor()
        
        cur_scz.execute(f"""
            SELECT ubicacion, estado, fecha_movimiento, observacion, 'Santa Cruz' as nodo
            FROM movimiento_scz
            WHERE id_paquete = (
                SELECT id_paquete FROM paquete_scz WHERE codigo_rastreo = '{codigo_paquete}'
            )
        """)
        
        for row in cur_scz.fetchall():
            historial.append({
                "ubicacion": row[0],
                "estado": row[1],
                "fecha": str(row[2]),
                "observacion": row[3] if len(row) > 3 else "",
                "nodo": row[4]
            })
        
        cur_scz.close()
        conn_scz.close()
    except:
        pass
    
    # Ordenar por fecha
    historial.sort(key=lambda x: x['fecha'])
    
    return historial
