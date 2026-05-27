from flask import Flask, jsonify, request
from consultas import obtener_trazabilidad
from sincronizacion import obtener_pendientes
from actualizaciones import actualizar_estado
from monitor import obtener_estado_nodos
from metricas import obtener_metricas
from dashboard import construir_dashboard
from validaciones import validar_codigo

app = Flask(__name__)

# -----------------------------------
# TRAZABILIDAD GLOBAL
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

@app.route('/pendientes')
def pendientes():

    return jsonify(obtener_pendientes())

# -----------------------------------
# ACTUALIZAR ESTADO
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

# -----------------------------------

if __name__ == '__main__':

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )