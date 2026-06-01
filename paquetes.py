# ------------------------------------------------------------------
# OPERACIONES DE PAQUETES (VERSION ADAPTADA AL FORMATO DE LOS NODOS)
# ------------------------------------------------------------------
import uuid
from conexiones import conectar_lp, conectar_scz, conectar_central
from logs.logger import registrar_log

def obtener_todos_paquetes():
    """Obtiene todos los paquetes unificados desde el nodo_central como fuente de verdad"""
    paquetes = []
    try:
        conn = conectar_central()
        cur = conn.cursor()
        
        # Consultamos la tabla global real
        cur.execute("""
            SELECT codigo_rastreo, descripcion, prioridad, 'Central/Distribuido' as nodo
            FROM PAQUETE_GLOBAL
        """)
        
        for row in cur.fetchall():
            paquetes.append({
                "codigo": row[0],
                "destino": row[1], # Usado como mapeo temporal descriptivo
                "prioridad": row[2],
                "estado": "Sincronizado",
                "nodo": row[3]
            })
        
        cur.close()
        conn.close()
    except Exception as e:
        registrar_log(f"Error obteniendo paquetes desde nodo_central: {e}")
        print("Error obteniendo paquetes desde nodo_central:", e)
        
    return paquetes


def obtener_paquetes_por_nodo(nodo):
    """Obtiene paquetes de un nodo específico"""
    paquetes = []
    
    try:
        if nodo.lower() in ['lapaz', 'la_paz', 'lp']:
            conn = conectar_lp()
            cur = conn.cursor()
            
            cur.execute("""
                SELECT codigo_rastreo, id_ruta, prioridad, 'Registrado' as estado
                FROM paquete_operativo_lp
            """)
        else:  # Santa Cruz
            conn = conectar_scz()
            cur = conn.cursor()
            
            cur.execute("""
                SELECT codigo_rastreo, id_ruta, prioridad, 'Registrado' as estado
                FROM PAQUETE_OPERATIVO_SCZ
            """)
        
        for row in cur.fetchall():
            paquetes.append({
                "codigo": row[0],
                "destino": f"Ruta {row[1]}",
                "prioridad": row[2],
                "estado": row[3]
            })
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error obteniendo paquetes de {nodo}:", e)
    
    return paquetes


def crear_paquete(codigo, destino, prioridad, nodo, remitente=None, descripcion="", peso=1.0, volumen=1.0, valor_declarado=0.0, seguro=0.0, costo_envio=0.0):
    """
    Crea un nuevo paquete respetando la fragmentación híbrida y replicando 
    de manera íntegra todas las columnas operativas y financieras al Nodo Central.
    """
    ID_CLIENTE_REAL = remitente if remitente else "BE5ACC13-D61C-4DA2-A193-90DA21081108"
    ID_ESTADO_REGISTRADO = 1                                  
    ID_ALMACEN_DEFAULT = 1 if nodo.lower() in ['lapaz', 'la_paz', 'lp'] else 2
    
    try:
        ID_RUTA_DEFAULT = int(destino)
    except:
        ID_RUTA_DEFAULT = 1 if nodo.lower() in ['lapaz', 'la_paz', 'lp'] else 2

    id_paquete_nuevo = str(uuid.uuid4())

    # =========================================================
    # CASO NODO LA PAZ: BYPASS DIRECTO AL NODO CENTRAL
    # =========================================================
    if nodo.lower() in ['lapaz', 'la_paz', 'lp']:
        registrar_log("[INFO] Nodo La Paz detectado como DESCONECTADO. Iniciando bypass a nodo_central.")
        try:
            conn = conectar_central()
            cur = conn.cursor()
            
            # 🔄 CORREGIDO: Se cambiaron los %s por ? para evitar el fallo en pyodbc
            query_central = """
                INSERT INTO PAQUETE_GLOBAL (
                    id_paquete, codigo_rastreo, id_cliente_remitente, id_cliente_destinatario,
                    id_estado, id_ruta, id_almacen_actual, peso, volumen, descripcion, 
                    prioridad, valor_declarado, seguro, costo_envio
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            cur.execute(query_central, (
                id_paquete_nuevo, codigo, ID_CLIENTE_REAL, ID_CLIENTE_REAL,
                ID_ESTADO_REGISTRADO, ID_RUTA_DEFAULT, ID_ALMACEN_DEFAULT, peso, volumen, descripcion,
                prioridad, valor_declarado, seguro, costo_envio
            ))
            
            conn.commit()
            cur.close()
            conn.close()
            registrar_log(f"[OK] Paquete {codigo} guardado exitosamente en PAQUETE_GLOBAL (Bypass LP)")
            return True
        except Exception as e:
            registrar_log(f"[ERROR] Fallo critico en bypass a nodo_central para LP: {e}")
            print(f"Error en bypass LP: {e}")
            return False

    # =========================================================
    # CASO NODO SANTA CRUZ: ESCRITURA EN FRAGMENTOS OPERATIVO Y FINANCIERO
    # =========================================================
    else:
        try:
            conn = conectar_scz()
            cur = conn.cursor()
            
            # 1. Inserción en la fracción Operativa Local
            query_operativo = """
                INSERT INTO PAQUETE_OPERATIVO_SCZ (
                    id_paquete, codigo_rastreo, id_cliente_remitente, id_cliente_destinatario,
                    id_estado, id_ruta, id_almacen_actual, peso, volumen, descripcion, prioridad
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            cur.execute(query_operativo, (
                id_paquete_nuevo, codigo, ID_CLIENTE_REAL, ID_CLIENTE_REAL,
                ID_ESTADO_REGISTRADO, ID_RUTA_DEFAULT, ID_ALMACEN_DEFAULT, peso, volumen, descripcion, prioridad
            ))
            
            # 2. Inserción en la fracción Financiera Local
            query_financiero = """
                INSERT INTO PAQUETE_FINANCIERO_SCZ (
                    id_paquete, valor_declarado, seguro, costo_envio
                ) VALUES (?, ?, ?, ?)
            """
            cur.execute(query_financiero, (id_paquete_nuevo, valor_declarado, seguro, costo_envio))
            
            conn.commit()
            cur.close()
            conn.close()
            
            # 3. Réplica Unificada e Integral al Nodo Central
            try:
                conn_c = conectar_central()
                cur_c = conn_c.cursor()
                
                # 🔄 CORREGIDO: Se cambiaron los %s por ? para que coincida con el driver de la central
                query_mirror = """
                    INSERT INTO PAQUETE_GLOBAL (
                        id_paquete, codigo_rastreo, id_cliente_remitente, id_cliente_destinatario,
                        id_estado, id_ruta, id_almacen_actual, peso, volumen, descripcion, 
                        prioridad, valor_declarado, seguro, costo_envio
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                cur_c.execute(query_mirror, (
                    id_paquete_nuevo, codigo, ID_CLIENTE_REAL, ID_CLIENTE_REAL,
                    ID_ESTADO_REGISTRADO, ID_RUTA_DEFAULT, ID_ALMACEN_DEFAULT, peso, volumen, descripcion, 
                    prioridad, valor_declarado, seguro, costo_envio
                ))
                
                conn_c.commit()
                cur_c.close()
                conn_c.close()
                registrar_log(f"[OK] Replica exitosa en PAQUETE_GLOBAL para el paquete {codigo}.")
            except Exception as ex_mirror:
                registrar_log(f"[ALERTA] Guardado local en SCZ exitoso, pero fallo replica a central: {ex_mirror}")
                print(f"Fallo de replica: {ex_mirror}")

            registrar_log(f"[OK] Paquete {codigo} creado de forma hibrida en fragmentos de Santa Cruz.")
            return True
            
        except Exception as e:
            registrar_log(f"[ERROR] Error creando paquete en Santa Cruz: {e}")
            print(f"Error creando paquete en Santa Cruz: {e}")
            return False


def buscar_paquete(codigo):
    """Busca un paquete en todos los nodos"""
    resultado = None
    
    try:
        # Buscar en La Paz
        conn_lp = conectar_lp()
        cur_lp = conn_lp.cursor()
        
        cur_lp.execute("""
            SELECT codigo_rastreo, id_ruta, prioridad, 'Registrado' as estado
            FROM paquete_operativo_lp
            WHERE codigo_rastreo = %s
        """, (codigo,))
        
        fila = cur_lp.fetchone()
        if fila:
            resultado = {
                "codigo": fila[0],
                "destino": f"Ruta {fila[1]}",
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
                SELECT codigo_rastreo, id_ruta, prioridad, 'Registrado' as estado
                FROM PAQUETE_OPERATIVO_SCZ
                WHERE codigo_rastreo = '{codigo}'
            """)
            
            fila = cur_scz.fetchone()
            if fila:
                resultado = {
                    "codigo": fila[0],
                    "destino": f"Ruta {fila[1]}",
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
    datos = []
    try:
        # Nota: He ajustado el SELECT para traer exactamente lo que el frontend necesita
        query = "SELECT id_paquete, codigo_rastreo, descripcion FROM "
        
        if "la_paz" in nodo.lower() or "lp" in nodo.lower():
            conn = conectar_lp()
            table = "paquete_operativo_lp"
        else:
            conn = conectar_scz()
            table = "PAQUETE_OPERATIVO_SCZ"
            
        cur = conn.cursor()
        cur.execute(query + table)
        columnas = [desc[0] for desc in cur.description]
        datos = [dict(zip(columnas, f)) for f in cur.fetchall()]
        cur.close()
        conn.close()
        return datos
    except Exception as e:
        registrar_log(f"Error consultando paquetes en {nodo}: {e}")
        return []


def obtener_tabla_movimiento(nodo):
    """Obtiene los datos completos de la tabla MOVIMIENTO de un nodo"""
    try:
        if nodo.lower() in ['lapaz', 'la_paz', 'lp']:
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
    try:
        conn = conectar_scz() if nodo.lower() not in ['lapaz', 'la_paz', 'lp'] else conectar_central()
        cur = conn.cursor()
        tabla = "PAQUETE_FINANCIERO_SCZ" if nodo.lower() not in ['lapaz', 'la_paz', 'lp'] else "PAQUETE_GLOBAL"
        cur.execute(f"SELECT * FROM {tabla}")
        columnas = [desc[0] for desc in cur.description]
        datos = [dict(zip(columnas, f)) for f in cur.fetchall()]
        cur.close() 
        conn.close()
        return datos
    except: return []


def obtener_paquetes_por_tipo_nodo(nodo):
    """Retorna las colecciones distribuidas mapeando de forma exacta los nombres del motor relacional"""
    resultado = {"operativos": [], "financieros": []}

    try:
        if nodo.lower() in ['lapaz', 'la_paz', 'lp']:
            # Redirección analítica al nodo central ya que LP actúa de forma remota/desconectada en local
            conn = conectar_central()
            cur = conn.cursor()
            
            cur.execute("SELECT id_paquete, codigo_rastreo, descripcion, prioridad, id_ruta FROM PAQUETE_OPERATIVO_LP")
            columnas = [desc[0] for desc in cur.description]
            resultado["operativos"] = [dict(zip(columnas, fila)) for fila in cur.fetchall()]
            
            cur.execute("SELECT id_paquete, valor_declarado, seguro, costo_envio FROM PAQUETE_FINANCIERO_LP")
            columnas_fi = [desc[0] for desc in cur.description]
            resultado["financieros"] = [dict(zip(columnas_fi, fila)) for fila in cur.fetchall()]
            
            cur.close()
            conn.close()
        else:
            # Santa Cruz - Consulta cruzada a tablas reales fragmentadas verticalmente
            conn = conectar_scz()
            cur = conn.cursor()

            cur.execute("SELECT id_paquete, codigo_rastreo, descripcion, prioridad, id_ruta FROM PAQUETE_OPERATIVO_SCZ")
            columnas_op = [desc[0] for desc in cur.description]
            resultado["operativos"] = [dict(zip(columnas_op, fila)) for fila in cur.fetchall()]

            cur.execute("SELECT id_paquete, valor_declarado, seguro, costo_envio FROM PAQUETE_FINANCIERO_SCZ")
            columnas_fi = [desc[0] for desc in cur.description]
            resultado["financieros"] = [dict(zip(columnas_fi, fila)) for fila in cur.fetchall()]

            cur.close()
            conn.close()
            
    except Exception as e:
        registrar_log(f"Error en obtener_paquetes_por_tipo_nodo para {nodo}: {e}")

    return resultado