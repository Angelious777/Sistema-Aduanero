cola_pendientes = []

# -----------------------------------
# GUARDAR OPERACION
# -----------------------------------

def guardar_operacion(operacion):

    cola_pendientes.append(operacion)

# -----------------------------------
# VER OPERACIONES
# -----------------------------------

def obtener_pendientes():

    return cola_pendientes

# -----------------------------------
# SINCRONIZAR
# -----------------------------------

def sincronizar():

    while len(cola_pendientes) > 0:

        operacion = cola_pendientes.pop(0)

        print(
            "Sincronizando:",
            operacion
        )

# -----------------------------------
# CONTAR PENDIENTES
# -----------------------------------

def cantidad_pendientes():

    return len(cola_pendientes)