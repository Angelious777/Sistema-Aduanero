from tolerancia import NODOS_ACTIVOS
from conexiones import conectar_central, conectar_lp, conectar_scz
from sincronizacion import cantidad_pendientes

# -----------------------------------
# VER ESTADO DE NODOS
# -----------------------------------

def obtener_estado_nodos():
    """Obtiene el estado de conectividad de todos los nodos"""
    estado_nodos = {}
    
    # La Paz - PostgreSQL
    try:
        conn = conectar_lp()
        conn.close()
        estado_nodos['La Paz'] = True
    except:
        estado_nodos['La Paz'] = False
    
    # Santa Cruz - SQL Server
    try:
        conn = conectar_scz()
        conn.close()
        estado_nodos['Santa Cruz'] = True
    except:
        estado_nodos['Santa Cruz'] = False
    
    # Coordinador - SQL Server
    try:
        conn = conectar_central()
        conn.close()
        estado_nodos['Coordinador'] = True
    except:
        estado_nodos['Coordinador'] = False
    
    return estado_nodos


def obtener_metricas_nodo(nodo):
    """Obtiene métricas específicas de un nodo"""
    try:
        if nodo == 'La Paz':
            conn = conectar_lp()
            cur = conn.cursor()
            
            cur.execute("SELECT COUNT(*) FROM paquete_lp")
            total_paquetes = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM movimiento_lp")
            total_movimientos = cur.fetchone()[0]
            
            cur.close()
            conn.close()
            
            return {
                'nodo': 'La Paz',
                'motor': 'PostgreSQL',
                'paquetes': total_paquetes,
                'movimientos': total_movimientos,
                'pendientes': cantidad_pendientes()
            }
        
        elif nodo == 'Santa Cruz':
            conn = conectar_scz()
            cur = conn.cursor()
            
            cur.execute("SELECT COUNT(*) FROM paquete_scz")
            total_paquetes = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM movimiento_scz")
            total_movimientos = cur.fetchone()[0]
            
            cur.close()
            conn.close()
            
            return {
                'nodo': 'Santa Cruz',
                'motor': 'SQL Server',
                'paquetes': total_paquetes,
                'movimientos': total_movimientos,
                'pendientes': cantidad_pendientes()
            }
    except Exception as e:
        print(f"Error obteniendo métricas de {nodo}:", e)
    
    return {}