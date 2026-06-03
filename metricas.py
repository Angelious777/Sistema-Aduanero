# -*- coding: utf-8 -*-
"""
metricas.py - Motor Analítico Distribuidor de Rampas Regionales
Captura contadores transaccionales e historial de logs directamente por nodo.
"""
from conexiones import conectar_central, conectar_lp, conectar_scz
import logging
import datetime  # Importación limpia para usar con isinstance

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Analitica_Nodos")

# ==============================================================================
# FUNCION 1: Métricas Globales del Clúster (Mantiene tu lógica previa)
# ==============================================================================
def obtener_metricas():
    """Obtiene métricas generales del estado del sistema distribuido"""
    try:
        metricas = {
            "pendientes": 0,
            "nodos_activos": 0,
            "fragmentos": 0,
            "motor_lp": "PostgreSQL",
            "motor_scz": "SQL Server"
        }
        
        # Contar nodos activos probando conexiones rápidas
        nodos_conectados = 0
        try:
            conectar_lp().close()
            nodos_conectados += 1
        except: pass
        
        try:
            conectar_scz().close()
            nodos_conectados += 1
        except: pass
        
        try:
            conectar_central().close()
            nodos_conectados += 1
        except: pass
        
        metricas["nodos_activos"] = nodos_conectados
        
        # Contar fragmentos desde el catálogo de la central
        try:
            conn = conectar_central()
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM catalogo_fragmentos")
            metricas["fragmentos"] = cur.fetchone()[0]
            cur.close()
            conn.close()
        except:
            metricas["fragmentos"] = 4  # Valor de contingencia por defecto
        
        return metricas
    except Exception as e:
        logger.error(f"Error obteniendo métricas globales: {e}")
        return {"pendientes": 0, "nodos_activos": 0, "fragmentos": 4, "motor_lp": "PostgreSQL", "motor_scz": "SQL Server"}


# ==============================================================================
# FUNCION 2: Transacciones Activas 2PC (Mantiene tu lógica previa)
# ==============================================================================
def obtener_transacciones_distribuidas():
    """Obtiene el número de transacciones distribuidas activas en el Coordinador"""
    try:
        conn = conectar_central()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM transacciones_2pc WHERE estado='activa'")
        resultado = cur.fetchone()[0]
        cur.close()
        conn.close()
        return resultado
    except:
        return 0


# ==============================================================================
# FUNCION 3: Métricas Específicas por Nodo (LA QUE USA TU DASHBOARD DE RAMPA)
# ==============================================================================
def obtener_metricas_nodo(nombre_nodo):
    """
    Se conecta al fragmento regional indicado y extrae de forma atómica 
    las métricas de las tarjetas y los registros de la bitácora local.
    """
    if not nombre_nodo:
        return {"success": False, "error": "El nombre del nodo no fue proporcionado."}

    nodo_limpio = str(nombre_nodo).lower().strip().replace('-', '_')
    
    # 1. Configurar mapeos dinámicos según el motor de base de datos
    if nodo_limpio in ['la_paz', 'nodo_lp', 'lp']:
        conector = conectar_lp
        db_type = 'postgresql'
        config_mapeo = {
            "tabla_paquetes": "paquete_operativo_lp",
            "tabla_movimientos": "movimiento_lp",
            "tabla_almacenes": "almacen",
            "tabla_clientes": "cliente_publico",
            "col_fecha": "fecha_movimiento",
            "col_observacion": "observacion",
            "metadata": {"id": "LA_PAZ", "nombre": "Sede Regional La Paz", "motor": "PostgreSQL"}
        }
    elif nodo_limpio in ['santa_cruz', 'nodo_scz', 'scz']:
        conector = conectar_scz
        db_type = 'sqlserver'
        config_mapeo = {
            "tabla_paquetes": "PAQUETE_OPERATIVO_SCZ",
            "tabla_movimientos": "MOVIMIENTO_SCZ",
            "tabla_almacenes": "almacen",
            "tabla_clientes": "CLIENTE_PUBLICO",
            "col_fecha": "fecha_movimiento",
            "col_observacion": "observacion",
            "metadata": {"id": "SANTA_CRUZ", "nombre": "Sede Regional Santa Cruz", "motor": "SQL Server (ODBC)"}
        }
    else:
        logger.error(f"❌ El nodo '{nombre_nodo}' no está mapeado en la infraestructura.")
        return {"success": False, "error": f"El nodo '{nombre_nodo}' no existe en el clúster."}

    # 2. Extracción analítica estructurada
    try:
        meta = config_mapeo["metadata"]
        
        conn = conector()
        cur = conn.cursor()

        # Consulta A: Paquetes Totales
        cur.execute(f"SELECT COUNT(*) FROM {config_mapeo['tabla_paquetes']}")
        total_paquetes = cur.fetchone()[0]

        # Consulta B: Movimientos Hoy
        if db_type == 'postgresql':
            cur.execute(f"SELECT COUNT(*) FROM {config_mapeo['tabla_movimientos']} WHERE {config_mapeo['col_fecha']}::date = CURRENT_DATE")
        else:
            cur.execute(f"SELECT COUNT(*) FROM {config_mapeo['tabla_movimientos']} WHERE CAST({config_mapeo['col_fecha']} AS DATE) = CAST(GETDATE() AS DATE)")
        total_movimientos_hoy = cur.fetchone()[0]

        # Consulta C: Clientes Replicados
        cur.execute(f"SELECT COUNT(*) FROM {config_mapeo['tabla_clientes']}")
        total_clientes = cur.fetchone()[0]

        # Consulta D: Almacenes
        cur.execute(f"SELECT COUNT(*) FROM {config_mapeo['tabla_almacenes']}")
        total_almacenes = cur.fetchone()[0]

        # Consulta E: Bitácora de Actividad Reciente (TOP 15 / LIMIT 15)
        if db_type == 'sqlserver':
            query_bitacora = f"""
                SELECT TOP 15
                    m.{config_mapeo['col_fecha']}, p.codigo_rastreo, m.{config_mapeo['col_observacion']}, a.nombre 
                FROM {config_mapeo['tabla_movimientos']} m
                INNER JOIN {config_mapeo['tabla_paquetes']} p ON m.id_paquete = p.id_paquete
                INNER JOIN {config_mapeo['tabla_almacenes']} a ON m.id_almacen = a.id_almacen
                ORDER BY m.{config_mapeo['col_fecha']} DESC
            """
        else:
            query_bitacora = f"""
                SELECT 
                    m.{config_mapeo['col_fecha']}, p.codigo_rastreo, m.{config_mapeo['col_observacion']}, a.nombre 
                FROM {config_mapeo['tabla_movimientos']} m
                INNER JOIN {config_mapeo['tabla_paquetes']} p ON m.id_paquete = p.id_paquete
                INNER JOIN {config_mapeo['tabla_almacenes']} a ON m.id_almacen = a.id_almacen
                ORDER BY m.{config_mapeo['col_fecha']} DESC
                LIMIT 15
            """
            
        cur.execute(query_bitacora)
        
        bitacora = []
        for row in cur.fetchall():
            fecha_cruda = row[0]
            
            if fecha_cruda is None:
                fecha_final = "—"
            elif isinstance(fecha_cruda, datetime.datetime):
                fecha_final = fecha_cruda.strftime('%Y-%m-%d %H:%M:%S')
            else:
                fecha_final = str(fecha_cruda)[:19]

            bitacora.append({
                "fecha": fecha_final,
                "paquete": row[1],
                "evento": row[2] if row[2] else 'Movimiento Operativo',
                "almacen": row[3]
            })

        cur.close()
        conn.close()

        return {
            "success": True,
            "config": {
                "id": meta["id"],
                "nombre": meta["nombre"],
                "motor": meta["motor"],
                "tabla_paquetes": config_mapeo["tabla_paquetes"]
            },
            "paquetes_count": total_paquetes,
            "movimientos_count": total_movimientos_hoy,
            "clientes_count": total_clientes,
            "almacenes_count": total_almacenes,
            "movimientos": bitacora
        }

    except Exception as e:
        logger.error(f"🚨 Fallo analítico en el nodo {nombre_nodo}. Detalle: {str(e)}")
        # CORRECCIÓN DE RETORNO: Forzamos a retornar el error explícito en el JSON
        return {"success": False, "error": f"Fallo en nodo {nombre_nodo}: {str(e)}"}