# -*- coding: utf-8 -*-
"""
sincronizacion.py (Versión Corregida con Nombres de Columna del Esquema Real)
"""
from conexiones import conectar_central, conectar_lp, conectar_scz
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Sincronizador")

def sincronizar_clientes_master():
    """
    Sincroniza CLIENTE_GLOBAL (Central) hacia las regiones.
    Tolerante a fallos de red y adaptado a las columnas reales de CLIENTE_GLOBAL.
    """
    reporte = {}
    
    # 1. INTENTAR CONECTAR AL NODO CENTRAL (La fuente de la verdad)
    try:
        conn_central = conectar_central()
        cur_central = conn_central.cursor()
        
        # CORRECCIÓN DE COLUMNAS REALES: Se usan los nombres definidos en tu vista SQL
        cur_central.execute("""
            SELECT 
                id_cliente, 
                nombre, 
                apellido_paterno, 
                apellido_materno, 
                telefono, 
                documento_identidad, 
                direccion, 
                email 
            FROM CLIENTE_GLOBAL
        """)
        
        clientes_central = {}
        for row in cur_central.fetchall():
            id_str = str(row[0]).upper()
            clientes_central[id_str] = {
                "id": id_str,
                "nombre_pila": row[1],
                "apellido_paterno": row[2],
                "apellido_materno": row[3] if row[3] else '',
                "telefono": row[4] if row[4] else '',
                "documento_identidad": row[5] if row[5] else '',
                "direccion": row[6] if row[6] else '',
                "email": row[7] if row[7] else ''
            }
            
        cur_central.close()
        conn_central.close()
    except Exception as e:
        logger.error(f"🚨 CRÍTICO: Error en el query o conectividad del Nodo Central: {e}")
        return {"success": False, "error": f"Fallo en Nodo Central: {str(e)}"}

    # Configuración de los nodos regionales
    nodos = {
        'la_paz': {'conectar': conectar_lp, 'db_type': 'postgresql'},
        'santa_cruz': {'conectar': conectar_scz, 'db_type': 'sqlserver'}
    }

    al_menos_uno_sincronizado = False

    for nombre_nodo, config in nodos.items():
        try:
            logger.info(f"🔄 Intentando conectar con el fragmento regional: {nombre_nodo}...")
            conn_reg = config['conectar']()
            cur_reg = conn_reg.cursor()
            
            # CORRECCIÓN EN ESCLAVOS: Tus tablas regionales se llaman 'cliente_publico' / 'CLIENTE_PUBLICO'
            tabla_regional = "cliente_publico" if config['db_type'] == 'postgresql' else "CLIENTE_PUBLICO"
            
            cur_reg.execute(f"""
                SELECT id_cliente, nombre, apellido_paterno, apellido_materno, telefono 
                FROM {tabla_regional}
            """)
            
            clientes_regionales = {
                str(row[0]).upper(): {
                    "id": str(row[0]).upper(), 
                    "nombre": row[1], 
                    "apellido_paterno": row[2],
                    "apellido_materno": row[3] if row[3] else '',
                    "telefono": row[4] if row[4] else ''
                } for row in cur_reg.fetchall()
            }

            inserts, updates, deletes = 0, 0, 0

            # --- FASE 1: Altas y Modificaciones ---
            for id_c, c_cen in clientes_central.items():
                
                if id_c not in clientes_regionales:
                    # El cliente falta en la base regional -> INSERT
                    if config['db_type'] == 'postgresql':
                        cur_reg.execute(f"""
                            INSERT INTO {tabla_regional} (id_cliente, nombre, apellido_paterno, apellido_materno, telefono)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (id_c, c_cen['nombre_pila'], c_cen['apellido_paterno'], c_cen['apellido_materno'], c_cen['telefono']))
                    else:
                        cur_reg.execute(f"""
                            INSERT INTO {tabla_regional} (id_cliente, nombre, apellido_paterno, apellido_materno, telefono)
                            VALUES ('{id_c}', '{c_cen['nombre_pila']}', '{c_cen['apellido_paterno']}', '{c_cen['apellido_materno']}', '{c_cen['telefono']}')
                        """)
                    inserts += 1
                else:
                    # El cliente existe -> Evaluar cambios en campos públicos para hacer UPDATE
                    c_reg = clientes_regionales[id_c]
                    
                    if (c_cen['nombre_pila'] != c_reg['nombre'] or 
                        c_cen['apellido_paterno'] != c_reg['apellido_paterno'] or 
                        c_cen['apellido_materno'] != c_reg['apellido_materno'] or 
                        c_cen['telefono'] != c_reg['telefono']):
                        
                        if config['db_type'] == 'postgresql':
                            cur_reg.execute(f"""
                                UPDATE {tabla_regional} 
                                SET nombre=%s, apellido_paterno=%s, apellido_materno=%s, telefono=%s
                                WHERE id_cliente=%s
                            """, (c_cen['nombre_pila'], c_cen['apellido_paterno'], c_cen['apellido_materno'], c_cen['telefono'], id_c))
                        else:
                            cur_reg.execute(f"""
                                UPDATE {tabla_regional} 
                                SET nombre='{c_cen['nombre_pila']}', apellido_paterno='{c_cen['apellido_paterno']}', apellido_materno='{c_cen['apellido_materno']}', telefono='{c_cen['telefono']}'
                                WHERE id_cliente='{id_c}'
                            """)
                        updates += 1

            # --- FASE 2: Purgado / Eliminaciones ---
            for id_reg in clientes_regionales.keys():
                if id_reg not in clientes_central:
                    if config['db_type'] == 'postgresql':
                        cur_reg.execute(f"DELETE FROM {tabla_regional} WHERE id_cliente = %s", (id_reg,))
                    else:
                        cur_reg.execute(f"DELETE FROM {tabla_regional} WHERE id_cliente = '{id_reg}'")
                    deletes += 1

            conn_reg.commit()
            cur_reg.close()
            conn_reg.close()

            reporte[nombre_nodo] = {
                "estado": "ONLINE",
                "inserciones": inserts,
                "modificaciones": updates,
                "eliminaciones": deletes
            }
            al_menos_uno_sincronizado = True
            logger.info(f"✅ Nodo {nombre_nodo} sincronizado correctamente.")

        except Exception as error_nodo:
            logger.warning(f"⚠️ El nodo {nombre_nodo} está OFFLINE. Saltando... Detalle: {error_nodo}")
            reporte[nombre_nodo] = {
                "estado": "OFFLINE / INACCESIBLE",
                "inserciones": 0,
                "modificaciones": 0,
                "eliminaciones": 0
            }

    return {
        "success": al_menos_uno_sincronizado, 
        "reporte": reporte,
        "nota": "Reconciliación parcial realizada" if not all(n["estado"] == "ONLINE" for n in reporte.values()) else "Esclavos sincronizados"
    }


def sincronizar_estados_master():
    """
    Sincroniza el catálogo ESTADO (Central) hacia las regiones de forma homogénea.
    Tolerante a fallos de red y adaptado a las columnas reales del catálogo.
    """
    reporte = {}
    
    # 1. LEER LA VERDAD ABSOLUTA DESDE EL NODO CENTRAL
    try:
        conn_central = conectar_central()
        cur_central = conn_central.cursor()
        
        cur_central.execute("SELECT id_estado, nombre FROM estado ORDER BY id_estado")
        
        estados_central = {}
        for row in cur_central.fetchall():
            id_int = int(row[0])
            estados_central[id_int] = {
                "id_estado": id_int,
                "nombre": str(row[1]).strip()
            }
            
        cur_central.close()
        conn_central.close()
    except Exception as e:
        logger.error(f"🚨 CRÍTICO: Error en el query o conectividad del Nodo Central (Estados): {e}")
        return {"success": False, "error": f"Fallo en Nodo Central: {str(e)}"}

    # Configuración de los nodos regionales
    nodos = {
        'la_paz': {'conectar': conectar_lp, 'db_type': 'postgresql'},
        'santa_cruz': {'conectar': conectar_scz, 'db_type': 'sqlserver'}
    }

    al_menos_uno_sincronizado = False

    for nombre_nodo, config in nodos.items():
        try:
            logger.info(f"🔄 Intentando conectar con el catálogo de: {nombre_nodo}...")
            conn_reg = config['conectar']()
            cur_reg = conn_reg.cursor()
            
            # Nota: En SQL Server es buena práctica poner la tabla en mayúsculas si corresponde
            tabla_regional = "estado" if config['db_type'] == 'postgresql' else "ESTADO"
            
            cur_reg.execute(f"SELECT id_estado, nombre FROM {tabla_regional}")
            
            estados_regionales = {
                int(row[0]): {
                    "id_estado": int(row[0]), 
                    "nombre": str(row[1]).strip()
                } for row in cur_reg.fetchall()
            }

            inserts, updates, deletes = 0, 0, 0

            # --- FASE 1: Altas y Modificaciones de Nombres de Estados ---
            for id_e, e_cen in estados_central.items():
                if id_e not in estados_regionales:
                    # El estado falta por completo en la región -> INSERT manual sin IDENTITY
                    if config['db_type'] == 'postgresql':
                        cur_reg.execute(f"INSERT INTO {tabla_regional} (id_estado, nombre) VALUES (%s, %s)", (id_e, e_cen['nombre']))
                    else:
                        cur_reg.execute(f"INSERT INTO {tabla_regional} (id_estado, nombre) VALUES (?, ?)", (id_e, e_cen['nombre']))
                    inserts += 1
                else:
                    # El estado existe -> Validar si cambiaron el nombre del texto (Ej: de "En tránsito" a "En Ruta Local")
                    e_reg = estados_regionales[id_e]
                    if e_cen['nombre'] != e_reg['nombre']:
                        if config['db_type'] == 'postgresql':
                            cur_reg.execute(f"UPDATE {tabla_regional} SET nombre=%s WHERE id_estado=%s", (e_cen['nombre'], id_e))
                        else:
                            cur_reg.execute(f"UPDATE {tabla_regional} SET nombre=? WHERE id_estado=?", (e_cen['nombre'], id_e))
                        updates += 1

            # --- FASE 2: Purgado / Eliminaciones ---
            for id_reg in estados_regionales.keys():
                if id_reg not in estados_central:
                    if config['db_type'] == 'postgresql':
                        cur_reg.execute(f"DELETE FROM {tabla_regional} WHERE id_estado = %s", (id_reg,))
                    else:
                        cur_reg.execute(f"DELETE FROM {tabla_regional} WHERE id_estado = ?", (id_reg,))
                    deletes += 1

            conn_reg.commit()
            cur_reg.close()
            conn_reg.close()

            reporte[nombre_nodo] = {
                "estado": "ONLINE",
                "inserciones": inserts,
                "modificaciones": updates,
                "eliminaciones": deletes
            }
            al_menos_uno_sincronizado = True
            logger.info(f"✅ Nodo {nombre_nodo} catálogo de estados sincronizado correctamente.")

        except Exception as error_nodo:
            logger.warning(f"⚠️ El nodo {nombre_nodo} está OFFLINE. Saltando Estados... Detalle: {error_nodo}")
            reporte[nombre_nodo] = {
                "estado": "OFFLINE / INACCESIBLE",
                "inserciones": 0,
                "modificaciones": 0,
                "eliminaciones": 0
            }

    return {
        "success": al_menos_uno_sincronizado, 
        "reporte": reporte,
        "nota": "Reconciliación de catálogo completada parcialmente" if not all(n["estado"] == "ONLINE" for n in reporte.values()) else "Catálogos homologados en todo el clúster"
    }