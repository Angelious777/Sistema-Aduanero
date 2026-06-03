# 202606030621 
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from consultas import obtener_trazabilidad
from sincronizacion import sincronizar_clientes_master, sincronizar_estados_master
from actualizaciones import actualizar_estado
from monitor import obtener_estado_nodos
from metricas import obtener_metricas, obtener_metricas_nodo
from dashboard import construir_dashboard
from validaciones import validar_codigo
from paquetes import obtener_todos_paquetes, obtener_paquetes_por_nodo, crear_paquete, obtener_tabla_paquete, obtener_tabla_movimiento, obtener_tabla_paquete_financiero, buscar_paquete, obtener_paquetes_coordinador_central, obtener_historial_movimientos_paquete
from paquetes import obtener_paquetes_por_tipo_nodo, actualizar_estado_distribuido, insertar_en_central
from clientes import obtener_clientes_global, registrar_cliente_nodo  # <-- Asegúrate de tener o mapear esta función
from movimientos import registrar_movimiento, obtener_movimientos_paquete, obtener_todos_movimientos, actualizar_estado_movimiento, obtener_historial_completo, obtener_movimientos_tabla_global
from catalogo import obtener_fragmentos
from respuestas import respuesta_ok, respuesta_error
from logs.logger import registrar_log
from conexiones import conectar_lp, conectar_scz, conectar_central
from clientes import obtener_clientes_local_lp, obtener_clientes_local_scz, obtener_clientes_local_central
from almacenes import obtener_almacenes_global, registrar_almacen_nodo, modificar_almacen_nodo, eliminar_almacen_nodo, sincronizar_almacenes_cascada
from rutas import obtener_rutas_global, registrar_ruta_nodo, modificar_ruta_nodo, eliminar_ruta_nodo, sincronizar_rutas_cascada
import logging

def respuesta_ok(data): return {"success": True, "data": data}
def respuesta_error(msg): return {"success": False, "error": msg}
def registrar_log(msg): print(f"[LOG SYSTEM]: {msg}")


# 1. Importamos el Blueprint que contiene todas las rutas y mocks del Coordinador
from routes.coordinador import coordinador_bp

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Servidor_Coordinador")
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

@app.route('/api/dashboard/metricas', methods=['GET'])
def api_dashboard_metricas():
    # Captura el parámetro de la URL, por defecto va a 'la_paz'
    nodo_solicitado = request.args.get('nodo', 'la_paz')
    
    # Normaliza guiones medios a guiones bajos para que coincida con el diccionario de mapeo
    nodo_solicitado = nodo_solicitado.replace('-', '_')
    
    try:
        # Ejecución analítica directa hacia el clúster
        resultado_analitica = obtener_metricas_nodo(nodo_solicitado)
        
        if not resultado_analitica or not resultado_analitica.get("success", False):
            # Si el diccionario interno reporta éxito falso, maneja el error correspondiente
            error_msg = resultado_analitica.get("error", "Error desconocido en el fragmento regional.")
            return jsonify({"success": False, "error": error_msg}), 400
            
        return jsonify(resultado_analitica)
        
    except Exception as e:
        logger.error(f"🚨 Error crítico en el ruteador de la API: {str(e)}")
        return jsonify({"success": False, "error": "Fallo interno en el servidor de coordinación."}), 500


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
    """Obtiene todos los paquetes reconstruidos desde el Nodo Central
    mapeando almacenes, estados, clientes y ciudades de origen/destino.
    """
    try:
        paquetes = obtener_paquetes_coordinador_central()
        return jsonify(respuesta_ok(paquetes)), 200
    except Exception as e:
        registrar_log(f"❌ Error al reconstruir paquetes globales: {e}")
        return jsonify(respuesta_error(str(e))), 500

@app.route('/api/paquetes/historial/<id_paquete>')
def api_historial_paquete_central(id_paquete):
    """Devuelve la traza cronológica de movimientos de un paquete para la 
    tabla de auditoría interna del modal en el Nodo Coordinador.
    """
    try:
        
        historial = obtener_historial_movimientos_paquete(id_paquete)
        return jsonify(respuesta_ok(historial)), 200
    except Exception as e:
        registrar_log(f"❌ Error al consultar la traza del paquete {id_paquete}: {e}")
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
    """
    Ruta federada que sirve los datos de clientes según el nodo solicitante.
    Maneja la autonomía regional (LP/SCZ) y la unificación del Nodo Central.
    """
    nodo = request.args.get('nodo', 'global')
    try:
        if nodo == "nodo_lp":
            # Autonomía de La Paz (PostgreSQL) - Retorna datos públicos locales
            datos_clientes = obtener_clientes_local_lp()
            
        elif nodo == "nodo_scz":
            # Autonomía de Santa Cruz (SQL Server Regional) - Retorna datos públicos locales
            datos_clientes = obtener_clientes_local_scz()
            
        else:
            # Autonomía del Nodo Central (SQL Server Master unificado con INNER JOIN)
            datos_clientes = obtener_clientes_local_central()
            
        return jsonify({"success": True, "data": datos_clientes}), 200
        
    except Exception as e:
        return jsonify({
            "success": False, 
            "error": f"Error al consultar la infraestructura distribuida en el nodo '{nodo}': {str(e)}"
        }), 500


@app.route('/api/clientes/sincronizar', methods=['POST'])
def api_sincronizar_clientes():
    # Llamada directa al script especializado
    resultado = sincronizar_clientes_master()
    
    if resultado.get("success"):
        return jsonify(resultado), 200
    else:
        return jsonify(resultado), 500



@app.route('/api/paquete/buscar/<codigo>', methods=['GET'])
def api_buscar_paquete(codigo):
    """
    Busca un paquete por código de rastreo único (Ej: PK-LP-2026-001).
    Valida la nomenclatura y consulta los fragmentos horizontales/verticales.
    """
    try:
        # Validación de nomenclatura formal del paquete
        if not validar_codigo(codigo):
            return jsonify(respuesta_error("Código de paquete inválido o formato incorrecto")), 400
        
        # Recuperación del diccionario de datos del paquete
        paquete = buscar_paquete(codigo)
        if not paquete:
            return jsonify(respuesta_error(f"El paquete con código '{codigo}' no fue localizado en ningún nodo")), 404
        
        return jsonify(respuesta_ok(paquete)), 200
        
    except Exception as e:
        return jsonify(respuesta_error(f"Fallo crítico en el motor de búsqueda federada: {str(e)}")), 500

