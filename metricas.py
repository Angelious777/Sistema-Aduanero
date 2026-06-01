from sincronizacion import cantidad_pendientes
from conexiones import conectar_central, conectar_lp, conectar_scz

# -----------------------------------
# METRICAS GENERALES
# -----------------------------------

def obtener_metricas():
    """Obtiene métricas del sistema distribuido"""
    try:
        metricas = {
            "pendientes": cantidad_pendientes(),
            "nodos_activos": 0,
            "fragmentos": 0,
            "motor_lp": "PostgreSQL",
            "motor_scz": "SQL Server"
        }
        
        # Contar nodos activos
        nodos_conectados = 0
        try:
            conectar_lp()
            nodos_conectados += 1
        except:
            pass
        
        try:
            conectar_scz()
            nodos_conectados += 1
        except:
            pass
        
        try:
            conectar_central()
            nodos_conectados += 1
        except:
            pass
        
        metricas["nodos_activos"] = nodos_conectados
        
        # Contar fragmentos
        try:
            conn = conectar_central()
            cur = conn.cursor()
            
            cur.execute("SELECT COUNT(*) FROM catalogo_fragmentos")
            metricas["fragmentos"] = cur.fetchone()[0]
            
            cur.close()
            conn.close()
        except:
            metricas["fragmentos"] = 4  # Valor por defecto
        
        return metricas
    
    except Exception as e:
        print("Error obteniendo métricas:", e)
        return {
            "pendientes": cantidad_pendientes(),
            "nodos_activos": 0,
            "fragmentos": 4,
            "motor_lp": "PostgreSQL",
            "motor_scz": "SQL Server"
        }


def obtener_transacciones_distribuidas():
    """Obtiene el número de transacciones distribuidas activas"""
    try:
        conn = conectar_central()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT COUNT(*) FROM transacciones_2pc 
            WHERE estado='activa'
        """)
        resultado = cur.fetchone()[0]
        
        cur.close()
        conn.close()
        
        return resultado
    except:
        return 0