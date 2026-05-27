from flask import Flask, jsonify
from consultas import obtener_trazabilidad
from sincronizacion import obtener_pendientes

app = Flask(__name__)

# -----------------------------------
# TRAZABILIDAD GLOBAL
# -----------------------------------

@app.route('/trazabilidad/<codigo>')
def trazabilidad(codigo):

    resultado = obtener_trazabilidad(codigo)

    return jsonify(resultado)

# -----------------------------------
# OPERACIONES PENDIENTES
# -----------------------------------

@app.route('/pendientes')
def pendientes():

    return jsonify(obtener_pendientes())

# -----------------------------------

if __name__ == '__main__':

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )