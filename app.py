from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from consultas import obtener_trazabilidad
from sincronizacion import obtener_pendientes, guardar_operacion
from actualizaciones import actualizar_estado
from monitor import obtener_estado_nodos, obtener_metricas_nodo
from metricas import obtener_metricas
from dashboard import construir_dashboard
from validaciones import validar_codigo
from paquetes import obtener_todos_paquetes, obtener_paquetes_por_nodo, crear_paquete, obtener_tabla_paquete, obtener_tabla_movimiento, obtener_tabla_paquete_financiero, buscar_paquete
from paquetes import obtener_paquetes_por_tipo_nodo
from clientes import obtener_clientes_global, registrar_cliente_nodo  # <-- Asegúrate de tener o mapear esta función
from movimientos import registrar_movimiento, obtener_movimientos_paquete, obtener_todos_movimientos, actualizar_estado_movimiento, obtener_historial_completo
from catalogo import obtener_fragmentos
from respuestas import respuesta_ok, respuesta_error
from logs.logger import registrar_log
from conexiones import conectar_lp, conectar_scz, conectar_central

def respuesta_ok(data): return {"success": True, "data": data}
def respuesta_error(msg): return {"success": False, "error": msg}
def registrar_log(msg): print(f"[LOG SYSTEM]: {msg}")


# 1. Importamos el Blueprint que contiene todas las rutas y mocks del Coordinador
from routes.coordinador import coordinador_bp

app = Flask(__name__)
CORS(app)

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

# ===================================
# ENDPOINTS DEL DASHBOARD
# ===================================

@app.route('/api/dashboard')
def api_dashboard():
    """Obtiene datos completos del dashboard"""
    try:
        dashboard = construir_dashboard()
        return jsonify(respuesta_ok(dashboard))
    except Exception as e:
        registrar_log(f"Error en dashboard: {e}")
        return jsonify(respuesta_error(str(e))), 500


@app.route('/api/metricas')
def api_metricas():
    """Obtiene las métricas del sistema"""
    try:
        metricas = obtener_metricas()
        return jsonify(respuesta_ok(metricas))
    except Exception as e:
        return jsonify(respuesta_error(str(e))), 500


@app.route('/api/estado_nodos')
def api_estado_nodos():
    """Obtiene el estado de todos los nodos"""
    try:
        estado = obtener_estado_nodos()
        return jsonify(respuesta_ok(estado))
    except Exception as e:
        return jsonify(respuesta_error(str(e))), 500


@app.route('/api/metricas_nodo/<nodo>')
def api_metricas_nodo(nodo):
    """Obtiene métricas específicas de un nodo"""
    try:
        metricas = obtener_metricas_nodo(nodo)
        if not metricas:
            return jsonify(respuesta_error("Nodo no encontrado")), 404
        return jsonify(respuesta_ok(metricas))
    except Exception as e:
        return jsonify(respuesta_error(str(e))), 500


# ===================================
# ENDPOINTS DE PAQUETES
# ===================================

@app.route('/api/paquetes')
def api_paquetes():
    """Obtiene todos los paquetes del sistema"""
    try:
        paquetes = obtener_todos_paquetes()
        return jsonify(respuesta_ok(paquetes))
    except Exception as e:
        return jsonify(respuesta_error(str(e))), 500


@app.route('/api/paquetes/<nodo>')
def api_paquetes_nodo(nodo):
    """Obtiene paquetes de un nodo específico"""
    try:
        paquetes = obtener_paquetes_por_nodo(nodo)
        return jsonify(respuesta_ok(paquetes))
    except Exception as e:
        return jsonify(respuesta_error(str(e))), 500


@app.route('/api/clientes', methods=['GET'])
def api_listar_clientes():
    try:
        data = obtener_clientes_global()
        return jsonify(respuesta_ok(data))
    except Exception as e:
        return jsonify(respuesta_error(str(e))), 500


@app.route('/api/paquete/buscar/<codigo>')
def api_buscar_paquete(codigo):
    """Busca un paquete por código"""
    try:
        if not validar_codigo(codigo):
            return jsonify(respuesta_error("Código de paquete inválido")), 400
        
        paquete = buscar_paquete(codigo)
        if not paquete:
            return jsonify(respuesta_error("Paquete no encontrado")), 404
        
        return jsonify(respuesta_ok(paquete))
    except Exception as e:
        return jsonify(respuesta_error(str(e))), 500


@app.route('/api/tabla/paquete/<nodo>')
def api_tabla_paquete(nodo):
    """Obtiene la tabla completa de paquetes de un nodo"""
    try:
        datos = obtener_tabla_paquete(nodo)
        return jsonify(respuesta_ok(datos))
    except Exception as e:
        return jsonify(respuesta_error(str(e))), 500


@app.route('/api/tabla/movimiento/<nodo>')
def api_tabla_movimiento(nodo):
    """Obtiene la tabla completa de movimientos de un nodo"""
    try:
        datos = obtener_tabla_movimiento(nodo)
        return jsonify(respuesta_ok(datos))
    except Exception as e:
        return jsonify(respuesta_error(str(e))), 500


@app.route('/api/tabla/paquete_operativo/<nodo>')
def api_tabla_paquete_operativo(nodo):
    """Obtiene la tabla operativa de paquetes (SCZ)"""
    try:
        datos = obtener_tabla_paquete(nodo)
        return jsonify(respuesta_ok(datos))
    except Exception as e:
        return jsonify(respuesta_error(str(e))), 500


@app.route('/api/tabla/paquete_financiero/<nodo>')
def api_tabla_paquete_financiero(nodo):
    """Obtiene la tabla financiera de paquetes (SCZ)"""
    try:
        datos = obtener_tabla_paquete_financiero(nodo)
        return jsonify(respuesta_ok(datos))
    except Exception as e:
        return jsonify(respuesta_error(str(e))), 500


@app.route('/api/paquetes/por-tipo/<nodo>')
def api_paquetes_por_tipo(nodo):
    """Obtiene paquetes operativos y financieros de un nodo específico"""
    try:
        datos = obtener_paquetes_por_tipo_nodo(nodo)
        return jsonify(respuesta_ok(datos))
    except Exception as e:
        registrar_log(f"Error obteniendo paquetes por tipo del nodo {nodo}: {e}")
        return jsonify(respuesta_error(str(e))), 500


@app.route('/api/paquete/crear', methods=['POST']) 
def api_crear_paquete():
    data = request.json or {}
    
    # Parámetros Base e Identificadores Relacionales
    codigo = data.get('codigo')
    destino = data.get('id_ruta')       # ID numérico real (1 o 2) de la ruta
    prioridad = data.get('prioridad')
    nodo = data.get('nodo')
    remitente = data.get('remitente')   # El UUID del cliente seleccionado
    descripcion = data.get('descripcion', '').strip()

    # Nuevos Parámetros Métricos de Carga
    # Nota: Se define 1.0 como fallback para evitar divisiones o restricciones de nulos en el motor operativo
    peso = data.get('peso')
    volumen = data.get('volumen')
    
    # Nuevos Parámetros Financieros / Aduaneros
    valor_declarado = data.get('valor_declarado')
    seguro = data.get('seguro')
    costo_envio = data.get('costo')     # Mapeado desde 'costo' en tu payload de JS

    # Conversión y Sanitización de Tipos antes de enviar a paquetes.py
    try:
        peso_conv = float(peso) if peso is not None else 1.0
        volumen_conv = float(volumen) if volumen is not None else 1.0
        valor_conv = float(valor_declarado) if valor_declarado is not None else 0.0
        seguro_conv = float(seguro) if seguro is not None else 0.0
        costo_conv = float(costo_envio) if costo_envio is not None else 0.0
    except (ValueError, TypeError) as err:
        return jsonify({
            "success": False, 
            "error": f"Error de casteo en campos numéricos (Métricas/Finanzas): {str(err)}"
        }), 400

    # Invocación con la firma extendida de paquetes.py
    exito = crear_paquete(
        codigo=codigo,
        destino=destino,
        prioridad=prioridad,
        nodo=nodo,
        remitente=remitente,
        descripcion=descripcion,
        peso=peso_conv,
        volumen=volumen_conv,
        valor_declarado=valor_conv,
        seguro=seguro_conv,
        costo_envio=costo_conv
    )
    
    if exito:
        return jsonify({
            "success": True, 
            "data": {"mensaje": "Paquete registrado exitosamente en el clúster (Operativo/Financiero)"}
        }), 200
    else:
        return jsonify({
            "success": False, 
            "error": "Error interno o desalineación relacional en el motor distribuido de base de datos"
        }), 500


# ===================================
# ENDPOINTS DE NUEVOS CLIENTES (DISTRIBUIDO)
# ===================================

@app.route('/api/cliente/crear', methods=['POST'])
def api_crear_cliente():
    try:
        data = request.json or {}
        
        # Extracción adaptada a los formatos de las tablas
        documento = data.get('documento_identidad')
        nombre = data.get('nombre')
        apellido_paterno = data.get('apellido_paterno')
        apellido_materno = data.get('apellido_materno')
        telefono = data.get('telefono')
        direccion = data.get('direccion')
        email = data.get('email')
        nodo_destino = data.get('nodo') # Viene directamente 'nodo_lp' o 'nodo_scz'

        if not documento or not nombre or not apellido_paterno or not nodo_destino:
            return jsonify({"success": False, "error": "Campos con restricción SQL NOT NULL incompletos"}), 400

        # Ejecutamos la función de inserción cruzada en clientes.py
        exito = registrar_cliente_nodo(
            nit_ci=documento,
            nombre=nombre,
            apellido_paterno=apellido_paterno,
            apellido_materno=apellido_materno,
            telefono=telefono,
            direccion=direccion,
            email=email,
            nodo_destino=nodo_destino
        )
        
        if exito:
            return jsonify({"success": True, "data": {"mensaje": f"INSERT exitoso en {nodo_destino} y sincronizado a nodo_central"}}), 200
        else:
            return jsonify({"success": False, "error": "Error interno al efectuar la transacción distributed"}), 500
            
    except Exception as e:
        return jsonify({"success": False, "error": f"Fallo crítico en el motor: {str(e)}"}), 500


# ===================================
# ENDPOINTS DE MOVIMIENTOS
# ===================================

@app.route('/api/movimientos/<nodo>')
def api_movimientos_nodo(nodo):
    """Obtiene todos los movimientos de un nodo"""
    try:
        movimientos = obtener_todos_movimientos(nodo)
        return jsonify(respuesta_ok(movimientos))
    except Exception as e:
        return jsonify(respuesta_error(str(e))), 500


@app.route('/api/movimientos/paquete/<codigo>/<nodo>')
def api_movimientos_paquete(codigo, nodo):
    """Obtiene movimientos asociados a un paquete"""
    try:
        movimientos = obtener_movimientos_paquete(codigo, nodo)
        return jsonify(respuesta_ok(movimientos))
    except Exception as e:
        return jsonify(respuesta_error(str(e))), 500


@app.route('/api/movimiento/registrar', methods=['POST'])
def api_registrar_movimiento():
    """Registra un nuevo movimiento"""
    try:
        data = request.json
        id_movimiento = data.get('id_movimiento')
        id_paquete = data.get('id_paquete')
        ubicacion = data.get('ubicacion')
        estado = data.get('estado')
        nodo = data.get('nodo')
        
        if not all([id_movimiento, id_paquete, ubicacion, estado, nodo]):
            return jsonify(respuesta_error("Parámetros requeridos incompletos")), 400
        
        exito = registrar_movimiento(id_movimiento, id_paquete, ubicacion, estado, nodo)
        if exito:
            return jsonify(respuesta_ok({"mensaje": "Movimiento registrado exitosamente"}))
        else:
            return jsonify(respuesta_error("Error al registrar el movimiento")), 500
    except Exception as e:
        return jsonify(respuesta_error(str(e))), 500


# ===================================
# ENDPOINTS DE TRAZABILIDAD
# ===================================

@app.route('/api/trazabilidad/<codigo>')
def api_trazabilidad(codigo):
    """Obtiene la trazabilidad completa de un paquete"""
    try:
        if not validar_codigo(codigo):
            return jsonify(respuesta_error("Código de paquete inválido")), 400
        
        historial = obtener_historial_completo(codigo)
        if not historial:
            return jsonify(respuesta_error("No se encontró historial para el paquete")), 404
        
        return jsonify(respuesta_ok({
            "codigo": codigo,
            "historial": historial
        }))
    except Exception as e:
        return jsonify(respuesta_error(str(e))), 500


@app.route('/trazabilidad/<codigo>')
def trazabilidad(codigo):
    if not validar_codigo(codigo):
        return jsonify({"error": "Código inválido"})
    resultado = obtener_trazabilidad(codigo)
    return jsonify(resultado)


@app.route('/api/pendientes')
def api_pendientes():
    """Obtiene operaciones pendientes"""
    try:
        pendientes = obtener_pendientes()
        return jsonify(respuesta_ok(pendientes))
    except Exception as e:
        return jsonify(respuesta_error(str(e))), 500


@app.route('/pendientes')
def pendientes():
    return jsonify(obtener_pendientes())


@app.route('/api/actualizar_estado', methods=['PUT'])
def api_actualizar_estado():
    """Actualiza el estado de un paquete"""
    try:
        data = request.json
        codigo = data.get('codigo')
        estado = data.get('estado')
        
        if not codigo or not estado:
            return jsonify(respuesta_error("Parámetros requeridos: codigo, estado")), 400
        
        actualizado = actualizar_estado(codigo, estado)
        if actualizado:
            return jsonify(respuesta_ok({"mensaje": "Estado actualizado exitosamente"}))
        else:
            return jsonify(respuesta_error("Paquete no encontrado")), 404
    except Exception as e:
        return jsonify(respuesta_error(str(e))), 500


@app.route('/actualizar_estado', methods=['PUT'])
def cambiar_estado():
    data = request.json
    codigo = data['codigo']
    estado = data['estado']
    actualizado = actualizar_estado(codigo, estado)
    if actualizado:
        return jsonify({"mensaje": "Estado actualizado"})
    return jsonify({"error": "No encontrado"})


@app.route('/estado_nodos')
def estado_nodos():
    return jsonify(obtener_estado_nodos())


# @app.route('/metricas')
# def metricas():
#     return jsonify(obtener_metricas())


# @app.route('/dashboard')
# def dashboard():
#     return jsonify(construir_dashboard())


@app.route('/fragmentos')
def fragmentos():
    return jsonify(obtener_fragmentos())


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


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )