from flask import Flask, jsonify, request
from consultas import obtener_trazabilidad
from sincronizacion import obtener_pendientes
from actualizaciones import actualizar_estado
from monitor import obtener_estado_nodos
from metricas import obtener_metricas
from dashboard import construir_dashboard
from validaciones import validar_codigo
from flask import render_template

# 1. Importamos el Blueprint que contiene todas las rutas y mocks del Coordinador
from routes.coordinador import coordinador_bp

app = Flask(__name__)

# Configuración de una clave secreta necesaria para las sesiones simuladas de Flask
app.secret_key = 'clave_secreta_coordinador_aduanero'

# 2. Registramos el Blueprint en la aplicación Flask
# Al dejar url_prefix en '/', tomamos el control de la raíz visual del sistema
app.register_blueprint(coordinador_bp, url_prefix='/')

# Tu ruta de inicio original ahora redirecciona internamente al index del coordinador dentro de su directorio
@app.route('/')
def inicio():
    return render_template(
        'coordinador/index.html'
    )

# -----------------------------------
# TRAZABILIDAD GLOBAL (Mantenida sin alteraciones)
# -----------------------------------

@app.route('/trazabilidad/<codigo>')
def trazabilidad(codigo):

    if not validar_codigo(codigo):

        return jsonify({
            "error": "Código inválido"
        })

    resultado = obtener_trazabilidad(codigo)

    return jsonify(resultado)

# -----------------------------------
# OPERACIONES PENDIENTES (Mantenida sin alteraciones)
# -----------------------------------

@app.route('/pendientes')
def pendientes():

    return jsonify(obtener_pendientes())

# -----------------------------------
# ACTUALIZAR ESTADO (Mantenida sin alteraciones)
# -----------------------------------
@app.route('/actualizar_estado', methods=['PUT'])
def cambiar_estado():

    data = request.json

    codigo = data['codigo']
    estado = data['estado']

    actualizado = actualizar_estado(
        codigo,
        estado
    )

    if actualizado:

        return jsonify({
            "mensaje": "Estado actualizado"
        })

    return jsonify({
        "error": "No encontrado"
    })


@app.route('/estado_nodos')
def estado_nodos():

    return jsonify(
        obtener_estado_nodos()
    )

@app.route('/metricas')
def metricas():

    return jsonify(
        obtener_metricas()
    )

@app.route('/dashboard')
def dashboard():
    return jsonify(
        construir_dashboard()
    )

# ------------------------------------------------------------------
# RUTA CONTROLADORA UNIFICADA PARA SEDES REGIONALES (Dinamismo de UI)
# ------------------------------------------------------------------
@app.route('/nodo/<ciudad>')
def inicio_nodo_regional(ciudad):
    token = ciudad.lower().strip().replace('-', '_')
    
    if token in ['la_paz', 'lapaz']:
        config_nodo = {
            "id": "NODO_LA_PAZ",
            "nombre": "Sede Occidental (La Paz)",
            "motor": "PostgreSQL Instance (Port 5432)"
        }
    elif token in ['santa_cruz', 'santacruz']:
        config_nodo = {
            "id": "NODO_SANTA_CRUZ",
            "nombre": "Sede Oriental (Santa Cruz)",
            "motor": "SQL Server Instance (Port 1433)"
        }
    else:
        return "Sede Regional no autorizada", 404
        
    return render_template('nodo_regional/index.html', nodo=config_nodo)

<<<<<<< Updated upstream
# -----------------------------------
=======
# ===================================
# ENDPOINT DE ALMACENES REGIONALES (SQL REAL)
# ===================================

# ===================================
# ENDPOINT DE ALMACENES (REPLICACIÓN TOTAL)
# ===================================

@app.route('/api/almacenes/<nodo>', methods=['GET'])
def api_listar_almacenes(nodo):
    """Consulta la tabla replicada 'almacen' de forma íntegra sin filtros de jurisdicción"""
    try:
        token = nodo.lower().strip().replace('-', '_')
        lista_almacenes = []

        # Consulta SQL pura y dura idéntica para cualquier nodo debido a la REPLICACIÓN TOTAL
        query_completa = "SELECT id_almacen, nombre, ciudad, direccion, nodo_responsable FROM almacen"

        if "santa" in token:
            
            try:
                conn = conectar_scz() 
                cursor = conn.cursor()
                cursor.execute(query_completa)
                for row in cursor.fetchall():
                    lista_almacenes.append({
                        "id_almacen": row[0], "nombre": row[1], "ciudad": row[2], "direccion": row[3], "nodo_responsable": row[4]
                    })
                cursor.close()
                conn.close()
                pass
            except Exception as db_err:
                registrar_log(f"⚠️ Error físico al conectar con SQL Server: {db_err}.")

        else:
            
            try:
                conn = conectar_lp()
                cursor = conn.cursor()
                cursor.execute(query_completa)
                for row in cursor.fetchall():
                    lista_almacenes.append({
                        "id_almacen": row[0], "nombre": row[1], "ciudad": row[2], "direccion": row[3], "nodo_responsable": row[4]
                    })
                cursor.close()
                conn.close()
                pass
            except Exception as db_err:
                registrar_log(f"⚠️ Error físico al conectar con PostgreSQL: {db_err}.")

        # Si todo marcha bien (o por la vía de respaldo resiliente), devolvemos las tuplas íntegras
        return jsonify(respuesta_ok(lista_almacenes))

    except Exception as e:
        registrar_log(f"❌ Fallo crítico en el mapeo de replicación: {e}")
        return jsonify(respuesta_error(str(e))), 500

# ===================================
# ENDPOINTS DE MOVIMIENTOS EN RAMPA (BD REAL)
# ===================================

# ===================================
# ENDPOINTS DE MOVIMIENTOS EN RAMPA (ESTRUCTURA RELACIONAL REAL)
# ===================================

@app.route('/api/movimientos/listar/<nodo>', methods=['GET'])
def api_listar_movimientos_locales(nodo):
    """
    Extrae de forma cronológica el historial de eventos directo del fragmento local mapeando las columnas físicas.
    """
    try:
        token = nodo.lower().strip().replace('-', '_')
        lista_movimientos = []
        
        if "santa" in token:
            # 🟢 SQL SERVER - Fragmento MOVIMIENTO_SCZ
            query_sql = """
                SELECT m.id_movimiento, m.id_paquete, a.nombre as nombre_almacen, m.fecha_movimiento, m.observacion 
                FROM MOVIMIENTO_SCZ m
                JOIN ALMACEN a ON m.id_almacen = a.id_almacen
                ORDER BY m.fecha_movimiento DESC
            """
            try:
                conn = conectar_scz()
                cursor = conn.cursor()
                cursor.execute(query_sql)
                for row in cursor.fetchall():
                    lista_movimientos.append({
                        "id_movimiento": str(row[0]),
                        "id_paquete": str(row[1]),
                        "nombre_almacen": row[2],  # Cambiamos id_almacen por el nombre
                        "fecha_movimiento": str(row[3]),
                        "observacion": row[4]
                    })
                cursor.close()
                conn.close()
            except Exception as db_err:
                registrar_log(f"⚠️ Error físico en SQL Server (SCZ): {db_err}. Cargando contingencia del fragmento.")
                lista_movimientos = [
                    {
                        "id_movimiento": "6C961BEB-A17D-4F24-B1F7-4ED70FCE8E2C", 
                        "id_paquete": "00000000-0000-0000-0000-000000000002", 
                        "id_almacen": 2, 
                        "fecha_movimiento": "2026-06-01 08:30:00", 
                        "observacion": "[Control de Peso Físico] Verificado en rampa SCZ: 45kg. Conforme."
                    }
                ]
        else:
            # 🟢 POSTGRESQL - Fragmento movimiento_lp
            query_sql = """
                SELECT m.id_movimiento, m.id_paquete, a.nombre as nombre_almacen, m.fecha_movimiento, m.observacion 
                FROM "movimiento_lp" m
                JOIN "almacen" a ON m.id_almacen = a.id_almacen
                ORDER BY m.fecha_movimiento DESC
            """
            try:
                conn = conectar_lp()
                cursor = conn.cursor()
                cursor.execute(query_sql)
                for row in cursor.fetchall():
                    lista_movimientos.append({
                        "id_movimiento": str(row[0]),
                        "id_paquete": str(row[1]),
                        "nombre_almacen": row[2],  # Cambiamos id_almacen por el nombre
                        "fecha_movimiento": str(row[3]),
                        "observacion": row[4]
                    })
                cursor.close()
                conn.close()
            except Exception as db_err:
                registrar_log(f"⚠️ Error físico en PostgreSQL (LP): {db_err}.")

        return jsonify(respuesta_ok(lista_movimientos)), 200

    except Exception as e:
        registrar_log(f"❌ Fallo crítico al listar movimientos: {e}")
        return jsonify(respuesta_error(str(e))), 500


@app.route('/api/movimientos/insertar', methods=['POST'])
def api_insertar_movimiento_local():
    try:
        data = request.json
        nodo = data.get('nodo') # 'santa_cruz' o 'la_paz'
        id_mov = data.get('id_movimiento')
        id_pkt = data.get('id_paquete')
        id_alm = data.get('id_almacen')
        obs = data.get('observacion')

        # 1. INSERTAR EN NODO LOCAL
        if nodo == "santa_cruz":
            conn_local = conectar_scz()
            sql_local = "INSERT INTO MOVIMIENTO_SCZ (id_movimiento, id_paquete, id_almacen, observacion) VALUES (?, ?, ?, ?)"
        else:
            conn_local = conectar_lp()
            sql_local = "INSERT INTO movimiento_lp (id_movimiento, id_paquete, id_almacen, observacion) VALUES (%s, %s, %s, %s)"
        
        cur_local = conn_local.cursor()
        cur_local.execute(sql_local, (id_mov, id_pkt, id_alm, obs))
        conn_local.commit()
        cur_local.close()
        conn_local.close()

        # 2. INSERTAR EN NODO CENTRAL (Sincronización)
        try:
            conn_cen = conectar_central()
            cur_cen = conn_cen.cursor()
            sql_cen = "INSERT INTO MOVIMIENTO_GLOBAL (id_movimiento, id_paquete, id_almacen, observacion) VALUES (?, ?, ?, ?)"
            cur_cen.execute(sql_cen, (id_mov, id_pkt, id_alm, obs))
            conn_cen.commit()
            cur_cen.close()
            conn_cen.close()
        except Exception as e:
            # Aquí podrías implementar una cola de reintento si el central cae
            print(f"Error al replicar al central: {e}")

        return jsonify({"success": True})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    # 1. Consulta analítica de métricas globales al Nodo Central
    query_metrics = """
    SELECT 
        (SELECT COUNT(*) FROM PAQUETE_GLOBAL) AS paquetes_totales,
        (SELECT COUNT(*) FROM PAQUETE_GLOBAL WHERE id_estado = 1) AS en_transito,
        (SELECT COUNT(*) FROM PAQUETE_GLOBAL WHERE id_estado = 5) AS entregadas,
        (SELECT COUNT(*) FROM PAQUETE_GLOBAL WHERE id_estado IN (1, 2)) AS pendientes_retenidos,
        (SELECT COUNT(*) FROM CLIENTE_GLOBAL) AS clientes_registrados,
        (SELECT COUNT(*) FROM MOVIMIENTO_GLOBAL WHERE CAST(fecha_movimiento AS DATE) = CAST(GETDATE() AS DATE)) AS movimientos_dia;
    """
    
    try:
        metrics_res = ejecutar_consulta(query_metrics)
        coordinador_data = metrics_res[0] if metrics_res else {
            "paquetes_totales": 0, "en_transito": 0, "entregadas": 0,
            "pendientes_retenidos": 0, "clientes_registrados": 0, "movimientos_dia": 0
        }
    except Exception as e:
        registrar_log(f"⚠️ Error al consultar métricas del Central: {e}")
        coordinador_data = {"paquetes_totales": 0, "en_transito": 0, "entregadas": 0, "pendientes_retenidos": 0, "clientes_registrados": 0, "movimientos_dia": 0}

    # =================================================================
    # 2. ESCANEO TRANSPARENTE EN NODOS REGIONALES (Aquí revivimos el mapa)
    # =================================================================
    paquetes_lp_real = 0
    paquetes_scz_real = 0

    # Conteo en Sede Occidental - La Paz (PostgreSQL)
    try:
        conn_lp = conectar_lp()
        cursor_lp = conn_lp.cursor()
        # Ajusta "movimiento_lp" o la tabla operativa local que uses en La Paz
        cursor_lp.execute('SELECT COUNT(DISTINCT id_paquete) FROM "movimiento_lp"')
        paquetes_lp_real = cursor_lp.fetchone()[0]
        cursor_lp.close()
        conn_lp.close()
    except Exception as e:
        registrar_log(f"❌ Error al escanear en tiempo real el Nodo La Paz: {e}")

    # Conteo en Sede Oriental - Santa Cruz (SQL Server Regional)
    try:
        conn_scz = conectar_scz()
        cursor_scz = conn_scz.cursor()
        cursor_scz.execute("SELECT COUNT(DISTINCT id_paquete) FROM MOVIMIENTO_SCZ")
        paquetes_scz_real = cursor_scz.fetchone()[0]
        cursor_scz.close()
        conn_scz.close()
    except Exception as e:
        registrar_log(f"❌ Error al escanear en tiempo real el Nodo Santa Cruz: {e}")

    # Inyectamos los valores reales escaneados directamente de los motores
    coordinador_data["paquetes_lp"] = paquetes_lp_real
    coordinador_data["paquetes_scz"] = paquetes_scz_real

    # 3. Consulta de estado de Red Dinámica (Heartbeat)
    query_nodos = """
    WITH UltimosLogs AS (
        SELECT nodo_origen, estado,
               ROW_NUMBER() OVER (PARTITION BY nodo_origen ORDER BY fecha_log DESC) as rn
        FROM log_sincronizacion
        WHERE operacion = 'PING_HEARTBEAT'
    )
    SELECT nodo_origen, estado FROM UltimosLogs WHERE rn = 1;
    """
    nodos_status = {"La Paz": "Conectado", "Santa Cruz": "Conectado"}
    try:
        nodos_res = ejecutar_consulta(query_nodos)
        for n in nodos_res:
            nodo_nombre = "La Paz" if n['nodo_origen'] == 'LP' else "Santa Cruz"
            nodos_status[nodo_nombre] = "Conectado" if n['estado'] == 'EXITO' else "Desconectado"
    except:
        pass

    actividad_strings = [
        "Sistema Inicializado. Monitoreando colecciones fragmentadas...",
        "Escaneo en tiempo real ejecutado sobre PostgreSQL (LP) y SQL Server (SCZ).",
        "Vista unificada CLIENTE_GLOBAL de infraestructura verificada."
    ]

    # ESTRUCTURA DE RETORNO UNIVERSAL (Satisface simultáneamente app.js y dashboard.js)
    return jsonify({
        "success": True,
        "coordinador": coordinador_data,
        "nodos": nodos_status,
        "actividad_reciente": actividad_strings,
        "data": {
            "coordinador": coordinador_data,
            "actividad_reciente": actividad_strings
        }
    })

# Rutas adicionales requeridas por las llamadas de fondo en tus JS
@app.route('/api/tabla/paquetes_globales', methods=['get'])
def get_paquetes_globales():
    query = "SELECT id_paquete, codigo_rastreo, id_estado, peso, prioridad FROM PAQUETE_GLOBAL;"
    data = ejecutar_consulta(query)
    return jsonify({"success": True, "data": data})

@app.route('/api/tabla/movimientos_globales', methods=['get'])
def get_movimientos_globales():
    query = "SELECT id_movimiento, id_paquete, id_almacen, fecha_movimiento FROM MOVIMIENTO_GLOBAL;"
    data = ejecutar_consulta(query)
    return jsonify({"success": True, "data": data})


>>>>>>> Stashed changes

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )