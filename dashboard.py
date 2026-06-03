from metricas import obtener_metricas
from monitor import obtener_estado_nodos
from conexiones import conectar_lp, conectar_scz, conectar_central

# -----------------------------------
# DASHBOARD
# -----------------------------------

def construir_dashboard():
    """Construye el dashboard con datos reales del sistema"""
    try:
        metricas = obtener_metricas()
        estado_nodos = obtener_estado_nodos()

        # Obtener datos de sincronización
        pendientes = 0  # placeholder si no existe contador específico

        # Obtener actividad reciente y consultas
        actividad_reciente = obtener_actividad_reciente()
        consultas_recientes = obtener_consultas_recientes()

        dashboard = {
            "metricas": {
                "nodos_sincronizados": len([n for n in estado_nodos.values() if n == 'Conectado']),
                "trafico_distribuido": 0,
                "operaciones_pendientes": pendientes,
                "fragmentos_activos": metricas.get("fragmentos", 4),
                "transacciones_2pc": 0
            },
            "coordinador": obtener_metricas_coordinador(),
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
            "coordinador": {
                "paquetes_totales": 0,
                "en_transito": 0,
                "entregadas": 0,
                "pendientes_retenidos": 0,
                "clientes_registrados": 0,
                "movimientos_dia": 0,
                "paquetes_lp": 0,
                "paquetes_scz": 0
            },
            "nodos": {},
            "estado_conectividad": [],
            "topologia": {},
            "actividad_reciente": [],
            "consultas_recientes": []
        }


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
        conn_lp = conectar_lp()
        cur_lp = conn_lp.cursor()
        cur_lp.execute("SELECT COUNT(*) FROM paquete_operativo_lp")
        paquetes_lp = cur_lp.fetchone()[0]
        cur_lp.close()
        conn_lp.close()

        topologia["nodos_regionales"].append({
            "nombre": "La Paz",
            "motor": "PostgreSQL",
            "fragmentos": ["PAQUETE_OPERATIVO_LP", "MOVIMIENTO_LP"],
            "registros": paquetes_lp
        })
    except Exception:
        pass

    try:
        conn_scz = conectar_scz()
        cur_scz = conn_scz.cursor()
        cur_scz.execute("SELECT COUNT(*) FROM PAQUETE_OPERATIVO_SCZ")
        paquetes_scz = cur_scz.fetchone()[0]
        cur_scz.close()
        conn_scz.close()

        topologia["nodos_regionales"].append({
            "nombre": "Santa Cruz",
            "motor": "SQL Server",
            "fragmentos": ["PAQUETE_OPERATIVO_SCZ", "MOVIMIENTO_SCZ"],
            "registros": paquetes_scz
        })
    except Exception:
        pass

    return topologia


def obtener_actividad_reciente():
    """Obtiene los eventos recientes del sistema distribuidos en columnas"""
    actividad = []

    try:
        conn = conectar_central()
        cur = conn.cursor()
        cur.execute("""
            SELECT TOP 5 p.codigo_rastreo, est.nombre, mg.fecha_movimiento, a.nombre
            FROM MOVIMIENTO_GLOBAL mg
            INNER JOIN PAQUETE_GLOBAL p ON mg.id_paquete = p.id_paquete
            INNER JOIN ALMACEN a ON mg.id_almacen = a.id_almacen
            INNER JOIN ESTADO est ON p.id_estado = est.id_estado
            ORDER BY mg.fecha_movimiento DESC
        """)

        for row in cur.fetchall():
            try:
                fecha = row[2].strftime('%Y-%m-%d %H:%M:%S') if row[2] else 'S/F'
            except Exception:
                fecha = str(row[2]) if row[2] else 'S/F'

            actividad.append({
                "fecha": fecha,
                "encomienda": row[0],
                "evento": row[1],
                "nodo": row[3]
            })

        cur.close()
        conn.close()
    except Exception as e:
        print("Error en obtener_actividad_reciente:", e)

    return actividad[:5]


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
    except Exception:
        consultas = [
            "SELECT * FROM PAQUETE WHERE region='SCZ'",
            "SELECT * FROM MOVIMIENTO WHERE region='LP'",
            "Reconstrucción global de CLIENTE_PUBLICO"
        ]

    return consultas


def obtener_metricas_coordinador():
    """Obtiene métricas operativas para el dashboard del coordinador"""
    result = {
        "paquetes_totales": 0,
        "en_transito": 0,
        "entregadas": 0,
        "pendientes_retenidos": 0,
        "clientes_registrados": 0,
        "movimientos_dia": 0,
        "paquetes_lp": 0,
        "paquetes_scz": 0
    }
    try:
        conn = conectar_central()
        cur = conn.cursor()

        cur.execute("""
            SELECT est.nombre, COUNT(*)
            FROM PAQUETE_GLOBAL p
            INNER JOIN ESTADO est ON p.id_estado = est.id_estado
            GROUP BY est.nombre
        """)
        estados = {row[0]: row[1] for row in cur.fetchall()}

        result["paquetes_totales"] = sum(estados.values()) if estados else 0
        result["en_transito"] = estados.get("En Tránsito", 0)
        result["entregadas"] = estados.get("Entregado", 0)
        result["pendientes_retenidos"] = estados.get("Retenido por Aduana", 0) + estados.get("Registrado", 0)

        cur.execute("SELECT COUNT(*) FROM CLIENTE_GLOBAL")
        cliente_count = cur.fetchone()[0]
        result["clientes_registrados"] = cliente_count if cliente_count is not None else 0

        cur.execute("SELECT COUNT(*) FROM MOVIMIENTO_GLOBAL WHERE CONVERT(date, fecha_movimiento) = CONVERT(date, GETDATE())")
        movimiento_count = cur.fetchone()[0]
        result["movimientos_dia"] = movimiento_count if movimiento_count is not None else 0

        cur.execute("""
            SELECT
                SUM(CASE WHEN p.codigo_rastreo LIKE 'PK-LP-%' THEN 1 ELSE 0 END),
                SUM(CASE WHEN p.codigo_rastreo LIKE 'PK-SCZ-%' THEN 1 ELSE 0 END)
            FROM PAQUETE_GLOBAL p
        """)
        row = cur.fetchone()
        if row:
            result["paquetes_lp"] = row[0] or 0
            result["paquetes_scz"] = row[1] or 0

        cur.close()
        conn.close()
    except Exception:
        pass
    return result