@app.route('/api/paquete/actualizar-estado', methods=['PUT'])
def api_actualizar_estado_paquete():
    try:
        data = request.json
        id_pkt = data.get('id_paquete')     # Recibe el UUID/GUID
        nuevo_estado = data.get('id_estado') # Recibe el Int (1 al 5)
        nodo_actual = data.get('nodo')       # Nodo desde el que se envía la petición

        # 1. Determinar cuál es el nodo origen y cuál el nodo destino
        # Consultamos el id_ruta del paquete en el nodo que hace la petición
        id_ruta = None
        if nodo_actual == "santa_cruz":
            conn_origen = conectar_scz()
            cursor_origen = conn_origen.cursor()
            cursor_origen.execute("SELECT id_ruta FROM PAQUETE_OPERATIVO_SCZ WHERE id_paquete = ?", (id_pkt,))
            fila = cursor_origen.fetchone()
            if fila: id_ruta = fila[0]
            cursor_origen.close()
            conn_origen.close()
        else:
            conn_origen = conectar_lp()
            cursor_origen = conn_origen.cursor()
            cursor_origen.execute('SELECT id_ruta FROM "paquete_operativo_lp" WHERE id_paquete = %s', (id_pkt,))
            fila = cursor_origen.fetchone()
            if fila: id_ruta = fila[0]
            cursor_origen.close()
            conn_origen.close()

        # Si el paquete no se encuentra en el nodo actual, cancelamos para evitar inconsistencias
        if id_ruta is None:
            return jsonify({"success": False, "error": "No se encontró el paquete en el nodo origen para determinar la ruta"}), 404

        # Deducir el nodo destino basándonos en tu lógica de negocio de rutas:
        # Ruta 1: LP -> SCZ (Destino Santa Cruz)
        # Ruta 2: SCZ -> LP (Destino La Paz)
        nodo_destino = "santa_cruz" if id_ruta == 1 else "la_paz"

        # 2. EJECUTAR EL UPDATE EN EL NODO ACTUAL (Origen)
        if nodo_actual == "santa_cruz":
            conn_act = conectar_scz()
            cursor_act = conn_act.cursor()
            cursor_act.execute("UPDATE PAQUETE_OPERATIVO_SCZ SET id_estado = ? WHERE id_paquete = ?", (nuevo_estado, id_pkt))
        else:
            conn_act = conectar_lp()
            cursor_act = conn_act.cursor()
            cursor_act.execute('UPDATE "paquete_operativo_lp" SET id_estado = %s WHERE id_paquete = %s', (nuevo_estado, id_pkt))
        conn_act.commit()
        cursor_act.close()
        conn_act.close()

        # 3. EJECUTAR EL UPDATE EN EL NODO DESTINO (Si es diferente al nodo actual)
        if nodo_actual != nodo_destino:
            try:
                if nodo_destino == "santa_cruz":
                    conn_dest = conectar_scz()
                    cursor_dest = conn_dest.cursor()
                    cursor_dest.execute("UPDATE PAQUETE_OPERATIVO_SCZ SET id_estado = ? WHERE id_paquete = ?", (nuevo_estado, id_pkt))
                else:
                    conn_dest = conectar_lp()
                    cursor_dest = conn_dest.cursor()
                    cursor_dest.execute('UPDATE "paquete_operativo_lp" SET id_estado = %s WHERE id_paquete = %s', (nuevo_estado, id_pkt))
                conn_dest.commit()
                cursor_dest.close()
                conn_dest.close()
            except Exception as dest_err:
                # Al ser un entorno distribuido, registramos si el otro nodo regional está caído temporalmente
                print(f"⚠️ Alerta: Nodo destino ({nodo_destino}) inaccesible para actualización: {dest_err}")

        # 4. Replicar la actualización al Nodo Central de control global (Tu código original intacto)
        try:
            conn_cen = conectar_central()
            cursor_cen = conn_cen.cursor()
            cursor_cen.execute("UPDATE PAQUETE_GLOBAL SET id_estado = ? WHERE id_paquete = ?", (nuevo_estado, id_pkt))
            conn_cen.commit()
            cursor_cen.close()
            conn_cen.close()
        except Exception as cen_err:
            print(f"⚠️ Alerta: Nodo Central inaccesible para replicación asíncrona: {cen_err}")

        return jsonify({"success": True, "mensaje": "Estado actualizado con éxito en el clúster"}), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

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
    """
    Orquesta la creación de un paquete de manera distribuida.
    Garantiza: Central (Global), Nodo Origen (Operativo + Financiero), Nodo Destino (Solo Operativo)
    """
    try:
        data = request.json or {}
        
        # 1. Extracción y Normalización de Datos del Payload JS
        codigo = data.get('codigo')
        id_ruta = data.get('id_ruta')       # Viaja como el destino/ID de ruta en el ruteador
        prioridad = data.get('prioridad', 'Normal')
        nodo_origen = data.get('nodo')      # 'lp', 'scz', 'la_paz', etc.
        
        remitente = data.get('id_cliente_remitente')
        destinatario = data.get('id_cliente_destinatario')
        descripcion = data.get('descripcion', '')
        
        # 2. Casteo Seguro de Magnitudes Físicas y Financieras (Evita caídas por strings vacíos)
        peso = float(data.get('peso', 0.0))
        volumen = float(data.get('volumen', 0.0))
        valor_declarado = float(data.get('valor_declarado', 0.0))
        seguro = float(data.get('seguro', 0.0))
        costo_envio = float(data.get('costo', 0.0)) # Mapea 'costo' del JS a 'costo_envio'

        # Validation de Campos Not Null
        if not all([codigo, id_ruta, nodo_origen, remitente, destinatario]):
            return jsonify(respuesta_error("Faltan campos obligatorios para procesar la inserción fragmentada.")), 400

        # 3. Delegación al Orquestador de paquetes.py
        # Esta única llamada procesa la transacción en todo el Clúster Híbrido
        exito = crear_paquete(
            codigo=codigo,
            destino=id_ruta,
            prioridad=prioridad,
            nodo=nodo_origen,
            remitente=remitente,
            destinatario=destinatario,
            descripcion=descripcion,
            peso=peso,
            volumen=volumen,
            valor_declarado=valor_declarado,
            seguro=seguro,
            costo_envio=costo_envio
        )

        if exito:
            registrar_log(f"📦 Transacción Distribuida Exitosa. Paquete {codigo} replicado parcialmente.")
            return jsonify(respuesta_ok({"mensaje": "Transacción distribuida realizada con éxito en el clúster"})), 200
        else:
            return jsonify(respuesta_error("El orquestador no pudo completar las inserciones regionales.")), 500

    except ValueError as val_err:
        registrar_log(f"⚠️ Error de topología: {val_err}")
        return jsonify(respuesta_error(str(val_err))), 422
    except Exception as e:
        registrar_log(f"❌ Fallo crítico en el clúster al crear paquete: {e}")
        return jsonify(respuesta_error(f"Fallo crítico en el motor de persistencia: {str(e)}")), 500


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

