# -----------------------------------
# RESPUESTA OK
# -----------------------------------

def respuesta_ok(datos):

    return {

        "success": True,
        "data": datos
    }

# -----------------------------------
# RESPUESTA ERROR
# -----------------------------------

def respuesta_error(mensaje):

    return {

        "success": False,
        "error": mensaje
    }