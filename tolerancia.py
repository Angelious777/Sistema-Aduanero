NODOS_ACTIVOS = {

    "La Paz": True,
    "Santa Cruz": True
}

# -----------------------------------
# DESACTIVAR NODO
# -----------------------------------

def desactivar_nodo(nombre):

    NODOS_ACTIVOS[nombre] = False

# -----------------------------------
# ACTIVAR NODO
# -----------------------------------

def activar_nodo(nombre):

    NODOS_ACTIVOS[nombre] = True