@app.route('/api/movimientos', methods=['GET'])
def api_movimientos_globales():
    nodo = request.args.get('nodo', 'global')
    datos = obtener_movimientos_tabla_global(nodo_filtro=nodo)
    return jsonify({"success": True, "data": datos})

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


# @app.route('/api/pendientes')
# def api_pendientes():
#     """Obtiene operaciones pendientes"""
#     try:
#         pendientes = obtener_pendientes()
#         return jsonify(respuesta_ok(pendientes))
#     except Exception as e:
#         return jsonify(respuesta_error(str(e))), 500


# @app.route('/pendientes')
# def pendientes():
#     return jsonify(obtener_pendientes())


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

# ==============================================================================
# ENDPOINTS DE LECTURA (REGIONAL Y GLOBAL)
# ==============================================================================

@app.route('/api/almacenes/<nodo>', methods=['GET'])
def api_listar_almacenes_regional(nodo):
    """Consulta la tabla local de un fragmento regional específico."""
    try:
        token = nodo.lower().strip().replace('-', '_')
        lista_almacenes = []
        query_completa = "SELECT id_almacen, nombre, ciudad, direccion, nodo_responsable FROM almacen"

        if "santa" in token or "scz" in token:
            conn = conectar_scz()
        else:
            conn = conectar_lp()
            
        cursor = conn.cursor()
        cursor.execute(query_completa)
        for row in cursor.fetchall():
            lista_almacenes.append({
                "id_almacen": row[0], "nombre": row[1], "ciudad": row[2], "direccion": row[3], "nodo_responsable": row[4]
            })
        cursor.close()
        conn.close()
        return jsonify({"success": True, "data": lista_almacenes}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/almacen/listar', methods=['GET'])
def api_listar_almacenes_global():
    try:
        almacenes = obtener_almacenes_global() 
        return jsonify({"success": True, "data": almacenes}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/almacen/crear', methods=['POST'])
def api_crear_almacen():
    try:
        data = request.json or {}
        id_almacen = data.get('id_almacen')
        nombre = data.get('nombre')
        ciudad = data.get('ciudad')
        direccion = data.get('direccion')
        nodo_responsable = data.get('nodo_responsable')

        exito = registrar_almacen_nodo(id_almacen, nombre, ciudad, direccion, nodo_responsable)
        if exito:
            return jsonify({"success": True, "mensaje": "Almacén creado globalmente."}), 200
        return jsonify({"success": False, "error": "Llave duplicada o falla de red."}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/almacen/editar', methods=['POST'])
def api_editar_almacen():
    try:
        data = request.json or {}
        id_almacen = data.get('id_almacen')
        nombre = data.get('nombre')
        ciudad = data.get('ciudad')
        direccion = data.get('direccion')
        nodo_responsable = data.get('nodo_responsable')

        exito = modificar_almacen_nodo(id_almacen, nombre, ciudad, direccion, nodo_responsable)
        if exito:
            return jsonify({"success": True, "mensaje": "Almacén actualizado globalmente."}), 200
        return jsonify({"success": False, "error": "No se pudo actualizar."}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/almacen/eliminar', methods=['POST'])
def api_eliminar_almacen():
    try:
        data = request.json or {}
        id_almacen = data.get('id_almacen')
        exito = eliminar_almacen_nodo(id_almacen)
        if exito:
            return jsonify({"success": True, "mensaje": "Almacén eliminado globalmente."}), 200
        return jsonify({"success": False, "error": "Error al eliminar."}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/almacen/sincronizar', methods=['POST'])
def api_sincronizar_almacenes():
    try:
        if sincronizar_almacenes_cascada():
            return jsonify({"success": True, "mensaje": "Catálogos alineados."}), 200
        return jsonify({"success": False, "error": "Sincronización fallida."}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

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


@app.route('/api/estados', methods=['GET'])
def api_listar_estados():
    """
    Obtiene el catálogo de estados desde el nodo central o regional 
    para poblar dinámicamente las vistas y modales.
    """
    try:
        # Reutilizamos la conexión al central ya que replica el catálogo
        conn = conectar_central()
        cursor = conn.cursor()
        cursor.execute("SELECT id_estado, nombre FROM estado ORDER BY id_estado")
        
        estados = []
        for row in cursor.fetchall():
            estados.append({
                "id_estado": int(row[0]),
                "nombre": str(row[1])
            })
            
        cursor.close()
        conn.close()
        return jsonify({"success": True, "data": estados}), 200
    except Exception as e:
        registrar_log(f"❌ Error al consultar catálogo de estados: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/estado/crear', methods=['POST'])
def api_crear_estado():
    try:
        data = request.json
        id_estado = data.get('id_estado')
        nombre = data.get('nombre')

        if not id_estado or not nombre:
            return jsonify({"success": False, "error": "Faltan parámetros requeridos"}), 400

        # 1. Insertar en el Nodo Central (Fuente de Verdad)
        conn_cen = conectar_central()
        cursor_cen = conn_cen.cursor()
        cursor_cen.execute("INSERT INTO estado (id_estado, nombre) VALUES (?, ?)", (id_estado, nombre))
        conn_cen.commit()
        cursor_cen.close()
        conn_cen.close()

        # 2. Replicación Inmediata a Nodos Regionales (Opcional/Síncrona)
        # Para evitar que dependas de que los nodos estén 100% online en este segundo, 
        # envolvemos la inserción directa en bloques try-catch individuales.
        try:
            conn_lp = conectar_lp()
            cursor_lp = conn_lp.cursor()
            cursor_lp.execute('INSERT INTO estado (id_estado, nombre) VALUES (%s, %s)', (id_estado, nombre))
            conn_lp.commit()
            cursor_lp.close()
            conn_lp.close()
        except Exception as e:
            registrar_log(f"⚠️ Réplica diferida en La Paz para ID {id_estado}: {e}")

        try:
            conn_scz = conectar_scz()
            cursor_scz = conn_scz.cursor()
            cursor_scz.execute("INSERT INTO ESTADO (id_estado, nombre) VALUES (?, ?)", (id_estado, nombre))
            conn_scz.commit()
            cursor_scz.close()
            conn_scz.close()
        except Exception as e:
            registrar_log(f"⚠️ Réplica diferida en Santa Cruz para ID {id_estado}: {e}")

        return jsonify({"success": True, "mensaje": "Estado catalogado con éxito"}), 201

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/estado/eliminar/<int:id_estado>', methods=['DELETE'])
def api_eliminar_estado(id_estado):
    try:
        # Eliminamos secuencialmente de todas las fuentes empezando por el Central
        conn_cen = conectar_central()
        cursor_cen = conn_cen.cursor()
        cursor_cen.execute("DELETE FROM estado WHERE id_estado = ?", (id_estado,))
        conn_cen.commit()
        cursor_cen.close()
        conn_cen.close()

        # Limpiamos los fragmentos regionales
        try:
            conn_lp = conectar_lp()
            cursor_lp = conn_lp.cursor()
            cursor_lp.execute('DELETE FROM estado WHERE id_estado = %s', (id_estado,))
            conn_lp.commit()
            cursor_lp.close()
            conn_lp.close()
        except Exception as e: registrar_log(f"No se pudo limpiar ID {id_estado} en LP: {e}")

        try:
            conn_scz = conectar_scz()
            cursor_scz = conn_scz.cursor()
            cursor_scz.execute("DELETE FROM ESTADO WHERE id_estado = ?", (id_estado,))
            conn_scz.commit()
            cursor_scz.close()
            conn_scz.close()
        except Exception as e: registrar_log(f"No se pudo limpiar ID {id_estado} en SCZ: {e}")

        return jsonify({"success": True, "mensaje": "Estado eliminado del clúster"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/estados/sincronizar-cascada', methods=['POST'])
def api_sincronizar_estados_cascada():
    """
    Ruta que manda a llamar la reconciliación analítica estructurada 
    dentro de sincronizacion.py para el catálogo de estados.
    """
    resultado = sincronizar_estados_master()
    
    if resultado.get("success"):
        # Construimos un desglose visual amigable basado en tu reporte por tuplas
        resumen_lineas = []
        for nodo, info in resultado["reporte"].items():
            resumen_lineas.append(
                f"📌 {nodo.upper()}: {info['estado']} (Ins: {info['inserciones']}, Mod: {info['modificaciones']}, Del: {info['eliminaciones']})"
            )
        mensaje_final = f"{resultado['nota']}\n" + "\n".join(resumen_lineas)
        
        return jsonify({"success": True, "mensaje": mensaje_final}), 200
    else:
        return jsonify({"success": False, "error": resultado.get("error", "Error desconocido de clúster")}), 500


@app.route('/api/rutas/<nodo>', methods=['GET'])
def api_listar_rutas_regional(nodo):
    try:
        token = nodo.lower().strip().replace('-', '_')
        lista_rutas = []
        query = "SELECT id_ruta, id_almacen_origen, id_almacen_destino, descripcion FROM ruta"

        if "santa" in token or "scz" in token:
            conn = conectar_scz()
        else:
            conn = conectar_lp()
            
        cursor = conn.cursor()
        cursor.execute(query)
        for row in cursor.fetchall():
            lista_rutas.append({
                "id_ruta": row[0], 
                "id_almacen_origen": row[1], 
                "id_almacen_destino": row[2], 
                "descripcion": row[3]
            })
        cursor.close()
        conn.close()
        return jsonify({"success": True, "data": lista_rutas}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/ruta/listar', methods=['GET'])
def api_listar_rutas_global():
    try:
        rutas = obtener_rutas_global()
        return jsonify({"success": True, "data": rutas}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/ruta/crear', methods=['POST'])
def api_crear_ruta():
    try:
        data = request.json or {}
        id_ruta = data.get('id_ruta')
        id_origen = data.get('id_almacen_origen')
        id_destino = data.get('id_almacen_destino')
        descripcion = data.get('descripcion')

        if registrar_ruta_nodo(id_ruta, id_origen, id_destino, descripcion):
            return jsonify({"success": True, "mensaje": "Ruta propagada con éxito."}), 200
        return jsonify({"success": False, "error": "Falla de claves: Asegúrate que los IDs de almacén existan y que no se repita el par Origen-Destino."}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/ruta/editar', methods=['POST'])
def api_editar_ruta():
    try:
        data = request.json or {}
        id_ruta = data.get('id_ruta')
        id_origen = data.get('id_almacen_origen')
        id_destino = data.get('id_almacen_destino')
        descripcion = data.get('descripcion')

        if modificar_ruta_nodo(id_ruta, id_origen, id_destino, descripcion):
            return jsonify({"success": True, "mensaje": "Modificación aplicada globalmente."}), 200
        return jsonify({"success": False, "error": "No se pudo actualizar."}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/ruta/eliminar', methods=['POST'])
def api_eliminar_ruta():
    try:
        data = request.json or {}
        if eliminar_ruta_nodo(data.get('id_ruta')):
            return jsonify({"success": True, "mensaje": "Trayecto revocado de la red."}), 200
        return jsonify({"success": False, "error": "Error al eliminar."}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/ruta/sincronizar', methods=['POST'])
def api_sincronizar_rutas():
    try:
        if sincronizar_rutas_cascada():
            return jsonify({"success": True, "mensaje": "Catálogos de rutas alineados con éxito."}), 200
        return jsonify({"success": False, "error": "Falla en reconciliación forzada."}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )