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
from movimientos import registrar_movimiento, obtener_movimientos_paquete, obtener_todos_movimientos, actualizar_estado_movimiento, obtener_historial_completo
from catalogo import obtener_fragmentos
from respuestas import respuesta_ok, respuesta_error
from logs.logger import registrar_log

app = Flask(__name__)
CORS(app)

@app.route('/')
def inicio():

    return render_template(
        'index.html'
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


@app.route('/api/paquete/crear', methods=['POST'])
def api_crear_paquete():
    """Crea un nuevo paquete"""
    try:
        data = request.json
        codigo = data.get('codigo')
        destino = data.get('destino')
        prioridad = data.get('prioridad', 'Media')
        nodo = data.get('nodo')
        
        if not codigo or not destino or not nodo:
            return jsonify(respuesta_error("Parámetros requeridos: codigo, destino, nodo")), 400
        
        if not validar_codigo(codigo):
            return jsonify(respuesta_error("Código de paquete inválido")), 400
        
        exito = crear_paquete(codigo, destino, prioridad, nodo)
        if exito:
            registrar_log(f"Paquete {codigo} creado en {nodo}")
            return jsonify(respuesta_ok({"mensaje": "Paquete creado exitosamente"}))
        else:
            return jsonify(respuesta_error("Error al crear el paquete")), 500
    except Exception as e:
        return jsonify(respuesta_error(str(e))), 500


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

# -----------------------------------
# TRAZABILIDAD GLOBAL (ANTIGUO)
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
# OPERACIONES PENDIENTES
# -----------------------------------

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

# -----------------------------------
# ACTUALIZAR ESTADO
# -----------------------------------

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

# ===================================
# ENDPOINTS DE CATALOGO
# ===================================

@app.route('/api/catalogo')
def api_catalogo():
    """Obtiene el catálogo de fragmentos"""
    try:
        fragmentos = obtener_fragmentos()
        return jsonify(respuesta_ok(fragmentos))
    except Exception as e:
        return jsonify(respuesta_error(str(e))), 500


# ===================================
# INICIO DE LA APLICACION
# ===================================

if __name__ == '__main__':
    registrar_log("Iniciando aplicación del Sistema Aduanero Distribuido")
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
