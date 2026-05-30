# -----------------------------------
# OPERACIONES DE PAQUETES
# -----------------------------------

from conexiones import conectar_lp, conectar_scz, conectar_central
from logs.logger import registrar_log

def obtener_todos_paquetes():
    """Obtiene todos los paquetes de ambos nodos"""
    paquetes = []
    
    try:
        # La Paz
        conn_lp = conectar_lp()
        cur_lp = conn_lp.cursor()
        
        cur_lp.execute("""
            SELECT codigo_rastreo, destino, prioridad, estado, 'La Paz' as nodo
            FROM paquete_lp
        """)
        
        for row in cur_lp.fetchall():
            paquetes.append({
                "codigo": row[0],
                "destino": row[1],
                "prioridad": row[2],
                "estado": row[3],
                "nodo": row[4]
            })
        
        cur_lp.close()
        conn_lp.close()
    except Exception as e:
        print("Error obteniendo paquetes de La Paz:", e)
    
    try:
        # Santa Cruz
        conn_scz = conectar_scz()
        cur_scz = conn_scz.cursor()
        
        cur_scz.execute("""
            SELECT codigo_rastreo, destino, prioridad, estado, 'Santa Cruz' as nodo
            FROM paquete_scz
        """)
        
        for row in cur_scz.fetchall():
            paquetes.append({
                "codigo": row[0],
                "destino": row[1],
                "prioridad": row[2],
                "estado": row[3],
                "nodo": row[4]
            })
        
        cur_scz.close()
        conn_scz.close()
    except Exception as e:
        print("Error obteniendo paquetes de Santa Cruz:", e)
    
    return paquetes


def obtener_paquetes_por_nodo(nodo):
    """Obtiene paquetes de un nodo específico"""
    paquetes = []
    
    try:
        if nodo.lower() == 'lapaz':
            conn = conectar_lp()
            cur = conn.cursor()
            
            cur.execute("""
                SELECT codigo_rastreo, destino, prioridad, estado
                FROM paquete_lp
            """)
        else:  # Santa Cruz
            conn = conectar_scz()
            cur = conn.cursor()
            
            cur.execute("""
                SELECT codigo_rastreo, destino, prioridad, estado
                FROM paquete_scz
            """)
        
        for row in cur.fetchall():
            paquetes.append({
                "codigo": row[0],
                "destino": row[1],
                "prioridad": row[2],
                "estado": row[3]
            })
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error obteniendo paquetes de {nodo}:", e)
    
    return paquetes


def crear_paquete(codigo, destino, prioridad, nodo):
    """Crea un nuevo paquete en el nodo especificado"""
    try:
        if nodo.lower() == 'lapaz':
            conn = conectar_lp()
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO paquete_lp (codigo_rastreo, destino, prioridad, estado)
                VALUES (%s, %s, %s, %s)
            """, (codigo, destino, prioridad, 'Registrado'))
            
        else:  # Santa Cruz
            conn = conectar_scz()
            cur = conn.cursor()
            
            cur.execute(f"""
                INSERT INTO paquete_scz (codigo_rastreo, destino, prioridad, estado)
                VALUES ('{codigo}', '{destino}', '{prioridad}', 'Registrado')
            """)
        
        conn.commit()
        cur.close()
        conn.close()
        
        registrar_log(f"Paquete {codigo} creado en {nodo}")
        return True
    except Exception as e:
        print(f"Error creando paquete: {e}")
        return False


def buscar_paquete(codigo):
    """Busca un paquete en todos los nodos"""
    resultado = None
    
    try:
        # Buscar en La Paz
        conn_lp = conectar_lp()
        cur_lp = conn_lp.cursor()
        
        cur_lp.execute("""
            SELECT codigo_rastreo, destino, prioridad, estado
            FROM paquete_lp
            WHERE codigo_rastreo = %s
        """, (codigo,))
        
        fila = cur_lp.fetchone()
        if fila:
            resultado = {
                "codigo": fila[0],
                "destino": fila[1],
                "prioridad": fila[2],
                "estado": fila[3],
                "nodo": "La Paz"
            }
        
        cur_lp.close()
        conn_lp.close()
    except:
        pass
    
    if not resultado:
        try:
            # Buscar en Santa Cruz
            conn_scz = conectar_scz()
            cur_scz = conn_scz.cursor()
            
            cur_scz.execute(f"""
                SELECT codigo_rastreo, destino, prioridad, estado
                FROM paquete_scz
                WHERE codigo_rastreo = '{codigo}'
            """)
            
            fila = cur_scz.fetchone()
            if fila:
                resultado = {
                    "codigo": fila[0],
                    "destino": fila[1],
                    "prioridad": fila[2],
                    "estado": fila[3],
                    "nodo": "Santa Cruz"
                }
            
            cur_scz.close()
            conn_scz.close()
        except:
            pass
    
    return resultado


def obtener_tabla_paquete(nodo):
    """Obtiene los datos completos de la tabla PAQUETE de un nodo"""
    try:
        if nodo.lower() == 'lapaz':
            conn = conectar_lp()
            cur = conn.cursor()
            cur.execute("SELECT * FROM paquete_lp")
        else:
            conn = conectar_scz()
            cur = conn.cursor()
            # En Santa Cruz la tabla de paquetes operativos se llama paquete_operativo_scz
            try:
                cur.execute("SELECT * FROM paquete_operativo_scz")
            except Exception:
                # Fallback a nombre genérico si no existe
                cur.execute("SELECT * FROM paquete_scz")
        
        columnas = [descripcion[0] for descripcion in cur.description]
        filas = cur.fetchall()
        
        datos = []
        for fila in filas:
            datos.append(dict(zip(columnas, fila)))
        
        cur.close()
        conn.close()
        
        return datos
    except Exception as e:
        print(f"Error obteniendo tabla PAQUETE de {nodo}:", e)
        return []


def obtener_tabla_movimiento(nodo):
    """Obtiene los datos completos de la tabla MOVIMIENTO de un nodo"""
    try:
        if nodo.lower() == 'lapaz':
            conn = conectar_lp()
            cur = conn.cursor()
            cur.execute("SELECT * FROM movimiento_lp")
        else:
            conn = conectar_scz()
            cur = conn.cursor()
            cur.execute("SELECT * FROM movimiento_scz")
        
        columnas = [descripcion[0] for descripcion in cur.description]
        filas = cur.fetchall()
        
        datos = []
        for fila in filas:
            datos.append(dict(zip(columnas, fila)))
        
        cur.close()
        conn.close()
        
        return datos
    except Exception as e:
        print(f"Error obteniendo tabla MOVIMIENTO de {nodo}:", e)
        return []


def obtener_tabla_paquete_financiero(nodo):
    """Obtiene la tabla de paquete financiero para un nodo (si aplica)"""
    try:
        if nodo.lower() == 'lapaz':
            # En La Paz no existe tabla financiera diferenciada en este esquema
            conn = conectar_lp()
            cur = conn.cursor()
            # Intentar nombre convencional
            cur.execute("SELECT * FROM paquete_financiero_lp")
        else:
            conn = conectar_scz()
            cur = conn.cursor()
            cur.execute("SELECT * FROM paquete_financiero_scz")

        columnas = [descripcion[0] for descripcion in cur.description]
        filas = cur.fetchall()

        datos = [dict(zip(columnas, fila)) for fila in filas]

        cur.close()
        conn.close()

        return datos
    except Exception as e:
        print(f"Error obteniendo tabla PAQUETE_FINANCIERO de {nodo}:", e)
        return []
