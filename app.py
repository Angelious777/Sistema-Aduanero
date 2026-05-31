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

# -----------------------------------

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )