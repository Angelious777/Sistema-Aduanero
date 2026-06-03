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
        
        cur.execute("""
            SELECT codigo_rastreo, descripcion, prioridad, 'Central/Distribuido' as nodo
            FROM PAQUETE_GLOBAL
        """)
        
        for row in cur.fetchall():
            paquetes.append({
                "codigo": row[0],
                "destino": row[1], 
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


def crear_paquete(codigo, destino, prioridad, nodo, remitente, destinatario, descripcion, peso, volumen, valor_declarado, seguro, costo_envio):
    id_paquete = str(uuid.uuid4())
    nodo_origen = str(nodo).strip().lower()
    
    # Asegúrate de mapear estas sub-funciones internas en tus scripts de inserción 
    # para que acepten tanto 'remitente' como 'destinatario' en los INSERT INTO de SQL.
    insertar_en_central(id_paquete, codigo, destino, prioridad, remitente, destinatario, descripcion, peso, volumen, valor_declarado, seguro, costo_envio)
        
    if nodo_origen in ['lapaz', 'la_paz', 'lp']:
        insertar_en_lp(id_paquete, codigo, destino, prioridad, remitente, destinatario, descripcion, peso, volumen, valor_declarado, seguro, costo_envio)
    elif nodo_origen in ['santacruz', 'santa_cruz', 'scz']:
        insertar_en_scz(id_paquete, codigo, destino, prioridad, remitente, destinatario, descripcion, peso, volumen, valor_declarado, seguro, costo_envio)
    else:
        raise ValueError(f"Nodo de origen '{nodo_origen}' no mapeado.")
        
    # Replicación cruzada parcial (Fragmento Operativo Inverso)
    if nodo_origen not in ['lapaz', 'la_paz', 'lp']:
        insertar_operativo_lp_solo(id_paquete, codigo, destino, prioridad, remitente, destinatario, descripcion, peso, volumen)
    else:
        insertar_operativo_scz_solo(id_paquete, codigo, destino, prioridad, remitente, destinatario, descripcion, peso, volumen)
            
    return True


def insertar_operativo_lp_solo(id_paquete, codigo, destino, prioridad, remitente, descripcion, peso, volumen):
    """Inserta la parte operativa en PostgreSQL (LP) respetando las restricciones NOT NULL"""
    conn = conectar_lp()
    cur = conn.cursor()
    
    id_cliente_destinatario = remitente  
    id_estado = 1                        
    id_almacen_actual = 1                 

    cur.execute("""
        INSERT INTO paquete_operativo_lp 
        (id_paquete, codigo_rastreo, id_cliente_remitente, id_cliente_destinatario, 
         id_estado, id_ruta, id_almacen_actual, peso, volumen, descripcion, prioridad) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        id_paquete, codigo, remitente, id_cliente_destinatario,
        id_estado, int(destino), id_almacen_actual, peso, volumen, descripcion, prioridad
    ))
    conn.commit()
    cur.close()
    conn.close()

def insertar_en_lp(id_paquete, codigo, destino, prioridad, remitente, descripcion, peso, volumen, valor_declarado, seguro, costo_envio):
    """Coordina la inserción fragmentada en La Paz"""
    # 1. Fragmento Operativo
    insertar_operativo_lp_solo(id_paquete, codigo, destino, prioridad, remitente, descripcion, peso, volumen)
    
    # 2. Fragmento Financiero
    conn = conectar_lp()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO paquete_financiero_lp 
        (id_paquete, valor_declarado, seguro, costo_envio) 
        VALUES (%s, %s, %s, %s)
    """, (id_paquete, valor_declarado, seguro, costo_envio))
    conn.commit()
    cur.close()
    conn.close()


def insertar_operativo_scz_solo(id_paquete, codigo, destino, prioridad, remitente, descripcion, peso, volumen):
    """Inserta la parte operativa en SQL Server (SCZ) respetando las restricciones NOT NULL"""
    conn = conectar_scz()
    cur = conn.cursor()
    
    id_cliente_destinatario = remitente  
    id_estado = 1                        
    id_almacen_actual = 1                 

    cur.execute("""
        INSERT INTO PAQUETE_OPERATIVO_SCZ 
        (id_paquete, codigo_rastreo, id_cliente_remitente, id_cliente_destinatario, 
         id_estado, id_ruta, id_almacen_actual, peso, volumen, descripcion, prioridad) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        id_paquete, codigo, remitente, id_cliente_destinatario,
        id_estado, int(destino), id_almacen_actual, peso, volumen, descripcion, prioridad
    ))
    conn.commit()
    cur.close()
    conn.close()

def insertar_en_scz(id_paquete, codigo, destino, prioridad, remitente, descripcion, peso, volumen, valor_declarado, seguro, costo_envio):
    """Coordina la inserción fragmentada en Santa Cruz"""
    # 1. Fragmento Operativo
    insertar_operativo_scz_solo(id_paquete, codigo, destino, prioridad, remitente, descripcion, peso, volumen)
    
    # 2. Fragmento Financiero
    conn = conectar_scz()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO PAQUETE_FINANCIERO_SCZ 
        (id_paquete, valor_declarado, seguro, costo_envio) 
        VALUES (?, ?, ?, ?)
    """, (id_paquete, valor_declarado, seguro, costo_envio))
    conn.commit()
    cur.close()
    conn.close()


def insertar_en_central(id_paquete, codigo, destino, prioridad, remitente, descripcion, peso, volumen, valor_declarado, seguro, costo_envio):
    """Registra el paquete con su esquema completo en el Nodo Central (SQL Server)"""
    try:
        conn = conectar_central()
        cur = conn.cursor()
        
        # Valores por defecto requeridos para cumplir los NOT NULL de las FKs maestras en Central
        id_cliente_destinatario = remitente  # Si el payload no trae destinatario, usamos el remitente
        id_estado = 1                        # ID de estado 'Registrado'
        id_almacen_actual = 1                 # ID del almacén inicial
        
        cur.execute("""
            INSERT INTO PAQUETE_GLOBAL 
            (id_paquete, codigo_rastreo, id_cliente_remitente, id_cliente_destinatario, 
             id_estado, id_ruta, id_almacen_actual, peso, volumen, descripcion, 
             prioridad, valor_declarado, seguro, costo_envio) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            id_paquete, codigo, remitente, id_cliente_destinatario,
            id_estado, int(destino), id_almacen_actual, peso, volumen, descripcion,
            prioridad, valor_declarado, seguro, costo_envio
        ))
        
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        registrar_log(f"FALLO CRÍTICO: No se pudo registrar en Central: {e}")
        raise e


def buscar_paquete(codigo):
    """Busca un paquete de forma transversal en el clúster"""
    resultado = None
    
    # Buscar en La Paz (PostgreSQL)
    try:
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
    
    # Buscar en Santa Cruz (SQL Server) si no se encontró en LP
    if not resultado:
        try:
            conn = conectar_scz()
            cur = conn.cursor()
            cur.execute("""
                SELECT codigo_rastreo, id_ruta, prioridad, 'Registrado' as estado
                FROM PAQUETE_OPERATIVO_SCZ
                WHERE codigo_rastreo = ?
            """, (codigo,))
            fila = cur.fetchone()  # Corregido: Usando el cursor correcto 'cur'
            if fila:
                resultado = {
                    "codigo": fila[0],
                    "destino": f"Ruta {fila[1]}",
                    "prioridad": fila[2],
                    "estado": fila[3],
                    "nodo": "Santa Cruz"
                }
            cur.close()
            conn.close()
        except:
            pass
    
    return resultado


def obtener_tabla_paquete(nodo):
    datos = []
    try:
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
    except Exception as e:
        registrar_log(f"Error consultando paquetes en {nodo}: {e}")
    return datos


def obtener_tabla_movimiento(nodo):
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
        datos = [dict(zip(columnas, fila)) for fila in filas]
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
    except: 
        return []


def obtener_paquetes_por_tipo_nodo(nodo):
    resultado = {"operativos": [], "financieros": []}
    try:
        if nodo.lower() in ['lapaz', 'la_paz', 'lp']:
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

def obtener_paquetes_coordinador_central():
    """Ejecuta la reconstrucción horizontal y relacional desde el Nodo Central
    para mapear los paquetes con sus datos logísticos, clientes y almacenes.
    """
    paquetes = []
    conn = None
    cur = None
    try:
        conn = conectar_central() # SQL Server Maestro
        cur = conn.cursor()
        
        query = """
            SELECT 
                p.id_paquete,
                p.codigo_rastreo,
                -- Remitente
                CONCAT(cr.nombre, ' ', cr.apellido_paterno, ' ', ISNULL(cr.apellido_materno, '')) AS remitente,
                -- Destinatario
                CONCAT(cd.nombre, ' ', cd.apellido_paterno, ' ', ISNULL(cd.apellido_materno, '')) AS destinatario,
                a_act.nombre AS almacen_actual,
                a_orig.ciudad AS ciudad_origen,
                a_dest.ciudad AS ciudad_destino,
                est.nombre AS estado_nombre,
                p.fecha_registro,
                -- Datos adicionales para el Modal
                p.peso, p.volumen, p.descripcion, p.prioridad,
                p.valor_declarado, p.seguro, p.costo_envio
            FROM PAQUETE_GLOBAL p
            INNER JOIN CLIENTE_PUBLICO cr ON p.id_cliente_remitente = cr.id_cliente
            INNER JOIN CLIENTE_PUBLICO cd ON p.id_cliente_destinatario = cd.id_cliente
            INNER JOIN ESTADO est ON p.id_estado = est.id_estado
            INNER JOIN RUTA r ON p.id_ruta = r.id_ruta
            INNER JOIN ALMACEN a_orig ON r.id_almacen_origen = a_orig.id_almacen
            INNER JOIN ALMACEN a_dest ON r.id_almacen_destino = a_dest.id_almacen
            INNER JOIN ALMACEN a_act ON p.id_almacen_actual = a_act.id_almacen
            ORDER BY p.fecha_registro DESC
        """
        cur.execute(query)
        filas = cur.fetchall()
        
        for f in filas:
            f_reg = f[8].strftime('%Y-%m-%d %H:%M:%S') if f[8] else '—'
            paquetes.append({
                "id": str(f[0]),
                "codigo": f[1],
                "remitente": f[2].strip(),
                "destinatario": f[3].strip(),
                "almacen_actual": f[4],
                "ciudad_origen": f[5],
                "ciudad_destino": f[6],
                "estado": f[7],
                "registro": f_reg,
                # Detalles Técnicos para mapeo rápido en modal
                "peso": float(f[9]) if f[9] else 0.0,
                "volumen": float(f[10]) if f[10] else 0.0,
                "descripcion": f[11] or "Sin descripción",
                "prioridad": f[12] or "Normal",
                # Información Financiera
                "valor_declarado": float(f[13]) if f[13] else 0.0,
                "seguro": float(f[14]) if f[14] else 0.0,
                "costo_envio": float(f[15]) if f[15] else 0.0
            })
    finally:
        if cur: cur.close()
        if conn: conn.close()
    return paquetes


def obtener_historial_movimientos_paquete(id_paquete):
    """Consulta los eventos de tránsito registrados del paquete unificando
    el almacén y el nodo responsable según el esquema distribuido.
    """
    historial = []
    conn = None
    cur = None
    try:
        conn = conectar_central()
        cur = conn.cursor()
        query = """
            SELECT h.fecha_movimiento, h.observacion, a.nombre, a.nodo_responsable
            FROM MOVIMIENTO_GLOBAL h
            INNER JOIN ALMACEN a ON h.id_almacen = a.id_almacen
            WHERE h.id_paquete = ?
            ORDER BY h.fecha_movimiento DESC
        """
        cur.execute(query, (id_paquete,))
        for f in cur.fetchall():
            historial.append({
                "fecha": f[0].strftime('%Y-%m-%d %H:%M:%S') if f[0] else '—',
                "observacion": f[1],
                "almacen": f[2],
                "nodo": f[3] # Ej: 'nodo_lp' o 'nodo_scz'
            })
    except Exception:
        # Fallback de simulación estructurada si la tabla de movimientos es dinámica
        pass
    finally:
        if cur: cur.close()
        if conn: conn.close()
    return historial


# ==============================================================================
# PERSISTENCIA DISTRIBUIDA DE ESTADOS EN EL CLÚSTER HÍBRIDO
# ==============================================================================
def actualizar_estado_distribuido(codigo, nuevo_estado, nodo_origen):
    nodo_limpio = str(nodo_origen).strip().lower()
    
    # Determinar qué tablas e instrucciones aplicar según el tipo de motor regional
    if nodo_limpio in ['santa_cruz', 'scz', 'nodo_scz']:
        tabla_regional = "PAQUETE_OPERATIVO_SCZ"
        conn_regional = conectar_scz()
    else:
        tabla_regional = "paquete_operativo_lp"
        conn_regional = conectar_lp()

    # 1. ACTUALIZACIÓN EN NODO CENTRAL (SQL Server - Catálogo Maestro Global)
    conn_central = conectar_central()
    try:
        cur_central = conn_central.cursor()
        # Se asume que el maestro global se encuentra unificado bajo la tabla maestra global 'paquetes'
        cur_central.execute(
            "UPDATE paquetes SET estado = ? WHERE codigo_rastreo = ?", 
            (nuevo_estado, codigo)
        )
        conn_central.commit()
    finally:
        conn_central.close()

    # 2. ACTUALIZACIÓN EN FRAGMENTO REGIONAL CORRESPONDIENTE
    try:
        cur_regional = conn_regional.cursor()
        # Se ejecuta de forma segura parametrizando de acuerdo al driver nativo
        if nodo_limpio in ['santa_cruz', 'scz', 'nodo_scz']:
            cur_regional.execute(
                f"UPDATE {tabla_regional} SET estado = ? WHERE codigo_rastreo = ?", 
                (nuevo_estado, codigo)
            )
        else:
            cur_regional.execute(
                f"UPDATE {tabla_regional} SET estado = %s WHERE codigo_rastreo = %s", 
                (nuevo_estado, codigo)
            )
        conn_regional.commit()
    finally:
        conn_regional.close()

    return True