from metricas import obtener_metricas, obtener_transacciones_distribuidas
from monitor import obtener_estado_nodos, obtener_metricas_nodo
from conexiones import conectar_central, conectar_lp, conectar_scz
from sincronizacion import cantidad_pendientes

# -----------------------------------
# CONSTRUIR DASHBOARD
# -----------------------------------

def construir_dashboard():
    """Construye el dashboard con datos reales del sistema"""
    try:
        metricas = obtener_metricas()
        estado_nodos = obtener_estado_nodos()
        
        # Obtener datos de sincronización
        pendientes = cantidad_pendientes()
        
        # Obtener actividad reciente
        actividad_reciente = obtener_actividad_reciente()
        
        # Obtener consultas recientes
        consultas_recientes = obtener_consultas_recientes()
        
        dashboard = {
            "metricas": {
                "nodos_sincronizados": len([n for n in estado_nodos.values() if n == 'Conectado']),
                "trafico_distribuido": obtener_trafico_distribuido(),
                "operaciones_pendientes": pendientes,
                "fragmentos_activos": metricas.get("fragmentos", 4),
                "transacciones_2pc": obtener_transacciones_distribuidas()
            },
            "nodos": estado_nodos,
            "estado_conectividad": [
                {"nombre": "Coordinador", "estado": estado_nodos.get("Coordinador", "Desconectado")},
                {"nombre": "La Paz", "estado": estado_nodos.get("La Paz", "Desconectado")},
                {"nombre": "Santa Cruz", "estado": estado_nodos.get("Santa Cruz", "Desconectado")}
            ],
            "topologia": obtener_topologia(),
            "actividad_reciente": actividad_reciente,
            "consultas_recientes": consultas_recientes
        }
        
        return dashboard
    
    except Exception as e:
        print("Error construyendo dashboard:", e)
        return {
            "metricas": {
                "nodos_sincronizados": 0,
                "trafico_distribuido": 0,
                "operaciones_pendientes": 0,
                "fragmentos_activos": 4,
                "transacciones_2pc": 0
            },
            "nodos": {},
            "estado_conectividad": [],
            "topologia": {},
            "actividad_reciente": [],
            "consultas_recientes": []
        }


def obtener_trafico_distribuido():
    """Obtiene el número de transacciones distribuidas"""
    try:
        conn = conectar_central()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT COUNT(*) FROM transacciones_2pc
        """)
        resultado = cur.fetchone()[0]
        
        cur.close()
        conn.close()
        
        return resultado
    except:
        return 0


def obtener_topologia():
    """Obtiene la topología del sistema distribuido"""
    topologia = {
        "nodos_regionales": [],
        "coordinador": {
            "nombre": "Coordinador",
            "motor": "SQL Server",
            "funciones": ["Query Parser", "Planificador", "Ensamblador"]
        }
    }
    
    try:
        # La Paz
        conn_lp = conectar_lp()
        cur_lp = conn_lp.cursor()
        cur_lp.execute("SELECT COUNT(*) FROM paquete_lp")
        paquetes_lp = cur_lp.fetchone()[0]
        cur_lp.close()
        conn_lp.close()
        
        topologia["nodos_regionales"].append({
            "nombre": "La Paz",
            "motor": "PostgreSQL",
            "fragmentos": ["PAQUETE_LP", "MOVIMIENTO_LP"],
            "registros": paquetes_lp
        })
    except:
        pass
    
    try:
        # Santa Cruz
        conn_scz = conectar_scz()
        cur_scz = conn_scz.cursor()
        cur_scz.execute("SELECT COUNT(*) FROM paquete_scz")
        paquetes_scz = cur_scz.fetchone()[0]
        cur_scz.close()
        conn_scz.close()
        
        topologia["nodos_regionales"].append({
            "nombre": "Santa Cruz",
            "motor": "SQL Server",
            "fragmentos": ["PAQUETE_SCZ", "MOVIMIENTO_SCZ"],
            "registros": paquetes_scz
        })
    except:
        pass
    
    return topologia


def obtener_actividad_reciente():
    """Obtiene los eventos recientes del sistema"""
    actividad = []
    
    try:
        # Últimos eventos de La Paz
        conn_lp = conectar_lp()
        cur_lp = conn_lp.cursor()
        
        cur_lp.execute("""
            SELECT codigo_rastreo, estado, fecha_actualizacion
            FROM paquete_lp
            ORDER BY fecha_actualizacion DESC
            LIMIT 3
        """)
        
        for row in cur_lp.fetchall():
            actividad.append(f"La Paz actualizó {row[0]} a {row[1]}")
        
        cur_lp.close()
        conn_lp.close()
    except:
        pass
    
    try:
        # Últimos eventos de Santa Cruz
        conn_scz = conectar_scz()
        cur_scz = conn_scz.cursor()
        
        cur_scz.execute("""
            SELECT TOP 3 codigo_rastreo, estado, fecha_actualizacion
            FROM paquete_scz
            ORDER BY fecha_actualizacion DESC
        """)
        
        for row in cur_scz.fetchall():
            actividad.append(f"Santa Cruz actualizó {row[0]} a {row[1]}")
        
        cur_scz.close()
        conn_scz.close()
    except:
        pass
    
    return actividad[:5]  # Retornar máximo 5 eventos


def obtener_consultas_recientes():
    """Obtiene las consultas recientes ejecutadas"""
    consultas = []
    
    try:
        conn = conectar_central()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT TOP 5 consulta, timestamp
            FROM consultas_ejecutadas
            ORDER BY timestamp DESC
        """)
        
        for row in cur.fetchall():
            consultas.append({
                "consulta": row[0],
                "timestamp": str(row[1])
            })
        
        cur.close()
        conn.close()
    except:
        # Si no existen registros, usar consultas por defecto
        consultas = [
            "SELECT * FROM PAQUETE WHERE region='SCZ'",
            "SELECT * FROM MOVIMIENTO WHERE region='LP'",
            "Reconstrucción global de CLIENTE_PUBLICO"
        ]
    
    return consultas